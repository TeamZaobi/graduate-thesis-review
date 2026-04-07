# Files-Driven Workflow Multi-Role Detailed Design

## Purpose

本设计稿把 `graduate-thesis-review` 按最新 Files Driven 理念做一轮“多角色详设”收敛，目标不是继续补说明，而是把当前仓库从“会描述 workflow 的 skill”升级成“拥有独立 workflow 真源的 skill”。

本轮只处理流程管理，不扩领域能力。

## Reframed Problem

如果回到这个 Skill 的根本起点，本项目要解决的问题不是“怎么把论文审查过程画成更复杂的流程图”，而是三件事：

1. 把导师 / 外审 / 方法学专家的审查经验沉淀成可复用资产
2. 让每轮审查结论都能回到明确证据，而不是只留下聊天式判断
3. 让 skill 自身的维护流程不要继续污染用户面向论文审查的主流程

因此，本轮系统性方案的判断标准不是“是否全面合同化”，而是：

1. 是否更贴近真实用户故事
2. 是否减少 repo 级流程混层
3. 是否为后续 `criteria -> evidence -> outputs` 主线留出稳定演化空间

## Mission Hierarchy

本 Skill 的使命不是并列的两件事，而是有严格前后置关系的两层使命：

1. 先尽可能深、尽可能专业、尽可能科学地完成评审
2. 再在评审基础上扮演导师角色，提出修改和提升建议

这里最重要的约束不是“先有评审，后有导师建议”，而是：

**只有在已经完成高水平评审的前提下，导师职责才成立。**

因此：

1. `评审层` 可以独立存在
2. `导师层` 不能脱离 `评审层` 单独成立
3. `导师层` 的合法入口条件不是“已经看过论文”，而是“已经完成足够深、足够专业、足够科学的评审覆盖”
4. 所有后续 workflow、rules、state、projection 设计，都必须服务于这条使命层级，而不能把“改稿建议”做成可与“高水平评审”并列启动的主流程

## High-Level Review Completion Standard

本项目里“已经完成高水平评审”不是主观感受，而应落成最小完成标准。

在 v1 里，至少同时满足以下条件，才能视为已经具备进入导师职责的资格：

1. `review_object` 已冻结
   - 当前论文对象、版本、真源和目标范围已明确
2. `specialty_route` 已完成到可用状态
   - 至少不是 `pending`
   - 若为 `partial / missing`，论文级补充已落地
3. 当前目标范围内的关键证据已被覆盖
   - 不允许只看局部文字而跳过关键图表、表格、引文或方法段
4. 当前目标范围内的核心闭环已过关
   - 至少覆盖研究身份、方法学/统计学、专项语境、结果解释这几个必要面
5. 当前仍未闭环的地方已被显式保留为限制条件
   - 不能把未核查项默默吞掉
6. 输出权限已经明确
   - 当前是否允许进入导师建议、答辩口径、学生执行页，必须由 gate 明示

在 contract/rules 层，这不应被实现成一个抽象口号，而应被实现成“进入 advisor 输出之前必须满足的一组前置条件”。

## Request Promotion Rules

本项目后续最关键的 route 设计，不是“用户说了什么就按字面走什么”，而是判断一个表面简单请求是否必须被升级成高水平评审优先。

### 1. 默认直接进入评审层的请求

以下请求默认进入 `review-first`：

1. 完整审查、深审、严格审查、科学性审查、专业性审查
2. 答辩导向评审
3. 外审意见复核
4. 专项方法学判断
5. 研究结论是否成立

### 2. 表面简单但必须升级的高风险请求

以下请求即使表面是“帮我改一下 / 看一下 / 润色一下”，也必须先升级到高水平评审优先：

1. 摘要改写
2. 结果段改写
3. 讨论段改写
4. 结论改写
5. 答辩口径生成或改写
6. 对疗效、因果、机制、统计显著性、临床意义的强化表达
7. 图表解读、表格结论提炼、图题表题改写
8. 针对导师 / 外审 / 答辩委员意见的专业性回应

这些请求的问题不在于“它们很难”，而在于它们天然会触碰高强度科学结论，所以不能直接按局部润色处理。

### 3. 允许有限例外的低风险局部请求

以下请求可以作为 `limited-advice exception`，不强制先走完整高水平评审，但必须显式保持边界：

1. 纯语病修正
2. 不改变科学含义的表达顺句
3. 非核心事实段的衔接优化
4. 标题、列表、版式、语气的轻量调整
5. 已有结论不变前提下的低风险压缩和去重复

### 4. 有限例外的硬边界

即便属于低风险局部请求，只要出现以下任一行为，就必须从例外升级回评审优先：

1. 改变结论强度
2. 改变因果方向或效应大小表述
3. 改变统计解释
4. 改变图表/表格所支撑的结论
5. 改变外审/导师意见的回应立场
6. 产出“可直接替换为最终版本”的高权威建议

## User Stories

基于现有审计，当前项目最真实的用户故事不是抽象的“管理 workflow”，而是以下八类：

1. 作为首次接手论文的审查者，我需要先冻结当前审阅对象、真源和模板状态，避免把脚手架或旧 HTML 当事实。
2. 作为收到论文新版本的审查者，我需要在旧结论基础上做 rebase，而不是从零重审或沿用旧锚点。
3. 作为收到补充表格 / 图件 / 引文的审查者，我需要只回归受影响判断，而不是把补证据误做成整轮重开。
4. 作为生成 HTML / 学生版 / 导师版的操作者，我需要只回归展示层，而不能反向污染主判断。
5. 作为跨线程 / 跨代理接手者，我需要看到压缩后的过程状态，而不是从零回放完整上下文。
6. 作为进入专项审查的审查者，我需要先知道当前专项手册够不够用，再决定是否能直接深审。
7. 作为请求导师式逐条改稿的使用者，我需要拿到可直接替换的局部改写，但不能越过事实边界，也不能偷渡成全文放行。
8. 作为 skill 维护者，我需要修改 skill 自身时有独立流程，不把 repo 审计文件和用户面向论文审查的稳定入口混在一起。

前七类来自论文审查工作区的真实运行需求；第八类来自 skill 仓库自身的治理需求。当前真正的结构性问题，正是这两类需求被混在同一仓库层里处理。

## Unified Diagnosis

当前仓库已经把“论文审查工作区”的四层分层讲清楚，并且把 `release_gate`、`specialty_gate`、`workflow_route`、`scoped_rewrite` 等关键控制点推进到了机器可读层。

但流程管理仍有四个核心缺口：

1. `workflow` 还没有独立结构家族；流程真源仍分散在 `SKILL.md`、`README.md`、`scripts/*.py`。
2. 仓库同时承载“论文审查业务 workflow”和“skill 自身维护 workflow”，但两条线还没有显式分离。
3. `scripts/check_review_workspace.py` 仍是当前唯一真正阻断越权的控制执行入口，合同面还没有从脚本中独立出来。
4. `task_plan.md / progress.md / findings.md / workflow_requirements_audit.md / context_isolation_retrospective.md` 这类审计过程文件还混在根目录，尚未按 `execution_object / status_projection` 收口。

但这四个缺口不应被误读成“当前论文审查 workflow 完全不够用”。更准确的诊断是：

1. 论文审查工作区已经达到“够用的 Files Driven”，尤其是 `entry_mode`、`review_version_manifest.json`、`release_gate` 和 `specialty_gate` 这几条链已经能支撑核心用户故事。
2. 当前最急的不是再把论文审查内部认知过程状态机化，而是先把 repo 自身维护流程从业务流程中拆出去。
3. 当前最值得保留的业务抽象不是“线性步骤”，而是 `criteria -> evidence -> outputs`。如果后续要继续做架构升级，优先级应放在标准结构化与证据绑定结构化，而不是先把所有业务流拉成重状态机。

## System Boundary

本轮系统方案明确区分三层：

1. `repo_governance`
   - skill 仓库自身的维护、审计、升级、发布
2. `review_runtime`
   - 单篇论文工作区的运行实例、入口模式、gate、handoff、projection
3. `review_knowledge`
   - 审查标准、专项 criteria、证据绑定规则、输出模板

本轮优先解决 `repo_governance` 与 `review_runtime` 的混层问题；
下一条真正影响评审质量的主线，应是逐步强化 `review_knowledge`。

## Severity Override

结合当前仓库已经暴露出来的问题，这里不再把 `review-workspace workflow.contract` 视为“以后再看”的条件动作，而是视为应立即启动的治理项。

原因不是追求形式完整，而是升级触发条件实际上已经被满足：

1. 当前 `entry_mode + workflow_route + release_gate + specialty_gate + scoped_rewrite + handoff` 已经形成了多 route、多 gate 的控制面。
2. 流程真源目前仍分散在 `SKILL.md / README.md / scripts/*.py / review_version_manifest.json` 之间，已经不是“小而稳”的单入口状态。
3. `check_review_workspace.py` 仍是唯一真正阻断越权的脚本入口，一旦继续扩展而没有上游合同真源，脚本会继续承担事实定义与执行器双重角色。
4. 当前项目已经连续经历多轮审计、路由修正、例外合同收口和执行型回归补建，说明“流程漂移”不是理论风险，而是实际运行压力。

因此，本稿后续所有“条件升级”的表述，以“立即升级，但控制边界保持克制”为准。

## Schema Alignment With `files-driven` Governance Capability v1

本稿后续所有关于 schema 的设计，统一参考 `/Users/jixiaokang/.agents/skills/files-driven` 当前 `codex/governance-capability-v1` 分支上的 governed-pack 方案。

这条线上已经明确的硬要求是：

1. `workflow.contract.json` 必须使用受限 envelope：
   - `schema_version`
   - `workflow_id`
   - `family`
   - `governance_level`
   - `execution_mode`
   - `version_anchor`
   - `entry_intents`
   - `nodes`
   - `transitions`
   - `checks`
2. project-level object 合同目录已从 `schemas/*.json` 迁到 `objects/*.json`
3. `rules.contract.json` 的 rule 必须使用结构化 `effect`
   - `allow / deny / require_review / require_evidence / require_rollback`
4. workflow 不再在 node / transition 层重复登记 checks，只保留 workflow 顶层 `checks.route / evidence / write / stop`
5. 运行实例的 canonical 控制面已拆成：
   - `workflow.state.json`
   - `workflow.events.jsonl`
   - `status.projection.json`
6. `status.projection.json` 只能是派生摘要：
   - 必须用 `source_last_event_id / generated_at`
   - 不得再携带 `allowed_next_step_refs`
   - 不得再携带 `can_* / next_step / approval_ref` 这类新放行权字段

对 thesis-review 的直接影响是：

1. 我们前面草拟的自定义 top-level `entry_modes / steps / gates / output_families / projection_rules / handoff / compatibility` 不应再作为正式 schema 目标。
2. `review-workspace` 的正式 contract 形状应直接向 upstream governed-pack 对齐。
3. `review_version_manifest.json` 不再适合作为长期唯一的控制运行真源；后续应把“控制 runtime slice”逐步迁到 `workflow.state.json / workflow.events.jsonl / status.projection.json`，而把 manifest 降级成 thesis-review 的补充执行对象。

## Runtime Authority Map

这次改道最大的风险不是字段细节，而是运行真源分布不清导致多重真源。这里先把 authority map 定死。

### 1. Repo-Level Truth Pack

repo 级真源固定放在：

- `workflow/review-workspace/`
- `workflow/skill-maintenance/`

其中只放：

- `WORKFLOW.md`
- `READ_ORDER.md`
- `workflow.contract.json`
- `rules.contract.json`
- `agent.contract.json`
- `objects/`

这两处才是长期可编辑真源。

### 2. Runtime Pack Snapshot

单篇论文运行时，不直接把 repo 级真源当运行目录修改，而是在论文工作区生成冻结快照：

- `papers/<paper-id>/reviews/governed/review-workspace-pack/`

该目录作为 runtime pack，承载：

- 从 repo truth pack 复制出的 `workflow.contract.json`
- 从 repo truth pack 复制出的 `rules.contract.json`
- 从 repo truth pack 复制出的 `agent.contract.json`
- 从 repo truth pack 复制出的 `objects/`
- `workflow.state.json`
- `workflow.events.jsonl`
- `status.projection.json`

规则：

1. repo 级 pack 是真源
2. paper 级 pack 是冻结执行快照
3. paper 级 pack 禁止手工改 contract，只允许通过重新生成或升级脚本刷新
4. 这样可以兼容 upstream validator 对 `pack_root` 的单目录要求，同时避免把论文工作区 runtime 和 repo 真源混成一套

### 3. Thesis-Review Supplemental Runtime

以下 thesis-review 特有慢变量，短期仍保留在 paper 工作区 `reviews/` 下，不强塞进 governed-pack v1：

- `review_version_manifest.json`
- `审阅对象冻结说明.md`
- `专业手册完备性判断.md`
- `专业专项补充说明.md`
- `评审闭环与放行判断.md`
- `process_projection.md`

其中：

1. `workflow.state.json / workflow.events.jsonl / status.projection.json` 负责 canonical 控制 runtime
2. `review_version_manifest.json` 负责 thesis-review 的补充执行对象
3. Markdown 台账继续保留为人类可读执行面与投影面，不反向成为控制真源

### 4. Validation Strategy

validator 分两层：

1. repo 层 smoke validation
   - 用最小 smoke pack 验证 truth pack 形状与 schema 对齐
2. paper 层 runtime validation
   - 直接对 `papers/<paper-id>/reviews/governed/review-workspace-pack/` 运行 upstream validator

这一步必须成为第一批实施的一部分，否则 schema 对齐只停留在文档层。

## Review-Before-Advice Rule Set

“导师职责必须建立在高水平评审之上”不能只写在说明里，必须落成最小规则集。

v1 最少需要四类规则：

1. `rule.require-high-level-review-before-advice`
   - effect: `require_evidence`
   - target: `advisor_line_editing / advisor_summary / defense_talking_points / student_execution_outputs`
   - required_refs: 高水平评审完成所需证据集合
2. `rule.deny-advisor-output-when-partial`
   - effect: `deny`
   - condition_ref: `state.review.partial`
   - target: 同上 advisor 输出对象
3. `rule.require-review-promotion-for-high-risk-targets`
   - effect: `require_review`
   - target: 高风险目标相关 action/output
4. `rule.deny-claim-strength-upgrade-without-review`
   - effect: `deny`
   - target: 结论强化、因果强化、统计解释强化相关输出对象

这四条规则的职责分工：

1. `require_evidence` 负责“没有高水平评审证据就不能进入导师层”
2. `deny` 负责“当前 gate_state 仍是 partial 时绝不放行”
3. `require_review` 负责“表面简单请求也必须先升级”
4. `deny` 负责“有限例外不能偷渡成高强度结论”

## High-Level Review Evidence Contract

`high_level_review_completed` 在 v1 不建议做成一个抽象布尔字段，而建议拆成一组可检查 evidence refs，由规则来组合判定。

### 1. 最小 evidence refs

至少定义这组 evidence/object 标识：

1. `evidence.review_object.frozen`
2. `evidence.specialty_route.completed`
3. `evidence.core_evidence.covered`
4. `evidence.core_loops.reviewed`
5. `evidence.limitations.explicit`
6. `evidence.output_authority.defined`

### 2. 组合规则

`rule.require-high-level-review-before-advice` 的 `required_refs` 至少覆盖上述 6 项。

这样做的好处是：

1. `workflow.state.json.missing_evidence_refs` 可以直接表达还缺什么
2. `status.projection.json` 可以只派生阻断信息，不发明新判断
3. 后续可以按研究类型或专项继续增补 evidence refs，而不破坏核心规则

### 3. 与 criteria 的关系

这里要明确区分：

1. `high_level_review_completed` 的 evidence contract
   - 属于控制面最小证据集合
2. 完整 `criteria -> evidence -> outputs`
   - 属于业务知识面

v1 先只把控制面最小 evidence refs 放进 governed pack；
更完整的研究类型标准、专项 criteria 和证据模板，放到后续 `knowledge/criteria/` 主线收口。

## Agent Contract Coverage

`agent.contract.json` 在 thesis-review 里不能等同于 `agents/*.md` 的提示词集合；它只负责“谁能执行、谁能复核、谁能批准、谁能回退”的权限矩阵。

### 1. `review-workspace` 最小 agent coverage

按 upstream v1 schema 与 validator，`review-workspace` 第一版应收敛为单 `agent.contract.json`、单 `agent_id`、多 `role` 的形态，而不是一个 pack 内多个顶层 agent。

建议第一版使用：

1. `agent.review-workspace`
   - 作为 pack 级参与 agent
   - 其内部 roles 覆盖 route、专项复核、导师输出与回退

对应最小 role 集合：

1. `role.route-governor`
   - 可批准 route promotion、resume、rollback
2. `role.review-approver`
   - 可批准“已完成高水平评审”相关节点或转移
3. `role.specialty-approver`
   - 可批准专项路线完成
4. `role.advisor-author`
   - 可生成导师层输出，但不能单独批准进入导师层
5. `role.rollback-approver`
   - 可批准回退、降级、重新审查

### 2. 与现有 `agents/*.md` 的映射原则

当前 `agents/` 下的专家角色继续保留为可复用执行/提示层，但在 governed-pack 里只通过单 `agent.review-workspace` 下的角色矩阵引用，不直接把 Markdown 文件本身当 approval 真源。

建议的第一版映射：

1. `academic-writing-agent.md`
2. `advisor-line-edit-agent.md`
3. `chapter-logic-surgeon.md`
4. `evidence-anchored-rewrite-agent.md`
5. `defense-risk-agent.md`
   - 主要归到 `role.advisor-author`
6. `causal-inference-observational-agent.md`
7. `epi-rct-agent.md`
8. `stats-endpoint-agent.md`
9. `neuroengineering-agent.md`
10. `figure-forensics-agent.md`
11. `citation-integrity-agent.md`
12. `workload-assessment-agent.md`
   - 主要归到 `role.specialty-approver`

### 3. 关键约束

1. `workflow.contract.json.agent_refs` 在 v1 只引用单个顶层 `agent.review-workspace`
2. `node.approver_ref` 只引用 `roles[].role_id`
3. 需要批准的 transition 必须声明 `approval_ref`
4. `approval_ref` 对应的批准对象定义必须放在 `objects/*.json`
5. `role.advisor-author` 可以执行导师层内容生成，但不能覆盖 `rule.require-high-level-review-before-advice`
6. “导师层可以写，但不能批自己进入导师层”必须成为显式权限边界

### 4. `skill-maintenance` 最小 agent coverage

第二条 workflow 同样先收敛成单 `agent_id`：

1. `agent.skill-maintenance`
   - `role.design-owner`
   - `role.release-approver`
   - `role.audit-executor`
   - `role.regression-reviewer`

这样 `review-workspace` 和 `skill-maintenance` 就不会共用一套模糊角色系统，同时也与 upstream validator 当前能力保持一致。

## Review Knowledge Placement

这次改道不能只把 workflow 收紧，而把真正影响审查质量的知识资产继续散放。这里把 `review_knowledge` 的落点也固定下来。

### 1. 控制面与知识面分离

1. `workflow/*/objects/*.json`
   - 只放控制面 object contract
   - 包括 state、action、evidence type、output type、approval type
2. 不把完整研究类型标准、方法学 rubric、写作 criteria 塞进 `objects/`
3. governed pack 只引用最小控制对象，不吞掉全部业务知识

### 2. 业务知识真源

repo 级业务知识建议单列：

- `knowledge/criteria/`
- `knowledge/evidence-templates/`
- `knowledge/output-guides/`

其中：

1. `knowledge/criteria/`
   - 结构化研究类型标准、专项方法学标准、写作标准
2. `knowledge/evidence-templates/`
   - 证据条目模板、章节风险模板、专项补证模板
3. `knowledge/output-guides/`
   - 导师层建议模板、答辩口径模板、不同受众输出说明

### 3. 与现有目录的关系

1. `references/`
   - 继续保留解释型说明和人工阅读材料
   - 不再承担结构化 criteria 真源职责
2. `knowledge/`
   - 成为后续 `criteria -> evidence -> outputs` 主线的 canonical 业务知识层
3. `papers/<paper-id>/reviews/evidence/`
   - 作为单篇论文的 evidence 实例层
   - 绑定具体 `criteria` 引用，不反向定义 criteria

## Role 1: Workflow Architect

### Scope

只负责“面向论文审查工作区”的业务 workflow，不负责仓库自身维护流程。

### Decision

立即新增独立 workflow 家族，但只合同化控制边界，不把审查内部认知过程过度状态机化：

- `workflow/review-workspace/WORKFLOW.md`
- `workflow/review-workspace/rules.contract.json`
- `workflow/review-workspace/agent.contract.json`
- `workflow/review-workspace/objects/`
- `workflow/review-workspace/workflow.contract.json`
- `workflow/review-workspace/READ_ORDER.md`

其中：

- `workflow.contract.json` 是机读控制真源
- `WORKFLOW.md` 只负责解释流程、进入条件、主回路、回退逻辑
- `READ_ORDER.md` 只负责接手顺序，不再把读取顺序散落在 `SKILL.md`、`README.md` 和多个 reference 中

### Contract Responsibilities

`workflow/review-workspace/workflow.contract.json` 不再使用 thesis-review 自定义顶层字段，而直接对齐 upstream `workflow.contract.schema.json`：

```json
{
  "schema_version": "1.0",
  "workflow_id": "workflow.review-workspace",
  "family": "workflow",
  "governance_level": "controlled",
  "execution_mode": "gated",
  "version_anchor": "v1",
  "explanation_ref": "workflow/review-workspace/WORKFLOW.md",
  "policy_refs": [],
  "object_refs": [],
  "agent_refs": [],
  "entry_intents": [],
  "nodes": [],
  "transitions": [],
  "checks": {
    "route": [],
    "evidence": [],
    "write": [],
    "stop": []
  }
}
```

对 thesis-review 现有控制语义，映射关系改成：

1. 当前 `entry_mode`
   - 映射到 `entry_intents[].intent_id`
2. 当前 `workflow_route`
   - 正式形态映射为 `nodes + transitions`
   - 现有 `required_steps / skipped_steps / active_step` 先保留在兼容层，不再成为目标 schema 的长期顶层字段
3. 当前 `route/evidence/write/stop`
   - 正式形态映射到顶层 `checks`
4. 当前输出族与放行边界
   - 正式形态映射到 `object_refs + rules.contract.json + workflow.state.json.forbidden_output_refs`
5. 当前 handoff、读取顺序、恢复规则
   - 保留在 `WORKFLOW.md / READ_ORDER.md`
   - 不再发明 contract 内部的私有 `handoff` 顶层字段
6. 当前兼容迁移规则
   - 放进迁移说明和 validator 兼容层
   - 不再发明 contract 内部的私有 `compatibility` 顶层字段
7. 当前“先高水平评审，后导师职责”的层级关系
   - 通过 `entry_intents + transitions + rules.contract.json` 表达
   - 不再依赖自然语言默契

### Relationship With Existing Runtime Artifacts

业务 workflow 真源与工作区实例的边界应改成：

- `workflow/review-workspace/workflow.contract.json`
  - 仓库级 `workflow` 真源
- `workflow/review-workspace/rules.contract.json`
  - 仓库级 `rules` 真源
- `workflow/review-workspace/agent.contract.json`
  - 仓库级 `agent` 真源
- `workflow/review-workspace/objects/`
  - 仓库级控制对象真源
- `papers/<paper-id>/reviews/governed/review-workspace-pack/workflow.state.json`
  - thesis-review 的 canonical 控制 runtime slice
  - 持有 `current_node_id / gate_state / required_evidence_refs / missing_evidence_refs / allowed_next_step_refs / forbidden_output_refs`
- `papers/<paper-id>/reviews/governed/review-workspace-pack/workflow.events.jsonl`
  - 事件轨迹
- `papers/<paper-id>/reviews/governed/review-workspace-pack/status.projection.json`
  - 最小机读状态投影
  - 只允许复述派生状态，不再生成放行权
- `papers/<paper-id>/reviews/review_version_manifest.json`
  - thesis-review 兼容层与补充执行对象
  - 暂存 `truth_source / rebase / slow_variables / specialty_gate / task_exceptions / handoff` 等尚未迁入 upstream governed-pack 的项目特有字段
- `papers/<paper-id>/reviews/评审闭环与放行判断.md`
  - `status_projection`
  - 人类可读投影
- `papers/<paper-id>/reviews/process_projection.md`
  - 条件型 `process_projection`
  - 只在 handoff / 多代理 / 多工具复杂度足够高时启用

### Implementation Rule

现有 `scripts/workflow_route_registry.py` 的常量表应降级为合同加载器或兼容层，不再是长期真源。

## Role 2: Files-Driven Repo Architect

### Scope

只负责仓库层面的结构家族与四层收口，不展开业务 gate 细节。

### Current Classification

建议把当前仓库中的关键文件按家族重分：

- `skill`
  - `SKILL.md`
- `agent`
  - `agents/*.md`
- `workflow`
  - 目前缺失，应新增 `workflow/` governed packs
- `object`
  - `evals/evals.json`
  - 未来可补 `workflow/*/objects/*.json`
- `execution_object`
  - `task_plan.md`
  - `workflow_requirements_audit.md`
  - `context_isolation_retrospective.md`
  - 每轮设计/审计实例
- `status_projection`
  - `progress.md`
  - 可能还包括对当前 audit 的摘要页
- `display_projection`
  - 目前基本没有仓库级 display 层，可暂不新增

### Target Repo Tree

```text
graduate-thesis-review/
  SKILL.md
  README.md
  agents/
  references/
  knowledge/
    criteria/
    evidence-templates/
    output-guides/
  scripts/
  evals/
  workflow/
    review-workspace/
      WORKFLOW.md
      READ_ORDER.md
      workflow.contract.json
      rules.contract.json
      agent.contract.json
      objects/
    skill-maintenance/
      WORKFLOW.md
      READ_ORDER.md
      workflow.contract.json
      rules.contract.json
      agent.contract.json
      objects/
  governance/
    execution/
      workflow-audit-2026-04/
        task_plan.md
        workflow_requirements_audit.md
        findings.md
        context_isolation_retrospective.md
    status/
      workflow-audit-status.md
    design/
      2026-04-files-driven-workflow-multirole-design.md
  papers/
    <paper-id>/
      reviews/
        governed/
          review-workspace-pack/
            workflow.contract.json
            rules.contract.json
            agent.contract.json
            objects/
            workflow.state.json
            workflow.events.jsonl
            status.projection.json
        evidence/
        review_version_manifest.json
        审阅对象冻结说明.md
        专业手册完备性判断.md
        专业专项补充说明.md
        评审闭环与放行判断.md
        process_projection.md
```

### Root-Level Cleanup Rule

根目录只保留稳定入口，不再放当前轮次的审计实例文件。

### Responsibility Downgrade

- `SKILL.md`
  - 只讲触发边界、任务类型、引用哪些 workflow/reference
- `README.md`
  - 只讲项目介绍、目录、安装、测试、当前稳定能力
- `references/*.md`
  - 只讲方法、专项、模板、检查标准
  - 不再兼任 workflow 真源

### Immediate ROI

仓库治理层当前最高 ROI 的动作不是新建更多业务合同，而是：

1. 先补 `workflow/skill-maintenance/`
2. 先迁出根目录的维护实例文件
3. 先把 repo 自己的 `execution_object / status_projection` 收干净

这是因为它能立刻消除 repo 级混层。但在当前严重度判断下，它不再排斥 `review-workspace` 同步进入第一批；两条线应并行推进。

## Role 3: Control & QA Architect

### Scope

围绕 `route_gate / evidence_gate / write_gate / stop_gate` 做合同化控制设计。

这里的“合同化”只针对控制边界，不等于把论文审查的内部探索过程线性状态机化。导师式审查、方法学追问和章节外科仍然允许探索式展开；合同只负责规定入口、证据门槛、可写输出和停止条件。

这里还必须额外表达一条：`advisor` 不是普通输出族，而是受“高水平评审完成”约束的下游职责。

### Gate 1: `route_gate`

输入：

- 当前 `entry_mode`
- 当前 `workflow_route.mode`
- `resume_to_mode`
- 当前任务意图类别

判定：

- 是否命中了合法入口
- 是否缺少该入口最小必经步骤
- 是否把 `handoff_resume`、`display_regression`、`evidence_upgrade` 等误走成别的路由
- 是否把表面简单请求错误留在局部路径，而没有提升到 `review-first`

输出：

- 当前有效路由
- `required_steps`
- `skipped_steps`
- `allowed_output_families`
- `forbidden_output_families`

合同位置：

```json
{
  "entry_intents": [
    {
      "intent_id": "intent.version-rebase",
      "entry_node": "node.version-rebase"
    }
  ],
  "checks": {
    "route": [
      "check.route.review"
    ]
  }
}
```

运行实例仍保留在：

- `papers/<paper-id>/reviews/review_version_manifest.json.workflow_route`

### Gate 2: `evidence_gate`

输入：

- `review_object`
- `truth_source`
- `rebase`
- `dependents`
- `specialty_gate`
- 对应 step 的完成状态

判定：

- 当前步骤声称已完成时，所需证据是否已落到实例对象或证据台账
- 是否存在“步骤 done，但对象层/台账为空”的假完成
- 是否已经达到“高水平评审完成”的最小覆盖

输出：

- `ready / partial / blocked`
- 缺口列表
- 是否允许进入下一步

合同位置：

```json
{
  "nodes": [
    {
      "node_id": "node.review",
      "state_ref": "state.review.partial",
      "action_ref": "action.review",
      "evidence_refs": [
        "evidence.review.note"
      ],
      "output_policy_refs": [
        "policy.guard.review"
      ]
    }
  ],
  "checks": {
    "evidence": [
      "check.evidence.review"
    ]
  }
}
```

运行实例仍保留在：

- `papers/<paper-id>/reviews/review_version_manifest.json`
- `papers/<paper-id>/reviews/专业手册完备性判断.md`
- `papers/<paper-id>/reviews/专业专项补充说明.md`
- `papers/<paper-id>/reviews/审阅对象冻结说明.md`

### Gate 3: `write_gate`

输入：

- `workflow_route.allowed_output_families`
- `workflow_route.forbidden_output_families`
- `release_gate`
- `task_exceptions.scoped_rewrite`

判定：

- 当前状态是否允许写入执行面、答辩结论、导师页、逐条改稿页
- 是否存在局部例外授权
- 当前是否已经满足“review before advisor”的前置条件

输出：

- 可写输出族
- 禁止输出族
- 例外范围

合同位置：

```json
{
  "checks": {
    "write": [
      "check.write.review"
    ]
  }
}
```

运行实例仍保留在：

- `papers/<paper-id>/reviews/review_version_manifest.json.release_gate`
- `papers/<paper-id>/reviews/review_version_manifest.json.task_exceptions.scoped_rewrite`

其中与本项目使命层级直接相关的一条硬规则应写成：

- 若未达到 `high_level_review_completed`
  - `advisor_line_editing`
  - `advisor_summary`
  - `defense_talking_points`
  - `student_execution_outputs`
  默认都属于禁止输出族

### Gate 4: `stop_gate`

输入：

- 当前 step_state
- 当前 release gate
- 当前输出族
- projection 同步状态

判定：

- 本轮是否提前放行
- 是否越权写入下游输出
- Markdown projection 是否与 manifest 漂移
- 是否出现“未完成高水平评审，却已进入导师职责”的越级

输出：

- `pass / warn / fail`
- 终止原因
- 必须回滚或补同步的对象

合同位置：

```json
{
  "checks": {
    "stop": [
      "check.stop.review"
    ]
  }
}
```

### What Must Stay In Runtime Artifacts

以下内容不应升格成仓库级 workflow 真源，而应继续保留在单篇论文工作区实例：

- `release_gate` 当前判定值
- `specialty_gate` 当前判定值
- `workflow_route.step_state`
- `active_step`
- `task_exceptions.scoped_rewrite`
- 本轮 `dependents`
- 本轮 `rebase` 窗口

### Regression Expansion

当前 runner 已覆盖：

- `handoff_resume`
- `specialty_gate`
- `scoped_rewrite`
- `release_gate`

下一批必须补的场景：

1. `version_rebase` 已记录 rebase，但对象层和 display 层未回归
2. `display_regression` 偷改 `release_gate` 或 readiness
3. `evidence_upgrade` 更新对象层但漏回归 `dependents`
4. `initial_review` 模板污染未清就进入深审输出
5. projection 漂移：manifest 已更新，Markdown 未同步
6. `handoff_resume` 恢复后直接产出 display 页

### Anti-Reversal Rule

防止 `status_projection / display_projection` 反向定义放行的规则必须写进合同：

- projection 文件永远不生产新的 `allowed_next_steps`
- projection 文件永远不生产新的 `can_*`
- projection 文件只能映射 manifest 与 execution artifacts
- 当 projection 与 manifest 冲突时，manifest 胜出，projection 只触发 drift warning

## Role 4: Maintenance Flow Architect

### Scope

只负责 skill 仓库自身的维护、审计、升级和发布流程。

### Decision

新增第二条 workflow 家族，并把它作为第一批实施重点：

- `workflow/skill-maintenance/WORKFLOW.md`
- `workflow/skill-maintenance/rules.contract.json`
- `workflow/skill-maintenance/agent.contract.json`
- `workflow/skill-maintenance/objects/`
- `workflow/skill-maintenance/workflow.contract.json`
- `workflow/skill-maintenance/READ_ORDER.md`

这条线的目标是把“修改 skill 本身”的流程和“用 skill 审查论文”的流程完全分开。

### Proposed Maintenance Stages

1. `intake`
2. `diagnosis`
3. `design`
4. `implementation`
5. `verification`
6. `release_or_hold`
7. `retrospective`

### Maintenance Execution Objects

每轮维护/审计实例至少落：

- `task_plan.md`
- `workflow_requirements_audit.md`
- `findings.md`
- `context_isolation_retrospective.md`

### Maintenance Status Projection

每轮实例不再直接把 `progress.md` 留在根目录。建议改成：

- `governance/status/workflow-audit-status.md`

它只摘要“当前在哪一阶段、阻塞点、下一步”，不再兼任全量过程记录。

### Rehoming Existing Files

本轮建议迁移：

- `task_plan.md` -> `governance/execution/workflow-audit-2026-04/task_plan.md`
- `findings.md` -> `governance/execution/workflow-audit-2026-04/findings.md`
- `workflow_requirements_audit.md` -> `governance/execution/workflow-audit-2026-04/workflow_requirements_audit.md`
- `context_isolation_retrospective.md` -> `governance/execution/workflow-audit-2026-04/context_isolation_retrospective.md`
- `progress.md` -> `governance/status/workflow-audit-status.md`

## Unified Convergence

四个角色收敛后的统一判断如下：

1. 立即把“skill 自身维护 workflow”和“论文审查业务 workflow”拆成两条显式流程
2. 立即让 `workflow.contract.json / rules.contract.json / agent.contract.json / objects/` 成为两条 workflow 的上游控制真源
3. 当前论文审查运行底座仍以 `entry_mode + review_version_manifest.json + check_review_workspace.py` 承载实例与执行，但不再承载 repo 级 governed pack 真源
4. 合同化的目标只限于入口、gate、输出权限、handoff 与 projection 规则，不把探索式审查过程过早状态机化
5. 导师职责不是与评审职责并列的独立入口；它必须建立在高水平评审完成之后
6. 下一条真正提升审查质量的主线，仍是 `criteria -> evidence -> outputs` 的结构化
7. 根目录过程实例文件清理，必须与两条 workflow 真源建设并行推进，而不是延后

## Recommended First Implementation Batch

### Phase 1: Immediate Workflow Separation

这是当前应立即执行的阶段，目标是在不打断现有审查运行的前提下，把两条 workflow 的真源同时立起来。

#### Batch A: Establish Both Workflow Families

新增：

- `workflow/review-workspace/WORKFLOW.md`
- `workflow/review-workspace/workflow.contract.json`
- `workflow/review-workspace/rules.contract.json`
- `workflow/review-workspace/agent.contract.json`
- `workflow/review-workspace/objects/`
- `workflow/review-workspace/READ_ORDER.md`
- `workflow/skill-maintenance/WORKFLOW.md`
- `workflow/skill-maintenance/workflow.contract.json`
- `workflow/skill-maintenance/rules.contract.json`
- `workflow/skill-maintenance/agent.contract.json`
- `workflow/skill-maintenance/objects/`
- `workflow/skill-maintenance/READ_ORDER.md`

#### Batch B: Extract Review Contract From Code

把当前这些内容按 upstream governed-pack 语义迁到 review pack：

1. `ENTRY_MODES`
   - 迁成 `entry_intents`
2. `ROUTE_*`
   - 迁成 `nodes / transitions / rules / object refs`
3. `route/evidence/write/stop`
   - 迁成顶层 `checks`
4. 输出限制与放行边界
   - 迁成 `rules.contract.json` + `workflow.state.json.forbidden_output_refs`
5. 高水平评审先于导师职责
   - 迁成显式 `review-before-advice` 规则
   - 把高风险目标的简单请求升级条件写进 route/write 规则，而不是留在说明文字里

并把 `scripts/workflow_route_registry.py` 改成：

- 合同加载器
- 默认值兼容层
- schema 校验器

#### Batch C: Reclassify Runtime And Projection Files

新增：

- `governance/execution/workflow-audit-2026-04/`
- `governance/status/`
- `papers/<paper-id>/reviews/governed/review-workspace-pack/workflow.state.json`
- `papers/<paper-id>/reviews/governed/review-workspace-pack/workflow.events.jsonl`
- `papers/<paper-id>/reviews/governed/review-workspace-pack/status.projection.json`

然后迁移现有审计文件。

并把 validator 接进最小回归链：

- `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py workflow/review-workspace`
- `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py workflow/skill-maintenance`
- `python3 /Users/jixiaokang/.agents/skills/files-driven/scripts/validate_governance_assets.py papers/<paper-id>/reviews/governed/review-workspace-pack`

### Phase 2: Review Knowledge Upgrade

这是下一条业务质量主线，不以 workflow 重构为前提。

#### Batch D: Structure Criteria And Evidence

逐步引入：

- `knowledge/criteria/`
- `knowledge/evidence-templates/`
- `papers/<paper-id>/reviews/evidence/` 或其等价实例层
- agent 对 criteria 的显式消费边界
- `high_level_review_completed` 的可检查证据集合

优先围绕研究类型、专项方法学和证据绑定展开，不先追求大而全。

### Phase 3: Regression Hardening

#### Batch E: Expand Regression

优先新增 6 条 fixture：

1. `version_rebase_missing_object_regression`
2. `display_regression_mutates_release_gate`
3. `evidence_upgrade_missing_dependents_regression`
4. `initial_review_tainted_template_emits_report`
5. `projection_drift_manifest_beats_markdown`
6. `handoff_resume_illegal_display_output`

## What We Are Not Doing Yet

以下事项当前明确不作为第一批动作：

1. 不把论文审查内部探索过程强行改写成全量线性状态机
2. 不把 `workflow.contract.json` 做成庞大、难维护的重合同系统
3. 不让 repo 治理讨论挤掉 `criteria` 与证据绑定这条业务主线
4. 不为了“形式上更 Files Driven”而牺牲当前已验证可运行的审查底座

## Guardrails

- 不再让 `README.md` 和 `SKILL.md` 双写合同内容
- 不再让 projection 文件承担真实 gate 判定
- 不再让脚本私有常量长期充当 workflow 真源
- 不再把 skill 仓库自己的维护流程混写进论文审查业务流程

## Definition Of Done

满足以下条件才算完成本轮 Files Driven 流程治理升级：

1. 仓库内存在独立 `workflow` 家族
2. 两条 workflow 已显式分离：`review-workspace` 与 `skill-maintenance`
3. repo truth pack 与 paper runtime pack 的 authority map 已固定且通过 validator
4. `workflow.contract.json / rules.contract.json / agent.contract.json / objects/` 已成为脚本的上游真源
5. `review-before-advice` 与 `high_level_review_completed` 证据合同已落成可检查规则
6. `agent.contract` 已明确执行、批准、回退角色边界，导师层无自批准路径
7. `knowledge/` 与 paper-level `evidence/` 的家族边界已固定
8. 根目录不再堆放当前轮次 execution/status 文件
9. regression runner 已覆盖关键负向场景

## Delegation Runtime Notes

本轮多角色详设实际通过本机 backend 外委完成，运行面观察如下：

1. `codex` 是当前最稳定的详设外委入口，已成功产出可收敛的设计稿。
2. `claude` 当前 print 路径因未登录失败，后续若继续使用需先完成登录态校验。
3. `kimi` 当前 CLI 的 `--output-format` 合同与现有 dispatcher 假设不一致；后续若要恢复该入口，需先把 print 模式切到当前实际支持的格式。
4. `glm` 当前 print 路径在长 prompt 下暴露出 shell/转义层脆弱性；后续若继续用 `kimicc` profile 做详设外委，建议先修 dispatcher 的 prompt 传递方式，再恢复复杂任务。
5. 下一轮多角色外委在未修复上述合同前，建议优先使用 `codex`，把 `claude / kimi / glm` 视为待修复运行面，而不是默认稳定入口。
