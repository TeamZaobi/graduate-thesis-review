from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_POLICY_PATH = (
    ROOT / "knowledge" / "output-policies" / "advice-output-policy.json"
)

OUTPUT_POLICY_REQUIRED_FIELDS = [
    "schema_version",
    "policy_id",
    "family",
    "version_anchor",
    "allowed_low_risk",
    "verdict_required_high_risk",
    "forbidden_transformations",
]

CLAIM_CEILING_ALLOWED_OUTPUTS = {
    "none": set(),
    "advisor_only": {
        "output.advisor.line-editing",
        "output.advisor.summary",
        "output.advisor.defense-talking-points",
    },
    "execution_ready": {
        "output.advisor.line-editing",
        "output.advisor.summary",
        "output.advisor.defense-talking-points",
        "output.student.execution-pack",
    },
}


def load_json(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_output_policy(path: Path | None = None) -> dict[str, object] | None:
    return load_json(path or DEFAULT_OUTPUT_POLICY_PATH)


def load_review_verdict(paper_dir: Path) -> dict[str, object] | None:
    return load_json(paper_dir / "evidence" / "review-verdict.json")


def validate_output_policy(policy: dict[str, object] | None) -> list[str]:
    if policy is None:
        return ["output policy is missing or unreadable"]

    errors = [
        f"missing field {field}"
        for field in OUTPUT_POLICY_REQUIRED_FIELDS
        if field not in policy
    ]
    for field in [
        "allowed_low_risk",
        "verdict_required_high_risk",
        "forbidden_transformations",
    ]:
        value = policy.get(field)
        if field in policy and not isinstance(value, list):
            errors.append(f"field {field} is not list-shaped")
    return errors


def output_policy_entries(
    policy: dict[str, object] | None,
) -> list[dict[str, object]]:
    if not isinstance(policy, dict):
        return []
    entries = policy.get("verdict_required_high_risk")
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def forbidden_transformation_entries(
    policy: dict[str, object] | None,
) -> list[dict[str, object]]:
    if not isinstance(policy, dict):
        return []
    entries = policy.get("forbidden_transformations")
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def forbidden_transformation_rules(
    policy: dict[str, object] | None,
) -> list[tuple[str, list[str]]]:
    rules: list[tuple[str, list[str]]] = []
    for entry in forbidden_transformation_entries(policy):
        rule_id = entry.get("rule_id")
        patterns = entry.get("patterns")
        if not isinstance(rule_id, str) or not isinstance(patterns, list):
            continue
        string_patterns = [item for item in patterns if isinstance(item, str)]
        if string_patterns:
            rules.append((rule_id, string_patterns))
    return rules


def high_risk_output_refs(policy: dict[str, object] | None) -> set[str]:
    refs: set[str] = set()
    for entry in output_policy_entries(policy):
        output_ref = entry.get("output_ref")
        if isinstance(output_ref, str):
            refs.add(output_ref)
    return refs


def claim_ceiling_allowed_refs(claim_ceiling: object) -> set[str] | None:
    if not isinstance(claim_ceiling, str):
        return None
    return CLAIM_CEILING_ALLOWED_OUTPUTS.get(claim_ceiling)


def validate_claim_ceiling_alignment(
    policy: dict[str, object] | None,
    verdict: dict[str, object] | None,
) -> list[str]:
    if not isinstance(verdict, dict):
        return ["review verdict is missing or unreadable"]

    claim_ceiling = verdict.get("claim_ceiling")
    ceiling_allowed = claim_ceiling_allowed_refs(claim_ceiling)
    if ceiling_allowed is None:
        supported = ", ".join(sorted(CLAIM_CEILING_ALLOWED_OUTPUTS))
        return [
            "review verdict claim_ceiling is missing or unsupported "
            f"({claim_ceiling!r}); supported values: {supported}"
        ]

    high_risk_refs = high_risk_output_refs(policy)
    allowed_output_refs = (
        {
            item
            for item in verdict.get("allowed_output_refs", [])
            if isinstance(item, str) and item in high_risk_refs
        }
        if isinstance(verdict.get("allowed_output_refs"), list)
        else set()
    )
    forbidden_output_refs = (
        {
            item
            for item in verdict.get("forbidden_output_refs", [])
            if isinstance(item, str) and item in high_risk_refs
        }
        if isinstance(verdict.get("forbidden_output_refs"), list)
        else set()
    )

    errors: list[str] = []
    overflow = sorted(allowed_output_refs - ceiling_allowed)
    if overflow:
        errors.append(
            "review verdict allowed outputs exceed claim_ceiling: "
            + ", ".join(overflow)
        )

    missing_forbidden = sorted((high_risk_refs - ceiling_allowed) - forbidden_output_refs)
    if missing_forbidden:
        errors.append(
            "review verdict does not explicitly forbid outputs above claim_ceiling: "
            + ", ".join(missing_forbidden)
        )

    conflicts = sorted(allowed_output_refs & forbidden_output_refs)
    if conflicts:
        errors.append(
            "review verdict marks the same output as both allowed and forbidden: "
            + ", ".join(conflicts)
        )

    return errors


def advice_output_decisions(
    policy: dict[str, object] | None,
    verdict: dict[str, object] | None,
) -> list[dict[str, object]]:
    claim_ceiling = verdict.get("claim_ceiling") if isinstance(verdict, dict) else None
    ceiling_allowed = claim_ceiling_allowed_refs(claim_ceiling)
    allowed_output_refs = (
        set(verdict.get("allowed_output_refs", []))
        if isinstance(verdict, dict) and isinstance(verdict.get("allowed_output_refs"), list)
        else set()
    )
    forbidden_output_refs = (
        set(verdict.get("forbidden_output_refs", []))
        if isinstance(verdict, dict) and isinstance(verdict.get("forbidden_output_refs"), list)
        else set()
    )

    decisions: list[dict[str, object]] = []
    for entry in output_policy_entries(policy):
        output_ref = entry.get("output_ref")
        route_family = entry.get("route_family")
        artifact_paths = entry.get("artifact_paths")
        if not isinstance(output_ref, str):
            continue
        if ceiling_allowed is None:
            allowed = False
            reason = "claim ceiling is missing or invalid"
        elif output_ref not in ceiling_allowed:
            allowed = False
            reason = f"claim ceiling {claim_ceiling!r} does not permit this output"
        elif output_ref in forbidden_output_refs:
            allowed = False
            reason = "forbidden by review verdict"
        elif output_ref in allowed_output_refs:
            allowed = True
            reason = "allowed by review verdict"
        else:
            allowed = False
            reason = "not yet allowed by review verdict"
        decisions.append(
            {
                "output_ref": output_ref,
                "route_family": route_family if isinstance(route_family, str) else None,
                "artifact_paths": artifact_paths if isinstance(artifact_paths, list) else [],
                "allowed": allowed,
                "reason": reason,
            }
        )
    return decisions


def build_output_policy_status(paper_dir: Path) -> dict[str, object]:
    policy_path = DEFAULT_OUTPUT_POLICY_PATH
    policy = load_output_policy(policy_path)
    verdict = load_review_verdict(paper_dir)
    errors = validate_output_policy(policy)
    alignment_errors = validate_claim_ceiling_alignment(policy, verdict) if not errors else []
    decisions = advice_output_decisions(policy, verdict) if not errors else []
    return {
        "path": str(policy_path),
        "present": policy_path.exists(),
        "shape_ok": not errors,
        "errors": errors,
        "alignment_ok": not alignment_errors,
        "alignment_errors": alignment_errors,
        "policy_id": policy.get("policy_id") if isinstance(policy, dict) else None,
        "claim_ceiling": verdict.get("claim_ceiling") if isinstance(verdict, dict) else None,
        "allowed_low_risk": (
            policy.get("allowed_low_risk")
            if isinstance(policy, dict) and isinstance(policy.get("allowed_low_risk"), list)
            else []
        ),
        "verdict_required_high_risk": decisions,
        "forbidden_transformations": [
            entry.get("rule_id")
            for entry in forbidden_transformation_entries(policy)
            if isinstance(entry.get("rule_id"), str)
        ],
    }
