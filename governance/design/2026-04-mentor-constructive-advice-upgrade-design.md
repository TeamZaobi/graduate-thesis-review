# 导师建设性建议层升级设计

## Purpose

本设计稿只收敛一个主题：**把“导师建设性建议”从评审意见中分离出来，并升级为一个有方法学依据、分层输出、前沿检索能力和语言规范约束的独立设计层。**

本稿只写 `governance/design/` 下的新文件，不修改主 `SKILL.md`、测试文件或现有 runtime/knowledge 资产。它是后续实现的设计真源，不是实现本身。

本稿继承并收敛以下既有设计材料：

- `references/methodology-backed-advice.md`
- `references/advisor-line-editing.md`
- `references/workload-evidence-criteria.md`
- `references/agent-tool-adaptation.md`

## Reframed Problem

当前系统已经具备“识别问题”和“做风险评审”的能力，但建设性意见仍有四个缺口：

1. 导师层与评审层的边界还不够硬，容易把修改建议当成评审结论的延伸。
2. 建设性建议没有按工作量和难度分层，导致低成本修复、高成本修复和不可修复问题混在一起。
3. 缺少外部知识检索与前沿判断层，导师建议还不够像“能对最新进展做出高水平定位的专家判断”。
4. 流行病学 / 生物统计学语言没有作为正式语言 contract 固化下来，导致建议风格容易经验化、口语化、局部化。

因此，这次升级的目标不是“写更多建议”，而是把建设性能力做成一个可路由、可分层、可审计、可投影的系统。

## Design Principles

1. `评审层先于导师层`
   - 先完成高水平评审，再允许进入建设性建议。
   - 导师建议只能建立在已确认的证据边界上，不能反向补造事实。

2. `建设性必须分层`
   - 低工作量修复、高工作量修复、结构性修复、前沿升级必须区别呈现。
   - 同一个问题，不允许只有一种“建议改一下”的抽象输出。

3. `前沿判断与文本修复分离`
   - 外部知识检索是导师能力补充，不是写作润色的替代。
   - 前沿判断可以改变结论边界、创新定位和答辩口径，但不能改写原始事实。

4. `语言先过流调/生统，再进专业语境`
   - 建设性建议的上位语言应优先使用流行病学和生物统计学表达。
   - 专业知识只负责解释边界和合法修复方式，不取代方法学表达。

5. `同一修复真源，多角色投影`
   - 同一个建议底层，只能有一个真源。
   - 学生版、导师版、答辩版、评审版只是不同投影，不应各自发明判断。

## Mission Split: Review vs Mentor

### Review Layer

评审层的职责是回答四个问题：

1. 这篇论文在研究设计上回答的是什么问题。
2. 现有证据能否支撑当前结论。
3. 风险和硬伤在哪里。
4. 哪些内容只能降级，哪些内容根本不能靠写作修复。

评审层的输出应以诊断、证据边界和风险分级为主。

### Mentor Layer

导师层的职责不是复述评审，而是把评审结论转成可执行的改进路径：

1. 哪些地方可以低成本修复。
2. 哪些地方需要结构性重写。
3. 哪些地方需要补证据、补检索或补前沿判断。
4. 哪些地方应当进入答辩口径而不是正文修复。

导师层的输出应以分层建议、工作量评估、前沿定位和角色投影为主。

### Hard Boundary

以下内容属于评审层，不属于导师层的自由发挥：

- 结论是否成立
- 设计硬伤是否存在
- 证据是否足够
- 统计解释是否站得住
- 是否允许进入修改建议阶段

导师层只能在这些前提上做“如何改得更好”的工作，不能倒过来重写前提。

## Constructive Advice Tiers

建设性建议建议固定分成四层，作为所有导师输出的统一分层标准。

| Tier | 定位 | 工作量 / 难度 | 典型问题 | 典型输出 |
|---|---|---|---|---|
| `L1` | 即时修复 | 低 | 术语不稳、语气过强、图表口径轻微不一致、局部局限性缺位 | 句子级替换、局部删改、降级表述 |
| `L2` | 科学加固 | 中 | 证据锚点不稳、讨论链条松散、统计解释不够严密、引文支撑不足 | 段落级重写、局部重排、补证据锚、补方法学依据 |
| `L3` | 结构修复 | 高 | 章节逻辑错位、结果主线不清、图表与正文脱节、答辩叙事不闭环 | 小节级重构、图表重排、主线重建、补充材料重组 |
| `L4` | 前沿升级 | 高到很高 | 创新点是否成立、方法是否落后、结论是否跟不上最新研究、答辩需要高水平定位 | 前沿知识简报、创新定位判断卡、升级路径建议 |

### Tier Selection Rules

1. 先判问题类型，再判工作量。
2. 先判是否可由写作修复，再判层级。
3. `L1` 和 `L2` 只允许在既有证据边界内做改写。
4. `L3` 允许改变结构，但不能改变事实真值。
5. `L4` 允许引入外部知识，但只能改变定位、讨论、局限性和未来研究方向，不能补造结果。

### Prohibited Collapse

以下折叠方式要明确禁止：

- 把 `L1` 的语言润色误当成 `L3` 的结构修复。
- 把 `L2` 的证据重锚误当成 `L4` 的创新升级。
- 把 `L4` 的前沿定位误写成正文里的事实性新增。

## Frontier-Augmented Mentor Layer

导师之所以是导师，不只是因为会改字句，而是因为能够结合理论高度、创新经验和前沿知识做判断。因此建议单独引入一个 `frontier-augmented mentor layer`。

### Trigger Conditions

当以下任一情形出现时，应触发前沿层：

1. 用户要求判断创新性、前沿性、研究价值或答辩定位。
2. 讨论部分需要和最新研究进展对齐。
3. 论文的“创新点”表述明显需要确认是否还成立。
4. 用户要求导师式建议，但问题已经超出局部改写，进入领域判断。

### Retrieval Policy

前沿检索必须受控，建议按以下顺序：

1. 官方指南、共识、规范、报告标准
2. 方法学一手论文
3. 最新高水平综述或系统综述
4. 最新高质量原始研究

检索结果只能用于以下四类输出：

- `前沿知识简报`
- `创新定位判断卡`
- `讨论部分的边界收缩`
- `未来研究方向建议`

禁止用途：

- 用外部文献替代论文自身证据
- 用前沿知识补造论文没做过的实验、分析或结果
- 用“最新进展”包装未验证的扩张性结论

### Frontier Outputs

前沿层建议最少产出两类对象：

1. `前沿知识简报`
   - 回答“当前领域最新最强进展是什么、哪些旧说法已经不够新、哪些方法/结论需要重新定位”。
2. `创新定位判断卡`
   - 回答“这篇论文的创新点现在还成立吗、是偏弱还是过时、是否需要重写定位”。

## Epistemic Language Contract: Epi + Biostat

建设性建议需要一个更高阶的语言 contract。这个 contract 不是替代专业，而是规定导师建议必须先经过流行病学和生物统计学的语言校准。

### Epi Axis

流行病学语言负责规范：

- 研究到底在回答什么问题
- 比较基础是否成立
- 偏倚结构是否清晰
- 因果边界是否越界
- 外部效度是否被过度扩张

### Biostat Axis

生物统计学语言负责规范：

- 估计对象是什么
- 不确定性有多大
- 模型和数据类型是否匹配
- 稳健性是否够
- 结论强度是否超出统计支持

### Language Contract Fields

建议所有导师建设性建议至少显式携带以下字段：

- `epi_basis`
- `stats_basis`
- `claim_boundary`
- `mentor_action`

### Preferred Wording

建议统一使用以下表达框架：

| 不建议 | 建议替换 |
|---|---|
| 结论太强 | 结论强度超出了当前研究设计与估计精度支持的范围 |
| 证据链不够 | 现有证据不足以支撑当前层级的推断 |
| 机制写大了 | 当前测量更支持代理指标解释，不足以支撑机制推断 |
| 结果不稳 | 估计精度有限，稳健性证据不足 |
| 对照不太行 | 当前比较框架不足以支持明确归因 |

### Claim Ceiling Rule

任何导师建议都必须先回答一个问题：

> 这句话最多可以说到什么强度？

这个 `claim ceiling` 必须由 epi / biostat 语言先决定，再决定是否进入专业化表述。

## Role Adapter

同一套导师建议，不能对不同角色给出不同真源，只能做投影。

### Target Roles

1. `学生`
   - 只看先改什么、怎么改、改到什么程度算完成。
2. `导师`
   - 只看风险收益、工作量、是否值得投入、是否要压住结论。
3. `评审`
   - 只看证据边界、风险级别、是否影响放行。
4. `答辩`
   - 只看如何安全表达、如何承认边界、如何解释创新位置。

### Role Projection Rules

1. 同一 repair map 只能生成不同表达，而不能生成不同事实。
2. 学生版强调动作清单，导师版强调优先级和投入回报，评审版强调证据边界，答辩版强调可 دفاع 的口径。
3. 任何角色投影都不得越过 `claim_boundary`。

### Recommended Role Outputs

- `output.student.execution-pack`
- `output.advisor.line-editing`
- `output.advisor.summary`
- `output.advisor.defense-talking-points`

## Specialty Adapter

专业知识不应该单独重写建设性逻辑，而是作为适配器，定义合法修复边界和术语映射。

### Adapter Inputs

专业适配器至少接收四类输入：

- 研究类型
- 问题类型
- 修复层级
- 前沿定位结果

### Adapter Responsibilities

1. 定义本专业里什么叫“高水平问题”。
2. 定义本专业里什么叫“合法修复”。
3. 定义本专业里什么叫“不能靠写作修复”。
4. 定义本专业里哪些前沿知识可以进入正文、哪些只能进入答辩或未来研究。

### Suggested Specialty Families

- 公共卫生 / 因果推断
- RCT / 临床试验
- 康复工程 / 神经工程
- 中西医结合 / 传统医学

### Adapter Rule

专业适配器只能在 epi / biostat 的 claim boundary 之内工作。它可以把同一条修复路径翻译成专业术语，但不能改写修复路径本身。

## Proposed Objects, Contracts, and Outputs

以下是建议新增或显式化的设计对象，供后续实现时落地。

### 1. Object Suggestions

| 对象 | 作用 |
|---|---|
| `evidence.methodology_repair.mapped.json` | 记录问题类型到修复类型的映射 |
| `evidence.advice_tier.assessed.json` | 记录当前问题落在哪一层 `L1-L4` |
| `evidence.frontier_scan.json` | 记录外部知识检索结果与来源分级 |
| `evidence.innovation_position.json` | 记录当前论文创新点的定位判断 |
| `evidence.language_contract.audit.json` | 记录 epi / biostat 语言是否被满足 |
| `evidence.role_projection.json` | 记录同一真源如何投影到不同角色 |
| `evidence.specialty_projection.json` | 记录专业适配边界与术语映射 |

### 2. Contract Suggestions

| 合同 | 作用 |
|---|---|
| `knowledge/advice/constructive-advice-taxonomy.md` | 固化问题类型、修复类型和层级规则 |
| `knowledge/advice/frontier-evaluation-rules.md` | 固化外部检索的触发、来源分级和使用边界 |
| `knowledge/advice/mentor-advice-layer.md` | 固化导师层与评审层的边界和输出原则 |
| `knowledge/language-contracts/epi-biostat-language-contract.md` | 固化流调 / 生统语言规范 |
| `knowledge/advice/role-projection-contract.md` | 固化学生 / 导师 / 评审 / 答辩的投影规则 |
| `knowledge/advice/specialty-adapter-contract.md` | 固化专业适配器的边界和术语规则 |

### 3. Output Suggestions

| 输出 | 适用场景 |
|---|---|
| `output.advisor.line-editing` | 逐条改稿、局部替换、低中成本修复 |
| `output.student.execution-pack` | 学生执行清单、按优先级落地 |
| `output.advisor.summary` | 导师汇报、风险收益概览 |
| `output.advisor.frontier-brief` | 前沿知识简报、创新判断摘要 |
| `output.advisor.defense-talking-points` | 答辩口径、边界说明、创新定位陈述 |

### Suggested Authority Flow

建议的输出授权链如下：

`review verdict -> advice tiering -> frontier gate -> language contract -> role/specialty projection -> output family`

这个链条的意义是：

1. 先确认是否允许进入导师建议。
2. 再确认建议应落在哪一层。
3. 再决定是否需要前沿检索。
4. 再做 epi / biostat 语言校准。
5. 最后才进入角色和专业投影。

## Implementation Boundary

本设计稿不要求立刻改主 `SKILL.md`，也不要求同步改测试文件。短期内最合理的执行顺序是：

1. 先把这份设计稿作为导师建设性建议层的统一真源。
2. 再把现有 `methodology-backed-advice`、`advisor-line-editing` 和 `workload-evidence-criteria` 的语义边界对齐到这里。
3. 最后再考虑把相关 contract 下沉到 `knowledge/` 和 `workflow/` 的机器可读对象。

## Acceptance Criteria

这次升级是否成立，不看口号，只看四个结果：

1. 导师层是否与评审层严格分离。
2. 建设性建议是否能稳定分成 `L1-L4`，并按工作量和难度输出。
3. 是否存在受控的前沿检索与创新定位判断。
4. 导师建议是否已经用 epi / biostat 语言完成校准，并能投影到不同角色和专业。

如果这四项不能同时成立，就说明建设性能力仍停留在“会改写”，还没有升到“会判断、会分层、会定位”。

