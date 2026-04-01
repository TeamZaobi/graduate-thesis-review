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

REQUIRED_OBJECT_FILES = [
    "figures.json",
    "tables.json",
    "citations.json",
    "assets_manifest.json",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the minimum workspace contract for a thesis review project."
    )
    parser.add_argument("--paper-dir", required=True, help="Path to papers/paperXX")
    args = parser.parse_args()

    paper_dir = Path(args.paper_dir).expanduser().resolve()
    reviews_dir = paper_dir / "reviews"
    objects_dir = paper_dir / "objects"
    assets_dir = paper_dir / "assets"

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
        errors.append(f"Missing HTML workspace: {paper_dir / '综合评审汇总.html'}")

    thesis_files = list(paper_dir.glob("*.docx")) + list(paper_dir.glob("*.pdf"))
    if not thesis_files:
        warnings.append("No source DOCX/PDF found at paper root")

    for name in REQUIRED_REVIEW_FILES:
        path = reviews_dir / name
        if not path.exists():
            errors.append(f"Missing review contract file: {path}")

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
