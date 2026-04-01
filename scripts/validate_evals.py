#!/usr/bin/env python3
"""Lightweight validation for graduate-thesis-review eval coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = ROOT / "evals" / "evals.json"

REQUIRED_THEMES = {
    "object_freeze": ["审阅对象冻结", "版本基线", "已存在但待重写", "学生口述"],
    "template_vs_filled": ["空骨架", "模板", "实填", "证据型中间文件"],
    "truth_source_regression": ["真源", "依赖回归", "版本漂移", "旧值"],
    "recompute_boundary": ["非复算审查", "原始数据", "脚本", "重新跑过模型"],
    "supplement_closure": ["主文", "补充", "附录", "结构性问题"],
    "compliance_citation": ["伦理", "注册", "数据可得性", "引文法证", "二手文献"],
    "context_isolation": ["上下文隔离", "workflow", "遗漏", "图表审阅"],
    "object_layer": ["figures.json", "tables.json", "assets_manifest.json", "对象层"],
    "process_projection": ["process_projection", "线程", "接手", "恢复"],
    "path_drift": ["旧绝对路径", "迁移", "路径漂移", "scan_stale_paths.py"],
    "table_pipeline": ["extract_docx_tables.py", "tables.json", "docx_csv", "表格"],
    "toolchain_evaluation": ["evaluate_review_toolchain.py", "准备时间", "接手", "覆盖率"],
    "citation_pipeline": ["extract_docx_citations.py", "citations.json", "claim_anchor", "参考文献"],
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)


def main() -> int:
    try:
        payload = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing eval file: {EVALS_PATH}")
        return 1
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {exc}")
        return 1

    if payload.get("skill_name") != "graduate-thesis-review":
        fail("skill_name must be graduate-thesis-review")
        return 1

    evals = payload.get("evals")
    if not isinstance(evals, list) or not evals:
        fail("evals must be a non-empty list")
        return 1

    if len(evals) < 10:
        fail(f"expected at least 10 evals, found {len(evals)}")
        return 1

    seen_ids: set[int] = set()
    ordered_ids: list[int] = []
    texts_by_id: dict[int, str] = {}

    for index, item in enumerate(evals, start=1):
        if not isinstance(item, dict):
            fail(f"eval #{index} is not an object")
            return 1

        eval_id = item.get("id")
        prompt = item.get("prompt")
        expected_output = item.get("expected_output")
        files = item.get("files")

        if not isinstance(eval_id, int) or eval_id <= 0:
            fail(f"eval #{index} has invalid id: {eval_id!r}")
            return 1
        if eval_id in seen_ids:
            fail(f"duplicate eval id: {eval_id}")
            return 1
        if not isinstance(prompt, str) or not prompt.strip():
            fail(f"eval {eval_id} has empty prompt")
            return 1
        if not isinstance(expected_output, str) or not expected_output.strip():
            fail(f"eval {eval_id} has empty expected_output")
            return 1
        if not isinstance(files, list):
            fail(f"eval {eval_id} has non-list files field")
            return 1

        seen_ids.add(eval_id)
        ordered_ids.append(eval_id)
        texts_by_id[eval_id] = f"{prompt}\n{expected_output}"

    expected_ids = list(range(1, len(evals) + 1))
    if ordered_ids != expected_ids:
        fail(f"eval ids must be sequential starting at 1; found {ordered_ids}")
        return 1

    coverage_report: dict[str, list[int]] = {}
    for theme, keywords in REQUIRED_THEMES.items():
        matched = []
        for eval_id, text in texts_by_id.items():
            hits = sum(1 for keyword in keywords if keyword in text)
            if hits >= 2:
                matched.append(eval_id)
        if not matched:
            fail(f"missing eval coverage for theme '{theme}' with keywords {keywords}")
            return 1
        coverage_report[theme] = matched

    print(f"Validated {len(evals)} evals from {EVALS_PATH}")
    for theme, matched in coverage_report.items():
        ids = ", ".join(str(eval_id) for eval_id in matched)
        print(f"- {theme}: eval {ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
