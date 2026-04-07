# Phase 1 Contract

## phase_goal

把 paper-level runtime pack 从历史 `reviews/` 伞目录中分离出来，固定到 `papers/<paper-id>/governance/review-workspace-pack/`，并补最小 validator 对齐。

## in_scope

1. `init_review_workspace.py` 的 runtime pack 脚手架
2. `evaluate_review_toolchain.py` 的 runtime pack 探测与 validator 对齐
3. `governance/` 相关执行约束文档与进度记录

## out_of_scope

1. 不改 `review_version_manifest.json` 的业务语义
2. 不改 `check_review_workspace.py` 的 release/specialty/scoped rewrite 判断逻辑
3. 不引入 `review-verdict.json`
4. 不改 `knowledge/` 家族
5. 不改 `outputs/` 和展示层合同

## files_or_families_touched

1. `governance/`
2. `scripts/`

## acceptance_checks

1. `init_review_workspace.py` 新建工作区后，会生成 `papers/<paper-id>/governance/review-workspace-pack/`
2. 该 runtime pack 能通过 upstream validator
3. `evaluate_review_toolchain.py` 能报告 runtime pack 存在与校验结果
4. 本 phase 不引入第二兼容层

## sunset_items

1. `reviews/` 仍作为 legacy 总伞暂存，sunset 于 Phase 3
2. `review_version_manifest.json` 仍保留中心位置读取，sunset 于 Phase 3
