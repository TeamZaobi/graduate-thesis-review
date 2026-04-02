#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


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
    objects_dir = paper_dir / "objects"
    assets_dir = paper_dir / "assets"
    docx_path = Path(args.docx).expanduser().resolve() if args.docx else detect_docx(paper_dir)

    report: dict[str, object] = {
        "paper_dir": str(paper_dir),
        "docx_path": str(docx_path) if docx_path else None,
        "workspace_contract_ok": None,
        "workspace_contract_status": None,
        "docx_lines_present": any(reviews_dir.glob("*docx_lines.txt")),
        "process_projection_present": (reviews_dir / "process_projection.md").exists(),
        "objects": {
            "figures_items": load_items_count(objects_dir / "figures.json"),
            "tables_items": load_items_count(objects_dir / "tables.json"),
            "citations_items": load_items_count(objects_dir / "citations.json"),
            "assets_manifest_items": load_items_count(objects_dir / "assets_manifest.json"),
        },
        "assets": {
            "figures_files": len(list((assets_dir / "figures").rglob("*"))) if (assets_dir / "figures").exists() else 0,
            "table_csv_files": len(list((assets_dir / "tables").rglob("*.csv"))) if (assets_dir / "tables").exists() else 0,
            "pdf_page_files": len(list((assets_dir / "pdf_pages").glob("*"))) if (assets_dir / "pdf_pages").exists() else 0,
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
        "has_process_projection": report["process_projection_present"],
        "has_docx_lines": report["docx_lines_present"],
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
