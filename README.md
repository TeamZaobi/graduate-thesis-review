# Graduate Thesis Review Skill

面向中文使用者的研究生毕业论文审查 Skill。执行“严格、答辩导向、可落地”的审查流程，支持中文和英文论文，并可在需要时进入导师式原子改稿模式。

## 核心能力

- **效率与效能优先**：所有结构和工具改动都以“减少人工成本、提升证据绑定强度和改稿可执行性”为判断标准
- **分级问题识别**：P0（送审硬伤）/ P1（答辩追问）/ P2（规范加固）
- **四层运行底座**：把工作区稳定拆成 `truth_source / execution_object / status_projection / display_projection`
- **对象层治理**：把图、表、引文和资产路径沉淀到 `objects/*.json`，不只放在 Markdown 台账里
- **多线程接手面**：用 `process_projection` 压缩多代理、多会话过程，降低恢复成本
- **专业领域路由**：自动识别论文所属小学科，加载对应专项模块，屏蔽不相关检查
- **专项手册完备性 gate**：先判定当前专项是 `complete / partial / missing`，再决定是否直接深审
- **多镜头审查**：流行病学、统计学、学术写作、医学工程、康复科学、神经科学、伦理合规
- **观察性因果推断专项**：目标试验模拟、`time zero`、新使用者设计、权重、竞争风险、交互作用
- **强制深审模式**：干预研究、随机对照、设备/影像密集型论文自动升级为专家 agent 分工审查
- **外部建议复核**：对导师、外审、AI 建议逐条判断 Adopt / Adopt with rewrite / Downgrade / Reject
- **导师式原子改稿**：输出逐段 / 逐句 / 可直接替换的证据绑定修改建议
- **引文与章节外科**：核查论断-引文匹配，并修复章节功能错位
- **答辩口径生成**：高频追问的安全应答框架
- **证据-结论匹配度评估**：工作量充足性的方法论判定，而非毕业资格审查

## 文件结构

```
graduate-thesis-review/
├── SKILL.md                          # 主技能文件，执行流程入口
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
│   ├── advisor-line-edit-agent.md    # 导师式原子改稿专家
│   ├── defense-risk-agent.md         # 答辩风险与口径专家
│   └── workload-assessment-agent.md  # 证据-结论匹配度评估专家
├── references/
    ├── review-operations-architecture.md # 四层运行底座、对象层、接手顺序、工具链
    ├── advisor-line-editing.md       # 导师式原子改稿流程
    ├── specialty-router.md           # 专业领域识别与路由（每次必加载）
    ├── specialty-manual-readiness-gate.md # 专项手册完备性判定与补建流程
    ├── specialty-manual-standard.md  # 共享专项手册的高标准规范
    ├── specialty-cardiology.md       # 心血管专项
    ├── specialty-tcm.md              # 中医/中西医结合专项
    ├── specialty-public-health-causal.md # 公共卫生与观察性因果推断专项
    ├── rehab-neuroengineering.md     # 康复医学+神经工程专项
    ├── clinical-study-types.md       # 研究类型分流（RCT/观察/诊断/预测/Meta）
    ├── deep-review-gates.md          # 强制深审闸门与五项必交付证据
    ├── review-rubric.md              # 多镜头审查评分框架
    ├── workload-evidence-criteria.md # 证据-结论匹配度判定标准
    ├── figure-table-standards.md     # 图表规范
    ├── output-templates.md           # 交付物模板
    ├── file-structure.md             # 目录与命名规范
    ├── agent-tool-adaptation.md      # 跨代理协作框架
    └── self-audit.md                 # 交付物自审清单
└── scripts/
    ├── init_review_workspace.py      # 初始化标准工作区与对象层
    ├── check_review_workspace.py     # 检查工作区结构合同
    ├── extract_docx_media.py         # 抽取 DOCX word/media 图像资产
    ├── extract_docx_tables.py        # 抽取 DOCX 表格到 CSV 与 objects/tables.json
    ├── extract_docx_citations.py     # 抽取 DOCX 数字引文到 objects/citations.json
    ├── evaluate_review_toolchain.py  # 对单篇论文工作区做轻量工具链评估
    ├── scan_stale_paths.py           # 扫描旧绝对路径和路径漂移
    ├── check_specialty_manual.py     # 校验共享专项手册是否满足高标准结构
    └── validate_evals.py             # 轻量校验 eval 覆盖
```

## 执行流程概览

```
1.   从原文建上下文（不先信外审）
1.0  建立运行底座与接手顺序
1.1  冻结审阅对象与版本基线
1.2  确认专业领域 → 先过专项手册完备性 gate → 再决定直接深审还是论文级补充
1.3  判断是否进入导师式原子改稿模式
1.4  冻结核心结果真源与依赖关系
1.5  判断是否跨代理协作场景
1.6  判断是否具备复算条件
1.7  对复杂 workflow 追加上下文隔离反思
1.8  判断是否进入强制深审模式
2.   多镜头审查 → 按研究类型升级为专家 agent 分工
2.5  判断是否需要工作量证据评估
3.   分级（P0/P1/P2/Strategy/Upgrade）
4.   严格复核外部建议
5.   守住事实边界
6.   先证据型中间文件，后总结交付物
7.   版本回归审查
8.   项目卫生检查
```

## 运行底座

对复杂论文项目，默认把工作区看成四层：

- `truth_source`：原论文、带行号底稿、结构化对象层、原始数据和可追溯结果
- `execution_object`：图表台账、版本冻结台账、合规审计表、原子级修改建议
- `status_projection`：执行状态总览、workflow、执行清单、学生版
- `display_projection`：HTML、导师摘要和展示页

图、表、引文和资产路径建议优先进入：

- `objects/figures.json`
- `objects/tables.json`
- `objects/citations.json`
- `objects/assets_manifest.json`

如果 workflow 跨线程、跨工具或跨代理，再补：

- `reviews/process_projection.md`

如果论文高度依赖 Word 原生表格，建议尽早补：

- `assets/tables/docx_csv/`
- `objects/tables.json`

如果文献综述、讨论和方法学论断高度依赖引用，建议尽早补：

- `objects/citations.json`
- `reviews/citation_extraction_manifest.json`

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

- `reviews/专业手册完备性判断.md`
- `reviews/专业专项补充说明.md`

## 推荐触发语句

```
用这个 Skill 审查这篇论文，给出 P0/P1/P2 清单。
帮我综合外审、导师和 AI 的意见，判断哪些该改。
把这篇论文做成答辩导向的审查报告和 HTML 汇总。
用导师视角给这篇论文做逐段 / 逐句 / 原子级修改建议。
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
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/validate_evals.py
```

这会检查：

- `evals.json` 是否可解析
- `id / prompt / expected_output / files` 结构是否完整
- `id` 是否连续且唯一
- 是否覆盖 `审阅对象冻结 / 模板假完成 / 真源与版本漂移 / 非复算审查 / 主文补充附录闭环 / 合规与引文法证 / 上下文隔离反思 / 对象层 / process_projection / 路径漂移 / 表格抽取流水线 / 工具链轻量评估` 等关键回归主题
- 文档抽取脚本是否仍能覆盖 `图 / 表 / 引文` 三条对象层流水线

如需校验共享专项手册结构，额外运行：

```bash
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/check_specialty_manual.py \
  --file /Users/jixiaokang/.agents/skills/graduate-thesis-review/references/rehab-neuroengineering.md \
  --file /Users/jixiaokang/.agents/skills/graduate-thesis-review/references/specialty-cardiology.md \
  --file /Users/jixiaokang/.agents/skills/graduate-thesis-review/references/specialty-tcm.md \
  --file /Users/jixiaokang/.agents/skills/graduate-thesis-review/references/specialty-public-health-causal.md
```

如需校验工作区和结构合同，额外运行：

```bash
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/check_review_workspace.py --paper-dir /path/to/project-root/papers/paper01
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/extract_docx_tables.py --docx /path/to/project-root/papers/paper01/thesis.docx --paper-dir /path/to/project-root/papers/paper01
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/extract_docx_citations.py --docx /path/to/project-root/papers/paper01/thesis.docx --paper-dir /path/to/project-root/papers/paper01
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/scan_stale_paths.py --root /path/to/project-root --match-root /old/absolute/root
python /Users/jixiaokang/.agents/skills/graduate-thesis-review/scripts/evaluate_review_toolchain.py --paper-dir /path/to/project-root/papers/paper01 --docx /path/to/project-root/papers/paper01/thesis.docx
```
