#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from legacy_asset_paths import (
    canonical_manifest_path,
    inspect_legacy_compatibility,
    migrated_note_path,
    notes_dir,
    resolve_manifest_path,
)
from output_policy_utils import (
    advice_output_decisions,
    forbidden_transformation_rules,
    load_output_policy,
    load_review_verdict,
    validate_claim_ceiling_alignment,
    validate_output_policy,
)
from release_gate_utils import (
    RELEASE_GATE_ALLOWED_VALUES,
    RELEASE_GATE_FIELDS,
    RELEASE_GATE_LIST_FIELDS,
    RELEASE_GATE_META_FIELDS,
    extract_release_gate_block,
    extract_release_gate_flags_from_manifest,
    extract_release_gate_flags_from_markdown,
    has_explicit_release_gate_authority,
    manifest_release_gate_is_placeholder,
)
from runtime_pack_utils import inspect_runtime_pack_drift
from specialty_gate_utils import (
    SPECIALTY_GATE_BOOLEAN_FIELDS,
    SPECIALTY_GATE_EXPLICIT_BOOLEAN_VALUES,
    SPECIALTY_GATE_EXPLICIT_STATUS_VALUES,
    SPECIALTY_GATE_BOOLEAN_VALUES,
    SPECIALTY_GATE_LIST_FIELDS,
    SPECIALTY_GATE_STATUS_FIELDS,
    SPECIALTY_GATE_STATUS_VALUES,
    SPECIALTY_GATE_STRING_FIELDS,
    extract_specialty_gate_block,
    extract_specialty_gate_flags_from_manifest,
    extract_specialty_gate_flags_from_markdown,
    has_explicit_specialty_gate_authority,
    manifest_specialty_gate_is_placeholder,
)
from workflow_route_registry import (
    ENTRY_MODE_SET,
    RESUMABLE_ENTRY_MODES,
    STEP_STATUS_VALUES,
    WORKFLOW_ROUTE_CONTRACT_VERSION,
    build_workflow_route,
    derive_workflow_route_from_entry_mode,
    route_registry_entry,
    route_steps,
)


CORE_REQUIRED_REVIEW_FILES = [
    "review_version_manifest.json",
    "审阅对象冻结说明.md",
    "版本冻结与依赖回归台账.md",
    "关键数值与复算准入台账.md",
    "图表索引台账.md",
    "图表专项核查.md",
]

STRICT_GATE_REVIEW_FILES = [
    "评审闭环与放行判断.md",
]

STRICT_DISPLAY_REVIEW_FILES = [
    "audience_language_contract.md",
    "display_projection_schema.md",
]

REQUIRED_OBJECT_FILES = [
    "figures.json",
    "tables.json",
    "citations.json",
    "assets_manifest.json",
]

REQUIRED_DISPLAY_FILES = [
    "问题清单页.html",
    "完整评审页.html",
    "学生执行页.html",
    "导师汇报页.html",
]

ENTRY_MODES = ENTRY_MODE_SET

DISPLAY_CONTENT_HINTS = {
    "问题清单页.html": ["应如何处理"],
    "完整评审页.html": ["审阅步骤", "交稿前终检", "readiness"],
    "学生执行页.html": ["待人工回查"],
    "导师汇报页.html": ["答辩口径"],
}

SUBSTANTIVE_TEXT_RE = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")
PLACEHOLDER_TOKENS = [
    "TODO",
    "TBD",
    "待补",
    "占位",
    "to be filled",
]

EXECUTION_OUTPUT_FILES = [
    "最终可执行修改清单.md",
    "学生执行版修改清单.md",
    "导师汇报版摘要.md",
    "答辩口径.md",
]

LINE_EDITING_FILES = [
    "原子级修改建议.md",
    "证据绑定改写表.md",
    "论断-引文核查表.md",
]

SCOPED_REWRITE_TASK_CARD = "局部改写任务卡.md"

LINE_EDITING_PROMOTION_PATTERNS = [
    re.compile(r"可转入定向改稿"),
    re.compile(r"优先处理.*定向改稿"),
    re.compile(r"继续直接写.*改稿"),
    re.compile(r"直接写.*可替换改稿"),
    re.compile(r"进入逐段改稿"),
    re.compile(r"进入逐条改稿"),
    re.compile(r"进入导师式逐条改稿"),
]

READINESS_PROMOTION_PATTERNS = [
    re.compile(r"建议送审"),
    re.compile(r"建议答辩"),
    re.compile(r"具备送审条件"),
    re.compile(r"具备答辩条件"),
    re.compile(r"可直接送审"),
    re.compile(r"可直接答辩"),
]

NEGATION_TOKENS = [
    "暂不",
    "不建议",
    "不允许",
    "不得",
    "不能",
    "禁止",
    "不可",
    "pending",
    "blocked",
    "= no",
]

WORKFLOW_ROUTE_LIST_FIELDS = [
    "required_steps",
    "skipped_steps",
    "allowed_output_families",
    "forbidden_output_families",
]


def load_json(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


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


def inspect_markdown_file(path: Path) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "review-template: tainted" in text:
        blocked.append(f"Template taint not cleared: {path}")
    body_lines = substantive_lines(text)
    if not body_lines:
        blocked.append(f"No substantive content yet: {path}")
    elif any(token in text for token in PLACEHOLDER_TOKENS):
        partial.append(f"Placeholder token remains in review file: {path}")
    return blocked, partial


def has_substantive_markdown_content(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return bool(substantive_lines(text)) and "review-template: tainted" not in text


def is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def extract_scoped_rewrite_exception(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return None
    task_exceptions = payload.get("task_exceptions")
    if not isinstance(task_exceptions, dict):
        return None
    scoped_rewrite = task_exceptions.get("scoped_rewrite")
    return scoped_rewrite if isinstance(scoped_rewrite, dict) else None


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

        heading_match = re.search(
            rf"^##\s*{re.escape(field_name)}\s*$([\s\S]*?)(?=^##\s|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if not heading_match:
            continue
        for line in substantive_lines(heading_match.group(1)):
            normalized = line.strip("`").lower()
            if normalized in allowed_values:
                return normalized
    return None


def inspect_release_gate_file(path: Path) -> tuple[list[str], list[str], dict[str, str | None]]:
    blocked, partial = inspect_markdown_file(path)
    text = path.read_text(encoding="utf-8")
    flags = extract_release_gate_flags_from_markdown(text)
    for field, value in flags.items():
        if value not in RELEASE_GATE_ALLOWED_VALUES:
            partial.append(f"Release gate field is missing or invalid: {field} in {path}")
    return blocked, partial, flags


def inspect_release_gate_manifest(
    path: Path,
    payload: dict,
) -> tuple[list[str], list[str], dict[str, str | None]]:
    blocked: list[str] = []
    partial: list[str] = []
    flags: dict[str, str | None] = {field: None for field in RELEASE_GATE_FIELDS}

    gate = extract_release_gate_block(payload)
    if gate is None:
        partial.append(f"Manifest release_gate block is missing or invalid: {path}")
        return blocked, partial, flags

    for field in RELEASE_GATE_META_FIELDS:
        value = gate.get(field)
        if not is_nonempty_string(value):
            partial.append(f"Manifest release_gate.{field} is missing: {path}")

    flags = extract_release_gate_flags_from_manifest(payload)
    for field, value in flags.items():
        if value not in RELEASE_GATE_ALLOWED_VALUES:
            partial.append(f"Manifest release_gate.{field} is missing or invalid: {path}")

    for field in RELEASE_GATE_LIST_FIELDS:
        value = gate.get(field)
        if not isinstance(value, list):
            partial.append(f"Manifest release_gate.{field} is not list-shaped: {path}")

    return blocked, partial, flags


def compare_release_gate_flags(
    path: Path,
    manifest_flags: dict[str, str | None],
    markdown_flags: dict[str, str | None],
) -> list[str]:
    partial: list[str] = []
    for field in RELEASE_GATE_FIELDS:
        manifest_value = manifest_flags.get(field)
        markdown_value = markdown_flags.get(field)
        if markdown_value is None:
            continue
        if manifest_value is None:
            continue
        if manifest_value == "pending":
            continue
        if markdown_value != manifest_value:
            partial.append(
                "Release gate projection drift between manifest and markdown: "
                f"{field} in {path} (manifest={manifest_value}, markdown={markdown_value})"
            )
    return partial


def inspect_specialty_gate_file(
    path: Path,
) -> tuple[list[str], list[str], dict[str, str | None]]:
    blocked, partial = inspect_markdown_file(path)
    text = path.read_text(encoding="utf-8")
    flags = extract_specialty_gate_flags_from_markdown(text)
    if flags.get("specialty_readiness") not in SPECIALTY_GATE_EXPLICIT_STATUS_VALUES:
        partial.append(
            f"Specialty readiness conclusion is missing or invalid in {path}"
        )
    if flags.get("discipline_register_status") not in SPECIALTY_GATE_EXPLICIT_STATUS_VALUES:
        partial.append(
            f"discipline_register_status is missing or invalid in {path}"
        )
    if flags.get("independent_audit_required") not in SPECIALTY_GATE_EXPLICIT_BOOLEAN_VALUES:
        partial.append(
            f"independent_audit_required is missing or invalid in {path}"
        )
    return blocked, partial, flags


def inspect_specialty_gate_manifest(
    path: Path,
    payload: dict,
) -> tuple[list[str], list[str], dict[str, str | None]]:
    blocked: list[str] = []
    partial: list[str] = []
    flags: dict[str, str | None] = {
        field: None
        for field in SPECIALTY_GATE_STATUS_FIELDS + SPECIALTY_GATE_BOOLEAN_FIELDS
    }

    gate = extract_specialty_gate_block(payload)
    if gate is None:
        partial.append(f"Manifest specialty_gate block is missing or invalid: {path}")
        return blocked, partial, flags

    flags = extract_specialty_gate_flags_from_manifest(payload)
    for field in SPECIALTY_GATE_STATUS_FIELDS:
        if flags.get(field) not in SPECIALTY_GATE_STATUS_VALUES:
            partial.append(f"Manifest specialty_gate.{field} is missing or invalid: {path}")
    for field in SPECIALTY_GATE_BOOLEAN_FIELDS:
        if flags.get(field) not in SPECIALTY_GATE_BOOLEAN_VALUES:
            partial.append(f"Manifest specialty_gate.{field} is missing or invalid: {path}")

    for field in SPECIALTY_GATE_LIST_FIELDS:
        value = gate.get(field)
        if not isinstance(value, list):
            partial.append(f"Manifest specialty_gate.{field} is not list-shaped: {path}")

    for field in SPECIALTY_GATE_STRING_FIELDS:
        value = gate.get(field)
        if value not in {None, ""} and not is_nonempty_string(value):
            partial.append(f"Manifest specialty_gate.{field} is invalid: {path}")

    if has_explicit_specialty_gate_authority(flags):
        if not isinstance(gate.get("domain_stack"), list) or not gate.get("domain_stack"):
            partial.append(f"Manifest specialty_gate.domain_stack is empty: {path}")
        if not is_nonempty_string(gate.get("primary_loop")):
            partial.append(f"Manifest specialty_gate.primary_loop is missing: {path}")
        if flags.get("independent_audit_required") not in SPECIALTY_GATE_EXPLICIT_BOOLEAN_VALUES:
            partial.append(
                f"Manifest specialty_gate.independent_audit_required is pending: {path}"
            )
        if not isinstance(gate.get("required_expert_checks"), list) or not gate.get("required_expert_checks"):
            partial.append(f"Manifest specialty_gate.required_expert_checks is empty: {path}")
        if not is_nonempty_string(gate.get("next_action")):
            partial.append(f"Manifest specialty_gate.next_action is missing: {path}")

    return blocked, partial, flags


def compare_specialty_gate_flags(
    path: Path,
    manifest_flags: dict[str, str | None],
    markdown_flags: dict[str, str | None],
) -> list[str]:
    partial: list[str] = []
    for field in SPECIALTY_GATE_STATUS_FIELDS + SPECIALTY_GATE_BOOLEAN_FIELDS:
        manifest_value = manifest_flags.get(field)
        markdown_value = markdown_flags.get(field)
        if markdown_value is None:
            continue
        if manifest_value is None:
            continue
        if manifest_value == "pending":
            continue
        if markdown_value != manifest_value:
            partial.append(
                "Specialty gate projection drift between manifest and markdown: "
                f"{field} in {path} (manifest={manifest_value}, markdown={markdown_value})"
            )
    return partial


def line_has_positive_promotion(line: str, patterns: list[re.Pattern[str]]) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if any(token in stripped for token in NEGATION_TOKENS):
        return False
    return any(pattern.search(stripped) for pattern in patterns)


def output_artifact_has_substantive_content(path: Path) -> bool:
    if not path.exists():
        return False
    if path.suffix == ".md":
        return has_substantive_markdown_content(path)
    if path.suffix == ".html":
        text = path.read_text(encoding="utf-8")
        return "display-template: tainted" not in text and "占位文件" not in text
    return path.stat().st_size > 0


def inspect_stage_promotion(
    paper_dir: Path,
    reviews_dir: Path,
    display_dir: Path,
    release_gate_flags: dict[str, str | None],
    release_gate_present: bool,
    workflow_route: dict | None,
) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []

    route_forbidden = set()
    if isinstance(workflow_route, dict):
        forbidden = workflow_route.get("forbidden_output_families")
        if isinstance(forbidden, list):
            route_forbidden = set(forbidden)

    output_policy = load_output_policy()
    output_policy_errors = validate_output_policy(output_policy)
    review_verdict = load_review_verdict(paper_dir)
    verdict_alignment_errors = (
        validate_claim_ceiling_alignment(output_policy, review_verdict)
        if not output_policy_errors
        else []
    )
    advice_decisions = (
        advice_output_decisions(output_policy, review_verdict)
        if not output_policy_errors
        else []
    )
    process_projection_path = migrated_note_path(paper_dir, "process_projection.md")

    if output_policy_errors:
        partial.append(
            "Policy-driven advice output gate is unavailable: "
            + "; ".join(output_policy_errors)
        )
    elif verdict_alignment_errors:
        partial.append(
            "Review verdict/output policy alignment is incomplete: "
            + "; ".join(verdict_alignment_errors)
        )
    if review_verdict is None:
        partial.append(
            f"Review verdict is missing or unreadable: {paper_dir / 'evidence' / 'review-verdict.json'}"
        )

    if output_policy_errors:
        fallback_paths = [
            *[reviews_dir / name for name in EXECUTION_OUTPUT_FILES],
            *[reviews_dir / name for name in LINE_EDITING_FILES],
            display_dir / "学生执行页.html",
            display_dir / "导师汇报页.html",
        ]
        for path in fallback_paths:
            if output_artifact_has_substantive_content(path):
                blocked.append(
                    "Advice output exists while policy-driven advice gate is unavailable: "
                    f"{path}"
                )
    else:
        forbidden_rule_patterns = [
            (rule_id, [re.compile(re.escape(pattern)) for pattern in patterns])
            for rule_id, patterns in forbidden_transformation_rules(output_policy)
        ]
        for decision in advice_decisions:
            output_ref = decision.get("output_ref")
            route_family = decision.get("route_family")
            artifact_paths = decision.get("artifact_paths")
            if not isinstance(output_ref, str) or not isinstance(artifact_paths, list):
                continue

            denial_reasons: list[str] = []
            if decision.get("allowed") is not True:
                denial_reasons.append(str(decision.get("reason")))
            if isinstance(route_family, str) and route_family in route_forbidden:
                denial_reasons.append(f"workflow route forbids {route_family}")

            for rel_path in artifact_paths:
                if not isinstance(rel_path, str):
                    continue
                path = paper_dir / rel_path
                if not output_artifact_has_substantive_content(path):
                    continue

                if denial_reasons:
                    blocked.append(
                        "Advice output exists before review-verdict/output policy allows it: "
                        f"{path} ({output_ref}; {'; '.join(denial_reasons)})"
                    )

                for rule_id, patterns in forbidden_rule_patterns:
                    for lineno, raw_line in enumerate(
                        path.read_text(encoding="utf-8").splitlines(),
                        start=1,
                    ):
                        if line_has_positive_promotion(raw_line, patterns):
                            blocked.append(
                                "Forbidden transformation appears in advice output: "
                                f"{path}:{lineno} ({rule_id})"
                            )

        line_editing_denied = next(
            (
                decision
                for decision in advice_decisions
                if decision.get("output_ref") == "output.advisor.line-editing"
            ),
            None,
        )
        if (
            line_editing_denied is None
            or line_editing_denied.get("allowed") is not True
            or "advisor_line_editing" in route_forbidden
        ):
            for path in [
                process_projection_path,
                reviews_dir / "论文多智能体审查报告.md",
            ]:
                if not path.exists():
                    continue
                for lineno, raw_line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                ):
                    if line_has_positive_promotion(raw_line, LINE_EDITING_PROMOTION_PATTERNS):
                        blocked.append(
                            "Stage drift: line editing promoted before current review verdict/output policy allows it: "
                            f"{path}:{lineno}"
                        )

    can_issue_readiness_verdict = release_gate_flags.get("can_issue_readiness_verdict")
    if not release_gate_present and not route_forbidden:
        partial.append(
            "Structured or legacy release gate flags are missing; readiness verdict remains blocked by default until explicit can_* flags exist"
        )

    if can_issue_readiness_verdict != "yes" or "readiness_verdict" in route_forbidden:
        for path in [
            process_projection_path,
            reviews_dir / "论文多智能体审查报告.md",
            reviews_dir / "导师汇报版摘要.md",
            paper_dir / "综合评审汇总.html",
            display_dir / "完整评审页.html",
            display_dir / "导师汇报页.html",
        ]:
            if not path.exists():
                continue
            for lineno, raw_line in enumerate(
                path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                if line_has_positive_promotion(raw_line, READINESS_PROMOTION_PATTERNS):
                    blocked.append(
                        "Stage drift: readiness verdict promoted before current workflow state allows it: "
                        f"{path}:{lineno}"
                    )

    if any(value is None for value in release_gate_flags.values()):
        partial.append("Release gate file exists but key can_* flags are not fully explicit yet")

    return blocked, partial


def inspect_display_file(
    path: Path,
    required_snippets: list[str],
    strict: bool,
) -> tuple[list[str], list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "display-template: tainted" in text or "占位文件" in text:
        message = f"Display page still template-shaped: {path}"
        if strict:
            blocked.append(message)
        else:
            partial.append(message)
        return blocked, partial, warnings

    has_required_content = any(snippet in text for snippet in required_snippets)
    if not has_required_content:
        message = (
            f"Display page missing required content contract {required_snippets}: {path}"
        )
        if strict:
            blocked.append(message)
        else:
            partial.append(message)

    if any(token in text for token in PLACEHOLDER_TOKENS):
        partial.append(f"Placeholder token remains in display page: {path}")
    return blocked, partial, warnings


def inspect_manifest(path: Path) -> tuple[list[str], list[str], dict | None]:
    blocked: list[str] = []
    partial: list[str] = []
    payload = load_json(path)
    if payload is None:
        blocked.append(f"Invalid JSON in {path}")
        return blocked, partial, None

    required_keys = {
        "schema_version",
        "template_status",
        "entry_mode",
        "review_object",
        "truth_source",
        "rebase",
        "slow_variables",
        "dependents",
        "readiness",
        "handoff",
    }
    missing = sorted(required_keys - payload.keys())
    if missing:
        blocked.append(f"Manifest missing required keys {missing}: {path}")
        return blocked, partial, payload

    if payload.get("template_status") == "tainted":
        blocked.append(f"Manifest template taint not cleared: {path}")

    entry_mode = payload.get("entry_mode")
    if entry_mode not in ENTRY_MODES | {None}:
        partial.append(f"Manifest entry_mode is invalid: {path}")
    if entry_mode is None and payload.get("template_status") != "tainted":
        partial.append(f"Manifest entry_mode is not set yet: {path}")

    review_object = payload.get("review_object")
    if not isinstance(review_object, dict):
        partial.append(f"Manifest review_object block is not object-shaped: {path}")
    elif payload.get("template_status") != "tainted":
        if not is_nonempty_string(review_object.get("path")):
            partial.append(f"Manifest review_object.path is missing: {path}")
        if not is_nonempty_string(review_object.get("label")):
            partial.append(f"Manifest review_object.label is missing: {path}")

    truth_source = payload.get("truth_source")
    if not isinstance(truth_source, dict):
        partial.append(f"Manifest truth_source block is not object-shaped: {path}")
    else:
        current = truth_source.get("current")
        if not isinstance(current, list):
            partial.append(f"Manifest truth_source.current is not list-shaped: {path}")
        elif payload.get("template_status") != "tainted" and not current:
            partial.append(f"Manifest truth_source.current is empty: {path}")

        historical_sources = truth_source.get("historical_sources")
        if not isinstance(historical_sources, list):
            partial.append(
                f"Manifest truth_source.historical_sources is not list-shaped: {path}"
            )

        deprecated_anchors = truth_source.get("deprecated_anchors")
        if not isinstance(deprecated_anchors, list):
            partial.append(
                f"Manifest truth_source.deprecated_anchors is not list-shaped: {path}"
            )

    rebase = payload.get("rebase")
    if not isinstance(rebase, dict):
        partial.append(f"Manifest rebase block is not object-shaped: {path}")
    else:
        impacted_artifacts = rebase.get("impacted_artifacts")
        if not isinstance(impacted_artifacts, list):
            partial.append(
                f"Manifest rebase.impacted_artifacts is not list-shaped: {path}"
            )

    slow_variables = payload.get("slow_variables")
    if not isinstance(slow_variables, list):
        partial.append(f"Manifest slow_variables is not list-shaped: {path}")

    dependents = payload.get("dependents")
    if not isinstance(dependents, list):
        partial.append(f"Manifest dependents is not list-shaped: {path}")

    readiness = payload.get("readiness")
    if not isinstance(readiness, dict):
        partial.append(f"Manifest readiness block is not object-shaped: {path}")
    else:
        gate = readiness.get("workspace_gate")
        if gate not in {"blocked", "partial", "ready"}:
            partial.append(f"Manifest readiness.workspace_gate is invalid: {path}")

    handoff = payload.get("handoff")
    if not isinstance(handoff, dict) or not isinstance(handoff.get("process_projection"), str):
        partial.append(f"Manifest handoff.process_projection is missing: {path}")

    task_exceptions = payload.get("task_exceptions")
    if task_exceptions is not None:
        if not isinstance(task_exceptions, dict):
            partial.append(f"Manifest task_exceptions block is not object-shaped: {path}")
        elif "scoped_rewrite" in task_exceptions and not isinstance(
            task_exceptions.get("scoped_rewrite"),
            dict,
        ):
            partial.append(
                f"Manifest task_exceptions.scoped_rewrite is not object-shaped: {path}"
            )
    return blocked, partial, payload


def inspect_workflow_route(
    path: Path,
    payload: dict,
) -> tuple[list[str], list[str], dict | None, str]:
    blocked: list[str] = []
    partial: list[str] = []

    template_status = payload.get("template_status")
    entry_mode = payload.get("entry_mode")
    if template_status == "tainted" or entry_mode not in ENTRY_MODES:
        return blocked, partial, None, "missing"

    manifest_route = payload.get("workflow_route")
    route_source = "manifest"
    effective_route = derive_workflow_route_from_entry_mode(entry_mode)
    if effective_route is None:
        return blocked, partial, None, "missing"

    if manifest_route is None:
        partial.append(
            f"Manifest workflow_route is missing; deriving default route from entry_mode in {path}"
        )
        return blocked, partial, effective_route, "derived"

    if not isinstance(manifest_route, dict):
        partial.append(
            f"Manifest workflow_route block is not object-shaped; deriving default route from entry_mode in {path}"
        )
        return blocked, partial, effective_route, "derived"

    if workflow_route_is_placeholder(manifest_route):
        partial.append(
            f"Manifest workflow_route is still placeholder-shaped; deriving default route from entry_mode in {path}"
        )
        return blocked, partial, effective_route, "derived"

    if manifest_route.get("contract_version") != WORKFLOW_ROUTE_CONTRACT_VERSION:
        partial.append(
            f"Manifest workflow_route.contract_version is missing or invalid: {path}"
        )

    if manifest_route.get("mode") != entry_mode:
        partial.append(
            "Manifest workflow_route.mode does not match entry_mode: "
            f"{path} (entry_mode={entry_mode}, route_mode={manifest_route.get('mode')})"
        )

    registry_entry = route_registry_entry(entry_mode)
    if registry_entry is None:
        return blocked, partial, effective_route, route_source

    for field in WORKFLOW_ROUTE_LIST_FIELDS:
        value = manifest_route.get(field)
        expected = registry_entry[field]
        if not isinstance(value, list):
            partial.append(f"Manifest workflow_route.{field} is not list-shaped: {path}")
            continue
        if value != expected:
            partial.append(
                f"Manifest workflow_route.{field} drifted from registry for mode {entry_mode}: {path}"
            )

    resume_to_mode = manifest_route.get("resume_to_mode")
    if entry_mode == "handoff_resume":
        if resume_to_mode not in RESUMABLE_ENTRY_MODES:
            partial.append(
                f"handoff_resume requires workflow_route.resume_to_mode in {RESUMABLE_ENTRY_MODES}: {path}"
            )
            resume_to_mode = None
    elif resume_to_mode not in {None, ""}:
        partial.append(
            f"workflow_route.resume_to_mode should be empty outside handoff_resume: {path}"
        )
        resume_to_mode = None

    effective_route = build_workflow_route(
        entry_mode,
        resume_to_mode=resume_to_mode,
    )

    step_state = manifest_route.get("step_state")
    known_steps = route_steps(entry_mode)
    if not isinstance(step_state, dict):
        partial.append(f"Manifest workflow_route.step_state is not object-shaped: {path}")
    else:
        merged_step_state = dict(effective_route["step_state"])
        for step in known_steps:
            value = step_state.get(step)
            if value not in STEP_STATUS_VALUES:
                partial.append(
                    f"Manifest workflow_route.step_state.{step} is missing or invalid: {path}"
                )
                continue
            merged_step_state[step] = value
        for step in effective_route["required_steps"]:
            if merged_step_state.get(step) == "skipped":
                partial.append(
                    f"Required workflow step may not be marked skipped: {step} in {path}"
                )
        for step in effective_route["skipped_steps"]:
            if merged_step_state.get(step) not in {"skipped", "done"}:
                partial.append(
                    f"Skipped workflow step should remain skipped/done: {step} in {path}"
                )
        effective_route["step_state"] = merged_step_state

    active_step = manifest_route.get("active_step")
    if active_step is not None and active_step not in known_steps:
        partial.append(f"Manifest workflow_route.active_step is invalid: {path}")
    elif isinstance(effective_route.get("step_state"), dict):
        effective_route["active_step"] = active_step

    return blocked, partial, effective_route, route_source


def workflow_step_done(route: dict | None, step: str) -> bool:
    if not isinstance(route, dict):
        return False
    step_state = route.get("step_state")
    return isinstance(step_state, dict) and step_state.get(step) == "done"


def workflow_route_is_placeholder(route: dict) -> bool:
    return (
        route.get("mode") in {None, ""}
        and route.get("resume_to_mode") in {None, ""}
        and route.get("active_step") in {None, ""}
        and route.get("required_steps") == []
        and route.get("skipped_steps") == []
        and route.get("allowed_output_families") == []
        and route.get("forbidden_output_families") == []
        and route.get("step_state") == {}
    )


def inspect_entry_mode_contract(
    path: Path,
    payload: dict,
    paper_dir: Path,
) -> tuple[list[str], list[str], list[str], dict | None, str]:
    blocked: list[str] = []
    partial: list[str] = []
    warnings: list[str] = []

    template_status = payload.get("template_status")
    entry_mode = payload.get("entry_mode")
    if template_status == "tainted" or entry_mode not in ENTRY_MODES:
        return blocked, partial, warnings, None, "missing"

    route_blocked, route_partial, workflow_route, route_source = inspect_workflow_route(
        path,
        payload,
    )
    blocked.extend(route_blocked)
    partial.extend(route_partial)
    if workflow_route is None:
        return blocked, partial, warnings, None, route_source

    rebase = payload.get("rebase") if isinstance(payload.get("rebase"), dict) else {}
    truth_source = (
        payload.get("truth_source") if isinstance(payload.get("truth_source"), dict) else {}
    )
    review_object = (
        payload.get("review_object") if isinstance(payload.get("review_object"), dict) else {}
    )
    handoff = payload.get("handoff") if isinstance(payload.get("handoff"), dict) else {}
    dependents = payload.get("dependents")
    process_projection_path = migrated_note_path(paper_dir, "process_projection.md")
    freeze_note_path = migrated_note_path(paper_dir, "审阅对象冻结说明.md")
    specialty_path = migrated_note_path(paper_dir, "专业手册完备性判断.md")

    mode = workflow_route["mode"]

    if workflow_step_done(workflow_route, "freeze_review_object"):
        if not is_nonempty_string(review_object.get("path")):
            partial.append(f"workflow_route.freeze_review_object is done but review_object.path is missing: {path}")
        if not is_nonempty_string(review_object.get("label")):
            partial.append(f"workflow_route.freeze_review_object is done but review_object.label is missing: {path}")
        if not freeze_note_path.exists() or not has_substantive_markdown_content(freeze_note_path):
            partial.append(
                f"workflow_route.freeze_review_object is done but 审阅对象冻结说明 is not substantive: {freeze_note_path}"
            )

    if workflow_step_done(workflow_route, "sync_truth_source"):
        current = truth_source.get("current")
        if not isinstance(current, list) or not current:
            partial.append(f"workflow_route.sync_truth_source is done but truth_source.current is empty: {path}")

    if workflow_step_done(workflow_route, "record_historical_sources"):
        historical_sources = truth_source.get("historical_sources")
        if not isinstance(historical_sources, list) or not historical_sources:
            partial.append(
                f"workflow_route.record_historical_sources is done but truth_source.historical_sources is empty: {path}"
            )

    if workflow_step_done(workflow_route, "record_rebase_window"):
        if rebase.get("enabled") is not True:
            partial.append(f"workflow_route.record_rebase_window is done but rebase.enabled is not true: {path}")
        if not is_nonempty_string(rebase.get("from_version")):
            partial.append(f"workflow_route.record_rebase_window is done but rebase.from_version is missing: {path}")
        if not is_nonempty_string(rebase.get("to_version")):
            partial.append(f"workflow_route.record_rebase_window is done but rebase.to_version is missing: {path}")
        if not is_nonempty_string(rebase.get("status")):
            partial.append(f"workflow_route.record_rebase_window is done but rebase.status is missing: {path}")

    if workflow_step_done(workflow_route, "enumerate_impacted_artifacts"):
        impacted_artifacts = rebase.get("impacted_artifacts")
        if mode == "version_rebase":
            if not isinstance(impacted_artifacts, list) or not impacted_artifacts:
                partial.append(
                    f"workflow_route.enumerate_impacted_artifacts is done but rebase.impacted_artifacts is empty: {path}"
                )
        elif not isinstance(dependents, list) or not dependents:
            partial.append(
                f"workflow_route.enumerate_impacted_artifacts is done but dependents is empty: {path}"
            )

    if workflow_step_done(workflow_route, "regress_dependents"):
        if not isinstance(dependents, list) or not dependents:
            partial.append(f"workflow_route.regress_dependents is done but dependents is empty: {path}")

    if workflow_step_done(workflow_route, "confirm_truth_source_stable"):
        if rebase.get("enabled") is True:
            partial.append(
                f"workflow_route.confirm_truth_source_stable is done but rebase.enabled is true: {path}"
            )

    if workflow_step_done(workflow_route, "complete_specialty_route"):
        if not specialty_path.exists() or not has_substantive_markdown_content(specialty_path):
            partial.append(
                f"workflow_route.complete_specialty_route is done but specialty readiness record is not substantive: {specialty_path}"
            )

    if mode == "handoff_resume":
        if not process_projection_path.exists():
            blocked.append(
                f"handoff_resume requires process_projection.md: {process_projection_path}"
            )
        else:
            file_blocked, file_partial = inspect_markdown_file(process_projection_path)
            blocked.extend(file_blocked)
            partial.extend(file_partial)
        if not is_nonempty_string(handoff.get("next_gate")):
            partial.append(
                f"handoff_resume should record handoff.next_gate in {path}"
            )
        if workflow_route.get("resume_to_mode") not in RESUMABLE_ENTRY_MODES:
            partial.append(
                f"handoff_resume must point to a resumable workflow_route.resume_to_mode in {path}"
            )
    elif process_projection_path.exists():
        file_blocked, file_partial = inspect_markdown_file(process_projection_path)
        partial.extend(file_blocked)
        partial.extend(file_partial)

    if mode == "initial_review":
        if rebase.get("enabled") is True:
            partial.append(f"initial_review should not set rebase.enabled = true in {path}")
    elif mode == "version_rebase":
        if rebase.get("enabled") is not True:
            partial.append(f"version_rebase requires rebase.enabled = true in {path}")
        if not is_nonempty_string(rebase.get("from_version")):
            partial.append(f"version_rebase is missing rebase.from_version in {path}")
        if not is_nonempty_string(rebase.get("to_version")):
            partial.append(f"version_rebase is missing rebase.to_version in {path}")
        if not is_nonempty_string(rebase.get("status")):
            partial.append(f"version_rebase is missing rebase.status in {path}")
        historical_sources = truth_source.get("historical_sources")
        if not isinstance(historical_sources, list) or not historical_sources:
            partial.append(
                f"version_rebase should record truth_source.historical_sources in {path}"
            )
        impacted_artifacts = rebase.get("impacted_artifacts")
        if not isinstance(impacted_artifacts, list) or not impacted_artifacts:
            partial.append(
                f"version_rebase should record rebase.impacted_artifacts in {path}"
            )
    elif mode == "evidence_upgrade":
        if rebase.get("enabled") is True:
            partial.append(f"evidence_upgrade should not enable rebase in {path}")
        if not isinstance(dependents, list) or not dependents:
            partial.append(
                f"evidence_upgrade should record impacted dependents in {path}"
            )
    elif mode == "display_regression":
        if rebase.get("enabled") is True:
            partial.append(f"display_regression should not enable rebase in {path}")
        if not isinstance(dependents, list) or not dependents:
            partial.append(
                f"display_regression should record affected display/lightweight artifacts in {path}"
            )

    return blocked, partial, warnings, workflow_route, route_source


def inspect_specialty_contract(
    payload: dict,
    paper_dir: Path,
    manifest_path: Path,
) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []

    if payload.get("template_status") == "tainted":
        return blocked, partial

    entry_mode = payload.get("entry_mode")
    if entry_mode not in ENTRY_MODES:
        return blocked, partial

    manifest_flags: dict[str, str | None] = {
        field: None
        for field in SPECIALTY_GATE_STATUS_FIELDS + SPECIALTY_GATE_BOOLEAN_FIELDS
    }
    manifest_blocked, manifest_partial, manifest_flags = inspect_specialty_gate_manifest(
        manifest_path,
        payload,
    )
    blocked.extend(manifest_blocked)
    partial.extend(manifest_partial)

    readiness_path = migrated_note_path(paper_dir, "专业手册完备性判断.md")
    flags = manifest_flags
    specialty_gate_source = "missing"

    manifest_has_authority = (
        has_explicit_specialty_gate_authority(manifest_flags)
        and not manifest_specialty_gate_is_placeholder(payload)
    )
    if manifest_has_authority:
        specialty_gate_source = "manifest"
        if not readiness_path.exists():
            partial.append(
                "Manifest specialty_gate is the machine gate, but the human-readable "
                f"projection file is missing: {readiness_path}"
            )
        else:
            readiness_blocked, readiness_partial, markdown_flags = inspect_specialty_gate_file(
                readiness_path
            )
            partial.extend(readiness_blocked)
            partial.extend(readiness_partial)
            partial.extend(
                compare_specialty_gate_flags(
                    readiness_path,
                    manifest_flags,
                    markdown_flags,
                )
            )
    else:
        if not readiness_path.exists():
            partial.append(f"Missing specialty readiness record: {readiness_path}")
            return blocked, partial

        readiness_blocked, readiness_partial, flags = inspect_specialty_gate_file(
            readiness_path
        )
        partial.extend(readiness_blocked)
        partial.extend(readiness_partial)
        if has_explicit_specialty_gate_authority(flags):
            specialty_gate_source = "markdown"
            if manifest_specialty_gate_is_placeholder(payload):
                partial.append(
                    "Manifest specialty_gate is still placeholder-shaped; using Markdown "
                    "projection until review_version_manifest.json.specialty_gate is synced"
                )
            else:
                partial.append(
                    "Using legacy Markdown specialty gate; migrate fields into "
                    "review_version_manifest.json.specialty_gate"
                )
        else:
            return blocked, partial

    if flags.get("specialty_readiness") not in {"partial", "missing"}:
        if specialty_gate_source == "manifest" and not readiness_path.exists():
            return blocked, partial
        return blocked, partial

    supplement_path = migrated_note_path(paper_dir, "专业专项补充说明.md")
    if not supplement_path.exists():
        partial.append(
            "Specialty readiness is partial/missing but supplement file is absent: "
            f"{supplement_path}"
        )
        return blocked, partial

    supplement_blocked, supplement_partial = inspect_markdown_file(supplement_path)
    partial.extend(supplement_blocked)
    partial.extend(supplement_partial)
    return blocked, partial


def inspect_scoped_rewrite_contract(
    payload: dict,
    paper_dir: Path,
    manifest_path: Path,
    release_gate_flags: dict[str, str | None],
) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []

    if payload.get("template_status") == "tainted":
        return blocked, partial

    entry_mode = payload.get("entry_mode")
    if entry_mode not in ENTRY_MODES:
        return blocked, partial

    scoped_rewrite = extract_scoped_rewrite_exception(payload)
    task_card_path = migrated_note_path(paper_dir, SCOPED_REWRITE_TASK_CARD)
    task_card_is_active = task_card_path.exists() and has_substantive_markdown_content(
        task_card_path
    )
    full_line_editing_gate = release_gate_flags.get("can_enter_line_editing")

    if scoped_rewrite is None:
        if task_card_is_active and full_line_editing_gate != "yes":
            blocked.append(
                "Scoped rewrite task card exists but manifest task_exceptions.scoped_rewrite "
                f"is missing: {task_card_path}"
            )
        return blocked, partial

    enabled = scoped_rewrite.get("enabled")
    targets = scoped_rewrite.get("targets")
    reason = scoped_rewrite.get("reason")

    if enabled not in {True, False}:
        partial.append(
                "Manifest task_exceptions.scoped_rewrite.enabled is missing or invalid: "
                f"{manifest_path}"
            )
        enabled = False

    if enabled:
        if full_line_editing_gate == "yes":
            partial.append(
                "Scoped rewrite exception should be cleared once can_enter_line_editing = yes: "
                f"{manifest_path}"
            )
        elif full_line_editing_gate not in {"no", "blocked"}:
            partial.append(
                "Scoped rewrite exception requires explicit can_enter_line_editing = no/blocked: "
                f"{manifest_path}"
            )

        if not isinstance(targets, list) or not targets:
            partial.append(
                "Manifest task_exceptions.scoped_rewrite.targets is missing or empty: "
                f"{manifest_path}"
            )
        if not is_nonempty_string(reason):
            partial.append(
                "Manifest task_exceptions.scoped_rewrite.reason is missing: "
                f"{manifest_path}"
            )

        if not task_card_path.exists():
            partial.append(f"Scoped rewrite task card is missing: {task_card_path}")
            return blocked, partial

        task_card_blocked, task_card_partial = inspect_markdown_file(task_card_path)
        partial.extend(task_card_blocked)
        partial.extend(task_card_partial)
        return blocked, partial

    if task_card_is_active and full_line_editing_gate != "yes":
        blocked.append(
            "Scoped rewrite task card exists before scoped exception is enabled: "
            f"{task_card_path}"
        )

    return blocked, partial


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the minimum workspace contract for a thesis review project."
    )
    parser.add_argument("--paper-dir", required=True, help="Path to papers/paperXX")
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Enforce the full multi-page display_projection contract. "
            "Without this flag, display/ pages and display_projection contract "
            "files are reported as warnings for legacy or lightweight projects."
        ),
    )
    args = parser.parse_args()

    paper_dir = Path(args.paper_dir).expanduser().resolve()
    reviews_dir = paper_dir / "reviews"
    notes_workspace_dir = notes_dir(paper_dir)
    objects_dir = paper_dir / "objects"
    assets_dir = paper_dir / "assets"
    display_dir = paper_dir / "display"
    manifest_path = resolve_manifest_path(paper_dir)
    legacy_compatibility = inspect_legacy_compatibility(paper_dir)
    runtime_pack_drift = inspect_runtime_pack_drift(paper_dir)

    blocked: list[str] = []
    partial: list[str] = []
    warnings: list[str] = []
    object_item_counts: dict[str, int] = {}
    manifest_payload: dict | None = None
    manifest_release_gate_flags: dict[str, str | None] = {
        field: None for field in RELEASE_GATE_FIELDS
    }
    workflow_route: dict | None = None
    workflow_route_source = "missing"
    release_gate_flags: dict[str, str | None] = {
        field: None for field in RELEASE_GATE_FIELDS
    }
    release_gate_present = False
    release_gate_source = "missing"

    if not paper_dir.exists():
        blocked.append(f"Missing paper directory: {paper_dir}")
    if not reviews_dir.exists():
        blocked.append(f"Missing reviews directory: {reviews_dir}")
    if not notes_workspace_dir.exists() and canonical_manifest_path(paper_dir).exists():
        warnings.append(
            f"Notes directory missing despite canonical legacy assets: {notes_workspace_dir}"
        )
    if not objects_dir.exists():
        blocked.append(f"Missing objects directory: {objects_dir}")
    if not assets_dir.exists():
        blocked.append(f"Missing assets directory: {assets_dir}")
    entry_page = paper_dir / "综合评审汇总.html"
    if not entry_page.exists():
        blocked.append(f"Missing display entry page: {entry_page}")
    else:
        entry_text = entry_page.read_text(encoding="utf-8")
        if "display-template: tainted" in entry_text or "占位文件" in entry_text:
            message = f"Display entry page still template-shaped: {entry_page}"
            if args.strict:
                blocked.append(message)
            else:
                partial.append(message)
    if not display_dir.exists():
        message = (
            f"Missing display directory: {display_dir}"
            if args.strict
            else (
                f"Missing display directory: {display_dir} "
                "(allowed in non-strict mode for legacy or single-page projects)"
            )
        )
        (blocked if args.strict else warnings).append(message)
    partial.extend(legacy_compatibility["partial"])
    warnings.extend(legacy_compatibility["warnings"])
    if runtime_pack_drift["errors"]:
        partial.extend(
            [
                "Runtime pack drift from repo truth pack: " + message
                for message in runtime_pack_drift["errors"]
            ]
        )

    thesis_files = (
        list(paper_dir.glob("*.docx"))
        + list(paper_dir.glob("*.doc"))
        + list(paper_dir.glob("*.wps"))
        + list(paper_dir.glob("*.pdf"))
    )
    if not thesis_files:
        partial.append("No source DOCX/DOC/WPS/PDF found at paper root")

    for name in CORE_REQUIRED_REVIEW_FILES:
        path = (
            manifest_path
            if name == "review_version_manifest.json"
            else migrated_note_path(paper_dir, name)
        )
        if not path.exists():
            blocked.append(f"Missing review contract file: {path}")
            continue
        if path.suffix == ".json":
            manifest_blocked, manifest_partial, manifest_payload = inspect_manifest(path)
            blocked.extend(manifest_blocked)
            partial.extend(manifest_partial)
            if manifest_payload is not None:
                gate_blocked, gate_partial, manifest_release_gate_flags = inspect_release_gate_manifest(
                    path,
                    manifest_payload,
                )
                blocked.extend(gate_blocked)
                partial.extend(gate_partial)
                if (
                    all(
                        value in RELEASE_GATE_ALLOWED_VALUES
                        for value in manifest_release_gate_flags.values()
                    )
                    and has_explicit_release_gate_authority(manifest_release_gate_flags)
                    and not manifest_release_gate_is_placeholder(manifest_payload)
                ):
                    release_gate_flags = manifest_release_gate_flags
                    release_gate_present = True
                    release_gate_source = "manifest"
            continue
        file_blocked, file_partial = inspect_markdown_file(path)
        blocked.extend(file_blocked)
        partial.extend(file_partial)

    for name in STRICT_GATE_REVIEW_FILES:
        path = migrated_note_path(paper_dir, name)
        if not path.exists():
            message = (
                f"Missing review release gate projection file: {path}"
                if args.strict
                else (
                    f"Missing review release gate projection file: {path} "
                    "(allowed in non-strict mode for legacy or lightweight projects)"
                )
            )
            (blocked if args.strict else warnings).append(message)
            continue
        file_blocked, file_partial, markdown_release_gate_flags = inspect_release_gate_file(path)
        if args.strict:
            blocked.extend(file_blocked)
        else:
            partial.extend(file_blocked)
        partial.extend(file_partial)
        if release_gate_source == "manifest":
            partial.extend(
                compare_release_gate_flags(
                    path,
                    manifest_release_gate_flags,
                    markdown_release_gate_flags,
                )
            )
        elif all(
            value in RELEASE_GATE_ALLOWED_VALUES
            for value in markdown_release_gate_flags.values()
        ):
            release_gate_flags = markdown_release_gate_flags
            release_gate_present = True
            release_gate_source = "markdown"
            if manifest_payload is not None and manifest_release_gate_is_placeholder(
                manifest_payload
            ):
                partial.append(
                    "Manifest release_gate is still placeholder-shaped; using Markdown "
                    "projection until review_version_manifest.json.release_gate is synced"
                )
            else:
                partial.append(
                    "Using legacy Markdown release gate; migrate flags into "
                    "review_version_manifest.json.release_gate"
                )

    for name in STRICT_DISPLAY_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            message = (
                f"Missing display projection contract file: {path}"
                if args.strict
                else (
                    f"Missing display projection contract file: {path} "
                    "(allowed in non-strict mode for legacy or lightweight projects)"
                )
            )
            (blocked if args.strict else warnings).append(message)
            continue
        file_blocked, file_partial = inspect_markdown_file(path)
        if args.strict:
            blocked.extend(file_blocked)
        else:
            partial.extend(file_blocked)
        partial.extend(file_partial)

    for name in REQUIRED_OBJECT_FILES:
        path = objects_dir / name
        if not path.exists():
            blocked.append(f"Missing object file: {path}")
            continue
        payload = load_json(path)
        if payload is None:
            blocked.append(f"Invalid JSON in {path}")
            continue
        if "items" not in payload or not isinstance(payload["items"], list):
            blocked.append(f"Object file missing list-shaped 'items': {path}")
            continue
        item_count = len(payload["items"])
        object_item_counts[name] = item_count
        if item_count == 0:
            partial.append(f"Object file exists but is still empty: {path}")

    for name in REQUIRED_DISPLAY_FILES:
        path = display_dir / name
        if not path.exists():
            message = (
                f"Missing display page: {path}"
                if args.strict
                else (
                    f"Missing display page: {path} "
                    "(allowed in non-strict mode for legacy or single-page projects)"
                )
            )
            (blocked if args.strict else warnings).append(message)
            continue
        display_blocked, display_partial, display_warnings = inspect_display_file(
            path,
            DISPLAY_CONTENT_HINTS.get(name, []),
            args.strict,
        )
        blocked.extend(display_blocked)
        partial.extend(display_partial)
        warnings.extend(display_warnings)

    if not (assets_dir / "figures").exists():
        blocked.append(f"Missing figures directory: {assets_dir / 'figures'}")
    page_renders_dir = assets_dir / "page_renders"
    legacy_pdf_pages_dir = assets_dir / "pdf_pages"
    if page_renders_dir.exists():
        pass
    elif legacy_pdf_pages_dir.exists():
        warnings.append(
            f"Using legacy page render directory: {legacy_pdf_pages_dir}; "
            f"prefer {page_renders_dir} for new workspaces"
        )
    else:
        message = (
            f"Missing page render directory: {page_renders_dir} "
            f"(legacy {legacy_pdf_pages_dir} is also accepted)"
        )
        if object_item_counts.get("figures.json", 0) > 0:
            partial.append(message)
        else:
            warnings.append(message)
    if not (assets_dir / "tables").exists():
        warnings.append(f"Missing tables directory: {assets_dir / 'tables'}")

    if manifest_payload is not None:
        route_blocked, route_partial, route_warnings, workflow_route, workflow_route_source = inspect_entry_mode_contract(
            manifest_path,
            manifest_payload,
            paper_dir,
        )
        blocked.extend(route_blocked)
        partial.extend(route_partial)
        warnings.extend(route_warnings)

        specialty_blocked, specialty_partial = inspect_specialty_contract(
            manifest_payload,
            paper_dir,
            manifest_path,
        )
        blocked.extend(specialty_blocked)
        partial.extend(specialty_partial)

        scoped_blocked, scoped_partial = inspect_scoped_rewrite_contract(
            manifest_payload,
            paper_dir,
            manifest_path,
            release_gate_flags,
        )
        blocked.extend(scoped_blocked)
        partial.extend(scoped_partial)

    stage_blocked, stage_partial = inspect_stage_promotion(
        paper_dir,
        reviews_dir,
        display_dir,
        release_gate_flags,
        release_gate_present,
        workflow_route,
    )
    blocked.extend(stage_blocked)
    partial.extend(stage_partial)
    release_projection_path = migrated_note_path(paper_dir, "评审闭环与放行判断.md")
    if release_gate_source == "manifest" and not release_projection_path.exists():
        warnings.append(
            "Manifest release_gate is the machine gate, but the human-readable "
            "projection file is missing: "
            f"{release_projection_path}"
        )

    if blocked:
        print("STATUS: BLOCKED")
        print("Workspace contract check failed:")
        for issue in blocked:
            print(f"- BLOCKED: {issue}")
        for issue in partial:
            print(f"- PARTIAL: {issue}")
        for warning in warnings:
            print(f"- WARN: {warning}")
        return 1

    status = "PARTIAL" if partial else "READY"
    print(f"STATUS: {status}")
    if status == "READY":
        print(f"Workspace contract is ready: {paper_dir}")
    else:
        print(f"Workspace contract is usable but not ready for release: {paper_dir}")
    for issue in partial:
        print(f"- PARTIAL: {issue}")
    for warning in warnings:
        print(f"- WARN: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
