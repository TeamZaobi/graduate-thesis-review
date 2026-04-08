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


def inspect_alias_state(canonical_path: Path, alias_path: Path) -> dict[str, object]:
    canonical_exists = canonical_path.exists()
    alias_exists = alias_path.exists()
    alias_is_symlink = alias_path.is_symlink()
    alias_target = None
    alias_points_to_canonical = False

    if alias_is_symlink:
        try:
            alias_target = alias_path.readlink()
            alias_points_to_canonical = (
                (alias_path.parent / alias_target).resolve(strict=False)
                == canonical_path.resolve(strict=False)
            )
        except OSError:
            alias_target = None

    if canonical_exists and alias_is_symlink and alias_points_to_canonical:
        status = "healthy"
    elif canonical_exists and not alias_exists and not alias_is_symlink:
        status = "canonical_only"
    elif canonical_exists and alias_exists and not alias_is_symlink:
        status = "dual_track_regular_file"
    elif canonical_exists and alias_is_symlink and not alias_points_to_canonical:
        status = "alias_target_mismatch"
    elif alias_exists or alias_is_symlink:
        status = "legacy_primary"
    else:
        status = "missing"

    return {
        "canonical_path": str(canonical_path),
        "alias_path": str(alias_path),
        "canonical_exists": canonical_exists,
        "alias_exists": alias_exists or alias_is_symlink,
        "alias_is_symlink": alias_is_symlink,
        "alias_target": str(alias_target) if alias_target is not None else None,
        "alias_points_to_canonical": alias_points_to_canonical,
        "status": status,
    }


def inspect_legacy_compatibility(paper_dir: Path) -> dict[str, object]:
    manifest = inspect_alias_state(
        canonical_manifest_path(paper_dir),
        legacy_manifest_alias_path(paper_dir),
    )
    migrated_notes = {
        filename: inspect_alias_state(
            canonical_note_path(paper_dir, filename),
            legacy_note_alias_path(paper_dir, filename),
        )
        for filename in sorted(MIGRATED_NOTE_FILENAMES)
    }

    partial: list[str] = []
    warnings: list[str] = []

    manifest_status = str(manifest["status"])
    if manifest_status == "legacy_primary":
        partial.append(
            "Legacy manifest alias is still acting as the primary path; "
            f"restore canonical {canonical_manifest_path(paper_dir)}"
        )
    elif manifest_status == "dual_track_regular_file":
        partial.append(
            "Legacy manifest alias is a regular file alongside canonical manifest; "
            "this creates dual-track drift"
        )
    elif manifest_status == "alias_target_mismatch":
        partial.append(
            "Legacy manifest alias does not point to canonical manifest; "
            "compatibility alias is drifting"
        )
    elif manifest_status == "canonical_only":
        warnings.append(
            "Canonical legacy manifest exists without reviews/ alias; "
            "compatibility layer is partially missing"
        )

    note_issue_count = 0
    note_warning_count = 0
    for filename, state in migrated_notes.items():
        status = str(state["status"])
        if status in {"legacy_primary", "dual_track_regular_file", "alias_target_mismatch"}:
            note_issue_count += 1
            partial.append(
                f"Migrated note alias drift for {filename}: {state['alias_path']} -> {status}"
            )
        elif status == "canonical_only":
            note_warning_count += 1
            warnings.append(
                f"Migrated note alias is missing for {filename}: {state['alias_path']}"
            )

    return {
        "manifest": manifest,
        "migrated_notes": migrated_notes,
        "partial": partial,
        "warnings": warnings,
        "note_issue_count": note_issue_count,
        "note_warning_count": note_warning_count,
    }
