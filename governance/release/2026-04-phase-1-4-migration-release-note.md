# Phase 1-4 Migration Release Note

## Scope

本次 release 覆盖：

1. runtime reclassify
2. evidence workspace introduction
3. legacy asset downgrade
4. policy-driven advice outputs

## Included Changes

### 1. Repo truth packs are now first-class

新增并固定：

- `workflow/review-workspace/`
- `workflow/skill-maintenance/`

两套 pack 已可被 upstream `validate_governance_assets.py` 校验。

### 2. Paper runtime has moved to `governance/`

每篇论文现在会生成：

- `papers/<paper-id>/governance/review-workspace-pack/`

其中包含：

- `workflow.state.json`
- `workflow.events.jsonl`
- `status.projection.json`

### 3. Paper evidence has moved to `evidence/`

每篇论文现在会生成：

- `criteria-coverage.json`
- `evidence-ledger.jsonl`
- `review-verdict.json`
- `limitations.json`

`review-verdict.json` 现在是 “高水平评审已完成到什么程度” 的 paper-level verdict object。

### 4. Legacy notes have moved to `notes/`

以下资产的 canonical 路径已迁入 `notes/`：

- `legacy-review-manifest.json`
- `process_projection.md`
- `评审闭环与放行判断.md`
- `专业手册完备性判断.md`
- `专业专项补充说明.md`
- 其他 note-like 说明资产

`reviews/` 当前保留 alias 兼容，不再是 authority 中心。

### 5. Advice outputs are now policy-driven

新增：

- `knowledge/output-policies/advice-output-policy.json`
- `scripts/output_policy_utils.py`

当前这三类高风险输出已切到 `review-verdict + output policy`：

- `output.advisor.line-editing`
- `output.advisor.summary`
- `output.advisor.defense-talking-points`
- `output.student.execution-pack`

## Post-Release Stabilization

在 `Phase 1-4` 首次合并后，又补了一轮非常窄的主线稳定化修复，并已通过 PR `#2` 合并到 `main`。

这轮只处理三个问题：

1. `output policy` 从顶层字段校验，补到高风险条目 shape 校验
2. `evaluate_review_toolchain.py` 不再把 policy 缺失/损坏误报成 `alignment_ok = true`
3. paper runtime pack 新增与 repo truth pack 的 drift 对账

同时补了两条 workflow fixtures：

- `invalid_output_policy_blocks_advice_output`
- `runtime_pack_drift_is_reported`

## Behavioral Changes

### Breaking-in-practice

以下行为对旧使用习惯有实际影响：

1. `reviews/review_version_manifest.json` 不再是长期唯一真源
2. `评审闭环与放行判断.md` 不再直接决定 advice outputs 是否放行
3. `补造盲法 / 补造注册 / 把观察性结果改写成确定性因果` 之类 forbidden transformations 现在会被显式拦截

### Compatibility retained

当前仍保留：

1. `reviews/` alias
2. `legacy-review-manifest.json.release_gate`
3. readiness 相关 legacy 兼容语义

## Upgrade Notes

对已有 paper workspace，推荐至少执行一次：

```bash
python3 scripts/init_review_workspace.py \
  --root /path/to/project-root \
  --paper-id paper01
```

这会把旧式 `reviews/` note-like 文件迁回 `notes/` canonical，并重建 alias。

建议同时运行：

```bash
python3 ../files-driven/scripts/validate_governance_assets.py \
  /path/to/project-root/papers/paper01/governance/review-workspace-pack
python3 scripts/evaluate_review_toolchain.py \
  --paper-dir /path/to/project-root/papers/paper01
python3 scripts/check_review_workspace.py \
  --paper-dir /path/to/project-root/papers/paper01
```

## Validation

本次 release 前已完成：

1. `python3 -m py_compile` 关键脚本回归
2. `python3 scripts/validate_evals.py`
3. `python3 scripts/run_workflow_regression.py`
4. repo truth pack validator
5. paper runtime pack validator
6. old workspace re-init migration replay
7. policy-driven advice replay

当前未发现阻断本次 release 的代码级缺陷。

补丁合并后再次确认：

1. `python3 -m py_compile scripts/*.py`
2. `python3 scripts/validate_evals.py`
3. `python3 scripts/run_workflow_regression.py`
4. `python3 ../files-driven/scripts/validate_governance_assets.py workflow/review-workspace`
5. `python3 ../files-driven/scripts/validate_governance_assets.py workflow/skill-maintenance`

当前 workflow fixtures 为 `6` 条，全部通过。
