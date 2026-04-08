#!/usr/bin/env python3
from __future__ import annotations

import re


SPECIALTY_GATE_STATUS_FIELDS = [
    "specialty_readiness",
    "discipline_register_status",
]

SPECIALTY_GATE_BOOLEAN_FIELDS = [
    "independent_audit_required",
]

SPECIALTY_GATE_STATUS_VALUES = {"complete", "partial", "missing", "pending"}
SPECIALTY_GATE_EXPLICIT_STATUS_VALUES = {"complete", "partial", "missing"}
SPECIALTY_GATE_BOOLEAN_VALUES = {"yes", "no", "pending"}
SPECIALTY_GATE_EXPLICIT_BOOLEAN_VALUES = {"yes", "no"}

SPECIALTY_GATE_LIST_FIELDS = [
    "domain_stack",
    "supporting_loops",
    "matched_manuals",
    "required_expert_checks",
]

SPECIALTY_GATE_STRING_FIELDS = [
    "primary_loop",
    "next_action",
]

SPECIALTY_GATE_FIELD_ALIASES = {
    "specialty_readiness": [
        "完备性结论",
        "specialty_readiness",
        "specialty_status",
        "manual_readiness",
    ],
    "discipline_register_status": [
        "discipline_register_status",
    ],
    "independent_audit_required": [
        "independent_audit_required",
    ],
    "domain_stack": [
        "domain_stack",
    ],
    "primary_loop": [
        "primary_loop",
    ],
    "supporting_loops": [
        "supporting_loops",
    ],
    "matched_manuals": [
        "命中的专项文件",
        "matched_manuals",
    ],
    "required_expert_checks": [
        "required_expert_checks",
    ],
    "next_action": [
        "下一动作",
        "next_action",
    ],
}

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


def extract_section_lines(text: str, field_names: list[str]) -> list[str]:
    for field_name in field_names:
        heading_match = re.search(
            rf"^##\s*{re.escape(field_name)}\s*$([\s\S]*?)(?=^##\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if not heading_match:
            continue
        return substantive_lines(heading_match.group(1))
    return []


def extract_scalar_value(
    text: str,
    field_names: list[str],
    allowed_values: set[str],
) -> str | None:
    for field_name in field_names:
        inline_match = re.search(
            rf"{re.escape(field_name)}\s*[:：=]\s*([A-Za-z_]+)",
            text,
            flags=re.IGNORECASE,
        )
        if inline_match:
            value = inline_match.group(1).lower()
            if value in allowed_values:
                return value

        for line in extract_section_lines(text, [field_name]):
            normalized = line.strip("`").lower()
            if normalized in allowed_values:
                return normalized
    return None


def extract_first_section_line(text: str, field_names: list[str]) -> str | None:
    for line in extract_section_lines(text, field_names):
        cleaned = line.strip("`").strip()
        if cleaned:
            return cleaned
    return None


def extract_list_value(text: str, field_names: list[str]) -> list[str]:
    items: list[str] = []
    for line in extract_section_lines(text, field_names):
        cleaned = re.sub(r"^[-*]\s*", "", line).strip().strip("`")
        cleaned = re.sub(r"^\d+[.)]\s*", "", cleaned).strip()
        if cleaned:
            items.append(cleaned)
    return items


def extract_specialty_gate_block(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return None
    gate = payload.get("specialty_gate")
    return gate if isinstance(gate, dict) else None


def extract_specialty_gate_flags_from_manifest(
    payload: dict | None,
) -> dict[str, str | None]:
    flags: dict[str, str | None] = {
        field: None
        for field in SPECIALTY_GATE_STATUS_FIELDS + SPECIALTY_GATE_BOOLEAN_FIELDS
    }
    gate = extract_specialty_gate_block(payload)
    if gate is None:
        return flags

    for field in SPECIALTY_GATE_STATUS_FIELDS:
        value = gate.get(field)
        if value in SPECIALTY_GATE_STATUS_VALUES:
            flags[field] = value
    for field in SPECIALTY_GATE_BOOLEAN_FIELDS:
        value = gate.get(field)
        if value in SPECIALTY_GATE_BOOLEAN_VALUES:
            flags[field] = value
    return flags


def extract_specialty_gate_lists_from_manifest(
    payload: dict | None,
) -> dict[str, list[str] | None]:
    values: dict[str, list[str] | None] = {
        field: None for field in SPECIALTY_GATE_LIST_FIELDS
    }
    gate = extract_specialty_gate_block(payload)
    if gate is None:
        return values

    for field in SPECIALTY_GATE_LIST_FIELDS:
        value = gate.get(field)
        if isinstance(value, list):
            values[field] = value
    return values


def extract_specialty_gate_strings_from_manifest(
    payload: dict | None,
) -> dict[str, str | None]:
    values: dict[str, str | None] = {
        field: None for field in SPECIALTY_GATE_STRING_FIELDS
    }
    gate = extract_specialty_gate_block(payload)
    if gate is None:
        return values

    for field in SPECIALTY_GATE_STRING_FIELDS:
        value = gate.get(field)
        if isinstance(value, str) and value.strip():
            values[field] = value.strip()
    return values


def extract_specialty_gate_flags_from_markdown(text: str) -> dict[str, str | None]:
    return {
        "specialty_readiness": extract_scalar_value(
            text,
            SPECIALTY_GATE_FIELD_ALIASES["specialty_readiness"],
            SPECIALTY_GATE_STATUS_VALUES,
        ),
        "discipline_register_status": extract_scalar_value(
            text,
            SPECIALTY_GATE_FIELD_ALIASES["discipline_register_status"],
            SPECIALTY_GATE_STATUS_VALUES,
        ),
        "independent_audit_required": extract_scalar_value(
            text,
            SPECIALTY_GATE_FIELD_ALIASES["independent_audit_required"],
            SPECIALTY_GATE_BOOLEAN_VALUES,
        ),
    }


def extract_specialty_gate_lists_from_markdown(text: str) -> dict[str, list[str]]:
    return {
        field: extract_list_value(text, SPECIALTY_GATE_FIELD_ALIASES[field])
        for field in SPECIALTY_GATE_LIST_FIELDS
    }


def extract_specialty_gate_strings_from_markdown(text: str) -> dict[str, str | None]:
    return {
        field: extract_first_section_line(text, SPECIALTY_GATE_FIELD_ALIASES[field])
        for field in SPECIALTY_GATE_STRING_FIELDS
    }


def has_explicit_specialty_gate_authority(
    flags: dict[str, str | None],
) -> bool:
    return any(
        flags.get(field) in SPECIALTY_GATE_EXPLICIT_STATUS_VALUES
        for field in SPECIALTY_GATE_STATUS_FIELDS
    )


def manifest_specialty_gate_is_placeholder(payload: dict | None) -> bool:
    gate = extract_specialty_gate_block(payload)
    if gate is None:
        return False

    flags = extract_specialty_gate_flags_from_manifest(payload)
    if has_explicit_specialty_gate_authority(flags):
        return False

    booleans_pending = True
    for field in SPECIALTY_GATE_BOOLEAN_FIELDS:
        value = gate.get(field)
        if value not in {None, "", "pending"}:
            booleans_pending = False
            break

    strings_empty = True
    for field in SPECIALTY_GATE_STRING_FIELDS:
        value = gate.get(field)
        if value in {None, ""}:
            continue
        strings_empty = False
        break

    lists_empty = True
    for field in SPECIALTY_GATE_LIST_FIELDS:
        value = gate.get(field)
        if isinstance(value, list) and not value:
            continue
        lists_empty = False
        break

    return booleans_pending and strings_empty and lists_empty
