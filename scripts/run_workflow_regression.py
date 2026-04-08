#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from legacy_asset_paths import migrated_note_path, resolve_manifest_path
from workflow_route_registry import ENTRY_MODE_SET, build_workflow_route


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURE_DIR = ROOT / "evals" / "workflow_fixtures"

CORE_REVIEW_CONTENT = {
    "审阅对象冻结说明.md": "# 审阅对象冻结说明\n\n已冻结当前审阅对象。\n",
    "版本冻结与依赖回归台账.md": "# 版本冻结与依赖回归台账\n\n已记录当前版本基线。\n",
    "关键数值与复算准入台账.md": "# 关键数值与复算准入台账\n\n当前按非复算审查边界处理。\n",
    "图表索引台账.md": "# 图表索引台账\n\n已建立图表索引。\n",
    "图表专项核查.md": "# 图表专项核查\n\n已记录图表核查入口。\n",
    "process_projection.md": "# process_projection\n\n## goal\n维持当前工作流。\n\n## actions\n- 继续按当前阶段处理。\n\n## findings\n- 已冻结最小工作区合同。\n\n## decisions\n- 暂不越权推进。\n\n## artifacts\n- notes/legacy-review-manifest.json\n\n## status\n进行中。\n\n## next_step\n继续当前阶段。\n",
}


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def deep_merge(base: dict, updates: dict) -> dict:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def set_path_value(payload: dict, path: str, value: object) -> None:
    current: object = payload
    parts = path.split(".")
    for part in parts[:-1]:
        if not isinstance(current, dict):
            raise KeyError(path)
        current = current[part]
    if not isinstance(current, dict):
        raise KeyError(path)
    current[parts[-1]] = value


def get_path_value(payload: dict, path: str) -> object:
    current: object = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            raise KeyError(path)
        current = current[part]
    return current


def normalize_json(obj: object) -> object:
    if isinstance(obj, list):
        return [normalize_json(item) for item in obj]
    if isinstance(obj, dict):
        return {key: normalize_json(value) for key, value in obj.items()}
    return obj


def prepare_workspace(root: Path, fixture: dict) -> Path:
    paper_id = fixture.get("paper_id")
    if not isinstance(paper_id, str) or not paper_id:
        raise ValueError(f"Invalid paper_id in fixture: {fixture.get('name')}")

    init = run_cmd(
        [
            sys.executable,
            str(SCRIPTS_DIR / "init_review_workspace.py"),
            "--root",
            str(root),
            "--paper-id",
            paper_id,
        ]
    )
    if init.returncode != 0:
        raise RuntimeError(init.stderr or init.stdout)

    paper_dir = root / "papers" / paper_id
    reviews_dir = paper_dir / "reviews"
    manifest_path = resolve_manifest_path(paper_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    manifest_updates = fixture.get("manifest_updates", {})
    if not isinstance(manifest_updates, dict):
        raise ValueError(f"manifest_updates must be object in fixture: {fixture.get('name')}")
    manifest = deep_merge(manifest, manifest_updates)

    entry_mode = manifest.get("entry_mode")
    if entry_mode in ENTRY_MODE_SET:
        workflow_route = manifest.get("workflow_route")
        if not isinstance(workflow_route, dict) or workflow_route.get("mode") in {None, ""}:
            manifest["workflow_route"] = build_workflow_route(entry_mode)

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for filename, content in CORE_REVIEW_CONTENT.items():
        migrated_note_path(paper_dir, filename).write_text(content, encoding="utf-8")

    file_overrides = fixture.get("file_overrides", {})
    if not isinstance(file_overrides, dict):
        raise ValueError(f"file_overrides must be object in fixture: {fixture.get('name')}")
    for relative_path, content in file_overrides.items():
        path = paper_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    removals = fixture.get("remove_paths", [])
    if not isinstance(removals, list):
        raise ValueError(f"remove_paths must be list in fixture: {fixture.get('name')}")
    for relative_path in removals:
        path = paper_dir / relative_path
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    return paper_dir


def evaluate_fixture(fixture_path: Path) -> tuple[bool, list[str]]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        paper_dir = prepare_workspace(Path(tmpdir), fixture)

        check = run_cmd(
            [
                sys.executable,
                str(SCRIPTS_DIR / "check_review_workspace.py"),
                "--paper-dir",
                str(paper_dir),
            ]
        )
        check_output = check.stdout.strip() or check.stderr.strip()
        status_line = next(
            (line for line in check_output.splitlines() if line.startswith("STATUS: ")),
            None,
        )
        actual_status = status_line.split("STATUS: ", 1)[1].strip() if status_line else None

        evaluate = run_cmd(
            [
                sys.executable,
                str(SCRIPTS_DIR / "evaluate_review_toolchain.py"),
                "--paper-dir",
                str(paper_dir),
            ]
        )
        if evaluate.returncode != 0:
            failures.append(
                f"evaluate_review_toolchain failed: {evaluate.stderr or evaluate.stdout}"
            )
            return False, failures
        report = json.loads(evaluate.stdout)

    expected = fixture.get("expected", {})
    if not isinstance(expected, dict):
        failures.append("expected block must be object")
        return False, failures

    expected_status = expected.get("check_status")
    if expected_status is not None and actual_status != expected_status:
        failures.append(
            f"check_status expected {expected_status!r}, got {actual_status!r}"
        )

    for snippet in expected.get("check_contains", []):
        if snippet not in check_output:
            failures.append(f"missing check_output snippet: {snippet!r}")

    for snippet in expected.get("check_not_contains", []):
        if snippet in check_output:
            failures.append(f"unexpected check_output snippet: {snippet!r}")

    report_equals = expected.get("report_equals", {})
    if not isinstance(report_equals, dict):
        failures.append("report_equals must be object")
    else:
        for path, expected_value in report_equals.items():
            try:
                actual_value = get_path_value(report, path)
            except KeyError:
                failures.append(f"missing report path: {path}")
                continue
            if normalize_json(actual_value) != normalize_json(expected_value):
                failures.append(
                    f"report path {path} expected {expected_value!r}, got {actual_value!r}"
                )

    return not failures, failures


def load_fixtures(selected: list[str]) -> list[Path]:
    if selected:
        fixtures = [FIXTURE_DIR / f"{name}.json" for name in selected]
    else:
        fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    missing = [path for path in fixtures if not path.exists()]
    if missing:
        raise FileNotFoundError(", ".join(str(path) for path in missing))
    return fixtures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run execution-style workflow regression fixtures."
    )
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Fixture name without .json suffix. Repeatable.",
    )
    args = parser.parse_args()

    fixtures = load_fixtures(args.fixture)
    failures = 0
    for fixture_path in fixtures:
        ok, messages = evaluate_fixture(fixture_path)
        if ok:
            print(f"PASS: {fixture_path.stem}")
            continue
        failures += 1
        print(f"FAIL: {fixture_path.stem}")
        for message in messages:
            print(f"- {message}")

    if failures:
        print(f"Workflow regression failed: {failures}/{len(fixtures)} fixture(s)")
        return 1

    print(f"Workflow regression passed: {len(fixtures)} fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
