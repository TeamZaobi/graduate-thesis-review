# Greenfield Files-Driven Thesis Review Skill Design

## Purpose

这不是对现有 `graduate-thesis-review` 的继续补丁，而是假设今天从零开始，按最新 Files Driven 与当前 upstream governed-pack schema，重写一个新的毕业论文评审 Skill。

判断标准只有三条：

1. 能否把“高水平评审”做成主产品，而不是把改稿建议做成主产品
2. 能否把专业性与科学性落到 `criteria -> evidence -> verdict -> advice`
3. 能否从一开始就把 repo 真源、paper runtime 和论文证据工作区彻底拆层

## Essence

这个新 Skill 的本质不是“一个会审论文的 AI 助手”，而是：

**一个把毕业论文评审标准、证据绑定和导师建议关系，组织成可重复、可验证、可回退系统的评审操作系统。**

它的主轴不是：

- `prompt -> answer`

也不是：

- `workflow -> output`

而是：

- `criteria -> evidence -> verdict -> advice`

其中：

1. `criteria`
   - 定义专业标准与审查边界
2. `evidence`
   - 定义这次判断到底凭什么成立
3. `verdict`
   - 定义这轮评审已经达到什么级别、还缺什么、能说到什么强度
4. `advice`
   - 只作为 `verdict` 的下游投影，不再是并列主流程

## Mission Hierarchy

这个新 Skill 必须按两层使命设计，而且是严格前后置关系：

1. 先完成高水平评审
2. 再进入导师职责

这里的关键不是“先评审后改稿”这么宽松，而是：

**只有在已经完成高水平评审的前提下，导师职责才成立。**

因此：

1. `review` 可以独立存在
2. `advice` 不能脱离 `review` 单独成立
3. 用户即使请求“帮我改摘要”“给我答辩口径”“逐条改稿”，系统也必须先判定是否需要回到 `review`

## Core User Stories

greenfield 版本只围绕最真实的用户故事建，不围绕旧文件兼容建。

1. 作为首次接手论文的审查者，我需要先冻结当前审阅对象、研究类型、专项语境和风险级别，再进入评审。
2. 作为只收到“帮我改摘要/讨论/结论”的使用者，系统要识别这是不是高风险简单请求，并在必要时强制升级为高水平评审优先。
3. 作为需要深审的审查者，我需要按研究类型和专项方法学进入明确标准，而不是只靠大段 Markdown 手册记忆规则。
4. 作为需要导师式帮助的使用者，我只能拿到建立在已完成评审基础上的修改建议、改稿卡和答辩口径，而不是无证据的自由重写。
5. 作为接手新版本论文的审查者，我需要刷新 runtime pack、重跑受影响 criteria 与 evidence，而不是在旧结论上手工回填。

## Non-Goals

这个新 Skill 明确不做：

1. 不做通用学术写作或普通润色 Skill
2. 不把专家认知过程硬塞成重线性状态机
3. 不默认生成大量 Markdown 台账来代替结构化真源
4. 不让 repo 维护流程和论文评审流程混在一起
5. 不再让任何单一脚本或 Markdown 文件兼任“唯一控制真源”

## System Boundary

系统只分四层，不再混写：

1. `repo truth`
   - skill 的 workflow、rules、agent、control objects、knowledge 真源
2. `paper runtime`
   - 单篇论文的 governed runtime pack
3. `paper evidence workspace`
   - 单篇论文的原文、抽取资产、evidence ledger、verdict objects
4. `outputs`
   - 学生版、导师版、答辩版、展示版等下游投影

其中：

1. `repo truth` 是唯一可编辑真源
2. `paper runtime` 是唯一 machine-readable 运行真源
3. `paper evidence workspace` 是事实与证据实例层
4. `outputs` 永远只是下游派生面

## Repo Truth Design

### 1. Workflow Truth Packs

repo 级只保留两套 governed packs：

1. `workflow/review-workspace/`
2. `workflow/skill-maintenance/`

每套固定包含：

1. `WORKFLOW.md`
2. `READ_ORDER.md`
3. `workflow.contract.json`
4. `rules.contract.json`
5. `agent.contract.json`
6. `objects/*.json`

### 2. Knowledge Families

业务知识不再继续塞进 `references/*.md`，而是独立成 `knowledge/` 家族：

1. `knowledge/criteria/`
   - 研究类型标准、专项方法学标准、答辩风险标准
2. `knowledge/evidence-models/`
   - evidence 字段、severity、confidence、manual check 规则
3. `knowledge/output-policies/`
   - 输出族边界、claim ceiling、禁改红线、降级规则
4. `knowledge/output-templates/`
   - 学生执行版、导师改稿卡、答辩口径、审查结论模板

### 3. Explanatory References

`references/` 仍保留，但只保留解释层与人工阅读材料：

1. 解释方法
2. 教学型说明
3. 样例与术语说明

它不再承担结构化 criteria 真源职责。

## Paper Workspace Design

对每篇论文，greenfield 工作区直接分成三块：

```text
papers/<paper-id>/
  source/
  extracted/
  governance/
    review-workspace-pack/
      workflow.contract.json
      rules.contract.json
      agent.contract.json
      objects/
      workflow.state.json
      workflow.events.jsonl
      status.projection.json
  evidence/
    criteria-coverage.json
    evidence-ledger.jsonl
    review-verdict.json
    limitations.json
  outputs/
    student/
    advisor/
    defense/
    display/
  notes/
    freeze.md
    specialty-gap.md
    handoff.md
```

规则：

1. `governance/review-workspace-pack/`
   - 只承载 frozen contracts + runtime state/events/status
2. `evidence/`
   - 只承载证据、coverage、verdict、limitations
3. `outputs/`
   - 只承载不同受众输出
4. `notes/`
   - 只在需要人工复核、handoff、专项缺口说明时生成

greenfield 不再默认生成一组 Markdown 台账作为控制真源。

## Runtime Authority Map

### 1. Repo Truth Pack

repo truth pack 是唯一合同真源：

1. 可编辑
2. 参与 CI 校验
3. 不直接承载单篇论文运行状态

### 2. Paper Runtime Pack

每篇论文初始化时，从 repo truth pack 冻结复制生成：

- `papers/<paper-id>/governance/review-workspace-pack/`

其中：

1. contracts 只允许 refresh，不允许手工改
2. 运行期只改：
   - `workflow.state.json`
   - `workflow.events.jsonl`
   - `status.projection.json`
3. 每次 refresh 必须显式记录 `contract_version`

### 3. Paper Evidence Workspace

论文原文、图表资产、表格抽取、引文对象、evidence ledger、review verdict，全部属于 evidence workspace，不属于 governed pack。

## Workflow Design

greenfield 的 `review-workspace` 不围绕“用户说什么”建，而围绕使命层级建。

### Core Nodes

最小节点建议是：

1. `node.intake`
   - 冻结审阅对象
   - 分流研究类型
   - 识别专项与高风险简单请求
2. `node.review`
   - 执行高水平评审
   - 回填 criteria coverage 与 evidence ledger
3. `node.verdict`
   - 生成本轮 review verdict
   - 计算 claim ceiling、limitations、allowed outputs
4. `node.advice`
   - 在 verdict 允许的范围内生成导师建议

### Core Entry Intents

最小入口建议是：

1. `intent.initial-review`
2. `intent.version-refresh`
3. `intent.evidence-refresh`
4. `intent.advice-request`
5. `intent.handoff-resume`

其中 `intent.advice-request` 也不直接进入 `node.advice`，而是先进入 `node.intake`，由 route/rules 判定是否必须提升到 `review`

### Core Rules

最小规则至少包括：

1. `require-review-for-high-risk-simple-requests`
2. `require-evidence-before-verdict`
3. `require-verdict-before-advice`
4. `deny-claim-upgrade-without-evidence`
5. `deny-advice-output-when-claim-ceiling-low`
6. `require-rollback-when-runtime-pack-refreshes`

## Knowledge Design

### 1. Criteria Contracts

`criteria` 真源必须结构化，至少按三轴组织：

1. `study-type`
   - 干预、观察性、诊断、预测、系统综述
2. `specialty`
   - 例如康复神经工程、公共卫生因果推断、心血管、中医
3. `scene`
   - 送审前、外审回复、预答辩、正式答辩前

建议文件形状示例：

1. `knowledge/criteria/study-type/clinical-rct.json`
2. `knowledge/criteria/study-type/observational-causal.json`
3. `knowledge/criteria/specialty/rehab-neuroengineering.json`
4. `knowledge/criteria/specialty/public-health-causal.json`
5. `knowledge/criteria/scene/defense-risk.json`

### 2. Evidence Models

evidence 不再只是自然语言条目，至少应有这些字段：

1. `evidence_id`
2. `criterion_ref`
3. `source_ref`
4. `location`
5. `claim`
6. `severity`
7. `confidence`
8. `needs_manual_check`
9. `limitation_ref`

### 3. Review Verdict

`高水平评审已完成` 不再被表达成一个模糊布尔值，而是 paper-level 的 verdict object：

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

一句话说，`high_level_review_completed` 在 greenfield 里不是布尔真源，而是 verdict 组合判定的结果。

### 4. Output Policies

导师式输出的允许边界不能只靠 workflow gate，而要有知识层真源。

`knowledge/output-policies/` 至少定义：

1. 允许的低风险输出
   - 纯语言顺句
   - 术语统一
   - 不改变科学含义的局部压缩
2. 需要 verdict 放行的高风险输出
   - 摘要改写
   - 结果/讨论/结论改写
   - 逐条改稿卡
   - 答辩口径
3. 永久禁改红线
   - 补造盲法、注册、机制、因果证明、统计意义

## Agent Design

按 upstream v1 schema，单个 pack 先收敛成单 `agent_id + roles`。

### `workflow/review-workspace/agent.contract.json`

建议使用：

1. `agent.review-workspace`

其下 roles 至少包括：

1. `role.intake-governor`
2. `role.review-executor`
3. `role.specialty-approver`
4. `role.verdict-approver`
5. `role.advisor-author`
6. `role.rollback-approver`

关键约束：

1. `role.advisor-author` 可以写建议
2. `role.advisor-author` 不能批准进入 advice
3. 进入 advice 必须由 `verdict-approver` 或等价 role 覆盖对应 `approval_ref`

### `workflow/skill-maintenance/agent.contract.json`

建议使用：

1. `agent.skill-maintenance`

其下 roles 至少包括：

1. `role.design-owner`
2. `role.audit-executor`
3. `role.release-approver`
4. `role.regression-reviewer`

## What To Delete From The Old Skill

如果真是 greenfield 重写，我会主动删掉这些历史包袱，而不是继续兼容：

1. 根目录过程文件长期共存
   - `task_plan.md`
   - `findings.md`
   - `progress.md`
   - `workflow_requirements_audit.md`
2. `review_version_manifest.json` 作为长期控制真源
3. `评审闭环与放行判断.md` 作为放行真源
4. `process_projection.md` 作为默认生成资产
5. `references/*.md` 同时承担流程入口、标准真源和解释层
6. “用户说改稿，就直接进导师式改稿”的历史默契

greenfield 版本里，这些最多只作为迁移兼容层临时存在，不进入正式架构中心。

## Validation

repo truth 与 paper runtime 都必须从第一天接入 upstream validator：

1. `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py workflow/review-workspace`
2. `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py workflow/skill-maintenance`
3. `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py papers/<paper-id>/governance/review-workspace-pack`

不做：

1. 不对 repo 根目录整体跑 validator
2. 不让 validator 跨 pack 扫描 evidence workspace
3. 不在 `status.projection.json` 里发明新放行字段

## Recommended Build Order

如果真要开始实现，不建议在现有 skill 上继续堆 patch，而建议按下面顺序起一个新的 greenfield 版本：

1. 先搭 repo truth packs
2. 再搭 `knowledge/` 家族
3. 再搭 paper workspace scaffold
4. 再实现 `intake -> review -> verdict -> advice` 的最小 runtime
5. 最后才迁移旧 skill 的专项材料、模板和脚本

## One-Sentence Design

如果用最新 Files Driven 重写一个新的毕业论文评审 Skill，我会把它设计成：

**一个以 `criteria -> evidence -> verdict -> advice` 为主轴、以 `repo truth pack -> paper runtime pack -> paper evidence workspace` 为分层、并且把“高水平评审先于导师职责”写成系统硬约束的评审操作系统。**
