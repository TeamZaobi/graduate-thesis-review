from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRUTH_PACK_ROOT = ROOT / "workflow" / "review-workspace"

RUNTIME_TRUTH_ROOT_FILES = [
    "workflow.contract.json",
    "rules.contract.json",
    "agent.contract.json",
]


def _load_normalized_json(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def truth_pack_relpaths(truth_pack_root: Path = TRUTH_PACK_ROOT) -> set[str]:
    relpaths = set(RUNTIME_TRUTH_ROOT_FILES)
    objects_dir = truth_pack_root / "objects"
    if objects_dir.exists():
        relpaths.update(
            str(path.relative_to(truth_pack_root))
            for path in sorted(objects_dir.rglob("*.json"))
        )
    return relpaths


def inspect_runtime_pack_drift(
    paper_dir: Path,
    truth_pack_root: Path = TRUTH_PACK_ROOT,
) -> dict[str, object]:
    runtime_pack_root = paper_dir / "governance" / "review-workspace-pack"
    expected_relpaths = truth_pack_relpaths(truth_pack_root)

    if not truth_pack_root.exists():
        return {
            "truth_pack_path": str(truth_pack_root),
            "runtime_pack_path": str(runtime_pack_root),
            "present": runtime_pack_root.exists(),
            "truth_pack_present": False,
            "ok": False,
            "missing_files": [],
            "extra_files": [],
            "mismatched_files": [],
            "errors": [f"repo truth pack is missing: {truth_pack_root}"],
        }

    if not runtime_pack_root.exists():
        return {
            "truth_pack_path": str(truth_pack_root),
            "runtime_pack_path": str(runtime_pack_root),
            "present": False,
            "truth_pack_present": True,
            "ok": False,
            "missing_files": sorted(expected_relpaths),
            "extra_files": [],
            "mismatched_files": [],
            "errors": [f"runtime pack is missing: {runtime_pack_root}"],
        }

    actual_relpaths = {
        str(runtime_pack_root / filename).replace(str(runtime_pack_root) + "/", "")
        for filename in RUNTIME_TRUTH_ROOT_FILES
        if (runtime_pack_root / filename).exists()
    }
    objects_dir = runtime_pack_root / "objects"
    if objects_dir.exists():
        actual_relpaths.update(
            str(path.relative_to(runtime_pack_root))
            for path in sorted(objects_dir.rglob("*.json"))
        )

    missing_files = sorted(expected_relpaths - actual_relpaths)
    extra_files = sorted(actual_relpaths - expected_relpaths)
    mismatched_files: list[str] = []
    unreadable_files: list[str] = []

    for relpath in sorted(expected_relpaths & actual_relpaths):
        truth_path = truth_pack_root / relpath
        runtime_path = runtime_pack_root / relpath
        truth_json = _load_normalized_json(truth_path)
        runtime_json = _load_normalized_json(runtime_path)
        if truth_json is None or runtime_json is None:
            unreadable_files.append(relpath)
            continue
        if truth_json != runtime_json:
            mismatched_files.append(relpath)

    errors: list[str] = []
    if missing_files:
        errors.append(
            "runtime pack is missing truth-pack files: " + ", ".join(missing_files)
        )
    if extra_files:
        errors.append(
            "runtime pack has unexpected truth-slice files: " + ", ".join(extra_files)
        )
    if mismatched_files:
        errors.append(
            "runtime pack files drifted from repo truth pack: "
            + ", ".join(mismatched_files)
        )
    if unreadable_files:
        errors.append(
            "runtime pack contains unreadable truth-slice JSON files: "
            + ", ".join(unreadable_files)
        )

    return {
        "truth_pack_path": str(truth_pack_root),
        "runtime_pack_path": str(runtime_pack_root),
        "present": True,
        "truth_pack_present": True,
        "ok": not errors,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "mismatched_files": mismatched_files,
        "unreadable_files": unreadable_files,
        "errors": errors,
    }
