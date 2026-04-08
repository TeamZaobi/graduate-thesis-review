# Closure Plan Improvement Decision

## Purpose

这份文档用于回答一个具体问题：

**在 greenfield 主稿已经成立的前提下，前面的封口方案应该如何改进。**

这里的“改进”不是继续补几个字段，而是重新定义旧封口方案的角色、边界和迁移任务。

## Inputs

本轮输入来自三部分：

1. 旧封口方案
   - `2026-04-files-driven-workflow-multirole-design.md`
2. greenfield 主稿
   - `2026-04-greenfield-files-driven-thesis-review-skill-design.md`
3. 一轮多角色 subagents 质询
   - 有效回收：
     - runtime/schema
     - knowledge/verdict
   - 未形成有效结论：
     - skeptical reviewer
     - migration pragmatist

主线程据此直接仲裁，不再等待缺失线程。

## Decision

### 1. 旧封口方案降级

旧封口方案不再作为目标架构主稿。

它的正式定位改为：

**从当前 thesis-review 仓库迁移到 greenfield 架构的过渡方案。**

因此：

1. greenfield 主稿定义“新 Skill 应该长成什么样”
2. 旧封口方案只定义“现有 Skill 如何迁过去”

### 2. 保留什么

旧封口方案里，以下内容仍有保留价值：

1. 两套 repo truth packs
   - `workflow/review-workspace/`
   - `workflow/skill-maintenance/`
2. upstream governed-pack 对齐
3. validator 接入
4. `review-before-advice` 原则
5. 单 `agent_id + roles` 的 agent contract 收敛

这些内容不是问题，问题在于旧方案还没有把它们放进一个真正的 greenfield 结构中。

### 3. 必须改什么

旧封口方案至少必须做 5 项结构性改写。

#### A. 把 `reviews/` 总伞拆开

旧方案最大的问题，不是缺字段，而是仍保留历史总伞：

- `papers/<paper-id>/reviews/`

应改成：

```text
papers/<paper-id>/
  governance/
    review-workspace-pack/
  evidence/
  outputs/
  notes/
```

具体迁位：

1. `reviews/governed/review-workspace-pack/`
   -> `governance/review-workspace-pack/`
2. `reviews/evidence/`
   -> `evidence/`
3. `reviews/*.md`
   -> `notes/`

#### B. 把 `manifest` 从中心位置降级

旧方案虽然承认 `review_version_manifest.json` 不再是长期唯一真源，但它仍占据中心 runtime 位置。

正式改法：

1. `workflow.state.json / workflow.events.jsonl / status.projection.json`
   - 成为唯一 machine-readable runtime
2. `review_version_manifest.json`
   - 降级为 legacy/supplemental asset
   - 迁入 `notes/legacy-review-manifest.json` 或等价兼容区
3. 任何 Markdown 放行页
   - 都不能再暗示控制权

#### C. 把“高水平评审完成”升级成 verdict，而不是 gate 组合

旧方案这一步做得还不够。

正式改法：

新增 paper-level 真对象：

- `papers/<paper-id>/evidence/review-verdict.json`

最少包含：

1. `study_type_resolved`
2. `specialty_resolved`
3. `criteria_coverage_level`
4. `evidence_sufficiency_level`
5. `limitations_disclosed`
6. `claim_ceiling`
7. `allowed_output_refs`
8. `forbidden_output_refs`
9. `missing_criterion_refs`
10. `missing_evidence_refs`

这一步的意义是：

1. gate 负责流转
2. verdict 负责结论强度
3. advice 只消费 verdict

#### D. 把知识层从“模板目录”升级成 canonical 家族

旧方案里：

1. `knowledge/evidence-templates/`
2. `knowledge/output-guides/`

仍然偏解释层。

正式改法应为：

1. `knowledge/criteria/`
2. `knowledge/evidence-models/`
3. `knowledge/output-policies/`
4. `knowledge/output-templates/`

同时新增 paper-level 真对象：

1. `evidence/criteria-coverage.json`
2. `evidence/evidence-ledger.jsonl`
3. `evidence/review-verdict.json`
4. `evidence/limitations.json`

#### E. 把导师职责从 write gate 控制，升级成 output policy 控制

旧方案主要靠：

1. `write_gate`
2. `deny` rules

这只能阻止越权，不能定义导师层到底允许说到哪一步。

正式改法：

由 `knowledge/output-policies/` 定义：

1. `allowed_low_risk`
2. `verdict_required_high_risk`
3. `forbidden_transformations`

其中：

1. 低风险输出
   - 纯语言顺句
   - 术语统一
   - 不改变科学含义的局部压缩
2. verdict-required 输出
   - 摘要改写
   - 结果/讨论/结论改写
   - 逐条改稿卡
   - 答辩口径
3. 永久禁改
   - 补造盲法、注册、机制
   - 观察性结果写成确证性因果
   - 改写统计意义或方向

## Supplemental Assets Policy

旧封口方案保留的 thesis-specific 说明资产，不应整体删除，但必须改成“按需生成”。

允许保留：

1. `freeze.md`
2. `specialty-gap.md`
3. `handoff.md`
4. `release-note.md`
5. `legacy-review-manifest.json`

生成时机：

1. `freeze.md`
   - 首次 intake、版本切换、真源变更
2. `specialty-gap.md`
   - `specialty = partial / missing`
3. `handoff.md`
   - 跨线程、跨代理、跨终端接手
4. `release-note.md`
   - 需要给人解释阻断或放行原因时
5. `legacy-review-manifest.json`
   - 旧项目迁移期短期保留

不再默认生成：

1. `process_projection.md`
2. `评审闭环与放行判断.md`
3. 任何与 runtime state 重复的 Markdown 台账

## Final Authority Map

最终 authority map 固定为：

1. `repo truth packs`
   - 唯一可编辑合同真源
2. `paper runtime pack`
   - 唯一 machine-readable runtime 真源
3. `paper evidence workspace`
   - 唯一事实、证据与 verdict 实例层
4. `outputs`
   - 唯一下游派生面
5. `notes`
   - 唯一按需人工说明面

任何资产都不应跨层兼任。

## Migration Strategy

### Phase 1: Reclassify Runtime

目标：

1. 把 `reviews/governed/` 改成 `governance/`
2. 明确 runtime pack 是唯一 machine runtime
3. validator 只对 repo truth packs 和 paper runtime packs 运行

### Phase 2: Introduce Evidence Workspace

目标：

1. 新增 `papers/<paper-id>/evidence/`
2. 引入：
   - `criteria-coverage.json`
   - `evidence-ledger.jsonl`
   - `review-verdict.json`
   - `limitations.json`
3. 把“高水平评审完成”从 gate 升级成 verdict

### Phase 3: Downgrade Legacy Assets

目标：

1. `review_version_manifest.json` 降级成 legacy asset
2. `评审闭环与放行判断.md`、`process_projection.md` 等迁入 `notes/`
3. 仅在需要人工解释时生成 notes

### Phase 4: Shift Advice To Policy-Driven Outputs

目标：

1. 从 `write_gate` 中剥离导师职责的最终语义
2. 由 `knowledge/output-policies/` 控制 claim ceiling 与 forbidden transformations
3. 让 `advice` 真正变成 `verdict` 的下游

## Execution Constraints

这轮迁移必须额外受控，否则极易在执行中再次漂移、溢出或过度设计。

### 1. Single-Phase Rule

任一时刻只允许一个活动 phase。

具体要求：

1. 不并行推进两个 phase
2. 上一 phase 未完成验收，不开启下一 phase
3. 任何“顺手一起改”的跨 phase 内容，默认延后

### 2. Narrow Change Budget

每个 phase 都有硬性的变更预算。

默认上限：

1. 只改一个主目标
2. 最多改两个结构家族
3. 最多新增一个新的 canonical 文件家族
4. 最多保留一个临时兼容层

超出任一上限，视为溢出，必须拆 phase。

### 3. No Dual-Track Reinvention

迁移过程中禁止同时维护“新结构”和“旧结构”的双真源。

允许：

1. 新真源 + 旧兼容投影

不允许：

1. 新旧两套都可编辑
2. 新旧两套都承载 runtime authority
3. 新旧两套都被脚本当成第一读取入口

### 4. Compatibility Must Expire

任何兼容层都必须带 sunset 条件。

每个兼容资产至少要明确：

1. 为什么暂时保留
2. 谁消费它
3. 何时删除
4. 删除前置条件是什么

没有 sunset 条件的兼容层，默认不允许引入。

### 5. No New Authority In Markdown

Markdown 在迁移期间只能解释，不能新增控制权。

禁止：

1. 在 Markdown 中新增 `can_*`
2. 在 Markdown 中新增 `allowed_next_steps`
3. 在 Markdown 中新增 readiness / release 真判断
4. 让 Markdown 成为 validator 依赖

### 6. No Schema Expansion Without Runtime Need

不允许为了“看起来更完整”扩 schema。

禁止：

1. 新增与当前 phase 无直接运行需求的 object kind
2. 新增暂时没有消费者的字段
3. 为未来可能场景提前设计多租户、多 workflow pack、多批准链
4. 把解释性概念硬塞进 contract

### 7. File-Family Placement Freeze

在迁移期间，四个 paper-level 家族位置冻结：

1. `governance/`
   - 只放 runtime pack
2. `evidence/`
   - 只放事实、证据、coverage、verdict、limitations
3. `outputs/`
   - 只放派生输出
4. `notes/`
   - 只放按需人工说明

任何新文件都必须先回答“它属于哪一族”，否则不落盘。

### 8. Advice Is Never A Shortcut

执行过程中不允许为了先交付“可见成果”而绕过评审层。

禁止：

1. 先产出导师卡，再回补 verdict
2. 先产出答辩口径，再回补 evidence
3. 先产出摘要/结论改写，再回补 claim ceiling

### 9. Validation Gate Per Phase

每个 phase 完成前，至少要过三道验收：

1. 结构验收
   - 目录与家族放置符合本决策稿
2. authority 验收
   - runtime authority 没有回流到 legacy/Markdown
3. 工具验收
   - 相关 validator / regression 在本 phase 范围内通过

任一失败，phase 不算完成。

## Per-Phase Contracts

执行每个 phase 前，先写一个极短的变更合同。没有合同，不开始改。

每份合同固定只写 6 项：

1. `phase_goal`
2. `in_scope`
3. `out_of_scope`
4. `files_or_families_touched`
5. `acceptance_checks`
6. `sunset_items`

合同要求：

1. 不写愿景，不写大而全背景
2. 只写这次真要动的东西
3. `out_of_scope` 必须显式写出“不顺手做什么”

## Phase-Specific Constraints

### Phase 1 Constraints

只允许做 runtime reclassify。

允许：

1. 路径迁位
2. pack_root 改写
3. validator 接口对齐

不允许：

1. 新增 knowledge verdict 语义
2. 改写 output policy
3. 改脚本业务判断逻辑

### Phase 2 Constraints

只允许引入 `evidence workspace` 与 `review-verdict`。

允许：

1. 新增 `evidence/` 家族
2. 引入 `review-verdict.json`
3. 引入 `criteria-coverage.json`
4. 引入 `limitations.json`

不允许：

1. 顺手重写全部专项手册
2. 顺手改 `outputs/`
3. 顺手新增更多 workflow nodes

### Phase 3 Constraints

只允许降级 legacy assets。

允许：

1. 迁 `review_version_manifest.json`
2. 迁 Markdown ledgers 到 `notes/`
3. 标记 sunset

不允许：

1. 重新赋权给 legacy 文件
2. 一边降级一边新增第二套兼容资产

### Phase 4 Constraints

只允许把导师职责切到 policy-driven outputs。

允许：

1. 新增 `knowledge/output-policies/`
2. 把 advice 输出绑定到 verdict
3. 明确 low-risk / high-risk / forbidden 三类输出

不允许：

1. 顺手重写全文改稿系统
2. 顺手新增更多展示层产物
3. 顺手扩大 Skill 适用边界

## Stop Conditions

执行过程中，出现以下任一情况必须暂停并回到决策层：

1. 需要新增第二个兼容层
2. 需要修改三个以上结构家族
3. 需要为一个 phase 改两个以上脚本主入口
4. 发现新旧真源同时可编辑
5. 发现某个 Markdown 文件又被重新赋予 authority
6. 发现某项改动的主要理由只是“以后也许用得上”

## What This Means For The Old Closure Plan

从现在开始，旧封口方案应按下面方式理解：

1. 它不是最终蓝图
2. 它是迁移蓝图
3. 它的第一优先级不是“补更多 gate”
4. 它的第一优先级是“把结构分层改对”
5. 它的第二优先级才是“让 knowledge/verdict 接管专业性”

## One-Sentence Decision

**封口方案应该从“旧 Skill 的流程治理方案”改写成“迁移到 greenfield 评审操作系统的过渡方案”，并立即补上 `evidence workspace + review verdict + output policy` 这三条旧稿里缺失的主轴。**
