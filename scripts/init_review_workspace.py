#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from evidence_workspace_utils import (
    build_criteria_coverage_payload,
    build_limitations_payload,
    build_review_verdict_payload,
)
from legacy_asset_paths import (
    MIGRATED_NOTE_FILENAMES,
    canonical_manifest_path,
    canonical_note_path,
    legacy_manifest_alias_path,
    legacy_note_alias_path,
    notes_dir,
)
from workflow_route_registry import WORKFLOW_ROUTE_CONTRACT_VERSION


README_TEXT = """# 论文审查项目整理说明

本目录按“论文原文 + 对象层 + 评审材料 + 多页展示层就近放置”的原则整理。每篇论文的主要原文、结构化对象、评审材料、图片资源和网页入口 / 子页尽量放在同一棵子目录下。
"""

CHANGELOG_TEXT = """# Changelog

## {date}

- 初始化论文审查工作区。
- 新建 `papers/{paper_id}/objects/`、`papers/{paper_id}/reviews/`、`papers/{paper_id}/assets/` 与 `papers/{paper_id}/display/` 标准结构。
- 新建 `papers/{paper_id}/governance/review-workspace-pack/` 运行时 pack 骨架。
- 新建 `papers/{paper_id}/evidence/` 证据工作区骨架。
- 新建 `papers/{paper_id}/notes/`，并将 legacy manifest / note assets 降级到该目录。
"""

REVIEW_PLACEHOLDERS = {
    "process_projection.md": """<!-- review-template: tainted -->
<!-- clear this marker after recording current decisions, artifacts, and next gate -->
# process_projection

## goal

## actions

## findings

## decisions

## artifacts

## status

## next_step
""",
    "评审闭环与放行判断.md": """<!-- review-template: tainted -->
<!-- clear this marker after writing an actual release gate judgement and syncing review_version_manifest.json.release_gate -->
# 评审闭环与放行判断

## scope_frozen

## deep_review_status

## coverage_status

## can_emit_problem_list

## can_emit_execution_outputs

## can_issue_readiness_verdict

## can_enter_line_editing

## blockers
""",
    "audience_language_contract.md": """<!-- review-template: tainted -->
<!-- clear this marker after freezing the audience language contract -->
# audience_language_contract

## 页面

## 论文所属学科

## 目标读者

## 使用场景

## 本学科常用审查用语

## 应避免的跨学科行话

## 允许术语

## 禁止直接出现的内部术语

## 首层应保留的判断

## 页面阅读规则

## 适合写成 tips 的内容

## tips 不应承担的内容

## drilldown 标题与展开方式

## 不应承担的职责
""",
    "display_projection_schema.md": """<!-- review-template: tainted -->
<!-- clear this marker after freezing the display projection contract -->
# display_projection_schema

## 页面

## 页面目标

## 目标读者要做出的判断

## 首层必须承载的判断

## tips 需要承载的阅读规则

## drilldown 需要承载的深层依据、例外或阻塞项

## 必须出现的内容块

## 不应出现的内容块

## 上游依据文件
""",
    "专业手册完备性判断.md": """<!-- review-template: tainted -->
<!-- clear this marker after writing the specialty readiness judgement -->
# 专业手册完备性判断

## 当前论文画像

## domain_stack

## primary_loop

## supporting_loops

## 命中的专项文件

## 完备性结论

## discipline_register_status

## independent_audit_required

## required_expert_checks

## 结论依据

## 下一动作
""",
    "专业专项补充说明.md": """<!-- review-template: tainted -->
<!-- clear this marker only when specialty_readiness is partial/missing and the paper-specific supplement is ready -->
# 专业专项补充说明

## 当前缺口

## 临时补充规则来源

## 本学科推荐用语

## 应避免的跨学科行话

## 临时承担的闭环

## 仅适用于本论文的内容

## 可升级为共享专项的内容
""",
    "局部改写任务卡.md": """<!-- review-template: tainted -->
<!-- clear this marker only when a scoped rewrite exception is explicitly enabled -->
# 局部改写任务卡

## 触发原因

## 允许处理范围

## 本轮禁止扩展

## 改写卡片
""",
    "审阅对象冻结说明.md": """<!-- review-template: tainted -->
<!-- clear this marker after freezing the current review object and source anchors -->
# 审阅对象冻结说明
""",
    "版本冻结与依赖回归台账.md": """<!-- review-template: tainted -->
<!-- clear this marker after freezing current slow variables and dependents -->
# 版本冻结与依赖回归台账
""",
    "关键数值与复算准入台账.md": """<!-- review-template: tainted -->
<!-- clear this marker after writing recompute boundary and key numeric evidence -->
# 关键数值与复算准入台账
""",
    "图表索引台账.md": """<!-- review-template: tainted -->
<!-- clear this marker after indexing actual figures/tables/assets -->
# 图表索引台账
""",
    "图表专项核查.md": """<!-- review-template: tainted -->
<!-- clear this marker after recording actual figure/table findings -->
# 图表专项核查
""",
    "形式审查清单.md": """<!-- review-template: tainted -->
<!-- clear this marker after formal-review checks are actually filled -->
# 形式审查清单
""",
    "论文多智能体审查报告.md": """<!-- review-template: tainted -->
<!-- clear this marker after writing the actual review report -->
# 论文多智能体审查报告
""",
    "最终可执行修改清单.md": """<!-- review-template: tainted -->
<!-- clear this marker after the release gate allows execution outputs -->
# 最终可执行修改清单
""",
    "学生执行版修改清单.md": """<!-- review-template: tainted -->
<!-- clear this marker after the release gate allows student-facing outputs -->
# 学生执行版修改清单
""",
    "导师汇报版摘要.md": """<!-- review-template: tainted -->
<!-- clear this marker after the release gate allows advisor-facing outputs -->
# 导师汇报版摘要
""",
    "第三方建议复核意见.md": """<!-- review-template: tainted -->
<!-- clear this marker after third-party inputs are actually reviewed -->
# 第三方建议复核意见
""",
}

ENTRY_HTML_PLACEHOLDER = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>综合评审汇总</title>
</head>
<body>
  <!-- display-template: tainted -->
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
  <!-- display-template: tainted -->
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

REVIEW_VERSION_MANIFEST = {
    "schema_version": "1.0",
    "template_status": "tainted",
    "entry_mode": None,
    "review_object": {
        "path": None,
        "label": None,
        "last_modified": None,
        "derived_text_source": None,
        "visual_truth_source": {
            "path": None,
            "authority_type": None,
            "renderer": None,
            "page_renders_dir": None,
            "fallback_pdf": None,
        },
        "derived_pdf_source": None,
        "stage": None,
    },
    "truth_source": {
        "current": [],
        "historical_sources": [],
        "deprecated_anchors": [],
    },
    "rebase": {
        "enabled": False,
        "from_version": None,
        "to_version": None,
        "status": None,
        "impacted_artifacts": [],
    },
    "slow_variables": [],
    "dependents": [],
    "readiness": {
        "workspace_gate": "blocked",
        "reason": "template_initialized",
    },
    "handoff": {
        "process_projection": "notes/process_projection.md",
        "decision_snapshot": [],
        "produced_artifacts": [],
        "next_gate": None,
    },
    "release_gate": {
        "scope_frozen": "pending",
        "deep_review_status": "pending",
        "coverage_status": "pending",
        "can_emit_problem_list": "pending",
        "can_emit_execution_outputs": "pending",
        "can_issue_readiness_verdict": "pending",
        "can_enter_line_editing": "pending",
        "blockers": [],
        "allowed_next_steps": [],
        "forbidden_outputs": [],
    },
    "specialty_gate": {
        "domain_stack": [],
        "primary_loop": None,
        "supporting_loops": [],
        "matched_manuals": [],
        "specialty_readiness": "pending",
        "discipline_register_status": "pending",
        "independent_audit_required": "pending",
        "required_expert_checks": [],
        "next_action": None,
    },
    "task_exceptions": {
        "scoped_rewrite": {
            "enabled": False,
            "targets": [],
            "reason": None,
        },
    },
    "workflow_route": {
        "contract_version": WORKFLOW_ROUTE_CONTRACT_VERSION,
        "mode": None,
        "resume_to_mode": None,
        "required_steps": [],
        "skipped_steps": [],
        "allowed_output_families": [],
        "forbidden_output_families": [],
        "active_step": None,
        "step_state": {},
    },
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


def ensure_symlink(alias_path: Path, canonical_path: Path) -> None:
    relative_target = Path("..") / canonical_path.parent.name / canonical_path.name
    if alias_path.is_symlink():
        if alias_path.readlink() == relative_target:
            return
        alias_path.unlink()
    elif alias_path.exists():
        return
    alias_path.symlink_to(relative_target)


def ensure_note_file(paper_dir: Path, filename: str, content: str) -> None:
    canonical_path = canonical_note_path(paper_dir, filename)
    alias_path = legacy_note_alias_path(paper_dir, filename)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    if not canonical_path.exists() and alias_path.exists() and not alias_path.is_symlink():
        canonical_path.write_text(alias_path.read_text(encoding="utf-8"), encoding="utf-8")
        alias_path.unlink()
    ensure_file(canonical_path, content)
    ensure_symlink(alias_path, canonical_path)


def ensure_manifest_file(paper_dir: Path, payload: dict) -> None:
    canonical_path = canonical_manifest_path(paper_dir)
    alias_path = legacy_manifest_alias_path(paper_dir)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    if not canonical_path.exists() and alias_path.exists() and not alias_path.is_symlink():
        canonical_path.write_text(alias_path.read_text(encoding="utf-8"), encoding="utf-8")
        alias_path.unlink()
    ensure_json(canonical_path, payload)
    ensure_symlink(alias_path, canonical_path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_runtime_pack(repo_root: Path, paper_dir: Path) -> dict[str, object]:
    truth_pack = repo_root / "workflow" / "review-workspace"
    runtime_pack = paper_dir / "governance" / "review-workspace-pack"
    objects_src = truth_pack / "objects"
    objects_dst = runtime_pack / "objects"

    runtime_pack.mkdir(parents=True, exist_ok=True)

    for filename in [
        "workflow.contract.json",
        "rules.contract.json",
        "agent.contract.json",
    ]:
        src = truth_pack / filename
        dst = runtime_pack / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)

    if objects_src.exists() and not objects_dst.exists():
        shutil.copytree(objects_src, objects_dst)

    workflow_contract_path = runtime_pack / "workflow.contract.json"
    if not workflow_contract_path.exists():
        return {
            "contract_version": None,
            "required_evidence_refs": [],
            "forbidden_output_refs": [],
        }

    workflow_contract = load_json(workflow_contract_path)
    workflow_id = workflow_contract.get("workflow_id", "workflow.review-workspace")
    contract_version = workflow_contract.get("version_anchor", "v1")
    nodes = workflow_contract.get("nodes", [])
    review_node = nodes[0] if nodes else {}
    current_node_id = review_node.get("node_id", "node.review")
    required_evidence_refs = review_node.get("evidence_refs", [])
    output_object_refs = [
        ref
        for ref in workflow_contract.get("object_refs", [])
        if isinstance(ref, str) and ref.startswith("output.")
    ]

    state_payload = {
        "schema_version": "1.0",
        "run_id": f"run.{paper_dir.name}.review-workspace",
        "workflow_id": workflow_id,
        "contract_version": contract_version,
        "current_node_id": current_node_id,
        "gate_state": "partial",
        "required_evidence_refs": required_evidence_refs,
        "missing_evidence_refs": required_evidence_refs,
        "allowed_next_step_refs": [],
        "forbidden_output_refs": output_object_refs,
        "updated_at": iso_now(),
        "last_event_id": f"event.{paper_dir.name}.review-workspace.001",
    }
    ensure_json(runtime_pack / "workflow.state.json", state_payload)

    events_path = runtime_pack / "workflow.events.jsonl"
    if not events_path.exists():
        event_payload = {
            "schema_version": "1.0",
            "event_id": state_payload["last_event_id"],
            "run_id": state_payload["run_id"],
            "workflow_id": workflow_id,
            "contract_version": contract_version,
            "timestamp": state_payload["updated_at"],
            "actor_id": "agent.review-workspace",
            "event_type": "state_refreshed",
            "subject_ref": current_node_id,
            "state_after": {
                "current_node_id": current_node_id,
                "gate_state": "partial",
                "missing_evidence_refs": required_evidence_refs,
            },
        }
        events_path.write_text(
            json.dumps(event_payload, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    projection_payload = {
        "schema_version": "1.0",
        "projection_id": f"projection.{paper_dir.name}.review-workspace.status",
        "family": "status_projection",
        "workflow_id": workflow_id,
        "run_id": state_payload["run_id"],
        "contract_version": contract_version,
        "source_last_event_id": state_payload["last_event_id"],
        "current_node_id": current_node_id,
        "gate_state": "partial",
        "summary": "Runtime pack initialized; review remains partial until paper evidence is supplied.",
        "missing_evidence_refs": required_evidence_refs,
        "forbidden_output_refs": output_object_refs,
        "generated_at": state_payload["updated_at"],
    }
    ensure_json(runtime_pack / "status.projection.json", projection_payload)
    return {
        "contract_version": contract_version,
        "required_evidence_refs": required_evidence_refs,
        "forbidden_output_refs": output_object_refs,
    }


def ensure_evidence_workspace(
    paper_dir: Path,
    required_evidence_refs: list[str],
    forbidden_output_refs: list[str],
) -> None:
    evidence_dir = paper_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ensure_json(
        evidence_dir / "criteria-coverage.json",
        build_criteria_coverage_payload(paper_dir.name),
    )
    ensure_file(evidence_dir / "evidence-ledger.jsonl", "")
    ensure_json(
        evidence_dir / "review-verdict.json",
        build_review_verdict_payload(
            paper_dir.name,
            required_evidence_refs,
            forbidden_output_refs,
        ),
    )
    ensure_json(
        evidence_dir / "limitations.json",
        build_limitations_payload(paper_dir.name),
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
    governance_dir = paper_dir / "governance"
    evidence_dir = paper_dir / "evidence"
    notes_workspace_dir = notes_dir(paper_dir)
    assets_dir = paper_dir / "assets"
    objects_dir = paper_dir / "objects"
    display_dir = paper_dir / "display"

    for subdir in [
        reviews_dir,
        governance_dir,
        evidence_dir,
        notes_workspace_dir,
        objects_dir,
        display_dir,
        assets_dir / "figures",
        assets_dir / "figures" / "docx_media",
        assets_dir / "figures" / "key",
        assets_dir / "tables",
        assets_dir / "tables" / "docx_csv",
        assets_dir / "zoom",
        assets_dir / "page_renders",
        assets_dir / "scans",
    ]:
        subdir.mkdir(parents=True, exist_ok=True)

    ensure_file(paper_dir / "综合评审汇总.html", ENTRY_HTML_PLACEHOLDER)

    for filename, title in DISPLAY_PLACEHOLDERS.items():
        ensure_file(display_dir / filename, DISPLAY_PAGE_TEMPLATE.format(title=title))

    for filename, content in REVIEW_PLACEHOLDERS.items():
        if filename in MIGRATED_NOTE_FILENAMES:
            ensure_note_file(paper_dir, filename, content)
        else:
            ensure_file(reviews_dir / filename, content)

    ensure_manifest_file(paper_dir, REVIEW_VERSION_MANIFEST)
    runtime_pack_meta = ensure_runtime_pack(root, paper_dir)
    ensure_evidence_workspace(
        paper_dir,
        runtime_pack_meta.get("required_evidence_refs", []),
        runtime_pack_meta.get("forbidden_output_refs", []),
    )

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
    ensure_json(
        objects_dir / "formal_findings.json",
        {"paper_id": args.paper_id, "kind": "formal_findings", "items": [], "checks": []},
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
