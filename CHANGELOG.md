# Changelog

## [1.1.0] - 2026-04-09

### Added

- 新增导师建设性建议真源：[methodology-backed-advice.md](./references/methodology-backed-advice.md)
- 新增导师建议分层：[mentor-constructive-layers.md](./references/mentor-constructive-layers.md)
- 新增流调 / 生统语言合同：[epi-biostat-language-contract.md](./references/epi-biostat-language-contract.md)
- 新增角色投影合同：[mentor-projection-contract.md](./references/mentor-projection-contract.md)
- 新增前沿检索 gate 与 agent：[frontier-innovation-gates.md](./references/frontier-innovation-gates.md)、[frontier-innovation-agent.md](./agents/frontier-innovation-agent.md)
- 新增激活矩阵：[activation-matrix.md](./references/activation-matrix.md)
- 新增导师层 workflow evidence 对象：
  - `evidence.methodology_repair.mapped`
  - `evidence.advice_tier.assessed`
  - `evidence.language_contract.audited`

### Changed

- 默认热路径收窄为 `review-rubric / specialty-router / specialty-manual-readiness-gate / review-operations-architecture`
- `output-templates` 从默认热路径降为显式冷路径
- 建设性建议统一先经过方法学修复路径、工作量分层、语言校准，再进入角色投影
- 外部知识检索改为受控触发，只在创新性 / 最新进展 / 领域定位场景进入
- `evaluate_review_toolchain.py` 现在会显式识别 `mentor_gate / frontier_gate / handoff_resume / scoped_rewrite`

### Validation

- `python3 -m py_compile scripts/check_review_workspace.py scripts/evaluate_review_toolchain.py scripts/validate_evals.py scripts/run_workflow_regression.py`
- `python3 scripts/validate_evals.py` 通过，当前 `50` 条 eval
- `python3 scripts/run_workflow_regression.py` 通过，当前 `9` 条 workflow fixtures

## [1.0.0] - 2026-04-08

### Added

- Phase 1-4 migration baseline
- repo truth packs 与 paper runtime / evidence / notes canonical 化
- `review-verdict + advice-output-policy` 驱动的导师 / 学生输出授权

### Notes

- 详见 [2026-04-phase-1-4-migration-release-note.md](./governance/release/2026-04-phase-1-4-migration-release-note.md)
