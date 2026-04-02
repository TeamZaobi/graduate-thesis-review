# 交付物文件结构规范

当需要为一篇新论文建立长期可维护的审查工作区时，使用这份规范。

## 1. 推荐目录树

优先使用“以论文为中心”的结构：

```text
project-root/
  papers/
    paper01/
      原论文.docx / 原论文.pdf
      综合评审汇总.html
      display/
        问题清单页.html
        完整评审页.html
        学生执行页.html
        导师汇报页.html
      objects/
        figures.json
        tables.json
        citations.json
        assets_manifest.json
      reviews/
        process_projection.md
        review_version_manifest.json
        评审闭环与放行判断.md
        audience_language_contract.md
        display_projection_schema.md
        专业手册完备性判断.md
        专业专项补充说明.md
        审阅对象冻结说明.md
        版本冻结与依赖回归台账.md
        关键数值与复算准入台账.md
        图表索引台账.md
        图表专项核查.md
        伦理合规与数据追溯审计表.md
        主文补充附录交叉索引台账.md
        文献对标与引文法证.md
        论文多智能体审查报告.md
        最终可执行修改清单.md
        学生执行版修改清单.md
        导师汇报版摘要.md
        第三方建议复核意见.md
      assets/
        figures/
          docx_media/
          key/
        tables/
          docx_csv/
        zoom/
        pdf_pages/
        scans/
    paper02/
      ...
  README.md
  CHANGELOG.md
```

如果用户已有别的目录体系，不必强行重构，但至少保证“原文、对象层、评审文档、图像资源、网页入口页与子页”彼此可追踪。

## 2. 命名规则

### 论文目录

- 推荐：`paper01`、`paper02`、`paper03`
- 不建议直接用超长中文标题做目录名

### 核心交付物

推荐固定使用：

- `论文多智能体审查报告.md`
- `最终可执行修改清单.md`
- `学生执行版修改清单.md`
- `导师汇报版摘要.md`
- `第三方建议复核意见.md`
- `综合评审汇总.html`

如果进入网页 / HTML 多页展示模式，推荐固定使用：

- `display/问题清单页.html`
- `display/完整评审页.html`
- `display/学生执行页.html`
- `display/导师汇报页.html`

对复杂或高风险项目，证据型中间文件也建议固定命名：

- `process_projection.md`
- `review_version_manifest.json`
- `评审闭环与放行判断.md`
- `audience_language_contract.md`
- `display_projection_schema.md`
- `专业手册完备性判断.md`
- `专业专项补充说明.md`
- `审阅对象冻结说明.md`
- `版本冻结与依赖回归台账.md`
- `关键数值与复算准入台账.md`
- `图表索引台账.md`
- `图表专项核查.md`
- `核心结果证据链表.md`
- `伦理合规与数据追溯审计表.md`
- `主文补充附录交叉索引台账.md`
- `文献对标与引文法证.md`

进入导师式精修模式时，允许追加：

- `原子级修改建议.md`
- `论断-引文核查表.md`
- `证据绑定改写表.md`
- `章节结构调整建议.md`

### 对外显示名与兼容策略

当前 Skill 为兼容既有工作区，仍保留一批历史文件名；但这些文件如果直接给导师、学生或网页读者看，显示名应优先翻译成学科可接受表达，而不是照抄内部或历史命名。

推荐做法：

- 保留内部兼容文件名，但在正文标题、链接文字、页面标题里使用对外显示名
- 新工作区如无兼容压力，可逐步把对外文件名也迁到更自然的中文学术表述

常见映射示例：

- `原子级修改建议.md` → 对外显示为 `逐条修改建议`
- `版本冻结与依赖回归台账.md` → 对外显示为 `结果定稿与一致性核查表`
- `文献对标与引文法证.md` → 对外显示为 `文献比对与引文核查`
- `process_projection.md` → 对外显示为 `多轮审查接续说明`

这样做的好处：

- 便于后续代理或脚本快速识别文件角色
- 不容易因命名风格变化而找不到材料
- 同一篇论文可以长期迭代，不必频繁重命名
- 能明确区分“冻结/审计台账”和“最终结论文档”
- 能明确区分“共享专项是否够用”和“本论文临时补充规则”

同一类文件要有唯一落点，不要在 workflow 里写模糊路径如 `reviews/...`。应始终写成精确文件名，必要时在 README 里注明哪个文件是该类信息的唯一真源。

### `review_version_manifest.json`

这是版本治理的机器可读锚点，放在 `reviews/` 下，与 Markdown 台账并列维护。

最少字段：

- `template_status`
- `entry_mode`
- `review_object`
- `truth_source`
- `rebase`
- `slow_variables`
- `dependents`
- `readiness`
- `handoff`

用途：

- 让 `initial_review / version_rebase / evidence_upgrade / display_regression / handoff_resume` 五种入口模式有统一落点
- 把 `current source / historical sources / deprecated anchors / impacted artifacts` 固定为可检查结构
- 给 `check_review_workspace.py`、`evaluate_review_toolchain.py` 和多线程接手提供稳定锚点

默认规则：

- 新工作区初始化后，`template_status = tainted`
- 只有在写入当前版本事实、入口模式和当前 readiness 后，才允许清掉 `tainted`
- 它不代替 `审阅对象冻结说明.md` 和 `版本冻结与依赖回归台账.md`；前者偏机器读写，后两者偏人类判断与证据叙述

## 3. 结构分工

建议把论文审阅工作区按四层理解，而不是只按目录看：

1. `truth_source`
2. `execution_object`
3. `status_projection`
4. `display_projection`

同一份事实优先只给一个明确真源；`status` 和 `display` 不应反向改写真源。

### `objects/`

放结构化慢变量，不放最终长文结论。

- `figures.json`：图号、caption、`source_kind`、当前证据路径、证据角色、摘要/结论可用性
- `tables.json`：表号、caption、结果类型、主分析/敏感性角色
- `citations.json`：关键引文、类型、一手/二手、绑定论断
- `assets_manifest.json`：图片原始来源类型、当前证据资产类型、输出路径、页图/裁图/关键图关系

### `reviews/`

放 Markdown 文本交付物。

- 详细长文档放这里
- 学生版和导师版也放这里
- 外部评审原文或复核意见也放这里
- 证据型中间台账也默认放这里，除非项目已经约定单独的 `reviews/evidence/`
- `process_projection.md` 也放这里，用作多线程、多代理接手面；它是过程投影，不是真源
- `review_version_manifest.json` 也放这里，用作版本入口、rebase 和 readiness 的机器锚点；它不是最终判断正文
- `评审闭环与放行判断.md` 也放这里，用作进入执行清单、导师摘要、网页决策页和逐条改稿前的最小放行锚点
- `audience_language_contract.md` 放这里，用作网页展示层的受众语言合同
- `display_projection_schema.md` 放这里，用作网页展示层的内容扩增合同
- `专业手册完备性判断.md` 和 `专业专项补充说明.md` 也放这里；它们属于当前论文的执行对象，不回写共享专项
- `citation_extraction_manifest.json` 可作为机器生成的引文抽取摘要放这里，用于人工快速回查

### `assets/`

放所有图片资源。

- `figures/`：拼图、汇总图
- `figures/docx_media/`：从 `DOCX word/media` 直接抽出的原始图件；它只覆盖 `docx_media`，不代表全部图件来源
- `figures/key/`：为引用和人工核查重命名后的关键图
- `tables/docx_csv/`：从 `DOCX` 抽出的原始表格 CSV
- `zoom/`：局部裁切放大图
- `pdf_pages/`：PDF 整页导出图；可作为 `shape_rendered` 图件的当前证据资产，但不自动等于原始来源
- `scans/`：扫描图或其他中间图像

### 论文根目录

仅保留：

- 原论文
- `综合评审汇总.html`
- `display/`
- `objects/`
- `reviews/`
- `assets/`

不要把大量中间文档或多张子页直接散落在 `paper01/` 根层。

### `display/`

放网页展示层子页，而不是把所有受众都混在根目录唯一 HTML 里。

- `问题清单页.html`：问题卡片与优先级矩阵
- `完整评审页.html`：完整判断、workflow、逐项核查、图表专项、执行顺序、终检
- `学生执行页.html`：动作、顺序、完成标准、待回查项
- `导师汇报页.html`：高层判断、风险摘要、关键决策、答辩口径

根目录的 `综合评审汇总.html` 默认承担入口页职责，负责导航到这四个子页，并展示当前状态总览。

`学生 / 导师` 两类轻量 Markdown 和对应 HTML 的主从关系默认如下：

- `学生执行版修改清单.md` 是主 `status_projection`
- `display/学生执行页.html` 是它的 `display_projection`
- `导师汇报版摘要.md` 是主 `status_projection`
- `display/导师汇报页.html` 是它的 `display_projection`

如果主 Markdown 尚未放行，不要先把 HTML 做成“已可执行 / 已可送审”的样子。

## 4. 何时拆版

当 `最终可执行修改清单.md` 出现以下迹象时，应拆出轻量版：

- 超过普通学生一天内能读完并执行的负担
- 同时承担“底稿”“教学说明”“导师决策”“未来工作”四种角色
- 用户开始反复问“我现在到底先改什么”

默认拆出：

- 学生执行版：只给动作和验收标准
- 导师摘要版：只给决策信息

## 5. HTML 落点规则

`综合评审汇总.html` 建议放在对应论文根目录，作为入口页；其余子页建议放在 `display/` 目录下，而不是统一堆在项目根目录。

原因：

- 入口页相对路径更稳定
- 子页和 `assets/`、`reviews/` 同级体系更清晰，后续搬迁成本低
- 同一项目下多篇论文不会互相污染路径

## 6. README / CHANGELOG 规则

只要目录结构改过，就同步改：

- `README.md`：描述当前真实结构
- `CHANGELOG.md`：记录何时、为什么改结构

不要让 README 停留在旧目录结构，否则后续所有修改者都会被误导。

## 7. 最低限度检查

每次做完结构调整后，至少检查：

1. HTML 图片路径是否都有效
2. README 描述是否仍然对应真实结构
3. CHANGELOG 是否记录了这轮结构性变动
4. `reviews/` 中是否已有完整版、学生版、导师版
5. `display/` 中是否已有问题清单页、完整评审页、学生执行页、导师汇报页
6. `reviews/` 中是否已有 `audience_language_contract.md` 与 `display_projection_schema.md`
7. `reviews/review_version_manifest.json` 是否已清除 `tainted`，并写明当前 `entry_mode`
8. 新建的台账文件是否已有实填内容，而不是只停留在空骨架
9. 结果真源、版本冻结和图表核查文件是否各自只有一个权威落点
10. `objects/` 是否存在，且图表密集项目不再只依赖手写 Markdown 路径
11. 迁移后是否跑过旧绝对路径扫描，而不是等到 HTML 或报告里才暴露路径漂移

补充说明：

- `scripts/check_review_workspace.py` 默认输出 `READY / PARTIAL / BLOCKED`
- 兼容模式下，缺少 `display/` 子页或展示层合同文件仍可能只是 warning，但 `review_version_manifest.json` 缺失、模板污点未清、占位 HTML 未清或核心台账仍为空会直接落到 `BLOCKED`
- 只有在明确采用标准多页 `display_projection` 时，才建议使用 `scripts/check_review_workspace.py --strict`
