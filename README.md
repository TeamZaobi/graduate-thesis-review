# Graduate Thesis Review Skill

面向中文使用者的研究生论文审查 Claude Agent Skill。执行"严格、答辩导向、可落地"的论文审查流程，支持中文和英文论文。

## 核心能力

- **分级问题识别**：P0（送审硬伤）/ P1（答辩追问）/ P2（规范加固）
- **专业领域路由**：自动识别论文所属小学科，加载对应专项模块，屏蔽不相关检查
- **多镜头审查**：流行病学、统计学、学术写作、医学工程、康复科学、神经科学、伦理合规
- **强制深审模式**：干预研究、随机对照、设备/影像密集型论文自动升级为专家 agent 分工审查
- **外部建议复核**：对导师、外审、AI 建议逐条判断 Adopt / Adopt with rewrite / Downgrade / Reject
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
│   ├── defense-risk-agent.md         # 答辩风险与口径专家
│   └── workload-assessment-agent.md  # 证据-结论匹配度评估专家
└── references/
    ├── specialty-router.md           # 专业领域识别与路由（每次必加载）
    ├── specialty-cardiology.md       # 心血管专项
    ├── specialty-tcm.md              # 中医/中西医结合专项
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
```

## 执行流程概览

```
1.   从原文建上下文（不先信外审）
1.2  确认专业领域 → 加载专项模块 / 屏蔽不相关检查
1.5  判断是否跨代理协作场景
1.8  判断是否进入强制深审模式
2.   多镜头审查 → 高风险论文升级为专家 agent 分工
2.5  判断是否需要工作量证据评估
3.   分级（P0/P1/P2/Strategy/Upgrade）
4.   严格复核外部建议
5.   守住事实边界
6.   分层产出（报告 + 修改清单 + HTML 汇总页）
7.   版本回归审查
8.   项目卫生检查
```

## 专业领域支持

| 专业 | 专项文件 | 状态 |
|---|---|---|
| 康复医学 + 神经工程 | `rehab-neuroengineering.md` | ✅ |
| 心血管内科/外科 | `specialty-cardiology.md` | ✅ |
| 中医 / 中西医结合 | `specialty-tcm.md` | ✅ |
| 其他专业 | 按需 deep-research 创建 | 动态扩展 |

未收录的专业，skill 会自动触发 deep-research 获取当前领域规范，并创建新专项文件。

## 推荐触发语句

```
用这个 Skill 审查这篇论文，给出 P0/P1/P2 清单。
帮我综合外审、导师和 AI 的意见，判断哪些该改。
把这篇论文做成答辩导向的审查报告和 HTML 汇总。
复核这些修改建议有没有过度解读或造事实风险。
审查这篇英文 thesis，按中文习惯给我输出修改优先级和答辩建议。
```

## 安装

```bash
claude skill install https://github.com/TeamZaobi/graduat-thesis-review
```

## 设计原则

- **论文审查 ≠ 毕业资格审查**：不评判字数、学分、发表要求，只评判证据链能否支撑结论
- **守住事实边界**：不建议补造数据，优先安全降级表述
- **专业隔离**：不同小学科的方法学标准不同，错误加载会导致错误判断
- **答辩导向**：每条批评都配可操作的修法和答辩口径
