#!/usr/bin/env python3
from __future__ import annotations


WORKFLOW_ROUTE_CONTRACT_VERSION = "1.0"

ENTRY_MODES = (
    "initial_review",
    "version_rebase",
    "evidence_upgrade",
    "display_regression",
    "handoff_resume",
)

ENTRY_MODE_SET = set(ENTRY_MODES)
RESUMABLE_ENTRY_MODES = tuple(mode for mode in ENTRY_MODES if mode != "handoff_resume")

STEP_STATUS_VALUES = {"pending", "in_progress", "done", "skipped"}

ROUTE_REQUIRED_STEPS = {
    "initial_review": [
        "freeze_review_object",
        "sync_truth_source",
        "clear_template_taint",
        "complete_specialty_route",
        "build_initial_diagnosis",
    ],
    "version_rebase": [
        "freeze_review_object",
        "record_historical_sources",
        "record_rebase_window",
        "enumerate_impacted_artifacts",
        "regress_dependents",
    ],
    "evidence_upgrade": [
        "freeze_review_object",
        "sync_truth_source",
        "update_object_layer",
        "enumerate_impacted_artifacts",
        "regress_dependents",
    ],
    "display_regression": [
        "freeze_review_object",
        "sync_truth_source",
        "confirm_truth_source_stable",
        "enumerate_impacted_artifacts",
        "regress_dependents",
    ],
    "handoff_resume": [
        "handoff_restore",
        "resume_route_confirmation",
    ],
}

ROUTE_SKIPPED_STEPS = {
    "initial_review": [
        "handoff_restore",
        "record_historical_sources",
        "record_rebase_window",
        "resume_route_confirmation",
    ],
    "version_rebase": [
        "handoff_restore",
        "update_object_layer",
        "confirm_truth_source_stable",
        "resume_route_confirmation",
    ],
    "evidence_upgrade": [
        "handoff_restore",
        "record_historical_sources",
        "record_rebase_window",
        "confirm_truth_source_stable",
        "resume_route_confirmation",
    ],
    "display_regression": [
        "handoff_restore",
        "record_historical_sources",
        "record_rebase_window",
        "update_object_layer",
        "resume_route_confirmation",
    ],
    "handoff_resume": [
        "record_historical_sources",
        "record_rebase_window",
        "update_object_layer",
        "confirm_truth_source_stable",
    ],
}

ROUTE_ALLOWED_OUTPUT_FAMILIES = {
    "initial_review": [
        "object_layer",
        "evidence_ledgers",
        "review_report",
        "problem_pages",
        "process_projection",
    ],
    "version_rebase": [
        "object_layer",
        "evidence_ledgers",
        "review_report",
        "problem_pages",
        "process_projection",
    ],
    "evidence_upgrade": [
        "object_layer",
        "evidence_ledgers",
        "review_report",
        "problem_pages",
        "display_projection",
        "process_projection",
    ],
    "display_regression": [
        "review_report",
        "problem_pages",
        "display_projection",
        "process_projection",
    ],
    "handoff_resume": [
        "process_projection",
        "review_report",
    ],
}

ROUTE_FORBIDDEN_OUTPUT_FAMILIES = {
    "initial_review": [
        "execution_outputs",
        "readiness_verdict",
        "advisor_line_editing",
        "release_gate_reset",
    ],
    "version_rebase": [
        "execution_outputs",
        "readiness_verdict",
        "advisor_line_editing",
        "release_gate_reset",
    ],
    "evidence_upgrade": [
        "execution_outputs",
        "readiness_verdict",
        "advisor_line_editing",
        "release_gate_reset",
    ],
    "display_regression": [
        "execution_outputs",
        "readiness_verdict",
        "advisor_line_editing",
        "release_gate_reset",
    ],
    "handoff_resume": [
        "execution_outputs",
        "readiness_verdict",
        "advisor_line_editing",
        "display_projection",
        "release_gate_reset",
    ],
}


def route_steps(mode: str) -> list[str]:
    required = ROUTE_REQUIRED_STEPS.get(mode, [])
    skipped = ROUTE_SKIPPED_STEPS.get(mode, [])
    seen: list[str] = []
    for step in required + skipped:
        if step not in seen:
            seen.append(step)
    return seen


def route_registry_entry(mode: str) -> dict[str, object] | None:
    if mode not in ENTRY_MODE_SET:
        return None
    return {
        "required_steps": list(ROUTE_REQUIRED_STEPS[mode]),
        "skipped_steps": list(ROUTE_SKIPPED_STEPS[mode]),
        "allowed_output_families": list(ROUTE_ALLOWED_OUTPUT_FAMILIES[mode]),
        "forbidden_output_families": list(ROUTE_FORBIDDEN_OUTPUT_FAMILIES[mode]),
    }


def build_workflow_route(
    mode: str,
    *,
    resume_to_mode: str | None = None,
) -> dict[str, object]:
    spec = route_registry_entry(mode)
    if spec is None:
        raise ValueError(f"Unsupported workflow route mode: {mode}")

    step_state = {
        step: ("skipped" if step in spec["skipped_steps"] else "pending")
        for step in route_steps(mode)
    }
    active_step = next(
        (step for step in spec["required_steps"] if step_state[step] == "pending"),
        None,
    )
    return {
        "contract_version": WORKFLOW_ROUTE_CONTRACT_VERSION,
        "mode": mode,
        "resume_to_mode": resume_to_mode,
        "required_steps": list(spec["required_steps"]),
        "skipped_steps": list(spec["skipped_steps"]),
        "allowed_output_families": list(spec["allowed_output_families"]),
        "forbidden_output_families": list(spec["forbidden_output_families"]),
        "active_step": active_step,
        "step_state": step_state,
    }


def derive_workflow_route_from_entry_mode(
    entry_mode: str | None,
    *,
    resume_to_mode: str | None = None,
) -> dict[str, object] | None:
    if entry_mode not in ENTRY_MODE_SET:
        return None
    return build_workflow_route(entry_mode, resume_to_mode=resume_to_mode)
