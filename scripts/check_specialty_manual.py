#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_METADATA = [
    "最后更新：",
    "适用范围：",
    "主要参考规范：",
]

REQUIRED_HEADINGS = [
    "## 触发条件",
    "## 适用边界",
    "## 研究类型分流",
    "## 毕业论文场景重点",
    "## 该领域特有的方法学要求",
    "## 核心结局指标与金标准",
    "## 学科语域与常用审查用语",
    "## 报告规范要点",
    "## 高频风险点",
    "## 安全定位建议",
    "## 屏蔽说明",
    "## 与通用框架/其他专项的优先级",
    "## 何时判定为手册不完备",
]


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"无法读取文件 {path}: {exc}"]

    stripped = text.lstrip()
    if not stripped.startswith("# "):
        errors.append("文件必须以一级标题开头")

    for field in REQUIRED_METADATA:
        if field not in text:
            errors.append(f"缺少元信息字段：{field}")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"缺少必需章节：{heading}")

    if "## 高频风险点" in text and not any(token in text for token in ["P0", "P1", "P2"]):
        errors.append("`## 高频风险点` 中至少应出现 P0/P1/P2")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint a specialty manual against the graduate-thesis-review standard."
    )
    parser.add_argument(
        "--file",
        action="append",
        required=True,
        help="Path to a specialty manual markdown file. Repeatable.",
    )
    args = parser.parse_args()

    failures = 0
    for raw_path in args.file:
        path = Path(raw_path).expanduser().resolve()
        errors = validate_file(path)
        if errors:
            failures += 1
            print(f"FAIL: {path}")
            for error in errors:
                print(f"- {error}")
            continue
        print(f"OK: {path}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
