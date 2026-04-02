#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


README_TEXT = """# 论文审查项目整理说明

本目录按“论文原文 + 对象层 + 评审材料 + 多页展示层就近放置”的原则整理。每篇论文的主要原文、结构化对象、评审材料、图片资源和网页入口 / 子页尽量放在同一棵子目录下。
"""

CHANGELOG_TEXT = """# Changelog

## {date}

- 初始化论文审查工作区。
- 新建 `papers/{paper_id}/objects/`、`papers/{paper_id}/reviews/`、`papers/{paper_id}/assets/` 与 `papers/{paper_id}/display/` 标准结构。
"""

REVIEW_PLACEHOLDERS = {
    "process_projection.md": """# process_projection

## goal

## actions

## findings

## decisions

## artifacts

## status

## next_step
""",
    "audience_language_contract.md": """# audience_language_contract

## 页面

## 目标读者

## 使用场景

## 允许术语

## 禁止直接出现的内部术语

## 首层应保留的判断

## 不应承担的职责
""",
    "display_projection_schema.md": """# display_projection_schema

## 页面

## 页面目标

## 目标读者要做出的判断

## 必须出现的内容块

## 不应出现的内容块

## 上游依据文件
""",
    "审阅对象冻结说明.md": "# 审阅对象冻结说明\n",
    "版本冻结与依赖回归台账.md": "# 版本冻结与依赖回归台账\n",
    "关键数值与复算准入台账.md": "# 关键数值与复算准入台账\n",
    "图表索引台账.md": "# 图表索引台账\n",
    "图表专项核查.md": "# 图表专项核查\n",
    "论文多智能体审查报告.md": "# 论文多智能体审查报告\n",
    "最终可执行修改清单.md": "# 最终可执行修改清单\n",
    "学生执行版修改清单.md": "# 学生执行版修改清单\n",
    "导师汇报版摘要.md": "# 导师汇报版摘要\n",
    "第三方建议复核意见.md": "# 第三方建议复核意见\n",
}

ENTRY_HTML_PLACEHOLDER = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>综合评审汇总</title>
</head>
<body>
  <h1>综合评审汇总</h1>
  <p>此页面为论文审查网页入口页占位文件。</p>
  <ul>
    <li><a href="display/问题清单页.html">问题清单页</a></li>
    <li><a href="display/完整评审页.html">完整评审页</a></li>
    <li><a href="display/学生执行页.html">学生执行页</a></li>
    <li><a href="display/导师汇报页.html">导师汇报页</a></li>
  </ul>
</body>
</html>
"""

DISPLAY_PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
</head>
<body>
  <h1>{title}</h1>
  <p>此页面为论文审查多页展示层占位文件。</p>
  <p><a href="../综合评审汇总.html">返回入口页</a></p>
</body>
</html>
"""

DISPLAY_PLACEHOLDERS = {
    "问题清单页.html": "问题清单页",
    "完整评审页.html": "完整评审页",
    "学生执行页.html": "学生执行页",
    "导师汇报页.html": "导师汇报页",
}


def ensure_file(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def ensure_json(path: Path, payload: dict) -> None:
    if not path.exists():
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="为新论文初始化标准审查工作区，不改动现有论文原文。"
    )
    parser.add_argument("--root", required=True, help="项目根目录")
    parser.add_argument("--paper-id", required=True, help="论文目录名，例如 paper03")
    parser.add_argument("--date", default="YYYY-MM-DD", help="写入 CHANGELOG 的日期")
    parser.add_argument(
        "--with-root-docs",
        action="store_true",
        help="如果根目录不存在 README.md / CHANGELOG.md，则一并创建",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    paper_dir = root / "papers" / args.paper_id
    reviews_dir = paper_dir / "reviews"
    assets_dir = paper_dir / "assets"
    objects_dir = paper_dir / "objects"
    display_dir = paper_dir / "display"

    for subdir in [
        reviews_dir,
        objects_dir,
        display_dir,
        assets_dir / "figures",
        assets_dir / "figures" / "docx_media",
        assets_dir / "figures" / "key",
        assets_dir / "tables",
        assets_dir / "tables" / "docx_csv",
        assets_dir / "zoom",
        assets_dir / "pdf_pages",
        assets_dir / "scans",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)

    ensure_file(paper_dir / "综合评审汇总.html", ENTRY_HTML_PLACEHOLDER)

    for filename, title in DISPLAY_PLACEHOLDERS.items():
        ensure_file(display_dir / filename, DISPLAY_PAGE_TEMPLATE.format(title=title))

    for filename, content in REVIEW_PLACEHOLDERS.items():
        ensure_file(reviews_dir / filename, content)

    ensure_json(
        objects_dir / "figures.json",
        {"paper_id": args.paper_id, "kind": "figures", "items": []},
    )
    ensure_json(
        objects_dir / "tables.json",
        {"paper_id": args.paper_id, "kind": "tables", "items": []},
    )
    ensure_json(
        objects_dir / "citations.json",
        {"paper_id": args.paper_id, "kind": "citations", "items": []},
    )
    ensure_json(
        objects_dir / "assets_manifest.json",
        {"paper_id": args.paper_id, "kind": "assets_manifest", "items": []},
    )

    if args.with_root_docs:
        ensure_file(root / "README.md", README_TEXT)
        ensure_file(
            root / "CHANGELOG.md",
            CHANGELOG_TEXT.format(date=args.date, paper_id=args.paper_id),
        )

    print(f"Initialized thesis review workspace at: {paper_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
