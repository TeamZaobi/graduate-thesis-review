# Graduate Thesis Review Skill

面向中文使用者的研究生毕业论文审查 Skill。当前执行“先完成高水平评审，再进入导师职责”的流程，支持中文和英文论文，并把论文工作区收口到 Files Driven 的 `governance / evidence / outputs / notes` 四族结构。

## 当前版本

- **Skill release version**：`v1.1.0`
- **Release date**：`2026-04-09`
- **Workflow / contract version_anchor**：`v1`

当前 release 聚焦三件事：

1. 把建设性意见收敛成导师层的结构化能力，而不是泛化的话术输出
2. 把流行病学 / 生物统计学语言校准与前沿检索 gate 接入导师建议链路
3. 把默认热路径压缩到最小核，并把高级能力全部改成显式冷路径触发

## 核心能力

- **效率与效能优先**：所有结构和工具改动都以“减少人工成本、提升证据绑定强度和改稿可执行性”为判断标准
- **分级问题识别**：P0/P1/P2 关键问题分级
- **使命层级固定**：先完成高水平评审，再进入导师式修改建议；导师职责不能脱离评审职责单独成立
- **默认热路径收口**：默认只前置 `review-rubric / specialty-router / specialty-manual-readiness-gate / review-operations-architecture`
- **显式冷路径触发**：导师修改、前沿检索、深审、形式审查、展示投影都按触发条件加载，不再默认展开
- **repo truth packs**：repo 级真源固定为 `workflow/review-workspace/` 与 `workflow/skill-maintenance/`
- **paper runtime pack**：每篇论文的 machine-readable runtime 真源固定为 `papers/<paper-id>/governance/review-workspace-pack/`
- **evidence verdict 中枢**：`papers/<paper-id>/evidence/review-verdict.json` 负责结论强度、缺失证据和输出授权边界
- **policy-driven advice**：导师/学生输出由 `knowledge/output-policies/advice-output-policy.json + review-verdict` 共同控制
- **可视化权威分层**：把作者文件、受控渲染权威和页面审计资产分开管理，不再默认要求先做 PDF
- **对象层治理**：把图、表、引文和资产路径沉淀到 `objects/*.json`，不只放在 Markdown 台账里
- **多线程接手面**：按需在 `notes/` 下生成过程说明，不再让 Markdown 承担 runtime authority
- **专业领域路由**：自动识别论文所属小学科，加载对应专项模块，屏蔽不相关检查
- **专项手册完备性 gate**：先判定当前专项是 `complete / partial / missing`，再决定是否直接深审
- **形式审查分层**：把通用形式项、院校模板项和导出回归项拆开检查，不与领域方法学规范混层
- **多角度复核**：流行病学、统计学、学术写作、医学工程、康复科学、神经科学、伦理合规
- **观察性因果推断专项**：目标试验模拟、`time zero`、新使用者设计、权重、竞争风险、交互作用
- **强制深审模式**：干预研究、随机对照、设备/影像密集型论文自动升级为专家 agent 分工审查
- **外部建议复核**：对导师、外审、AI 建议逐条判断 Adopt / Adopt with rewrite / Downgrade / Reject
- **方法学修复路径表**：所有建设性建议先落到问题类型、修复类型、依据、最小动作、验证动作
- **导师建议分层**：按 `L1-L4` 输出工作量、难度、收益和创新升级层级
- **流调 / 生统语言校准**：导师建议先经过 `epi_basis / stats_basis / claim_boundary / mentor_action`
- **受控前沿检索**：只有命中创新性、最新进展、领域定位等条件时，才进入外部知识检索
- **导师式逐条改稿**：输出逐段 / 逐句 / 可直接替换的证据绑定修改建议
- **引文与章节外科**：核查论断-引文匹配，并修复章节功能错位
- **答辩口径生成**：高频追问的安全应答框架
- **证据-结论匹配度评估**：工作量充足性的方法论判定，而非毕业资格审查

## 当前 Canonical 工作区

当前 release 之后，单篇论文工作区以这四个 paper-level 家族为准：

- `governance/`
  - 只放 `review-workspace-pack/` 及其 `workflow.state.json / workflow.events.jsonl / status.projection.json`
- `evidence/`
  - 只放 `criteria-coverage.json / evidence-ledger.jsonl / review-verdict.json / limitations.json`
- `outputs/`
  - 只放派生输出
- `notes/`
  - 只放 legacy manifest 和按需人工说明

兼容说明：

- `reviews/review_version_manifest.json` 现在是 `notes/legacy-review-manifest.json` 的 alias
- `reviews/process_projection.md`、`reviews/评审闭环与放行判断.md`、`reviews/专业手册完备性判断.md` 等历史路径仍可读，但 canonical 内容已迁入 `notes/`
- 下文仍出现的 `reviews/...` 路径，如果没有特别说明，默认视作 legacy alias，而不是新的 authority 落点

实现说明、版本与 release 说明见：

- `VERSION`
- `CHANGELOG.md`
- `governance/design/2026-04-mentor-constructive-advice-upgrade-design.md`
- `governance/design/2026-04-hot-cold-path-closure-decision.md`
- `governance/release/2026-04-v1-1-0-mentor-hot-path-release-note.md`
- `governance/design/2026-04-phase-1-4-implementation-note.md`
- `governance/release/2026-04-phase-1-4-migration-release-note.md`

## 文件结构

```
graduate-thesis-review/
├── README.md                         # 对外说明与使用入口
├── CHANGELOG.md                      # 发布变更记录
├── VERSION                           # 当前 skill release 版本锚点
├── SKILL.md                          # 主技能文件，执行流程入口
├── workflow/
│   ├── review-workspace/             # 论文评审 repo truth pack
│   └── skill-maintenance/            # skill 维护 repo truth pack
├── knowledge/
│   └── output-policies/
│       └── advice-output-policy.json # 导师/学生输出授权策略
├── agents/
│   ├── epi-rct-agent.md              # 流行病学与RCT专家
│   ├── stats-endpoint-agent.md       # 统计与结局证据链专家
│   ├── figure-forensics-agent.md     # 图表法证核查专家
│   ├── neuroengineering-agent.md     # 神经工程可复现性专家
│   ├── academic-writing-agent.md     # 学术写作专家
│   ├── causal-inference-observational-agent.md # 观察性因果推断专家
│   ├── citation-integrity-agent.md   # 引文完整性专家
│   ├── chapter-logic-surgeon.md      # 章节逻辑外科专家
│   ├── evidence-anchored-rewrite-agent.md # 证据绑定改写专家
│   ├── advisor-line-edit-agent.md    # 导师式逐条改稿专家
│   ├── frontier-innovation-agent.md  # 前沿检索与创新定位专家
│   ├── defense-risk-agent.md         # 答辩风险与口径专家
│   └── workload-assessment-agent.md  # 证据-结论匹配度评估专家
├── references/
    ├── activation-matrix.md          # 默认热路径 / 显式冷路径激活矩阵
    ├── review-operations-architecture.md # 四层运行底座、对象层、接手顺序、工具链
    ├── methodology-backed-advice.md  # 方法学修复路径表与建设性建议真源
    ├── mentor-constructive-layers.md # 导师建议 `L1-L4` 分层
    ├── epi-biostat-language-contract.md # 流调 / 生统语言校准合同
    ├── mentor-projection-contract.md # 学生 / 导师 / 评审 / 答辩投影合同
    ├── frontier-innovation-gates.md  # 前沿检索与创新定位 gate
    ├── advisor-line-editing.md       # 导师式逐条改稿流程
    ├── specialty-router.md           # 专业领域识别与路由（每次必加载）
    ├── specialty-manual-readiness-gate.md # 专项手册完备性判定与补建流程
    ├── specialty-manual-standard.md  # 共享专项手册的高标准规范
    ├── specialty-cardiology.md       # 心血管专项
    ├── specialty-tcm.md              # 中医/中西医结合专项
    ├── specialty-public-health-causal.md # 公共卫生与观察性因果推断专项
    ├── rehab-neuroengineering.md     # 康复医学+神经工程专项
    ├── clinical-study-types.md       # 研究类型分流（RCT/观察/诊断/预测/Meta）
    ├── deep-review-gates.md          # 强制深审闸门与五项必交付证据
    ├── review-rubric.md              # 多角度复核评分框架
    ├── workload-evidence-criteria.md # 证据-结论匹配度判定标准
    ├── formal-review-checklist.md    # 形式审查清单
    ├── figure-table-standards.md     # 图表规范
    ├── output-templates.md           # 交付物模板
    ├── file-structure.md             # 目录与命名规范
    ├── agent-tool-adaptation.md      # 跨代理协作框架
    └── self-audit.md                 # 交付物自审清单
└── scripts/
    ├── init_review_workspace.py      # 初始化标准工作区与对象层
    ├── check_review_workspace.py     # 检查工作区结构与 READY/PARTIAL/BLOCKED gate
    ├── extract_docx_media.py         # 抽取 DOCX word/media 图像资产，并标注 docx_media 来源类型
    ├── extract_docx_tables.py        # 抽取 DOCX 表格到 CSV 与 objects/tables.json
    ├── extract_docx_citations.py     # 抽取 DOCX 数字引文到 objects/citations.json
    ├── check_docx_formal_rules.py    # 抽取 DOCX 形式审查机械项，并输出 objects/formal_findings.json
    ├── render_docx_with_word.py      # 通过常驻 daemon 复用 Word 原生导出 PDF，并生成整页 page_renders
    ├── export_docx_to_pdf_word.jxa   # 供 render_docx_with_word.py 调用的 Word JXA 导出脚本
    ├── word_export_daemon.py         # 常驻 Word 导出 daemon，避免每次请求都重新授权
    ├── word_export_worker.jxa        # daemon 内部复用的长驻 Word 控制 worker
    ├── evaluate_review_toolchain.py  # 对单篇论文工作区做轻量工具链评估
    ├── run_workflow_regression.py    # 用真实脚手架 + fixture 执行代表性 workflow 回归
    ├── scan_stale_paths.py           # 扫描旧绝对路径和路径漂移
    ├── check_specialty_manual.py     # 校验共享专项手册是否满足高标准结构
    └── validate_evals.py             # 轻量校验 eval 覆盖
```

论文级 canonical 结构当前固定为：

```text
papers/
  paper01/
    governance/
      review-workspace-pack/
    evidence/
      criteria-coverage.json
      evidence-ledger.jsonl
      review-verdict.json
      limitations.json
    outputs/
    notes/
      legacy-review-manifest.json
      process_projection.md
      评审闭环与放行判断.md
      专业手册完备性判断.md
      专业专项补充说明.md
      审阅对象冻结说明.md
      ...
    reviews/                          # 仅保留兼容 alias
    objects/
    assets/
    display/
```

## 执行流程概览

```
1.   从原文建上下文（不先信外审）
1.0  建立运行底座与接手顺序
1.0.1 先判 entry_mode（initial_review / version_rebase / evidence_upgrade / display_regression / handoff_resume）
1.1  冻结审阅对象与版本基线
1.2  确认专业领域 → 先过专项手册完备性 gate → 再决定直接深审还是论文级补充
1.3  先形成 review-verdict，再判断是否进入导师式逐条改稿模式
1.4  冻结核心结果真源与依赖关系
1.5  判断是否跨代理协作场景
1.6  判断是否具备复算条件
1.7  对复杂 workflow 追加上下文隔离反思
1.8  判断是否进入强制深审模式
2.   多角度复核 → 按研究类型升级为专家 agent 分工
2.5  判断是否需要工作量证据评估
3.   分级（P0/P1/P2/Strategy/Upgrade）
4.   严格复核外部建议
5.   守住事实边界
6.   先证据型中间文件，后总结交付物
7.   版本回归审查
8.   项目卫生检查
```

如果完整评审尚未闭环，但用户明确只要求处理局部高风险段落，当前只允许启用 `legacy-review-manifest.json.task_exceptions.scoped_rewrite`，并补 `notes/局部改写任务卡.md`；不要直接把它放大成全文逐条改稿。

## 默认加载策略

当前默认心智模型固定为三层：

1. `Review`
2. `Mentor`
3. `Frontier`

其中默认热路径只保留：

1. `references/review-rubric.md`
2. `references/specialty-router.md`
3. `references/specialty-manual-readiness-gate.md`
4. `references/review-operations-architecture.md`

以下能力全部改为显式冷路径触发：

- `output-templates`
- `methodology-backed-advice`
- `mentor-constructive-layers`
- `epi-biostat-language-contract`
- `mentor-projection-contract`
- `frontier-innovation-gates`
- `formal-review-checklist`
- `deep-review-gates`
- `display-projection-gates`

正式触发矩阵以 `references/activation-matrix.md` 为准。

## 运行底座

对复杂论文项目，默认把工作区看成四层：

- `truth_source`：原论文、带行号底稿、结构化对象层、原始数据和可追溯结果
- `execution_object`：图表台账、版本冻结台账、合规审计表、逐条修改建议
- `status_projection`：执行状态总览、workflow、执行清单、学生版
- `display_projection`：HTML、导师摘要和展示页

图、表、引文和资产路径建议优先进入：

- `objects/figures.json`
- `objects/tables.json`
- `objects/citations.json`
- `objects/assets_manifest.json`

对图件对象，至少同时回答两件事：

- 图件原始来源类型是什么，例如 `docx_media` 还是 `shape_rendered`
- 当前证据文件是怎么来的，例如 `docx_media_extract`、`page_render_capture` 或 `zoom_crop`

如果原文来自 `Word / WPS` 这类所见即所得编辑器，建议再额外回答一件事：

- 本轮可视化权威来自哪里，例如 `word_native`、`wps_native`、`word_web` 或 `pdf_export_snapshot`

如果 workflow 跨线程、跨工具或跨代理，再补：

- `governance/review-workspace-pack/workflow.state.json`
- `governance/review-workspace-pack/workflow.events.jsonl`
- `governance/review-workspace-pack/status.projection.json`
- `notes/process_projection.md`

如果你要先固定一条稳健的可视化路线，当前推荐命令是：

```bash
python3 scripts/render_docx_with_word.py --docx thesis.docx --paper-dir papers/paper01 --overwrite
```

这条路线要求 `macOS + Microsoft Word + gs`，默认会启动一个常驻 daemon 复用同一个 `Word` 控制进程；第一次授权后，后续请求直接复用，不再每次重新弹授权。

当前最关键的 machine-readable 锚点有三类：

- `governance/review-workspace-pack/workflow.state.json`
- `governance/review-workspace-pack/status.projection.json`
- `evidence/review-verdict.json`

其中 `notes/legacy-review-manifest.json` 仍保留 thesis-specific 补充字段，例如：

- `entry_mode`
- `review_object`
- `truth_source`
- `rebase`
- `handoff`
- `release_gate`
- `specialty_gate`
- `task_exceptions`

如果论文高度依赖 Word 原生表格，建议尽早补：

- `assets/tables/docx_csv/`
- `objects/tables.json`

如果文献综述、讨论和方法学论断高度依赖引用，建议尽早补：

- `objects/citations.json`
- `notes/citation_extraction_manifest.json`

## 专业领域支持

| 专业 | 专项文件 | 状态 |
|---|---|---|
| 康复医学 + 神经工程 | `rehab-neuroengineering.md` | ✅ |
| 心血管内科/外科 | `specialty-cardiology.md` | ✅ |
| 中医 / 中西医结合 | `specialty-tcm.md` | ✅ |
| 公共卫生 / 临床流行病学 / 真实世界因果推断 | `specialty-public-health-causal.md` | ✅ |
| 其他专业 | 按需 deep-research 创建 | 动态扩展 |

未收录的专业，skill 不会直接硬套相邻专项，而是先判定为 `missing`，用通用框架快筛，再按需用 deep-research 和 `specialty-manual-standard.md` 补建。

## 专项手册 Gate

每篇论文进入专业路由后，固定先判定专项状态：

- `complete`：当前共享专项足以支撑这篇论文的研究类型与论文阶段，直接进入深审
- `partial`：共享专项存在，但不足以覆盖当前论文的关键问题；先补 `专业专项补充说明`
- `missing`：没有合适共享专项；先用通用框架快筛，再按标准补建专项

只要判成 `partial` 或 `missing`，建议最少落两份文件：

- `notes/专业手册完备性判断.md`
- `notes/专业专项补充说明.md`

当前实现里：

- `notes/legacy-review-manifest.json.specialty_gate` 是 thesis-specific 机器可读 gate
- `notes/专业手册完备性判断.md` 是人类可读投影与判断记录
- `reviews/专业手册完备性判断.md` 只是兼容 alias
- 如果 `specialty_gate` 仍是占位，脚本会暂时回退读取 Markdown，并提示迁移回 manifest

## 推荐触发语句

```
用这个 Skill 审查这篇论文，给出 P0/P1/P2 清单。
帮我综合外审、导师和 AI 的意见，判断哪些该改。
把这篇论文做成答辩导向的审查报告和 HTML 汇总。
用导师视角给这篇论文做逐段 / 逐句 / 逐条修改建议。
不要只告诉我哪里错，直接给我能替换回正文的安全改写。
复核这些修改建议有没有过度解读或造事实风险。
审查这篇英文 thesis，按中文习惯给我输出修改优先级和答辩建议。
```

## 安装

```bash
claude skill install https://github.com/TeamZaobi/graduate-thesis-review
```

## 设计原则

- **效率和效能优先**：如果一个改动不能减少准备/接手/回查成本，或不能提高证据绑定和改稿可执行性，就不应优先
- **论文审查 ≠ 毕业资格审查**：不评判字数、学分、发表要求，只评判证据链能否支撑结论
- **守住事实边界**：不建议补造数据，优先安全降级表述
- **先冻结再判断**：先冻结审阅对象、版本基线和结果真源，再写综合结论
- **模板不等于完成**：空台账和脚手架文件不算审查完成，必须有可回查证据
- **复算边界要说清**：没有原始数据和脚本时，只能做非复算审查，不能假装重跑过模型
- **专业隔离**：不同小学科的方法学标准不同，错误加载会导致错误判断
- **先判断手册够不够**：有专项文件不等于当前论文已经被覆盖；先过完备性 gate
- **改写必须绑证据**：不给“脱锚润色”，不给无出处的漂亮句子
- **答辩导向**：每条批评都配可操作的修法和答辩口径

## 测试

`evals/evals.json` 包含常规场景和失败模式回归样例。修改 skill 后，至少运行：

```bash
python3 scripts/validate_evals.py
python3 scripts/run_workflow_regression.py
```

这会检查：

- `evals.json` 是否可解析
- `id / prompt / expected_output / files` 结构是否完整
- `id` 是否连续且唯一
- 是否覆盖 `审阅对象冻结 / 模板假完成 / 真源与版本漂移 / 非复算审查 / 主文补充附录闭环 / 合规与引文法证 / 上下文隔离反思 / 对象层 / process_projection / review_version_manifest / 路径漂移 / 表格抽取流水线 / 工具链轻量评估 / workspace gate / release gate / 结构化 release gate / 提前改稿 / 提前 readiness / 形式审查` 等关键回归主题
- 文档抽取脚本是否仍能覆盖 `图 / 表 / 引文` 三条对象层流水线
- 9 条执行型 workflow fixture 是否仍能通过，包括默认热路径、导师冷路径、前沿冷路径、`handoff_resume` 路由、结构化 specialty gate、局部改写例外合同、release gate 阶段拦截、runtime drift 和无效 output policy

如果要校验 repo truth packs 和 paper runtime pack，额外运行：

```bash
python3 ../files-driven/scripts/validate_governance_assets.py \
  workflow/review-workspace
python3 ../files-driven/scripts/validate_governance_assets.py \
  workflow/skill-maintenance
python3 ../files-driven/scripts/validate_governance_assets.py \
  /path/to/project-root/papers/paper01/governance/review-workspace-pack
```

如需校验共享专项手册结构，额外运行：

```bash
python3 scripts/check_specialty_manual.py \
  --file references/rehab-neuroengineering.md \
  --file references/specialty-cardiology.md \
  --file references/specialty-tcm.md \
  --file references/specialty-public-health-causal.md
```

如需校验工作区和结构合同，额外运行：

```bash
python3 scripts/check_review_workspace.py --paper-dir /path/to/project-root/papers/paper01
python3 scripts/extract_docx_tables.py --docx /path/to/project-root/papers/paper01/thesis.docx --paper-dir /path/to/project-root/papers/paper01
python3 scripts/extract_docx_citations.py --docx /path/to/project-root/papers/paper01/thesis.docx --paper-dir /path/to/project-root/papers/paper01
python3 scripts/check_docx_formal_rules.py --docx /path/to/project-root/papers/paper01/thesis.docx --paper-dir /path/to/project-root/papers/paper01
python3 scripts/scan_stale_paths.py --root /path/to/project-root --match-root /old/absolute/root
python3 scripts/evaluate_review_toolchain.py --paper-dir /path/to/project-root/papers/paper01 --docx /path/to/project-root/papers/paper01/thesis.docx
```

其中 `check_review_workspace.py` 默认输出三态：

- `READY`：当前工作区已通过最小合同检查
- `PARTIAL`：结构可用，但仍有未收口项
- `BLOCKED`：仍缺核心文件、模板污点未清或关键页面 / JSON 仍是占位状态

当前脚本还会做四类与 workflow 直接相关的条件校验：

- 按 `legacy-review-manifest.json.entry_mode` 判断 `process_projection.md` 是否真的必需；`handoff_resume` 必需，其它入口不再一刀切阻断
- 对 `version_rebase / evidence_upgrade / display_regression / handoff_resume` 检查最小路由字段是否真的写回 legacy manifest
- 对 `专业手册完备性判断.md` 与 `专业专项补充说明.md` 做专项完备性 gate 回查，避免 `partial / missing` 时直接跳进深审
- 对 `output.advisor.line-editing / output.advisor.summary / output.student.execution-pack` 优先按 `review-verdict + advice-output-policy` 放行；`readiness verdict` 仍保留 legacy `release_gate` 兼容语义
