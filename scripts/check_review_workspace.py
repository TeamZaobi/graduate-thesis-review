#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_REVIEW_FILES = [
    "process_projection.md",
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


def inspect_manifest(path: Path) -> tuple[list[str], list[str]]:
    blocked: list[str] = []
    partial: list[str] = []
    payload = load_json(path)
    if payload is None:
        blocked.append(f"Invalid JSON in {path}")
        return blocked, partial

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
        return blocked, partial

    if payload.get("template_status") == "tainted":
        blocked.append(f"Manifest template taint not cleared: {path}")

    entry_mode = payload.get("entry_mode")
    allowed_entry_modes = {
        None,
        "initial_review",
        "version_rebase",
        "evidence_upgrade",
        "display_regression",
        "handoff_resume",
    }
    if entry_mode not in allowed_entry_modes:
        partial.append(f"Manifest entry_mode is invalid: {path}")
    if entry_mode is None and payload.get("template_status") != "tainted":
        partial.append(f"Manifest entry_mode is not set yet: {path}")

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
    objects_dir = paper_dir / "objects"
    assets_dir = paper_dir / "assets"
    display_dir = paper_dir / "display"

    blocked: list[str] = []
    partial: list[str] = []
    warnings: list[str] = []

    if not paper_dir.exists():
        blocked.append(f"Missing paper directory: {paper_dir}")
    if not reviews_dir.exists():
        blocked.append(f"Missing reviews directory: {reviews_dir}")
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

    thesis_files = list(paper_dir.glob("*.docx")) + list(paper_dir.glob("*.pdf"))
    if not thesis_files:
        partial.append("No source DOCX/PDF found at paper root")

    for name in REQUIRED_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            blocked.append(f"Missing review contract file: {path}")
            continue
        if path.suffix == ".json":
            manifest_blocked, manifest_partial = inspect_manifest(path)
            blocked.extend(manifest_blocked)
            partial.extend(manifest_partial)
            continue
        file_blocked, file_partial = inspect_markdown_file(path)
        blocked.extend(file_blocked)
        partial.extend(file_partial)

    for name in STRICT_GATE_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            message = (
                f"Missing review release gate file: {path}"
                if args.strict
                else (
                    f"Missing review release gate file: {path} "
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
        if len(payload["items"]) == 0:
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
    if not (assets_dir / "pdf_pages").exists():
        blocked.append(f"Missing pdf_pages directory: {assets_dir / 'pdf_pages'}")
    if not (assets_dir / "tables").exists():
        warnings.append(f"Missing tables directory: {assets_dir / 'tables'}")

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
