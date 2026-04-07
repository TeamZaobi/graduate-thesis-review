#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from evidence_workspace_utils import validate_evidence_workspace
from legacy_asset_paths import (
    canonical_manifest_path,
    legacy_manifest_alias_path,
    migrated_note_path,
    notes_dir,
    resolve_manifest_path,
)
from output_policy_utils import build_output_policy_status
from release_gate_utils import (
    RELEASE_GATE_ALLOWED_VALUES,
    RELEASE_GATE_FIELDS,
    extract_release_gate_flags_from_manifest,
    extract_release_gate_flags_from_markdown,
    extract_release_gate_lists_from_manifest,
    has_explicit_release_gate_authority,
    manifest_release_gate_is_placeholder,
)
from specialty_gate_utils import (
    SPECIALTY_GATE_BOOLEAN_FIELDS,
    SPECIALTY_GATE_STATUS_FIELDS,
    extract_specialty_gate_flags_from_manifest,
    extract_specialty_gate_flags_from_markdown,
    extract_specialty_gate_lists_from_manifest,
    extract_specialty_gate_strings_from_manifest,
    has_explicit_specialty_gate_authority,
    manifest_specialty_gate_is_placeholder,
)
from workflow_route_registry import derive_workflow_route_from_entry_mode

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
GOVERNANCE_VALIDATOR = Path("/Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py")


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        text=True,
        capture_output=True,
        check=False,
    )


def detect_docx(paper_dir: Path) -> Path | None:
    docx_files = sorted(paper_dir.glob("*.docx"))
    return docx_files[0] if docx_files else None


def load_items_count(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    items = payload.get("items")
    return len(items) if isinstance(items, list) else None


def load_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def extract_scoped_rewrite(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return None
    task_exceptions = payload.get("task_exceptions")
    if not isinstance(task_exceptions, dict):
        return None
    scoped_rewrite = task_exceptions.get("scoped_rewrite")
    return scoped_rewrite if isinstance(scoped_rewrite, dict) else None


def extract_specialty_gate_from_manifest(
    payload: dict | None,
) -> tuple[str, dict[str, str | None]]:
    flags = extract_specialty_gate_flags_from_manifest(payload)
    if has_explicit_specialty_gate_authority(flags) and not manifest_specialty_gate_is_placeholder(payload):
        return "manifest", flags
    return "missing", flags


def extract_specialty_gate_policy(
    payload: dict | None,
) -> dict[str, object]:
    return {
        **extract_specialty_gate_lists_from_manifest(payload),
        **extract_specialty_gate_strings_from_manifest(payload),
    }


def extract_specialty_gate_from_markdown(
    path: Path,
) -> tuple[str, dict[str, str | None]]:
    flags = {
        field: None
        for field in SPECIALTY_GATE_STATUS_FIELDS + SPECIALTY_GATE_BOOLEAN_FIELDS
    }
    if not path.exists():
        return "missing", flags
    text = path.read_text(encoding="utf-8")
    flags = extract_specialty_gate_flags_from_markdown(text)
    if has_explicit_specialty_gate_authority(flags):
        return "markdown", flags
    return "missing", flags


def extract_release_gate_from_manifest(payload: dict | None) -> tuple[str, dict[str, str | None]]:
    flags = extract_release_gate_flags_from_manifest(payload)
    if (
        all(value in RELEASE_GATE_ALLOWED_VALUES for value in flags.values())
        and has_explicit_release_gate_authority(flags)
        and not manifest_release_gate_is_placeholder(payload)
    ):
        return "manifest", flags
    return "missing", flags


def extract_release_gate_policy(payload: dict | None) -> dict[str, list[str] | None]:
    return extract_release_gate_lists_from_manifest(payload)


def extract_release_gate_from_markdown(path: Path) -> tuple[str, dict[str, str | None]]:
    flags = {field: None for field in RELEASE_GATE_FIELDS}
    if not path.exists():
        return "missing", flags
    text = path.read_text(encoding="utf-8")
    flags = extract_release_gate_flags_from_markdown(text)
    if all(value in RELEASE_GATE_ALLOWED_VALUES for value in flags.values()):
        return "markdown", flags
    return "missing", flags


def extract_workflow_route(payload: dict | None) -> tuple[str, dict | None]:
    if not isinstance(payload, dict):
        return "missing", None

    route = payload.get("workflow_route")
    if isinstance(route, dict) and not (
        route.get("mode") in {None, ""}
        and route.get("resume_to_mode") in {None, ""}
        and route.get("required_steps") == []
        and route.get("skipped_steps") == []
        and route.get("allowed_output_families") == []
        and route.get("forbidden_output_families") == []
        and route.get("active_step") in {None, ""}
        and route.get("step_state") == {}
    ):
        return "manifest", route

    entry_mode = payload.get("entry_mode")
    derived = derive_workflow_route_from_entry_mode(entry_mode)
    if derived is not None:
        return "derived", derived
    return "missing", None


def parse_workspace_status(output: str) -> str | None:
    for line in output.splitlines():
        if line.startswith("STATUS: "):
            return line.split("STATUS: ", 1)[1].strip()
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate thesis-review toolchain readiness on a paper workspace."
    )
    parser.add_argument("--paper-dir", required=True, help="Path to papers/paperXX")
    parser.add_argument("--docx", help="Optional DOCX override")
    parser.add_argument(
        "--match-root",
        action="append",
        default=[],
        help="Optional stale absolute root prefix to scan for",
    )
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    paper_dir = Path(args.paper_dir).expanduser().resolve()
    if not paper_dir.exists():
        print(f"Missing paper directory: {paper_dir}", file=sys.stderr)
        return 1

    reviews_dir = paper_dir / "reviews"
    notes_workspace_dir = notes_dir(paper_dir)
    runtime_pack_dir = paper_dir / "governance" / "review-workspace-pack"
    evidence_dir = paper_dir / "evidence"
    objects_dir = paper_dir / "objects"
    assets_dir = paper_dir / "assets"
    manifest_path = resolve_manifest_path(paper_dir)
    manifest_payload = load_manifest(manifest_path)
    entry_mode = manifest_payload.get("entry_mode") if isinstance(manifest_payload, dict) else None
    workflow_route_source, workflow_route = extract_workflow_route(manifest_payload)
    release_gate_source, release_gate_flags = extract_release_gate_from_manifest(
        manifest_payload
    )
    release_gate_policy = extract_release_gate_policy(manifest_payload)
    specialty_gate_source, specialty_gate_flags = extract_specialty_gate_from_manifest(
        manifest_payload
    )
    specialty_gate_policy = extract_specialty_gate_policy(manifest_payload)
    scoped_rewrite = extract_scoped_rewrite(manifest_payload)
    if release_gate_source == "missing":
        release_gate_source, release_gate_flags = extract_release_gate_from_markdown(
            migrated_note_path(paper_dir, "评审闭环与放行判断.md")
        )
    if specialty_gate_source == "missing":
        specialty_gate_source, specialty_gate_flags = extract_specialty_gate_from_markdown(
            migrated_note_path(paper_dir, "专业手册完备性判断.md")
        )
    docx_path = Path(args.docx).expanduser().resolve() if args.docx else detect_docx(paper_dir)

    report: dict[str, object] = {
        "paper_dir": str(paper_dir),
        "docx_path": str(docx_path) if docx_path else None,
        "notes": {
            "path": str(notes_workspace_dir),
            "present": notes_workspace_dir.exists(),
        },
        "legacy_manifest": {
            "path": str(manifest_path),
            "canonical": manifest_path == canonical_manifest_path(paper_dir),
            "legacy_alias_path": str(legacy_manifest_alias_path(paper_dir)),
        },
        "workspace_contract_ok": None,
        "workspace_contract_status": None,
        "docx_lines_present": any(reviews_dir.glob("*docx_lines.txt")),
        "entry_mode": entry_mode,
        "workflow_route": {
            "source": workflow_route_source,
            "mode": workflow_route.get("mode") if isinstance(workflow_route, dict) else None,
            "resume_to_mode": workflow_route.get("resume_to_mode") if isinstance(workflow_route, dict) else None,
            "active_step": workflow_route.get("active_step") if isinstance(workflow_route, dict) else None,
            "required_steps": workflow_route.get("required_steps") if isinstance(workflow_route, dict) else None,
            "forbidden_output_families": workflow_route.get("forbidden_output_families") if isinstance(workflow_route, dict) else None,
        },
        "process_projection_present": migrated_note_path(
            paper_dir, "process_projection.md"
        ).exists(),
        "process_projection_required": entry_mode == "handoff_resume",
        "runtime_pack": {
            "path": str(runtime_pack_dir),
            "present": runtime_pack_dir.exists(),
            "validator": None,
        },
        "evidence_workspace": validate_evidence_workspace(evidence_dir),
        "output_policy": build_output_policy_status(paper_dir),
        "release_gate": {
            "source": release_gate_source,
            **release_gate_flags,
            **release_gate_policy,
        },
        "specialty": {
            "source": specialty_gate_source,
            "readiness_record_present": migrated_note_path(
                paper_dir, "专业手册完备性判断.md"
            ).exists(),
            "supplement_present": migrated_note_path(
                paper_dir, "专业专项补充说明.md"
            ).exists(),
            **specialty_gate_flags,
            **specialty_gate_policy,
        },
        "task_exceptions": {
            "scoped_rewrite_enabled": (
                scoped_rewrite.get("enabled")
                if isinstance(scoped_rewrite, dict)
                else None
            ),
            "scoped_rewrite_targets": (
                scoped_rewrite.get("targets")
                if isinstance(scoped_rewrite, dict)
                else None
            ),
            "scoped_rewrite_reason": (
                scoped_rewrite.get("reason")
                if isinstance(scoped_rewrite, dict)
                else None
            ),
            "scoped_rewrite_task_card_present": (
                migrated_note_path(paper_dir, "局部改写任务卡.md")
            ).exists(),
        },
        "objects": {
            "figures_items": load_items_count(objects_dir / "figures.json"),
            "tables_items": load_items_count(objects_dir / "tables.json"),
            "citations_items": load_items_count(objects_dir / "citations.json"),
            "assets_manifest_items": load_items_count(objects_dir / "assets_manifest.json"),
        },
        "assets": {
            "figures_files": len(list((assets_dir / "figures").rglob("*"))) if (assets_dir / "figures").exists() else 0,
            "table_csv_files": len(list((assets_dir / "tables").rglob("*.csv"))) if (assets_dir / "tables").exists() else 0,
            "page_render_files": len(list((assets_dir / "page_renders").glob("*"))) if (assets_dir / "page_renders").exists() else 0,
            "legacy_pdf_page_files": len(list((assets_dir / "pdf_pages").glob("*"))) if (assets_dir / "pdf_pages").exists() else 0,
        },
        "timings_ms": {},
        "extraction": {},
        "stale_path_scan": None,
    }

    started = time.perf_counter()
    contract = run_cmd(
        [
            sys.executable,
            str(SCRIPTS_DIR / "check_review_workspace.py"),
            "--paper-dir",
            str(paper_dir),
        ]
    )
    report["timings_ms"]["check_review_workspace"] = round((time.perf_counter() - started) * 1000, 2)
    contract_output = contract.stdout.strip() or contract.stderr.strip()
    workspace_status = parse_workspace_status(contract_output)
    report["workspace_contract_ok"] = contract.returncode == 0
    report["workspace_contract_status"] = workspace_status
    report["workspace_contract_output"] = contract_output

    if runtime_pack_dir.exists() and GOVERNANCE_VALIDATOR.exists():
        started = time.perf_counter()
        runtime_validation = run_cmd(
            [
                sys.executable,
                str(GOVERNANCE_VALIDATOR),
                str(runtime_pack_dir),
            ]
        )
        report["timings_ms"]["validate_runtime_pack"] = round((time.perf_counter() - started) * 1000, 2)
        output = runtime_validation.stdout.strip() or runtime_validation.stderr.strip()
        report["runtime_pack"]["validator"] = {
            "ok": runtime_validation.returncode == 0 and not output,
            "output": output or None,
        }

    if docx_path and docx_path.exists():
        with tempfile.TemporaryDirectory() as tmpdir:
            media_dir = Path(tmpdir) / "media"
            tables_dir = Path(tmpdir) / "tables"

            started = time.perf_counter()
            media = run_cmd(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "extract_docx_media.py"),
                    "--docx",
                    str(docx_path),
                    "--output",
                    str(media_dir),
                ]
            )
            report["timings_ms"]["extract_docx_media"] = round((time.perf_counter() - started) * 1000, 2)
            media_manifest = media_dir / "manifest.json"
            media_count = None
            if media_manifest.exists():
                media_count = json.loads(media_manifest.read_text(encoding="utf-8")).get("item_count")

            started = time.perf_counter()
            tables = run_cmd(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "extract_docx_tables.py"),
                    "--docx",
                    str(docx_path),
                    "--output-dir",
                    str(tables_dir),
                ]
            )
            report["timings_ms"]["extract_docx_tables"] = round((time.perf_counter() - started) * 1000, 2)
            table_manifest = tables_dir / "manifest.json"
            table_count = None
            if table_manifest.exists():
                table_count = json.loads(table_manifest.read_text(encoding="utf-8")).get("table_count")

            started = time.perf_counter()
            citations = run_cmd(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "extract_docx_citations.py"),
                    "--docx",
                    str(docx_path),
                    "--output-dir",
                    str(Path(tmpdir) / "citations"),
                ]
            )
            report["timings_ms"]["extract_docx_citations"] = round((time.perf_counter() - started) * 1000, 2)
            citation_manifest = Path(tmpdir) / "citations" / "manifest.json"
            citation_count = None
            reference_count = None
            if citation_manifest.exists():
                citation_payload = json.loads(citation_manifest.read_text(encoding="utf-8"))
                citation_count = citation_payload.get("item_count")
                reference_count = citation_payload.get("reference_count")

            report["extraction"] = {
                "media_ok": media.returncode == 0,
                "media_count": media_count,
                "tables_ok": tables.returncode == 0,
                "table_count": table_count,
                "citations_ok": citations.returncode == 0,
                "citation_count": citation_count,
                "reference_count": reference_count,
            }

    if args.match_root:
        started = time.perf_counter()
        stale = run_cmd(
            [
                sys.executable,
                str(SCRIPTS_DIR / "scan_stale_paths.py"),
                "--root",
                str(paper_dir.parent.parent),
                *sum([["--match-root", value] for value in args.match_root], []),
            ]
        )
        report["timings_ms"]["scan_stale_paths"] = round((time.perf_counter() - started) * 1000, 2)
        matches = [
            line
            for line in stale.stdout.splitlines()
            if line.strip() and not line.startswith("Found ")
        ]
        report["stale_path_scan"] = {
            "ok": stale.returncode == 0,
            "match_count": len(matches),
            "matches": matches[:20],
        }

    report["proxy_summary"] = {
        "has_structured_objects": all(
            report["objects"][key] is not None for key in report["objects"]
        ),
        "entry_mode": report["entry_mode"],
        "workflow_route_source": report["workflow_route"]["source"],
        "workflow_route_mode": report["workflow_route"]["mode"],
        "workflow_route_active_step": report["workflow_route"]["active_step"],
        "evidence_workspace_present": report["evidence_workspace"]["present"],
        "evidence_workspace_shape_ok": report["evidence_workspace"]["shape_ok"],
        "review_verdict_claim_ceiling": (
            report["evidence_workspace"]["review_verdict"]["claim_ceiling"]
            if isinstance(report["evidence_workspace"]["review_verdict"], dict)
            else None
        ),
        "review_verdict_criteria_coverage_level": (
            report["evidence_workspace"]["review_verdict"]["criteria_coverage_level"]
            if isinstance(report["evidence_workspace"]["review_verdict"], dict)
            else None
        ),
        "output_policy_present": report["output_policy"]["present"],
        "output_policy_shape_ok": report["output_policy"]["shape_ok"],
        "policy_high_risk_outputs_allowed": [
            item["output_ref"]
            for item in report["output_policy"]["verdict_required_high_risk"]
            if isinstance(item, dict) and item.get("allowed") is True
        ],
        "has_process_projection": report["process_projection_present"],
        "process_projection_required": report["process_projection_required"],
        "release_gate_source": report["release_gate"]["source"],
        "has_docx_lines": report["docx_lines_present"],
        "specialty_gate_source": report["specialty"]["source"],
        "has_specialty_readiness_record": report["specialty"]["readiness_record_present"],
        "specialty_readiness_status": report["specialty"]["specialty_readiness"],
        "scoped_rewrite_enabled": report["task_exceptions"]["scoped_rewrite_enabled"],
        "media_extractable": report["extraction"].get("media_ok"),
        "tables_extractable": report["extraction"].get("tables_ok"),
        "citations_extractable": report["extraction"].get("citations_ok"),
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).expanduser().resolve().write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
