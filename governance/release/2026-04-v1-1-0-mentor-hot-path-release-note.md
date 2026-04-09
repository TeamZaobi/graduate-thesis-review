# v1.1.0 Mentor Advice and Hot-Path Release Note

## Release Identity

- Skill release version: `v1.1.0`
- Release date: `2026-04-09`
- Contract line: `workflow/review-workspace` 与 `workflow/skill-maintenance` 的 `version_anchor` 继续保持 `v1`

这次 release 补的是“基础发布面 + 导师层能力收口”，不是新的 greenfield 代际。

## Scope

本次 release 覆盖四件事：

1. 建设性意见升级为导师层结构化能力
2. 流调 / 生统语言校准进入导师建议链路
3. 前沿检索与创新定位改为受控 gate
4. 默认热路径 / 显式冷路径正式收口

## Included Changes

### 1. Mentor constructive architecture is now first-class

新增并接入：

- `references/methodology-backed-advice.md`
- `references/mentor-constructive-layers.md`
- `references/epi-biostat-language-contract.md`
- `references/mentor-projection-contract.md`
- `agents/frontier-innovation-agent.md`

当前导师建议链路固定经过：

1. 方法学修复路径
2. `L1-L4` 工作量与收益分层
3. `epi_basis / stats_basis / claim_boundary / mentor_action`
4. role / specialty projection

### 2. Frontier judgment is now gated

新增：

- `references/frontier-innovation-gates.md`

当前只有在以下场景才进入前沿检索：

1. 创新性判断
2. 最新研究进展对标
3. 领域定位
4. 高水平导师判断

外部知识只能改变：

1. 讨论定位
2. 结论边界
3. 答辩口径
4. 未来研究建议

不能补造论文事实。

### 3. Hot path is now intentionally narrow

新增：

- `references/activation-matrix.md`
- `governance/design/2026-04-hot-cold-path-closure-decision.md`

默认热路径当前只保留：

1. `review-rubric`
2. `specialty-router`
3. `specialty-manual-readiness-gate`
4. `review-operations-architecture`

以下能力全部降为冷路径：

- 输出模板
- 导师修改
- 前沿检索
- 深审加闸
- 形式审查
- 展示投影
- 跨代理收口

### 4. Toolchain and workflow regression now cover path projection

更新：

- `scripts/evaluate_review_toolchain.py`
- `scripts/validate_evals.py`
- `evals/evals.json`
- `evals/workflow_fixtures/*.json`

当前工具链已能显式识别：

- `mentor_gate`
- `frontier_gate`
- `handoff_resume`
- `scoped_rewrite`

新增的 workflow fixtures 直接覆盖：

1. 默认热路径
2. 导师冷路径
3. 导师 + 前沿冷路径

## Behavioral Notes

### What changed in practice

1. 出现方法学修复路径表 / 导师分层建议 / 流调统计语言校准表后，不再允许继续声称“仍停留在默认热路径”
2. `output-templates` 不再属于默认入口层
3. 前沿检索不再以“更强建议”的名义被隐式触发，必须先过 gate

### What did not change

1. workflow / rules / object contracts 的 `version_anchor` 仍是 `v1`
2. `review-verdict + advice-output-policy` 仍是导师 / 学生输出的第一授权面
3. `legacy release_gate` 仍只保留 readiness 等兼容语义

## Upgrade Notes

如果你在维护已有文档或对外说明，建议同步更新：

1. `README.md`
2. `CHANGELOG.md`
3. `VERSION`

如果你在维护已有 paper workspace，建议至少重跑：

```bash
python3 scripts/check_review_workspace.py --paper-dir /path/to/project-root/papers/paper01
python3 scripts/evaluate_review_toolchain.py --paper-dir /path/to/project-root/papers/paper01
```

## Validation

本次 release 已通过：

1. `python3 -m py_compile scripts/check_review_workspace.py scripts/evaluate_review_toolchain.py scripts/validate_evals.py scripts/run_workflow_regression.py`
2. `python3 scripts/validate_evals.py`
3. `python3 scripts/run_workflow_regression.py`

当前结果：

1. `50` 条 eval 通过
2. `9` 条 workflow fixtures 通过
