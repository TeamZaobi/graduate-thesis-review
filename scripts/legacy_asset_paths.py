from __future__ import annotations

from pathlib import Path


LEGACY_MANIFEST_ALIAS_NAME = "review_version_manifest.json"
LEGACY_MANIFEST_CANONICAL_NAME = "legacy-review-manifest.json"

MIGRATED_NOTE_FILENAMES = {
    "process_projection.md",
    "评审闭环与放行判断.md",
    "专业手册完备性判断.md",
    "专业专项补充说明.md",
    "局部改写任务卡.md",
    "审阅对象冻结说明.md",
    "版本冻结与依赖回归台账.md",
    "关键数值与复算准入台账.md",
    "图表索引台账.md",
    "图表专项核查.md",
}


def notes_dir(paper_dir: Path) -> Path:
    return paper_dir / "notes"


def reviews_dir(paper_dir: Path) -> Path:
    return paper_dir / "reviews"


def canonical_manifest_path(paper_dir: Path) -> Path:
    return notes_dir(paper_dir) / LEGACY_MANIFEST_CANONICAL_NAME


def legacy_manifest_alias_path(paper_dir: Path) -> Path:
    return reviews_dir(paper_dir) / LEGACY_MANIFEST_ALIAS_NAME


def canonical_note_path(paper_dir: Path, filename: str) -> Path:
    return notes_dir(paper_dir) / filename


def legacy_note_alias_path(paper_dir: Path, filename: str) -> Path:
    return reviews_dir(paper_dir) / filename


def resolve_manifest_path(paper_dir: Path) -> Path:
    canonical = canonical_manifest_path(paper_dir)
    if canonical.exists():
        return canonical
    return legacy_manifest_alias_path(paper_dir)


def resolve_note_path(paper_dir: Path, filename: str) -> Path:
    canonical = canonical_note_path(paper_dir, filename)
    if canonical.exists():
        return canonical
    return legacy_note_alias_path(paper_dir, filename)


def migrated_note_path(paper_dir: Path, filename: str) -> Path:
    if filename in MIGRATED_NOTE_FILENAMES:
        return resolve_note_path(paper_dir, filename)
    return legacy_note_alias_path(paper_dir, filename)
