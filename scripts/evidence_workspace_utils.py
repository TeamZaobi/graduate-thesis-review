from __future__ import annotations

import json
from pathlib import Path


EVIDENCE_REQUIRED_FILES = {
    "criteria_coverage": "criteria-coverage.json",
    "evidence_ledger": "evidence-ledger.jsonl",
    "review_verdict": "review-verdict.json",
    "limitations": "limitations.json",
}

CRITERIA_COVERAGE_REQUIRED_FIELDS = [
    "schema_version",
    "paper_id",
    "kind",
    "template_status",
    "coverage_level",
    "required_criterion_refs",
    "covered_criterion_refs",
    "missing_criterion_refs",
]

REVIEW_VERDICT_REQUIRED_FIELDS = [
    "schema_version",
    "paper_id",
    "kind",
    "template_status",
    "study_type_resolved",
    "specialty_resolved",
    "criteria_coverage_level",
    "evidence_sufficiency_level",
    "limitations_disclosed",
    "claim_ceiling",
    "allowed_output_refs",
    "forbidden_output_refs",
    "missing_criterion_refs",
    "missing_evidence_refs",
]

LIMITATIONS_REQUIRED_FIELDS = [
    "schema_version",
    "paper_id",
    "kind",
    "template_status",
    "limitations_disclosed",
    "items",
]


def build_criteria_coverage_payload(paper_id: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "kind": "criteria_coverage",
        "template_status": "tainted",
        "study_type_ref": None,
        "specialty_refs": [],
        "scene_ref": None,
        "coverage_level": "pending",
        "required_criterion_refs": [],
        "covered_criterion_refs": [],
        "missing_criterion_refs": [],
        "notes": [],
    }


def build_review_verdict_payload(
    paper_id: str,
    required_evidence_refs: list[str],
    forbidden_output_refs: list[str],
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "kind": "review_verdict",
        "template_status": "tainted",
        "study_type_resolved": False,
        "specialty_resolved": False,
        "criteria_coverage_level": "pending",
        "evidence_sufficiency_level": "pending",
        "limitations_disclosed": False,
        "claim_ceiling": "none",
        "allowed_output_refs": [],
        "forbidden_output_refs": forbidden_output_refs,
        "missing_criterion_refs": [],
        "missing_evidence_refs": required_evidence_refs,
        "summary": None,
    }


def build_limitations_payload(paper_id: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "kind": "limitations",
        "template_status": "tainted",
        "limitations_disclosed": False,
        "items": [],
    }


def load_json(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_jsonl(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    records: list[dict[str, object]] = []
    errors: list[str] = []
    if not path.exists():
        errors.append(f"missing {path.name}")
        return records, errors

    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"{path.name}: invalid JSON on line {line_no}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{path.name}: line {line_no} is not a JSON object")
            continue
        records.append(payload)
    return records, errors


def validate_required_fields(
    payload: dict[str, object] | None,
    required_fields: list[str],
    filename: str,
) -> list[str]:
    if payload is None:
        return [f"{filename}: invalid or unreadable JSON object"]
    return [f"{filename}: missing field {field}" for field in required_fields if field not in payload]


def validate_field_type(
    payload: dict[str, object] | None,
    field: str,
    expected_type: type | tuple[type, ...],
    filename: str,
) -> list[str]:
    if payload is None or field not in payload:
        return []
    if not isinstance(payload[field], expected_type):
        return [f"{filename}: field {field} has invalid type"]
    return []


def validate_evidence_workspace(evidence_dir: Path) -> dict[str, object]:
    files = {
        key: evidence_dir / filename for key, filename in EVIDENCE_REQUIRED_FILES.items()
    }
    result: dict[str, object] = {
        "path": str(evidence_dir),
        "present": evidence_dir.exists(),
        "files": {key: path.exists() for key, path in files.items()},
        "shape_ok": False,
        "errors": [],
        "criteria_coverage": None,
        "ledger": None,
        "review_verdict": None,
        "limitations": None,
    }
    errors: list[str] = []
    if not evidence_dir.exists():
        errors.append("evidence workspace missing")
        result["errors"] = errors
        return result

    criteria_payload = load_json(files["criteria_coverage"])
    verdict_payload = load_json(files["review_verdict"])
    limitations_payload = load_json(files["limitations"])
    ledger_records, ledger_errors = load_jsonl(files["evidence_ledger"])

    errors.extend(
        validate_required_fields(
            criteria_payload,
            CRITERIA_COVERAGE_REQUIRED_FIELDS,
            files["criteria_coverage"].name,
        )
    )
    errors.extend(
        validate_field_type(
            criteria_payload,
            "coverage_level",
            str,
            files["criteria_coverage"].name,
        )
    )
    for field in [
        "required_criterion_refs",
        "covered_criterion_refs",
        "missing_criterion_refs",
    ]:
        errors.extend(
            validate_field_type(
                criteria_payload,
                field,
                list,
                files["criteria_coverage"].name,
            )
        )
    errors.extend(
        validate_required_fields(
            verdict_payload,
            REVIEW_VERDICT_REQUIRED_FIELDS,
            files["review_verdict"].name,
        )
    )
    for field in [
        "study_type_resolved",
        "specialty_resolved",
        "limitations_disclosed",
    ]:
        errors.extend(
            validate_field_type(
                verdict_payload,
                field,
                bool,
                files["review_verdict"].name,
            )
        )
    for field in [
        "criteria_coverage_level",
        "evidence_sufficiency_level",
        "claim_ceiling",
    ]:
        errors.extend(
            validate_field_type(
                verdict_payload,
                field,
                str,
                files["review_verdict"].name,
            )
        )
    for field in [
        "allowed_output_refs",
        "forbidden_output_refs",
        "missing_criterion_refs",
        "missing_evidence_refs",
    ]:
        errors.extend(
            validate_field_type(
                verdict_payload,
                field,
                list,
                files["review_verdict"].name,
            )
        )
    errors.extend(
        validate_required_fields(
            limitations_payload,
            LIMITATIONS_REQUIRED_FIELDS,
            files["limitations"].name,
        )
    )
    errors.extend(
        validate_field_type(
            limitations_payload,
            "limitations_disclosed",
            bool,
            files["limitations"].name,
        )
    )
    errors.extend(
        validate_field_type(
            limitations_payload,
            "items",
            list,
            files["limitations"].name,
        )
    )
    errors.extend(ledger_errors)

    result["criteria_coverage"] = (
        {
            "coverage_level": criteria_payload.get("coverage_level"),
            "required_criterion_refs": criteria_payload.get("required_criterion_refs"),
            "covered_criterion_refs": criteria_payload.get("covered_criterion_refs"),
            "missing_criterion_refs": criteria_payload.get("missing_criterion_refs"),
        }
        if isinstance(criteria_payload, dict)
        else None
    )
    result["ledger"] = {
        "record_count": len(ledger_records),
    }
    result["review_verdict"] = (
        {
            "study_type_resolved": verdict_payload.get("study_type_resolved"),
            "specialty_resolved": verdict_payload.get("specialty_resolved"),
            "criteria_coverage_level": verdict_payload.get("criteria_coverage_level"),
            "evidence_sufficiency_level": verdict_payload.get("evidence_sufficiency_level"),
            "limitations_disclosed": verdict_payload.get("limitations_disclosed"),
            "claim_ceiling": verdict_payload.get("claim_ceiling"),
            "allowed_output_refs": verdict_payload.get("allowed_output_refs"),
            "forbidden_output_refs": verdict_payload.get("forbidden_output_refs"),
            "missing_criterion_refs": verdict_payload.get("missing_criterion_refs"),
            "missing_evidence_refs": verdict_payload.get("missing_evidence_refs"),
        }
        if isinstance(verdict_payload, dict)
        else None
    )
    result["limitations"] = (
        {
            "limitations_disclosed": limitations_payload.get("limitations_disclosed"),
            "item_count": len(limitations_payload.get("items", []))
            if isinstance(limitations_payload.get("items"), list)
            else None,
        }
        if isinstance(limitations_payload, dict)
        else None
    )
    result["shape_ok"] = not errors
    result["errors"] = errors
    return result
