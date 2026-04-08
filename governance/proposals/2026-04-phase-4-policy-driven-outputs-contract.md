# Phase 4 Contract

## phase_goal

把导师/学生输出的授权面从 legacy release gate 切到 `review-verdict + knowledge/output-policies`，让 advice 真正成为 verdict 的下游。

## in_scope

1. 新增最小 `knowledge/output-policies/` canonical 文件
2. 新增一个仅服务于本 phase 的 output policy 共享脚本
3. `check_review_workspace.py` 改成对 advice/student outputs 走 `verdict + output policy` 授权
4. `evaluate_review_toolchain.py` 增加 output policy 与 verdict-driven advice 摘要
5. `governance/` 进度与执行记录同步

## out_of_scope

1. 不改 `README.md`、`SKILL.md`、`references/`
2. 不重写全文改稿系统
3. 不新增更多展示层产物或新 output 文件
4. 不改 problem-list / readiness verdict 的 legacy gate 语义
5. 不扩大 Skill 适用边界

## files_or_families_touched

1. `governance/`
2. `knowledge/`
3. `scripts/`

## acceptance_checks

1. `knowledge/output-policies/` 存在最小 canonical policy 文件，并定义 `allowed_low_risk / verdict_required_high_risk / forbidden_transformations`
2. `check_review_workspace.py` 对 line-editing / advisor summary / student execution 类输出，不再以 release gate 作为第一授权，而以 `review-verdict + output policy` 判定
3. `evaluate_review_toolchain.py` 能报告 output policy 存在、verdict claim ceiling 和 advice outputs allowance 摘要
4. readiness/problem-list 仍由原有 legacy gate 控制，本 phase 不引入第二条 advice authority 兼容线

## sunset_items

1. `review_version_manifest.json.release_gate.can_emit_execution_outputs` 对 advice/student outputs 只保留 legacy 兼容说明价值，sunset 于后续 legacy 清理
2. `review_version_manifest.json.release_gate.can_enter_line_editing` 对 advice outputs 只保留 legacy 兼容说明价值，sunset 于后续 legacy 清理
