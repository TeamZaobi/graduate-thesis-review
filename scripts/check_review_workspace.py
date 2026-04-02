#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_REVIEW_FILES = [
    "process_projection.md",
    "审阅对象冻结说明.md",
    "版本冻结与依赖回归台账.md",
    "关键数值与复算准入台账.md",
    "图表索引台账.md",
    "图表专项核查.md",
]

STRICT_REVIEW_FILES = [
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

    errors: list[str] = []
    warnings: list[str] = []

    if not paper_dir.exists():
        errors.append(f"Missing paper directory: {paper_dir}")
    if not reviews_dir.exists():
        errors.append(f"Missing reviews directory: {reviews_dir}")
    if not objects_dir.exists():
        errors.append(f"Missing objects directory: {objects_dir}")
    if not assets_dir.exists():
        errors.append(f"Missing assets directory: {assets_dir}")
    if not (paper_dir / "综合评审汇总.html").exists():
        errors.append(f"Missing display entry page: {paper_dir / '综合评审汇总.html'}")
    if not display_dir.exists():
        message = (
            f"Missing display directory: {display_dir}"
            if args.strict
            else (
                f"Missing display directory: {display_dir} "
                "(allowed in non-strict mode for legacy or single-page projects)"
            )
        )
        (errors if args.strict else warnings).append(message)

    thesis_files = list(paper_dir.glob("*.docx")) + list(paper_dir.glob("*.pdf"))
    if not thesis_files:
        warnings.append("No source DOCX/PDF found at paper root")

    for name in REQUIRED_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            errors.append(f"Missing review contract file: {path}")

    for name in STRICT_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            message = (
                f"Missing display projection contract file: {path}"
                if args.strict
                else (
                    f"Missing display projection contract file: {path} "
                    "(allowed in non-strict mode for legacy or single-page projects)"
                )
            )
            (errors if args.strict else warnings).append(message)

    for name in REQUIRED_OBJECT_FILES:
        path = objects_dir / name
        if not path.exists():
            errors.append(f"Missing object file: {path}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {path}: {exc}")
            continue
        if "items" not in payload or not isinstance(payload["items"], list):
            errors.append(f"Object file missing list-shaped 'items': {path}")

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
            (errors if args.strict else warnings).append(message)

    if not (assets_dir / "figures").exists():
        errors.append(f"Missing figures directory: {assets_dir / 'figures'}")
    if not (assets_dir / "pdf_pages").exists():
        errors.append(f"Missing pdf_pages directory: {assets_dir / 'pdf_pages'}")
    if not (assets_dir / "tables").exists():
        warnings.append(f"Missing tables directory: {assets_dir / 'tables'}")

    if errors:
        print("Workspace contract check failed:")
        for error in errors:
            print(f"- ERROR: {error}")
        for warning in warnings:
            print(f"- WARN: {warning}")
        return 1

    print(f"Workspace contract looks valid: {paper_dir}")
    for warning in warnings:
        print(f"- WARN: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
