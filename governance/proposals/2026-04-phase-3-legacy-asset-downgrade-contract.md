# Phase 3 Contract

## phase_goal

把 legacy manifest 与 note-like Markdown 从 `reviews/` 的中心位置降级到 `notes/`，并保留单一兼容 alias，确保脚本入口改为 canonical `notes/` 优先读取。

## in_scope

1. `init_review_workspace.py` 为新工作区创建 `notes/` canonical 资产，并建立 `reviews/` 兼容 alias
2. `check_review_workspace.py` 与 `evaluate_review_toolchain.py` 改为 `notes/` canonical-first 读取 legacy manifest / note assets
3. 如有必要，新增一个仅服务于本 phase 的 legacy path 共享脚本
4. `governance/` 进度与执行记录同步

## out_of_scope

1. 不改 `release_gate / specialty_gate / scoped_rewrite` 的业务规则
2. 不改 `README.md`、`SKILL.md`、`references/`
3. 不改 `outputs/` 或 advice policy
4. 不删除 `reviews/` 目录本身
5. 不引入第二套 compatibility layer

## files_or_families_touched

1. `governance/`
2. `scripts/`

## acceptance_checks

1. `init_review_workspace.py` 初始化新论文时，会生成 `papers/<paper-id>/notes/legacy-review-manifest.json`
2. 已迁移的 note assets 以 `notes/` 为 canonical 位置，`reviews/` 只保留单一 alias
3. `check_review_workspace.py` 与 `evaluate_review_toolchain.py` 在 canonical notes 存在时优先读取 `notes/`
4. 本 phase 不把 legacy manifest 或 Markdown 重新升回 runtime authority

## sunset_items

1. `reviews/review_version_manifest.json` 当前仅作为 alias 保留，sunset 于 Phase 4 后的 legacy 清理
2. `reviews/<migrated-note>.md` 当前仅作为 alias 保留，sunset 于 Phase 4 后的 legacy 清理
3. `reviews/` 目录中的非迁移文件仍维持 legacy 位置，后续按家族继续拆分
