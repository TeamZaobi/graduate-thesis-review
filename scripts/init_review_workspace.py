#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


README_TEXT = """# 论文审查项目整理说明

本目录按“论文原文 + 评审材料就近放置”的原则整理。每篇论文的主要原文、评审材料、图片资源和汇总页面尽量放在同一棵子目录下。
"""

CHANGELOG_TEXT = """# Changelog

## {date}

- 初始化论文审查工作区。
- 新建 `papers/{paper_id}/reviews/` 与 `papers/{paper_id}/assets/` 标准结构。
"""

REVIEW_PLACEHOLDERS = {
    "论文多智能体审查报告.md": "# 论文多智能体审查报告\n",
    "最终可执行修改清单.md": "# 最终可执行修改清单\n",
    "学生执行版修改清单.md": "# 学生执行版修改清单\n",
    "导师汇报版摘要.md": "# 导师汇报版摘要\n",
    "第三方建议复核意见.md": "# 第三方建议复核意见\n",
}

HTML_PLACEHOLDER = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>综合评审汇总</title>
</head>
<body>
  <h1>综合评审汇总</h1>
  <p>此页面为论文审查 HTML 工作台占位文件。</p>
</body>
</html>
"""


def ensure_file(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


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

    for subdir in [
        reviews_dir,
        assets_dir / "figures",
        assets_dir / "zoom",
        assets_dir / "pdf_pages",
        assets_dir / "scans",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)

    ensure_file(paper_dir / "综合评审汇总.html", HTML_PLACEHOLDER)

    for filename, content in REVIEW_PLACEHOLDERS.items():
        ensure_file(reviews_dir / filename, content)

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
