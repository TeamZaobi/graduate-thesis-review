#!/usr/bin/env python3
from __future__ import annotations

import re


RELEASE_GATE_FIELDS = [
    "can_emit_problem_list",
    "can_emit_execution_outputs",
    "can_issue_readiness_verdict",
    "can_enter_line_editing",
]

RELEASE_GATE_META_FIELDS = [
    "scope_frozen",
    "deep_review_status",
    "coverage_status",
]

RELEASE_GATE_ALLOWED_VALUES = {"yes", "no", "pending", "blocked"}
RELEASE_GATE_EXPLICIT_VALUES = {"yes", "no", "blocked"}

RELEASE_GATE_LIST_FIELDS = [
    "blockers",
    "allowed_next_steps",
    "forbidden_outputs",
]

SUBSTANTIVE_TEXT_RE = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")


def substantive_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("<!--"):
            continue
        if line in {"---", "..."}:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("```"):
            continue
        if set(line) <= {"|", "-", ":", " "}:
            continue
        if SUBSTANTIVE_TEXT_RE.search(line):
            lines.append(line)
    return lines


def extract_release_gate_flags_from_markdown(text: str) -> dict[str, str | None]:
    flags: dict[str, str | None] = {field: None for field in RELEASE_GATE_FIELDS}

    for field in RELEASE_GATE_FIELDS:
        inline_match = re.search(
            rf"{re.escape(field)}\s*[:：=]\s*([A-Za-z_]+)",
            text,
            flags=re.IGNORECASE,
        )
        if inline_match:
            value = inline_match.group(1).lower()
            if value in RELEASE_GATE_ALLOWED_VALUES:
                flags[field] = value
                continue

        heading_match = re.search(
            rf"^##\s*{re.escape(field)}\s*$([\s\S]*?)(?=^##\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if not heading_match:
            continue
        for line in substantive_lines(heading_match.group(1)):
            value = line.strip("`").lower()
            if value in RELEASE_GATE_ALLOWED_VALUES:
                flags[field] = value
                break

    return flags


def extract_release_gate_block(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return None
    gate = payload.get("release_gate")
    return gate if isinstance(gate, dict) else None


def extract_release_gate_flags_from_manifest(
    payload: dict | None,
) -> dict[str, str | None]:
    flags: dict[str, str | None] = {field: None for field in RELEASE_GATE_FIELDS}
    gate = extract_release_gate_block(payload)
    if gate is None:
        return flags

    for field in RELEASE_GATE_FIELDS:
        value = gate.get(field)
        if value in RELEASE_GATE_ALLOWED_VALUES:
            flags[field] = value
    return flags


def extract_release_gate_lists_from_manifest(
    payload: dict | None,
) -> dict[str, list[str] | None]:
    values: dict[str, list[str] | None] = {
        field: None for field in RELEASE_GATE_LIST_FIELDS
    }
    gate = extract_release_gate_block(payload)
    if gate is None:
        return values

    for field in RELEASE_GATE_LIST_FIELDS:
        value = gate.get(field)
        if isinstance(value, list):
            values[field] = value
    return values


def has_explicit_release_gate_authority(flags: dict[str, str | None]) -> bool:
    return any(value in RELEASE_GATE_EXPLICIT_VALUES for value in flags.values())


def manifest_release_gate_is_placeholder(payload: dict | None) -> bool:
    gate = extract_release_gate_block(payload)
    if gate is None:
        return False

    flags = extract_release_gate_flags_from_manifest(payload)
    if has_explicit_release_gate_authority(flags):
        return False

    meta_pending = True
    for field in RELEASE_GATE_META_FIELDS:
        value = gate.get(field)
        if value not in {None, "", "pending"}:
            meta_pending = False
            break

    lists_empty = True
    for field in RELEASE_GATE_LIST_FIELDS:
        value = gate.get(field)
        if isinstance(value, list) and not value:
            continue
        lists_empty = False
        break

    return meta_pending and lists_empty
