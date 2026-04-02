---
name: graduate-thesis-review
description: 面向中文使用者操作的研究生毕业论文审查技能，支持中文和英文工作对象。默认只用于硕士或博士学位论文、预答辩材料、开题材料、答辩稿及其配套 PDF、DOCX；尤其适合临床干预、随机对照、康复工程、神经工程，以及公共卫生与真实世界因果推断论文。可综合外审、导师和其他代理意见；从方法学、统计学、学术写作、工程实现与答辩风险等角度做多角度复核，并在需要时输出证据绑定的逐条修改建议、答辩口径、必要的证据型附录，以及面向不同受众的多页网页展示。
---

# Graduate Thesis Review

## 概览

执行一套“严格、答辩导向、可落地”的毕业论文审查流程：先识别硬伤，再做高回报的答辩增强，最后给出下一轮研究的上升空间；全过程始终守住事实边界，不把事后包装成事前设计。Skill 的说明和操作习惯以中文为主，但审查对象可以是中文或英文毕业论文。

这次技能升级的总目标，不是继续增加“会说的话”，而是提升**具体毕业论文评审工作**的效率和效能。判断标准只有两条：

1. 是否减少建底稿、接手、回查、迁移和多轮回归的人工成本
2. 是否提高图表、表格、引文、数字和结论之间的证据绑定强度，以及改稿建议的可执行性

如果一项结构或工具改动不能明显提升这两项，默认不优先。

## 适用边界

本 Skill 的默认触发范围，先收窄在“毕业论文审查”：

1. 硕士论文
2. 博士论文
3. 预答辩材料
4. 开题材料
5. 答辩稿、答辩 PPT 配套底稿
6. 与上述材料直接绑定的导师意见、外审意见、修改说明

默认不用于以下场景，除非后续单独扩边界：

1. 项目参考资料复核
2. 行业趋势报告、研究综述、政策 briefing
3. 普通期刊论文、会议论文、白皮书
4. 一般产品文档、项目方案、网站文案
5. 非“学位论文 / 答辩材料”主线的任意长文审查

如果用户给的是“学术风格文档”，但没有明确属于毕业论文或答辩材料，默认不要触发本 Skill，先回问或改走更轻的通用审查路径。

默认把审查输出分成四类：

1. 关键问题：`P0 / P1 / P2`
2. 答辩增益策略：高回报、但不改变事实的叙事和展示优化
3. 导师式逐条改稿：逐段 / 逐句 / 逐图表述的证据绑定修改建议
4. 研究升级路线：工作量更大、面向下一轮研究的结构性升级

在真实工作区里，再按四层运行底座治理：

1. `truth_source`
2. `execution_object`
3. `status_projection`
4. `display_projection`

图、表、引文和资产索引优先进入 `truth_source` 的结构化对象层，不要只活在 Markdown 台账里。多线程、多代理或多轮迁移时，再补一个统一接手用的 `process_projection`。

在审查方法、统计、图表、外部建议时，加载 [references/review-rubric.md](./references/review-rubric.md)。在起草 Markdown 报告、修改清单、HTML / 网页展示层、答辩口径和导师式精修材料时，加载 [references/output-templates.md](./references/output-templates.md)。只要任务进入网页 / HTML / display_projection 模式，再额外加载 [references/display-projection-gates.md](./references/display-projection-gates.md)。在规划目录、文件命名、交付物落点时，加载 [references/file-structure.md](./references/file-structure.md)。在判断工作区四层、对象层、默认读取顺序、图表/表格/引文结构化资产和多线程接手面时，加载 [references/review-operations-architecture.md](./references/review-operations-architecture.md)。当论文涉及统计图、结果图、脑图、连接图、表格重构或答辩 PPT 图表时，加载 [references/figure-table-standards.md](./references/figure-table-standards.md)。当需要区分干预研究、观察性研究、诊断研究、预测模型或系统综述时，加载 [references/clinical-study-types.md](./references/clinical-study-types.md)。当用户明确要求导师式逐段改稿、原子级修改建议或可直接替换的文字版本时，加载 [references/advisor-line-editing.md](./references/advisor-line-editing.md)。**每次审查任务开启，必须先加载 [references/specialty-router.md](./references/specialty-router.md) 识别专业领域，再加载 [references/specialty-manual-readiness-gate.md](./references/specialty-manual-readiness-gate.md) 判断当前专项手册是否 `complete / partial / missing`，然后再按路由结果决定加载哪些专项文件**：当论文属于康复医学、神经工程、脑机接口、神经影像或多模态设备研究时，加载 [references/rehab-neuroengineering.md](./references/rehab-neuroengineering.md)；当论文属于心血管内科/外科时，加载 [references/specialty-cardiology.md](./references/specialty-cardiology.md)；当论文属于中医或中西医结合时，加载 [references/specialty-tcm.md](./references/specialty-tcm.md)；当论文属于公共卫生、临床流行病学、真实世界队列、药物流行病学或目标试验模拟时，加载 [references/specialty-public-health-causal.md](./references/specialty-public-health-causal.md)；其他专业按 `specialty-router.md` 第6节流程处理。只有当需要新建或重写共享专项文件时，才加载 [references/specialty-manual-standard.md](./references/specialty-manual-standard.md)，并在完成后运行 `scripts/check_specialty_manual.py`。当论文属于临床干预、随机对照、康复工程交叉，或用户明确要求“更深的科学性/学术性检查”时，追加加载 [references/deep-review-gates.md](./references/deep-review-gates.md)。当任务需要综合 `Codex`、`Claude Code`、`AntiGrativity` 或其他代理的输出，或用户明确要求跨工具复核时，加载 [references/agent-tool-adaptation.md](./references/agent-tool-adaptation.md)。如果论文原文是英文，则用同样流程核查，只把术语、图题、结果层级和答辩口径切换为英文论文常见表达。

如果任务需要核对最新指南、规范或对照研究，优先查官方或一手来源，并可配合 [$deep-research](/Users/jixiaokang/.agents/skills/deep-research/SKILL.md)。如果任务需要做结构清晰、适合打印和展示的 HTML / 网页交付物，可配合 [$design-taste-frontend](/Users/jixiaokang/.agents/skills/taste-skill/SKILL.md)。但视觉设计不能替代证据映射深度；display_projection 的内容边界、拆页规则、映射粒度和回归检查由本 Skill 本身负责。

## 推荐触发语句

- “用这个 Skill 审查这篇硕士 / 博士论文，给出 P0/P1/P2 清单。”
- “帮我综合外审、导师和 AI 的意见，判断这篇毕业论文哪些必须改。”
- “把这篇毕业论文做成答辩导向的审查报告。”
- “用导师视角给这篇论文做逐段 / 逐句 / 逐条修改建议。”
- “不要只告诉我哪里错，直接给我能替换回正文的安全改写。”
- “复核这些针对答辩稿的修改建议有没有过度解读或造事实风险。”
- “审查这篇英文 thesis，按中文习惯给我输出答辩建议。”
- “把 Codex、Claude Code 和 AntiGrativity 对这篇毕业论文的意见一起复核，统一成一套结论。”

## 默认不触发语句

以下请求默认不应触发本 Skill：

- “审查这个项目参考材料 / 内部 briefing。”
- “帮我看这份行业趋势报告写得怎么样。”
- “把这篇综述文章改成更好的公开说明。”
- “复核这份政策研究 / 市场研究 / 网站内容。”
- “给项目之外的人写一份低门槛说明材料。”

## 执行流程

### 1. 先从原文建上下文，不先信外审

- 先读论文原文，再读外部评审。
- 论文原文可能是中文或英文，但审查输出默认优先服务中文使用者的决策和执行习惯。
- 如果任务混入了其他代理的 transcript、截图、建议或中间产出，先把它们标记为“二手输入”，不要直接当原文事实。
- 如果有 DOCX，优先抽纯文本并加行号；在 macOS 上，`textutil -convert txt -stdout thesis.docx | nl -ba` 很适合做定位底稿。
- 如果论文高度依赖图片、流程图、森林图、页图或截图，先判断图件来源类型，再决定走哪条结构化流水线：`docx_media` 图件可用 `scripts/extract_docx_media.py` 抽出 `word/media`；`Word shape / 文本框 / 版式渲染后成图` 这类图件应登记为 `shape_rendered`，并单独记录当前证据资产与渲染链路，不要把所有图件都当成同一条“抽图”流程。
- 如果论文高度依赖 Word 原生表格、基线表、结果表或补充表，优先运行 `scripts/extract_docx_tables.py --docx <thesis.docx> --paper-dir <paperXX>`，把表格落到 `assets/tables/docx_csv/` 并同步 `objects/tables.json`。
- 如果论文的方法学论断、讨论和文献综述明显依赖数字序号引用，优先运行 `scripts/extract_docx_citations.py --docx <thesis.docx> --paper-dir <paperXX>`，把“正文引用锚点 → 参考文献条目”先落到 `objects/citations.json`，不要继续只靠人工翻参考文献列表。
- 用 `rg` 快速找：样本量、随机、盲法、结局、`P` 值、伦理、注册、设备参数、图号、表题。
- 先建立论文自身结构，再去判断外部建议对不对，这样不容易被别人的误读带偏。
- 只要图表是核心证据，就必须看真实图片，不能只看文字描述。

### 1.0 先建立运行底座与接手顺序

在冻结版本之前，先把工作区的运行底座判清。固定做五件事：

1. 判断四层落点：哪些文件是 `truth_source`，哪些只是 `execution_object / status_projection / display_projection`
2. 如果论文图表、表格、引文或资产较重，先建立对象层：
   - `objects/figures.json`
   - `objects/tables.json`
   - `objects/citations.json`
   - `objects/assets_manifest.json`
   - `objects/figures.json` 至少写明每个图件的 `source_kind`，例如 `docx_media` 或 `shape_rendered`，不要只在自然语言备注里临时解释
   - `objects/assets_manifest.json` 至少写明 `source_kind` 和 `asset_type`，区分“图件原始来源是什么”与“当前证据资产是怎么取得的”
   - 对表格密集项目，优先用 `scripts/extract_docx_tables.py` 生成 `assets/tables/docx_csv/` 和 `objects/tables.json`，不要继续手工在 Markdown 里抄表号和列名
   - 对引文密集项目，优先用 `scripts/extract_docx_citations.py` 生成 `objects/citations.json` 和 `reviews/citation_extraction_manifest.json`，先把引用锚点结构化，再做引文法证
3. 如果本轮依赖多个线程、多个代理、多个终端工具或多轮交接，先补 `reviews/process_projection.md`，统一记录 `goal / actions / findings / decisions / artifacts / status / next_step`
4. 按固定读取顺序接手：原始论文与底稿 → 对象层 → 冻结与版本台账 → workflow 与执行台账 → display_projection 与摘要
5. 对迁移过的项目或多轮改动项目，尽早跑一次 `scripts/check_review_workspace.py`、`scripts/scan_stale_paths.py`，必要时再跑 `scripts/evaluate_review_toolchain.py` 做轻量 readiness 评估，不要等到交付前才发现结构漂移

补充说明：

- `scripts/check_review_workspace.py` 默认以兼容模式运行，允许遗留项目或轻量单页项目把多页 `display/` 与展示层合同文件视为 warning
- 只有当项目明确进入标准多页 `display_projection` 模式时，才使用 `scripts/check_review_workspace.py --strict`

如果对象层或接手面缺失，不代表不能审；但要先把本轮边界降清楚，避免后续反复手工补路径、补图号和补线程摘要。

### 1.1 先冻结审阅对象与版本基线

开始下结论前，先明确“现在到底审哪一个文件、哪一个版本、哪些章节处于什么状态”。固定做四件事：

1. 记录唯一审阅对象：文件路径、文件名、最近修改时间，以及可用时的页数或行号底稿。
2. 对照学生、导师或其他代理给出的进度描述，逐项标记为 `已存在但待重写`、`确实缺失`、`已完成但需回归`、`不可判定`。
3. 把原论文、抽取文本、页图/裁图、补充材料和当前工作区中间产物分成“原始证据”和“派生产物”。
4. 先写一份 `审阅对象冻结说明`，再进入深审、逐条改稿或综合结论阶段。

没有版本基线时，不要直接下“这一章还没写/已经完成”的结论；尤其不要把学生自述、旧截图或旧 HTML 当成当前版本事实。

### 1.2 确认专业领域，先过专项手册完备性 gate

在读完论文基本结构后，立即执行专业识别，再开始任何实质性审查。

固定按这个顺序走：

1. 加载 [references/specialty-router.md](./references/specialty-router.md)，从封面、摘要、关键词、研究对象中识别**大学科 + 小学科**
2. 加载 [references/specialty-manual-readiness-gate.md](./references/specialty-manual-readiness-gate.md)，把当前专项状态判成 `complete / partial / missing`
3. 只有在 `complete` 时，才直接加载对应专项进入深审
4. 如果是 `partial`，先生成 `reviews/专业手册完备性判断.md` 和 `reviews/专业专项补充说明.md`，再用“专项 + 论文级补充”进入深审
5. 如果是 `missing`，先用通用框架快筛，同时触发 deep-research 获取该领域当前规范；只有当补充内容具备跨论文复用性时，才加载 [references/specialty-manual-standard.md](./references/specialty-manual-standard.md) 新建或重写共享专项

这一步不只判断“方法学规则够不够”，还要同步判断“学科语域够不够”：

1. 先确认这篇论文的学科审查常用语是什么
2. 再确认现有专项手册是否已经覆盖这套语域
3. 如果没有覆盖，在 `专业手册完备性判断` 里把它记成 `discipline_register_status = partial / missing`
4. 对公共卫生、临床流行病学、真实世界因果推断等非软件工程学科，默认不要把 `漂移 / 法证 / 冻结 / 回写 / 闭环 / 阻塞 / 原子级` 这类工程话术直接写进对外交付物
5. 需要这些内部概念时，先在专项阶段给出本学科可接受的替代表述，再进入学生版、导师版和网页展示层

**当前已有专项文件**：
- 康复医学 + 神经工程 → `references/rehab-neuroengineering.md`
- 心血管内科/外科 → `references/specialty-cardiology.md`
- 中医 / 中西医结合 → `references/specialty-tcm.md`
- 公共卫生 / 临床流行病学 / 真实世界因果推断 → `references/specialty-public-health-causal.md`

**如果无法从论文中判断专业**，直接问用户："这篇论文属于哪个科室/专业方向？"，不要猜测后默默加载错误模块。

专项文件的屏蔽规则见 `specialty-router.md` 第5节。不同专业的方法学标准不同；而“专项文件存在但不够用”同样会导致错误判断，所以不要跳过完备性 gate。

术语治理分两层：

1. 绝对禁用层：`truth_source / execution_object / status_projection / display_projection / process_projection / gate` 这类系统内部概念，不得直接进入导师、学生和网页成品
2. 学科语域适配层：`原子级 / 漂移 / 冻结 / 回写 / 回归 / 闭环 / 收口 / 阻塞 / 上游 / 下游 / 依赖 / 镜头 / 硬伤 / 污染` 这类工程隐喻，不是全局绝对禁用，但在非工程学科交付物里默认应替换为该学科常用表述

### 1.2.1 判断是否启动多专家独立审计

专项路由完成后，不要立刻把“多镜头审查”当成已经足够。先判断这篇论文是否需要把不同领域闭环拆开，做独立审计后再收敛。

以下任一情况满足时，默认启动多专家独立审计：

- 主结论同时依赖 `流行病学/研究设计`、`生物统计` 和 `具体临床领域` 三条以上闭环
- 因果识别、终点定义和统计估计对象三者中任意两者高度耦合
- 同一核心结论既要靠设计合法性成立，又要靠临床意义解释成立
- 论文同时跨“观察性因果推断 + 专病终点”或“临床干预 + 设备/信号处理”两条以上主线
- 外部专家、不同 agent 或不同台账对同一核心结论出现跨领域冲突

启动时，至少先明确五件事，并写进 `reviews/专业手册完备性判断.md`；如果现有共享专项不够，再同步写入 `reviews/专业专项补充说明.md`：

1. `domain_stack`：这篇论文到底命中了哪些闭环，例如 `流行病学 / 生物统计 / 心血管临床`
2. `primary_loop`：哪条闭环负责定义主判断边界
3. `supporting_loops`：哪些闭环只补约束，不主导最终结论
4. `independent_audit_required`：是否必须独立审计后再收敛
5. `required_expert_checks`：本轮至少要跑哪些专家切面

默认分工原则：

- `流行病学 / 研究设计`：负责研究身份、样本流程、暴露/结局定义、偏倚和识别边界
- `生物统计`：负责估计对象、数据类型、模型、比较口径、不确定性和摘要-正文-表图一致性
- `具体临床领域`：负责终点是否有临床意义、测量是否可信、解释是否越过专病语境
- `工程 / 设备 / 信号处理`：只在论文真的把设备链路作为关键证据时加入主闭环

如果某条闭环暂时没有对应的专门 agent，不等于这条闭环不存在；此时由命中的共享专项文件或 `专业专项补充说明` 暂代该专家闭环，但仍要单独写出判断，不要让统计或写作 agent 代替临床闭环发言。

默认专家启动组合、串并行选择和无对应专病 agent 时的暂代规则，统一以 [references/deep-review-gates.md](./references/deep-review-gates.md) 第2节为准，这里不再双写。

没有先写清 `domain_stack / primary_loop / required_expert_checks`，就不要宣布“已启动多专家审计”。

### 1.3 判断是否进入“导师式逐条改稿”模式

以下任一条件满足时，可在常规评审之外追加导师式改稿流程；但不要把它当成“评审已经完成”的信号：

- 用户明确说“导师视角”“逐段改”“逐句改”“原子级修改”“可直接替换”
- 用户不只要问题清单，还要能直接回填到正文的改写建议
- `reviews/评审闭环与放行判断.md` 已明确 `can_enter_line_editing = yes`

以下情况只提高逐条改稿的优先级，不单独构成进入条件：

- 论文已经进入送审、盲审、预答辩或正式答辩前精修阶段

进入该模式后，固定执行四件事：

1. 先做诊断，再给改写，不反过来
2. 每条改写都绑定原句、证据锚点和安全改写目标
3. 对需要回查原始数据、代码、伦理批件或参考文献原文的句子，标记 `待人工回查`，不要代写事实
4. 默认优先精修摘要、结果、讨论、结论、图题表题和答辩高风险段落，再决定是否扩展到全文

如果完整评审尚未闭环，但用户明确要求先处理某个局部高风险段落，只允许做有范围边界的局部改写；不要顺势产出全文执行清单、送审判断或导师决策页。

此模式下，固定加载 [references/advisor-line-editing.md](./references/advisor-line-editing.md)，并按需要调用：

- [agents/advisor-line-edit-agent.md](./agents/advisor-line-edit-agent.md)
- [agents/evidence-anchored-rewrite-agent.md](./agents/evidence-anchored-rewrite-agent.md)
- [agents/citation-integrity-agent.md](./agents/citation-integrity-agent.md)
- [agents/chapter-logic-surgeon.md](./agents/chapter-logic-surgeon.md)

### 1.4 先冻结核心结果真源与依赖关系

只要论文里存在多张表、多轮版本、多个摘要/结论改写稿，或多个代理同时参与，就先做一次“结果真源冻结”。固定做四件事：

1. 为每个核心数字指定唯一真源：正文表格、图注、补充附录，或可追溯的分析结果文件。
2. 建立依赖回归台账：摘要、结论、图注、表题、目录、HTML、修改清单哪些地方引用了该数字。
3. 发现旧值残留时，先判定为“版本漂移”，不要急着做文字润色。
4. 没有真源、真源互相冲突、或只来自二手转述的数字，不得写入最终结论或“可直接替换文本”。

复杂项目默认补一份 `版本冻结与依赖回归台账.md`；没有这一步，就容易把旧版结果继续带进摘要、结论和答辩口径。

### 1.5 先判断是不是跨代理协作场景

如果用户拿来了 `Codex`、`Claude Code`、`AntiGrativity` 或其他终端型代理的建议、terminal 内容、截图、自动生成文件，先加载 [references/agent-tool-adaptation.md](./references/agent-tool-adaptation.md)。

固定做四件事：

1. 先分清哪些是原始证据，哪些只是代理的判断或转述
2. 再按证据层级回查本地文件、图片和官方来源
3. 最后把不同代理的意见统一落到 `Adopt / Adopt with rewrite / Downgrade / Reject`
4. 如果过程已经跨越多个线程或工具，补一份 `process_projection`，不要让接手继续依赖完整聊天回放

### 1.6 先判断是否具备复算条件

不要默认“审论文”就等于“复算了结果”。固定判断三件事：

1. 是否有原始数据、分析脚本、结果导出、补充附录，或至少可追溯的中间结果文件。
2. 是否足够复算关键数字，还是只够做 `文本 + 图表 + 证据锚点` 核查。
3. 缺什么资产会阻断复算，以及这会把本轮审查降级到什么边界。

如果不具备复算条件，要在工作区和最终报告里明确标注：本轮属于“非复算审查”，不要让读者误以为模型或统计量被重新跑过。

### 1.7 对复杂 workflow 固定做一次上下文隔离反思

当论文进入多代理、多台账、强制深审，或用户明确要求“严谨推进”时，在 workflow 初稿稳定后固定追加一轮上下文隔离质询。目标不是重复审一遍，而是专门追问：

- 还有哪些审阅角度被主流程遗漏了
- 哪些中间文件只是模板，还没有实质证据
- 哪些 gate 应该前移，哪些收尾项被误放成前置完成
- 图表、补充材料、伦理合规、引文法证、复算准入有没有被低估

这轮反思的产物要单独落成文件或明确段落；没有经过隔离反思的大型 workflow，不要直接宣称“已覆盖全部关键风险”。

### 1.8 判断是否进入“强制深审”模式

以下任一条件满足，就不要停留在普通多镜头快筛，必须进入第二阶段深审：

- 干预、随机、假刺激、对照、疗效比较是主轴
- 论文同时涉及康复治疗和设备/传感器/神经调控/脑成像
- 关键证据依赖图表、流程图、信号图、脑图或多页表格
- 用户明确要求送审把关、答辩把关、科学性深审
- 不同代理或外审对同一核心结局给出了冲突判断

进入强制深审后，固定执行两段：

1. `首轮快筛`：研究身份、样本流程、统计口径、伦理合规、明显图表错号
2. `第二阶段深审`：核心结局证据链、干预与对照矩阵、图片法证核查、工程可复现性、答辩高风险点

如果环境支持子代理或专家并行，优先按 `agents/` 下的专门 agent 分工执行；如果环境不支持，就按相同清单顺序串行模拟，不要因为没有 agent 机制而跳过深审动作。

### 2. 用多镜头审查，但把高风险论文升级为专门 agent 流

### 2.5 判断是否需要工作量证据评估

以下情况触发 [agents/workload-assessment-agent.md](./agents/workload-assessment-agent.md)：

- 用户明确要求审查"工作量"或"证据充分性"
- 样本量与研究类型或结论强度明显不匹配
- 机制宣称明显强于测量深度（如行为数据→神经机制）
- 关键结论缺乏图表支撑
- 对照设置与疗效宣称不匹配

满足1条：纳入快筛，在综合报告中附带说明。满足2条及以上：触发完整四维度评估。

判定标准见 [references/workload-evidence-criteria.md](./references/workload-evidence-criteria.md)。

先判断研究类型，再决定哪些镜头和规范是主轴。不要默认所有临床论文都按干预研究去审。

- 研究类型分流见 [references/clinical-study-types.md](./references/clinical-study-types.md)
- 康复与神经工程专项见 [references/rehab-neuroengineering.md](./references/rehab-neuroengineering.md)
- 观察性因果推断专项见 [references/specialty-public-health-causal.md](./references/specialty-public-health-causal.md)
- 强制深审闸门见 [references/deep-review-gates.md](./references/deep-review-gates.md)

按论文类型选择镜头，不必机械全开，但至少覆盖会影响可信度、可解释性、可重复性、合规性和答辩风险的部分：

- 流行病学：研究设计身份、样本流程、纳排标准、偏倚风险、外部效度
- 统计学：结局层级、数据类型、检验方法、多重比较、缺失值、效应量
- 学术写作：标题-目的-结果一致性，术语，摘要，讨论，参考文献
- 医学/生物医学工程：设备来源、参数透明度、信号处理、可复现性
- 康复科学：干预靶点、剂量、治疗构成、对照可信度、生态效度
- 神经科学：任务是否有效、脑-行为桥接是否成立、激活与连接是否混写
- 伦理与报告规范：伦理审批、知情同意、注册状态、CONSORT/TIDieR 类信息是否缺失

对高风险论文，不要只停留在“镜头提示”。固定把下面这些专家任务落成证据产出：

- [agents/epi-rct-agent.md](./agents/epi-rct-agent.md)：临床干预研究的研究身份、样本流程、分析集、干预与对照可信度
- [agents/causal-inference-observational-agent.md](./agents/causal-inference-observational-agent.md)：观察性队列、目标试验模拟、时间零点、权重、竞争风险、交互作用解释
- [agents/stats-endpoint-agent.md](./agents/stats-endpoint-agent.md)：主要/次要结局、数据类型、模型、多重比较、摘要-正文-表图一致性
- [agents/figure-forensics-agent.md](./agents/figure-forensics-agent.md)：图页导出、裁图、坐标轴/图题/图注/正文互证
- [agents/neuroengineering-agent.md](./agents/neuroengineering-agent.md)：设备参数、采样、滤波、特征提取、归一化、黑箱边界
- [agents/academic-writing-agent.md](./agents/academic-writing-agent.md)：默认写作与规范扫雷，附带轻量结构闭合检查
- [agents/citation-integrity-agent.md](./agents/citation-integrity-agent.md)：论断-引文匹配、一手来源与错引核查
- [agents/chapter-logic-surgeon.md](./agents/chapter-logic-surgeon.md)：仅用于重度章节错位、迁移和重构
- [agents/evidence-anchored-rewrite-agent.md](./agents/evidence-anchored-rewrite-agent.md)：改写安全闸门，负责证据绑定、强度降级和禁改提醒
- [agents/advisor-line-edit-agent.md](./agents/advisor-line-edit-agent.md)：最终导师式逐条改写卡与可直接替换文本
- [agents/defense-risk-agent.md](./agents/defense-risk-agent.md)：答辩高风险追问、可守口径、禁区表述

如果时间或环境有限，至少保留最贴近研究类型的前四个；但只要题目、结局和图像证据高度耦合，就不允许跳过 `stats-endpoint-agent` 和 `figure-forensics-agent`；只要用户明确要求导师式精修，就不允许跳过 `advisor-line-edit-agent` 和 `evidence-anchored-rewrite-agent`。

### 3. 先分级，再提修改

固定使用以下分层：

- `P0`：不改就不建议送审/答辩
- `P1`：不改会被明显追问，论文显得不严谨
- `P2`：表述、规范、展示层面的收口和加固
- `Strategy`：高回报答辩策略，不改变事实，只重排解释层级
- `Upgrade`：下一轮研究的升级路线，不算本轮必须完成事项

不要混层。`Upgrade` 不能拿来替代未处理的 `P0`。

### 4. 严格复核外部建议，不照单全收

当用户拿来 Opus、Claude、Gemini、导师、外审、`Codex`、`Claude Code`、`AntiGrativity` 或其他 AI / 代理的建议时，不要整包接受或否定。每条建议都要落到下列四类之一：

- `Adopt`
- `Adopt with rewrite`
- `Downgrade`
- `Reject`

逐条判断：

1. 它和论文原文、表格、图片对得上吗？
2. 它是不是已经被修掉、因此过时了？
3. 采纳它会不会引入新的方法学风险？
4. 它到底是硬伤修复、实用增强，还是纯粹审美折腾？

### 5. 守住事实边界，绝不补造

以下是硬红线：

- 不能补造盲法、独立评估者、注册号、算法细节、标准化步骤
- 不能把事后解释写成事前预设
- 不能把 `t` 值图改写成 `ΔHbO2` 或其他物理量，除非原图就是那个量
- 不能把探索性机制结果说成确证性证明
- 不能为了“修好论文”而重写研究设计身份

优先用这类安全表述：

- “开放标签随机对照研究”
- “探索性机制分析”
- “支持性临床证据”
- “初步信号 / 潜在优势”
- “后续研究需进一步直接测量……”

### 6. 产出分层，而不是只给一份长文档

先产出证据型中间文件，再产出总结型交付物。对复杂或高风险论文，至少先完成与本项目相关的几类台账：

- `process_projection`
- `审阅对象冻结说明`
- `版本冻结与依赖回归台账`
- `关键数值与复算准入台账`
- `图表索引台账 / 图表专项核查`
- `核心结果证据链表`
- `伦理合规与数据追溯审计表`
- `主文补充附录交叉索引台账`
- `文献对标与引文法证`

脚手架或空模板不算“已完成审查”；只有填入了具体证据、定位和判断的文件，才算有效产出。

如果论文属于图表密集型、表格密集型或多线程接手型项目，优先把这几类结构化对象补到 `truth_source`：

- `objects/figures.json`
- `objects/tables.json`
- `objects/citations.json`
- `objects/assets_manifest.json`

这些对象文件优先承担“图号、caption、来源类型、证据资产路径、证据角色、引用可达性”的慢变量。Markdown 台账继续保留，但默认承担 `execution_object`，不要再让它们同时兼任数据库和最终交付。

在把问题诊断升级成执行清单、导师决策或送审 / 答辩判断前，先补一份 `reviews/评审闭环与放行判断.md`，至少回答：

- `scope_frozen`
- `deep_review_status`
- `coverage_status`
- `can_emit_problem_list`
- `can_emit_execution_outputs`
- `can_issue_readiness_verdict`
- `can_enter_line_editing`
- `blockers`

没有这份判断，或其中关键字段仍是 `no / pending / blocked` 时，不要默认产出执行清单、学生页、导师页、送审判断或全文逐条改稿。

大多数完整审查，先按“评审进行中”与“评审闭环后”两段产出，而不是一上来把所有执行面都做完：

评审进行中，至少产出三类：

1. 综合审查报告，或等价的持续更新审查主文
2. 证据型台账、问题映射或问题清单页
3. display_projection 展示层中的入口页 / 问题清单页 / 完整评审页（如果用户需要网页）

只有 `reviews/评审闭环与放行判断.md` 明确放行后，才默认补以下执行或决策型产物：

1. 最终可执行修改清单
2. 学生执行版 / 导师摘要版
3. display_projection 中的学生执行页 / 导师汇报页
4. 送审 / 答辩 readiness 判断

如果进入网页 / HTML 交付模式，display_projection 默认不要压成单页。除非用户明确要求只做单页且项目极轻，否则至少产出一个入口页和四个子页：

- `综合评审汇总.html`：入口页 / 总导航 / 当前状态总览
- `display/问题清单页.html`
- `display/完整评审页.html`
- `display/学生执行页.html`
- `display/导师汇报页.html`

只要进入网页 / HTML 交付模式，先固定检查一份放行判断，再补两份展示层合同文件：

- `reviews/评审闭环与放行判断.md`

- `reviews/audience_language_contract.md`
- `reviews/display_projection_schema.md`

必要时补充：

- 图表专项审查
- 答辩口径 / 高频追问应答
- 第三方建议复核意见
- 下一轮研究升级路线

进入导师式逐条改稿模式时，再补 2-4 样精修材料：

- 逐条修改建议卡 / 导师式逐段改稿
- 证据绑定改写表
- 论断-引文核查表
- 章节功能重构建议

如果进入了“强制深审”模式，再补三样证据型材料，或把它们并入综合报告附录：

- 核心结局证据链表
- 干预与对照矩阵
- 图片法证核查底稿

如果材料很多，建议再拆出两份轻量文档；即使已经有多页网页，这两份 Markdown 也不应省略：

- 学生执行版：只保留当前要改什么
- 导师摘要版：只保留最高风险项、答辩定位和关键决策

具体模板见 [references/output-templates.md](./references/output-templates.md)。

### 6.4 先判断是否进入多页 display_projection 模式

只要任务包含以下任一特征，就默认进入多页 display_projection 模式，而不是把所有内容压进一个 HTML：

- 用户明确要求网页、HTML、可分享页面、完整评审页、学生页或导师页
- 用户明确说“不要只列问题，要把完整结果都展示出来”
- 同一套交付物同时面向学生、导师和内部接手者
- 页面需要同时承载问题清单、完整判断、执行顺序和汇报决策

进入多页模式后，先做五件事，再开始写页面：

1. 先看 `reviews/评审闭环与放行判断.md`，明确当前是否只允许展示“评审进行中”，还是已经放行到执行 / 决策层
2. 先建立共享的问题映射台账或等价结构，作为所有页面共同上游
3. 先判每一页的受众与职责边界，再决定内容落点
4. 先写 `reviews/audience_language_contract.md`，冻结各页的受众语言合同
5. 先写 `reviews/display_projection_schema.md`，冻结各页的内容扩增合同

四个子页的默认职责如下：

- 问题清单页：按 `P0 / P1 / P2 / P3 / P4` 集中展示问题、证据和修法，不承担完整 workflow 解释
- 完整评审页：展示总体判断、当前评审状态、审阅步骤、逐项核查结果、图表专项和终检；只有放行后才给送审 readiness 和执行顺序
- 学生执行页：只在 `can_emit_execution_outputs = yes` 时产出；放行后只保留当前动作、顺序、完成标准、阻塞项和禁止事项，不堆长篇背景论证
- 导师汇报页：只在 `can_emit_execution_outputs = yes` 时产出；放行后只保留当前定位、是否建议送审 / 答辩、最高风险项、保留主线、关键决策和答辩口径

不要把“问题清单页 / 完整评审页 / 学生执行页 / 导师汇报页”做成同一页里的四个 tab 再算完工；默认按多页 display_projection 处理。

### 6.5 对多页 HTML / display_projection 做分阶段质量约束

HTML 不是把 Markdown 报告压缩一遍。普通项目可以偏概览；但只要进入“强制深审”或多受众交付，display_projection 默认要承担“入口页 + 多页证据工作台”的职责。

生成前先做三件事：

- 先建立问题映射台账，至少包含 `问题 ID / 级别 / 原文或图表定位 / 证据路径 / 为什么危险 / 安全修法 / 答辩追问点 / 确认状态`
- 没有进入台账的问题，不要直接写进任何网页子页
- 尚未核实、但必须提醒用户人工回查的点，统一标成 `待人工回查`

生成前还要再过三道闸门：

- `评审闭环与放行判断`：先判断当前页面是否已经有资格承载执行动作、导师决策或送审 / 答辩 readiness
- `audience_language_contract`：逐页确认页面语言是否已经翻译成受众语言，而不是内部工作语言
- `display_projection_schema`：逐页确认新增内容是否真的是评审判断、核查结果或修订决策，而不是只增加展示结构

如果 `can_emit_execution_outputs = no`，不要产出学生执行页或导师汇报页；如果 `can_issue_readiness_verdict = no`，入口页、完整评审页和导师汇报页只能写“评审进行中 / 暂不放行”，不要提前写“建议送审 / 答辩”。

生成中固定约束：

- `P0 / P1 / P2` 每条问题至少在问题清单页或完整评审页出现一次
- 图表问题直接嵌入本地图证、页图或裁图，不能只放“见附件”入口
- 非图表问题也要给原文定位、摘录或文件行号，不能只写抽象判断
- 问题卡片固定包含 `定位映射 / 证据 / 为什么危险 / 安全修法 / 答辩追问点 / 确认状态`
- 当问题总数 `<= 15` 时默认全部展开；超过时至少把 `P0 / P1` 全展开，`P2` 才允许折叠
- 四个子页要边界清楚：学生页不反向复制导师口径，导师页不反向承担学生逐项执行细则，完整评审页不退化成问题清单页，问题清单页也不代替完整评审页

生成后固定回查：

- 入口页和四个子页的计数、优先级矩阵、问题卡片数量要和综合报告、修改清单一致
- 所有锚点、图片路径、图号、表号、证据链接都要能点通或能定位
- 完整评审页中的结论强度不能弱化 `P0`，也不能为了页面简洁删掉关键映射字段
- 问题清单页 / 完整评审页 / 学生执行页 / 导师汇报页之间不能互相矛盾；如果一条问题被降级、关闭或改写，相关页面都要同步
- 图像和表格路径优先从 `objects/assets_manifest.json` 或对象层索引生成，不要手写漂移中的绝对路径

如果论文、清单、图证、图号或目录结构后来被二次改动，必须重新跑一轮多页 HTML 回归检查，不能默认旧页面仍然有效。

### 7. 做版本回归审查，防止“越改越乱”

如果论文、清单、HTML 或目录结构被别人二次改动过，必须追加一次“回归检查”：

- 新增内容是否真的修复了问题，还是只是改了表面措辞
- 是否引入了新的错号、错引、脏字符、路径错误、过时内容
- README、CHANGELOG、实际目录结构是否一致
- 入口页与各子页的锚点、图片路径、指标数量是否与正文同步
- 完整评审页与问题清单页是否仍完整覆盖当前版本的 `P0 / P1 / P2`，而不是停留在旧版摘要
- 清单里的“终检动作”是否仍然对应当前版本，而不是旧版本残留
- 如果项目经过目录迁移或跨项目搬运，优先跑 `scripts/scan_stale_paths.py` 抓旧绝对路径和路径漂移
- 如果这一轮还改了对象层、表格资产、引文锚点或接手面，再跑 `scripts/evaluate_review_toolchain.py`，确认不是只多了文件而没有提升准备度

### 8. 做项目卫生检查，避免产出物自己失控

当审查材料开始增多时，除了看论文，还要看项目本身是否整洁：

- 目录命名是否稳定
- 说明文档是否和实际文件落点一致
- 是否有明显过期文件、重复文件或误导性副本
- 长清单是否已经膨胀到需要拆版
- “问题清单页 / 完整评审页 / 学生页 / 导师页 / Markdown 版”是否边界清楚

### 9. 对新论文优先先建标准工作区

如果用户要开始审查下一篇论文，不要先随手堆文件。优先按标准结构建立工作区，再开始产出。

- 目录和命名规则见 [references/file-structure.md](./references/file-structure.md)
- 可以直接运行 `scripts/init_review_workspace.py` 初始化标准结构
- 工作区建好后，优先跑 `scripts/check_review_workspace.py` 检查对象层、交付层和接手面是否齐全；如果本轮明确采用标准多页 `display_projection`，再补跑 `scripts/check_review_workspace.py --strict`
- 如果原文是 DOCX，初始化后优先补三条结构化流水线，并按来源分流：`docx_media` 图件用 `scripts/extract_docx_media.py` 抽出 `word/media`；`shape_rendered` 图件先登记到 `objects/figures.json` 与 `objects/assets_manifest.json`，必要时再补页图、重导出页图或渲染链路审计；`scripts/extract_docx_tables.py --paper-dir <paperXX>` 抽表；`scripts/extract_docx_citations.py --paper-dir <paperXX>` 抽引文锚点
- 脚手架只创建目录和占位文件，不改动用户原有论文文件

### 10. 交付前做一次交付物自审

审查报告本身也可能出错。在综合报告、修改清单、网页入口页与子页、学生版、导师版全部完成后，加载 [references/self-audit.md](./references/self-audit.md) 做一轮自检。

重点不是重新审一遍论文，而是快速验证我们自己的产出：引用是否准确、分级是否一致、多份交付物之间是否同步、有没有越过事实边界。

如果交付物被二次修改过，也要再跑一轮自审。

### 10.5 用轻量指标判断这轮工具和流程有没有真正帮上忙

如果本轮修改涉及工作区结构、对象层、提取脚本或多线程接手面，至少回看以下五个指标：

- 建底稿与建资产索引的准备时间有没有下降
- 新接手者恢复现场的时间有没有下降
- 图表、表格和关键结论的覆盖率有没有上升
- 旧值、错链、旧路径和版本漂移的发现率有没有上升
- 逐条改稿建议的可采纳性有没有提升

如果只是增加了文件数量，却没有减少人工步骤或提高证据绑定强度，就不算有效升级。

## 优先盯住这些高频论文风险

- 样本流程在摘要、方法、结果、表格、图注中前后不一致
- 目标试验模拟声称很强，但 `资格判定 / time zero / 暴露归属 / 随访起点` 没对齐
- `IPTW / IPCW / MSM / competing risk / RERI` 写得很满，但诊断和解释边界没有交代
- 等级资料被当连续变量处理
- 没有明确结果层级，看上去像“挑阳性讲”
- 图号重复、图注错误、正文引用错位、色标不可比
- 机制宣称明显强于证据
- 改写建议只会“润色”，却没有把每一句绑定到表、图、统计量或文献
- 干预剂量、设备参数、刺激标准化说不透
- 伦理、注册、知情同意信息不完整
- 讨论只是被动防守，没有讲清研究真正贡献
- 图表只是数据陈列，没有形成独立说服力
- 把其他代理的结论当成已经核实的事实，没有回查原文、图表和当前文件状态

## 语言适配规则

- 默认用中文输出审查结论、修改建议、答辩口径和优先级判断。
- 如果工作对象是英文论文，保留英文术语、章节名、图题和统计表达，但解释、判断和执行说明仍优先用中文组织。
- 如果用户明确要求英文版交付物，再把综合报告或清单改写成英文。
- 不要因为论文是英文，就把中文使用者最需要的“结论、风险、怎么改”也改成难用的英文长文。

## 语气要求：严格，但可执行

- 严格指出风险，不要空泛吓唬人。
- `P0` 可以用重话，但要配具体修法。
- 正式文档里少用“直接毙掉”“一票否决”这类戏剧化措辞，除非用户明确要内部警示口径。
- 多给“怎么改”，少给“你这不行”。
- 尽量把每条批评都落到可验证动作上。
