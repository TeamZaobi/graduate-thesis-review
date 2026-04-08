# Phase 2 Contract

## phase_goal

把 paper-level `evidence/` 家族正式引入工作区，并为 `review-verdict.json` 落最小 canonical 形状，使“高水平评审完成”开始有独立 evidence/verdict 承载面。

## in_scope

1. `init_review_workspace.py` 新建 `papers/<paper-id>/evidence/` 与四个最小文件
2. `evaluate_review_toolchain.py` 增加 `evidence/` shape 探测与 `review-verdict` 摘要
3. 如有必要，新增一个仅服务于本 phase 的 `evidence workspace` 共享脚本
4. `governance/` 进度与执行记录同步

## out_of_scope

1. 不改 `check_review_workspace.py` 的 release/specialty/scoped rewrite 业务判断
2. 不改 `review_version_manifest.json` 的 authority 位置
3. 不改 `README.md`、`SKILL.md`、`references/`
4. 不引入 `knowledge/criteria` 或 `knowledge/output-policies`
5. 不把 `review-verdict.json` 直接升成 output release gate

## files_or_families_touched

1. `governance/`
2. `scripts/`

## acceptance_checks

1. `init_review_workspace.py` 初始化新论文时，会生成 `papers/<paper-id>/evidence/`
2. `evidence/criteria-coverage.json`、`evidence/evidence-ledger.jsonl`、`evidence/review-verdict.json`、`evidence/limitations.json` 都有最小可解析形状
3. `evaluate_review_toolchain.py` 能报告 `evidence_workspace.present`、shape 校验结果和 verdict 摘要
4. 本 phase 不引入第二个 release/output authority 真源

## sunset_items

1. `review_version_manifest.json` 仍保留 legacy release/output gate 角色，sunset 于 Phase 3/4
2. `评审闭环与放行判断.md` 仍保留人类可读投影角色，sunset 于 Phase 3
3. `review-verdict.json` 当前只承载 evidence/verdict 真源，不直接替代旧 release gate
