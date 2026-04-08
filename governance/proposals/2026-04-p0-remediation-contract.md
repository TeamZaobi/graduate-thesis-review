# P0 Remediation Contract

## phase_goal

在不扩张架构表面的前提下，修掉当前 release 后最真实的四类 drift：硬编码路径、canonical 路径口径残留、`claim_ceiling` 只记录不执行、legacy compatibility 缺少 sunset/drift 检查。

## in_scope

1. 去掉脚本中的绝对路径依赖，改为可移植的 validator 发现方式
2. 修正 entry docs、关键 references 和少数脚本帮助文本中的 canonical 路径漂移
3. 给 `claim_ceiling` 增加最小可执行约束，并把结果接到现有 advice/output gate
4. 为 `notes/legacy-review-manifest.json` 与 `reviews/` alias 增加最小 drift/sunset 检查
5. 回归、validator 与 targeted replay 验证
6. `governance/` 进度与结论同步

## out_of_scope

1. 不实现 `agent.contract` runtime enforcement
2. 不新增 `knowledge/criteria/` 或任何第二业务主线
3. 不扩 thesis-specific schema 体系
4. 不改 greenfield 架构，不把 legacy compatibility 直接删除
5. 不实现“高风险简单请求自动升级评审”的 route promotion 机制
6. 不把更多 Markdown 升回 authority

## files_or_families_touched

1. `governance/`
2. `scripts/`
3. `README.md`
4. `SKILL.md`
5. `references/`

## acceptance_checks

1. `evaluate_review_toolchain.py` 不再依赖硬编码绝对路径；在 sibling `files-driven` skill 存在时仍能自动发现 validator
2. `claim_ceiling` 与 `allowed_output_refs / forbidden_output_refs` 的最小一致性检查生效；高风险 advice outputs 不能无依据跨级升级
3. `check_review_workspace.py` 与 `evaluate_review_toolchain.py` 都能报告 legacy canonical/alias drift，而不是默默接受冲突状态
4. `README.md`、`SKILL.md` 和本轮选定 references 不再把已迁移到 `notes/` 的文件写成 canonical `reviews/` 路径
5. `validate_evals.py`、`run_workflow_regression.py`、repo truth pack validator 与至少一组 targeted replay 通过

## sunset_items

1. `reviews/review_version_manifest.json` 继续只作为 alias 保留；本轮新增 drift/sunset 检查，后续再决定彻底移除时间点
2. `claim_ceiling` 当前只做最小执行化；更细粒度 claim policy 仍留到后续专门批次
3. `references/` 的全量 canonical-path lint 暂不做成独立工具；本轮只修高频误导入口
