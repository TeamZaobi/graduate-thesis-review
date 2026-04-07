# Phase 1-4 Implementation Note

## Purpose

这份说明只回答一个问题：

**当前仓库里，哪些 greenfield / closure 设计已经真正实现。**

它不是新的目标架构主稿，也不替代：

- `2026-04-greenfield-files-driven-thesis-review-skill-design.md`
- `2026-04-closure-plan-improvement-decision.md`

## Implemented Authority Map

当前 authority map 已经收口成：

1. `workflow/review-workspace/`
   - repo-level review truth pack
2. `workflow/skill-maintenance/`
   - repo-level maintenance truth pack
3. `papers/<paper-id>/governance/review-workspace-pack/`
   - paper-level machine-readable runtime true source
4. `papers/<paper-id>/evidence/`
   - paper-level evidence and verdict true source
5. `papers/<paper-id>/outputs/`
   - downstream derived outputs
6. `papers/<paper-id>/notes/`
   - legacy manifest and on-demand human explanation

`reviews/` 仍保留，但当前定位已经降成：

1. compatibility aliases
2. historical output landing zone
3. not the primary authority center

## Mission Hierarchy

当前实现固定采用：

1. 先完成高水平评审
2. 再进入导师职责

这条原则在代码中的具体落点是：

1. `evidence/review-verdict.json`
   - 定义 `claim_ceiling / allowed_output_refs / forbidden_output_refs`
2. `knowledge/output-policies/advice-output-policy.json`
   - 定义 `allowed_low_risk / verdict_required_high_risk / forbidden_transformations`
3. `scripts/check_review_workspace.py`
   - 对 advice/student outputs 先检查 verdict + policy

因此，导师/学生输出不再由 legacy `release_gate` 直接放行。

## Implemented Paper Runtime Shape

当前 paper runtime pack 已实现：

- `workflow.contract.json`
- `rules.contract.json`
- `agent.contract.json`
- `objects/`
- `workflow.state.json`
- `workflow.events.jsonl`
- `status.projection.json`

当前 evidence workspace 已实现：

- `criteria-coverage.json`
- `evidence-ledger.jsonl`
- `review-verdict.json`
- `limitations.json`

当前 notes canonical 已实现：

- `legacy-review-manifest.json`
- `process_projection.md`
- `评审闭环与放行判断.md`
- `专业手册完备性判断.md`
- `专业专项补充说明.md`
- `审阅对象冻结说明.md`
- 其他迁入的 note-like 说明资产

## Implemented Behavioral Changes

当前已经成立的行为变化有四条：

1. 新工作区会直接生成 paper runtime pack
2. 新工作区会直接生成 evidence workspace
3. legacy manifest 与 note-like Markdown 已 canonical-first 迁入 `notes/`
4. advice/student outputs 已切到 policy-driven authority

其中第 4 条的当前边界是：

1. `output.advisor.line-editing`
2. `output.advisor.summary`
3. `output.student.execution-pack`

这三类输出先看 `review-verdict + advice-output-policy`。

## Current Compatibility Boundary

当前仍保留的兼容边界：

1. `notes/legacy-review-manifest.json`
   - 仍承载 thesis-specific supplemental fields
2. `release_gate`
   - 仍保留 readiness 等 legacy 兼容语义
3. `reviews/`
   - 仍保留 alias 和历史产物路径

当前没有继续保留的旧中心：

1. `reviews/review_version_manifest.json` 作为唯一 runtime authority
2. `评审闭环与放行判断.md` 作为 advice outputs 第一授权面
3. `reviews/` 作为 paper workspace 唯一主族

## Acceptance State

截至 `2026-04-08`，当前实现已经过一轮集中验收：

1. `py_compile`
2. `validate_evals.py`
3. `run_workflow_regression.py`
4. repo truth pack validator
5. paper runtime pack validator
6. legacy workspace re-init migration replay
7. policy-driven output replay

当前结论是：

**Phase 1-4 已可视为实现完成，允许进入设计说明整理与发版准备。**
