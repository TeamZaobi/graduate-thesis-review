# 激活矩阵

这份矩阵定义 `graduate-thesis-review` 的默认加载面。

规则很简单：

1. 默认只激活热路径
2. 冷路径只在触发条件满足时加载
3. 机器合同保留，但不默认展开

## 默认热路径

| 模块 | 默认状态 | 触发条件 | 作用 |
|---|---|---|---|
| `references/review-rubric.md` | 热 | 每次审查 | 基础审查标准、严重度判断、证据边界 |
| `references/specialty-router.md` | 热 | 每次审查 | 识别大学科 / 小学科，决定专项路由 |
| `references/specialty-manual-readiness-gate.md` | 热 | 每次审查 | 判断专项是 `complete / partial / missing` |
| `references/review-operations-architecture.md` | 热 | 每次审查 | 运行底座、对象层、投影关系、默认读取顺序 |

## 冷路径

| 模块 | 默认状态 | 触发条件 | 作用 |
|---|---|---|---|
| `references/formal-review-checklist.md` | 冷 | 送审、预答辩、正式答辩前终稿、模板核查 | 版式、页码、目录、声明页、提交卫生 |
| `references/output-templates.md` | 冷 | 需要写修改清单、报告、导师摘要、HTML / 网页输出 | 输出形态模板与写作骨架 |
| `references/figure-table-standards.md` | 冷 | 图表密集、结果图、脑图、连接图、答辩图表 | 图表真源、编号、图注、互引规范 |
| `references/clinical-study-types.md` | 冷 | 需要区分研究类型、判定方法学主轴 | 干预 / 观察 / 诊断 / 预测 / 综述分流 |
| `references/advisor-line-editing.md` | 冷 | 用户明确要求导师式逐段改稿、原子级替换文本 | 逐条改稿与可直接替换文字 |
| `references/methodology-backed-advice.md` | 冷 | 进入建设性修改建议、学生执行清单、导师式改稿 | 方法学修复路径表 |
| `references/mentor-constructive-layers.md` | 冷 | 需要分层导师建议 | `L1-L4` 工作量 / 难度 / 收益分层 |
| `references/epi-biostat-language-contract.md` | 冷 | 导师建议需要流行病学 / 生物统计语言校准 | 语言规范与结论边界 |
| `references/mentor-projection-contract.md` | 冷 | 需要按角色投影同一建议 | 学生 / 导师 / 评审 / 答辩投影 |
| `references/frontier-innovation-gates.md` | 冷 | 创新性、最新进展、领域定位、前沿判断 | 前沿检索与创新定位 |
| `references/agent-tool-adaptation.md` | 冷 | 需要综合其他代理或工具输出 | 跨工具建议收口 |
| `references/deep-review-gates.md` | 冷 | 临床干预、随机对照、康复工程交叉、要求更深科学性 | 深审加闸 |
| `references/display-projection-gates.md` | 冷 | 进入网页 / HTML / display_projection | 展示投影门控 |
| `references/specialty-cardiology.md` | 冷 | 识别为心血管领域且专项完备性通过 | 心血管专项细则 |
| `references/rehab-neuroengineering.md` | 冷 | 识别为康复医学 / 神经工程且专项完备性通过 | 康复与神经工程专项细则 |
| `references/specialty-tcm.md` | 冷 | 识别为中医 / 中西医结合且专项完备性通过 | 中医专项细则 |
| `references/specialty-public-health-causal.md` | 冷 | 识别为公共卫生 / 临床流行病学 / 因果推断且专项完备性通过 | 公共卫生因果专项细则 |
| `references/specialty-manual-standard.md` | 冷 | 需要新建或重写共享专项 | 共享专项标准 |
| `references/self-audit.md` | 冷 | 所有主要输出完成后做最终自检 | 输出一致性与遗漏检查 |

## 冷路径触发速查

| 触发场景 | 加载模块 |
|---|---|
| 只做基础评审 | 只保留热路径 |
| 要求导师式改稿 | `methodology-backed-advice.md` + `mentor-constructive-layers.md` + `epi-biostat-language-contract.md` + `mentor-projection-contract.md` + `advisor-line-editing.md` |
| 要求创新性判断 | `frontier-innovation-gates.md` |
| 图表、表格、结果图多 | `figure-table-standards.md` |
| 形式审查、送审前、答辩前 | `formal-review-checklist.md` |
| 多代理复核或强冲突 | `agent-tool-adaptation.md` + `deep-review-gates.md` |
| 网页 / HTML 展示输出 | `display-projection-gates.md` |
| 命中特定专业 | 加载对应 `specialty-*.md` |
| 专项缺失或需重写 | `specialty-manual-standard.md` |

## 保留机器合同

以下对象不进入默认热路径，但必须保留为机器合同或可验证中间层：

1. runtime / workflow state
2. evidence / verdict / limitation
3. output policy / projection contract
4. 专项 gate 与路由规则

收口原则是“默认不展开”，不是“删除”。

## 一句话摘要

默认热路径只保留 `review-rubric`、`specialty-router`、`specialty-manual-readiness-gate`、`review-operations-architecture` 四个核心模块；其余能力全部作为冷路径按任务触发加载，但机器合同继续保留，不做删除。
