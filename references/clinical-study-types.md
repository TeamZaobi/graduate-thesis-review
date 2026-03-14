# 临床研究类型分流

当审查对象属于临床医学研究，但不确定该用哪一套检查重点时，先加载此文件。

核心原则：**先识别研究类型，再启动对应的高风险检查。**  
不要把干预研究、观察性研究、诊断研究、预测模型和系统综述用同一套标准硬审。

## 1. 先判断研究类型

优先从标题、摘要、方法中的这些词判断：

- `randomized` / `trial` / `intervention` / `allocation`
- `cohort` / `prospective` / `retrospective`
- `case-control`
- `diagnostic accuracy` / `sensitivity` / `specificity` / `AUC`
- `prediction model` / `nomogram` / `calibration`
- `systematic review` / `meta-analysis`
- `non-inferiority` / `equivalence`

如果论文混合多种成分，按**主研究问题**来定主类型。

## 2. 常见研究类型与优先检查点

### A. 干预研究 / 随机对照研究

典型关键词：

- randomized controlled trial
- intervention
- allocation
- parallel group

优先检查：

- 样本流程和分析集
- 随机方法与分配隐藏
- 盲法和开放标签申报
- 主要 / 次要结局是否清楚
- 干预剂量、对照组、共干预是否平衡
- CONSORT 流程图是否存在

高频风险：

- 主要结局未定义
- 样本流程冲突
- 组间总暴露不一致
- 多重比较未说明

### B. 观察性研究（队列 / 病例对照 / 横断面）

典型关键词：

- cohort
- retrospective
- prospective
- case-control
- cross-sectional

优先检查：

- 纳入、排除、随访和缺失值
- 暴露与结局定义
- 混杂因素控制
- 倾向评分、匹配、多变量调整是否合理
- STROBE 要点是否齐全

高频风险：

- 混杂控制不足
- 因果语气过强
- 选择偏倚和信息偏倚没有交代

### C. 诊断准确性研究

典型关键词：

- diagnostic accuracy
- sensitivity
- specificity
- ROC
- gold standard

优先检查：

- 指标试验和参考标准定义
- 阈值是预设还是事后选择
- 受试者来源和谱偏倚
- STARD 要点是否齐全

高频风险：

- 缺参考标准
- 阈值事后最优化
- 只报 AUC，不报敏感度/特异度和区间

### D. 预测模型研究

典型关键词：

- prediction model
- risk score
- nomogram
- calibration
- validation

优先检查：

- 结局定义和预测时间窗
- 候选变量来源
- 缺失值处理
- 内部验证 / 外部验证
- 区分 discrimination 与 calibration
- TRIPOD 要点是否覆盖

高频风险：

- 只报 AUC，不报校准
- 事件数过少仍塞很多变量
- 没有验证却宣称可推广

### E. 系统综述 / Meta 分析

典型关键词：

- systematic review
- meta-analysis
- pooled
- heterogeneity

优先检查：

- 检索策略
- 纳入排除标准
- 偏倚风险评估
- 异质性和亚组分析
- PRISMA 流程图是否存在

高频风险：

- 检索不完整
- 质量评价缺失
- 异质性很高却结论很强

### F. 非劣效 / 等效研究

典型关键词：

- non-inferiority
- equivalence

优先检查：

- 界值是否事先定义
- 分析集是否合理（通常要同时看 ITT 和 PP）
- 结论是否围绕界值而不是单纯 `P<0.05`

高频风险：

- 把“无差异”误写成“非劣效”
- 不报告界值依据

## 3. 各类型对应的报告规范

优先参考：

- 干预研究：CONSORT / TIDieR
- 观察性研究：STROBE
- 诊断准确性研究：STARD
- 预测模型研究：TRIPOD
- 系统综述 / Meta：PRISMA

如果论文带 AI、算法或数字医疗成分，还应留意相应扩展规范是否需要补充。

## 4. 图表和结果类型也要跟研究类型匹配

### 干预研究

- 受试者流程图
- 主要结局变化图
- 安全性表

### 观察性研究

- 基线表
- 回归结果表
- 分层 / 亚组图

### 诊断研究

- ROC 图
- 敏感度 / 特异度表
- 阈值说明

### 预测模型

- ROC / C-index
- calibration plot
- decision curve

### 系统综述 / Meta

- PRISMA 流程图
- forest plot
- risk of bias 图

## 5. 何时进入专项模块

如果论文除了临床研究属性外，还明显带有这些特征，就继续加载专项模块：

- 康复医学
- 神经工程 / 脑机接口
- 神经影像 / fNIRS / EEG
- 多模态设备和闭源算法

当前 Skill 中，这类论文请继续加载 [rehab-neuroengineering.md](./rehab-neuroengineering.md)。
