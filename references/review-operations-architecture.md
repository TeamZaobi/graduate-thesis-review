# 审查运行架构与资产管线

当目标是提升**具体毕业论文评审工作**的效率和效能时，加载此文件。

它不替代方法学审查细则，而是回答三件事：

1. 事实、执行、状态和展示分别落在哪
2. 图、表、引文和路径怎么从“手工记忆”升级成结构化资产
3. 多线程、多代理、多工具时，怎么降低接手和恢复成本

## 1. 总目标

只保留两类真正有价值的改动：

1. 降低建底稿、接手、回查、迁移和回归检查的人工作业量
2. 提高图表、表格、引文、数字和结论之间的证据绑定强度

如果一个改动只增加了文件数量，没有减少人工步骤或提高证据强度，就不应优先。

## 2. 四层运行底座

默认按四层理解论文审阅工作区：

1. `truth_source`
2. `execution_object`
3. `status_projection`
4. `display_projection`

推荐映射：

- `truth_source`
  - 原论文 `DOCX/PDF`
  - `paperXX_docx_lines.txt`
  - `objects/figures.json`
  - `objects/tables.json`
  - `objects/citations.json`
  - `objects/assets_manifest.json`
  - 原始数据、分析导出和复算结果
- `execution_object`
  - 各类台账、审计表、改稿卡片
- `status_projection`
  - `审阅工作流.md`
  - `执行状态总览.md`
  - 学生版和执行清单
- `display_projection`
  - `综合评审汇总.html`
  - 导师摘要
  - 最终展示页

核心规则：

- `status` 和 `display` 只能 summarize/display，不改写真源
- 同一慢变量优先只有一个明确真源

## 3. 对象层最小集合

图表和表格密集型项目，优先建立这四个对象文件：

### `objects/figures.json`

每项至少包含：

- `id`
- `figure_no`
- `caption`
- `source_path`
- `page_or_line_anchor`
- `role`
- `can_enter_abstract`
- `can_enter_conclusion`

### `objects/tables.json`

每项至少包含：

- `id`
- `table_no`
- `caption`
- `source_anchor`
- `role`
- `is_primary`

### `objects/citations.json`

每项至少包含：

- `id`
- `claim_anchor`
- `citation_text`
- `citation_type`
- `is_primary_source`

### `objects/assets_manifest.json`

每项至少包含：

- `id`
- `asset_type`
- `source_kind`
- `source_path`
- `output_path`
- `linked_object_ids`

Markdown 台账继续保留，但默认只承担执行面，不再兼任结构化数据库。

## 4. `process_projection`

如果当前项目跨越：

- 多线程
- 多代理
- 多工具
- 多轮交接

就补一个统一接手面：`reviews/process_projection.md`

最小字段固定为：

- `goal`
- `actions`
- `findings`
- `decisions`
- `artifacts`
- `status`
- `next_step`

它是过程投影，不是真源；作用是降低恢复成本，而不是替代上游文件。

## 5. 默认读取顺序

接手时优先按这个顺序：

1. 原始论文和当前底稿
2. 对象层
3. 审阅对象冻结说明
4. 版本冻结与依赖回归台账
5. 审阅工作流和执行状态页
6. 证据型台账
7. HTML、导师摘要和其他展示页

如果项目已经漂移，先判断哪些入口还可信，再按这个顺序读。

## 6. 最小工具链

当前最小推荐组合：

1. `textutil + nl + rg`
   - 建文本底稿和快速定位
2. `scripts/extract_docx_media.py`
   - 从 `DOCX word/media` 抽图
3. `scripts/extract_docx_tables.py`
   - 从 `DOCX` 抽表到 `assets/tables/docx_csv` 并回写 `objects/tables.json`
4. `scripts/extract_docx_citations.py`
   - 从 `DOCX` 抽取正文引用锚点与参考文献条目映射，并回写 `objects/citations.json`
5. `scripts/check_review_workspace.py`
   - 检查工作区合同和对象层
6. `scripts/scan_stale_paths.py`
   - 扫旧绝对路径和迁移漂移
7. `scripts/evaluate_review_toolchain.py`
   - 量化单篇论文的对象层、图表资产、表格可抽取性、引文可抽取性、接手面和路径漂移状态

如果这些工具不可用，也要尽量保留同样的结构合同，而不是直接退回纯聊天记忆。

## 7. 轻量效果评估

结构或工具升级后，至少回看：

1. 建底稿和建图表资产索引的准备时间
2. 新接手者恢复现场的时间
3. 图表/表格/结论的覆盖率
4. 旧值、旧路径、错链和版本漂移的发现率
5. 原子级改稿建议的采纳率

只要这五项没有明显改善，就不应把改动当成成功升级。
