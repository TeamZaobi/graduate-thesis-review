# Overflow Drift Overdesign Cross-Audit Decision

## Purpose

这份决策稿只回答一个问题：

**结合 `audit_report_2026-04-08.md` 与 `governance_audit_report_2026-04-08.md`，当前仓库里哪些问题属于真实缺口，哪些只是兼容期残留，哪些已经开始滑向过度设计。**

本稿不再重开 greenfield 愿景，也不重做 Phase 1-4 迁移设计。

## Inputs

本轮输入固定为四份：

1. `audit_report_2026-04-08.md`
2. `governance_audit_report_2026-04-08.md`
3. `governance/design/2026-04-phase-1-4-implementation-note.md`
4. `governance/design/2026-04-closure-plan-improvement-decision.md`

其中第 4 份提供本轮的约束基线：

1. `Single-Phase Rule`
2. `Narrow Change Budget`
3. `No Dual-Track Reinvention`
4. `Compatibility Must Expire`
5. `No New Authority In Markdown`
6. `No Schema Expansion Without Runtime Need`

## Question Set

本轮只做三条质询：

1. 哪些问题是真正的 `overflow`
2. 哪些问题是真正的 `drift`
3. 哪些建议已经属于 `overdesign`

所有结论都按三档裁定：

1. `成立`
2. `部分成立`
3. `不成立 / 已过时`

## A. Overflow

### A1. 成立的 overflow

当前没有发现新的 `Critical` 级 implementation overflow。

本轮更真实的风险不是“已经改太多”，而是**下一步容易在补强时继续扩太多**。

唯一需要记录的 overflow 倾向是：

1. 说明层已经开始同时讨论 `criteria family`、`agent contract execution`、`schema expansion`、`dependency graph`
2. 这些方向都是真问题，但都不属于当前 release 后的第一补丁窗口

裁定：

**当前 overflow 主要是“下一步想做的事太多”，不是“已经落地的代码超出边界太多”。**

### A2. 不成立或被说重的点

以下不应再被直接记成 overflow：

1. `pack + verdict + legacy manifest` 三层并存
   - 这是兼容期分层，不等于 scope 已经溢出
2. repo truth packs + paper runtime pack 并存
   - 这是 Files Driven 的正常分层，不是重复建设
3. `reviews/` 仍保留 alias
   - 这是明示兼容层，不是未受控扩张

## B. Drift

### B1. 成立的 drift

当前成立的 drift 有四条：

1. **可移植性 drift**
   - `scripts/evaluate_review_toolchain.py` 仍硬编码上游 validator 绝对路径
2. **文档路径 drift**
   - `references/` 仍有部分文档把 `reviews/` 写成 canonical，而实现已经转到 `notes/`
3. **design-to-execution drift**
   - `claim_ceiling` 已进入 verdict shape，但当前主要是记录字段，还没成为独立执行约束
4. **compatibility sunset drift**
   - `legacy manifest / reviews alias` 的 sunset 条件还没形成自动检查

### B2. 不成立或已被实现收口的点

以下不能再判成当前 drift：

1. `output policy 与 verdict 没接通`
   - 已不成立；`check_review_workspace.py` 已经先检查 `review-verdict + output policy`
2. `forbidden_transformations 未执行`
   - 已不成立；当前对 advice outputs 已有模式拦截
3. `没有 schema validation`
   - 不成立；repo truth packs 已能跑 upstream validator

### B3. 最值得加自动检查的 drift 面

只保留四项：

1. `hardcoded path detector`
2. `references canonical-path lint`
3. `legacy manifest vs runtime pack drift warning`
4. `claim_ceiling execution coverage`

## C. Overdesign

### C1. 成立的 overdesign

以下方向现在就推进，会明显违反 `No Schema Expansion Without Runtime Need`：

1. **立即做 `agent.contract` 执行化**
   - 当前没有迫切运行面在消费 `approval_ref / roles`
   - 直接推进会把 closure patch 扩成第二条主线
2. **立即建立完整 `knowledge/criteria/` 三轴家族**
   - 这是 greenfield 主线，不是当前 release 后的第一补丁窗口
3. **为所有 JSON 家族补全独立 schema 体系**
   - 当前已有 upstream pack validator；继续扩自有 schema 容易先长出第二治理面
4. **立刻把对象层深度并入 evidence workspace**
   - 这是中期数据建模问题，不是当前阻断项
5. **补完整依赖图、术语映射、插件化路线**
   - 这些都对，但当前收益低于 P0 修复

### C2. 不成立 / 必要骨架

以下不应再被误判为 overdesign：

1. `workflow/review-workspace/` 与 `workflow/skill-maintenance/`
2. `papers/<paper-id>/governance/review-workspace-pack/`
3. `evidence/review-verdict.json`
4. `knowledge/output-policies/advice-output-policy.json`
5. `notes/legacy-review-manifest.json`

它们已经是当前运行所需骨架，不是“为了以后也许会用到”的提前设计。

### C3. 建议暂缓实现的方向

明确冻结以下五项，直到当前 P0 补丁完成：

1. `agent.contract` runtime enforcement
2. `knowledge/criteria/` 全面结构化
3. 自有全量 schema 扩展
4. 对象层与 evidence workspace 的深度融合
5. 依赖图 / 术语映射 / 插件化路线

## Decision

本轮收敛后的正式裁定是：

### 1. 当前最真实的问题，不是 overflow，而是 drift

尤其是：

1. 绝对路径
2. references canonical-path 不一致
3. `claim_ceiling` 有 shape、缺执行
4. legacy sunset 还没自动检查

### 2. 下一步最该避免的，不是继续修 drift，而是顺手把 greenfield 主线提前落地

特别禁止：

1. 顺手实现 `agent.contract` 审批执行
2. 顺手开 `knowledge/criteria/`
3. 顺手补一套新的 thesis-specific schema

### 3. 对两份审计的统一改写

把原审计建议压缩为两组：

#### 立即处理

1. 消除硬编码路径
2. 清理 references canonical 路径口径
3. 给 `claim_ceiling` 加最小执行约束
4. 为 legacy compatibility 增加 sunset/drift 检查

#### 明确延期

1. `agent.contract` 执行化
2. `knowledge/criteria/` 家族
3. 全量 schema 体系
4. 对象层深度整合
5. 大规模治理型附加文档

## Immediate Guardrail

在下一轮真正动代码前，固定增加一条执行护栏：

**不允许把任何“下一代 greenfield 资产”伪装成“当前 release 的必要修复”。**

如果某项工作不能直接回答下面任一问题，就延后：

1. 它能否降低当前 drift
2. 它能否降低当前 portability 风险
3. 它能否把已有字段从“只记录”升级成“可执行”

否则，一律视为本轮不做。
