# 审查运行架构与资产管线

当目标是提升**具体毕业论文评审工作**的效率和效能时，加载此文件。

它不替代方法学审查细则，而是回答三件事：

1. 事实、执行、状态和展示分别落在哪
2. 图、表、引文和路径怎么从“手工记忆”升级成结构化资产
3. 多线程、多代理、多工具时，怎么降低接手和恢复成本

## 当前 Canonical 映射

当前实现不再把 `reviews/` 当成 paper workspace 的 authority 中心。

paper-level canonical 家族固定为：

1. `governance/review-workspace-pack/`
   - machine-readable runtime 真源
2. `evidence/`
   - 事实、coverage、verdict、limitations 真源
3. `outputs/`
   - 派生输出
4. `notes/`
   - legacy manifest 与按需人工说明

兼容说明：

1. `reviews/` 仍保留历史 alias
2. 本文后续如继续出现 `reviews/...` 路径，默认都可映射到 canonical 文件
3. advice outputs 的最终授权已从 legacy `release_gate` 切到 `review-verdict + output policy`

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
  - 原论文 `DOCX/WPS/PDF`
  - `paperXX_docx_lines.txt`
  - `objects/figures.json`
  - `objects/tables.json`
  - `objects/citations.json`
  - `objects/assets_manifest.json`
  - 原始数据、分析导出和复算结果
- `execution_object`
  - 各类台账、审计表、改稿卡片
  - `notes/legacy-review-manifest.json`
  - `notes/评审闭环与放行判断.md`
- `status_projection`
  - `governance/review-workspace-pack/status.projection.json`
  - `students/导师` Markdown 或其他派生摘要
- `display_projection`
  - `综合评审汇总.html`
  - `display/问题清单页.html`
  - `display/完整评审页.html`
  - `display/学生执行页.html`
  - `display/导师汇报页.html`

核心规则：

- `status` 和 `display` 只能 summarize/display，不改写真源
- 同一慢变量优先只有一个明确真源
- 对 `Word / WPS` 这类所见即所得原稿，默认分清三层：`authoring_truth_source`、`visual_truth_source`、`evidence_asset`
- `authoring_truth_source` 是学生实际编辑的作者文件；`visual_truth_source` 是本轮受控渲染权威；`page_renders/`、裁图和拼图只是审计资产
- 是否允许进入 `导师/学生` 输出，当前机器可读真源默认放在 `evidence/review-verdict.json + knowledge/output-policies/`
- `notes/评审闭环与放行判断.md` 与 `notes/legacy-review-manifest.json.release_gate` 当前只保留 readiness 等 legacy 兼容语义，不要再把它们当成 advice outputs 的第一推进器
- 学生 / 导师 Markdown 默认是主 `status_projection`；对应 HTML 子页是它们的 `display_projection`，不要让两套投影各写各的

## 3. 对象层最小集合

图表和表格密集型项目，优先建立这四个对象文件：

### `objects/figures.json`

每项至少包含：

- `id`
- `figure_no`
- `caption`
- `source_kind`
- `source_path`
- `page_or_line_anchor`
- `role`
- `can_enter_abstract`
- `can_enter_conclusion`

图件来源类型至少区分：

- `docx_media`：原始图件作为二进制图片存放在 `DOCX word/media`
- `shape_rendered`：图件本体来自 `Word shape / 文本框 / SmartArt / 分组绘图 / 版式渲染`

补充约束：

- `source_kind` 表示图件原始来源类型，不表示当前证据文件是怎么取得的
- `source_path` 表示当前默认引用的证据资产路径；如果图件属于 `shape_rendered`，这里可以指向页面渲染图、重导出页图或审计文件，但不能因此把 `source_kind` 改写成 `page_render_capture`
- 对 `shape_rendered` 图件，建议补 `source_paths`、`status_note`、`render_chain_status` 或 `requires_render_audit`

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

字段边界：

- `source_kind`：原始来源类型，当前至少区分 `docx_media`、`shape_rendered`
- `asset_type`：当前证据资产的取得方式，当前至少区分 `docx_media_extract`、`page_render_capture`、`zoom_crop`

约束：

- 不要把 `page_render_capture` 或历史兼容值 `pdf_page_capture` 混写成 `source_kind`
- 对 `docx_media_extract`，`source_path` 可以是 `word/media/image7.png` 这类 `DOCX` 成员路径，并配合 `source_docx` 使用
- 对 `page_render_capture`，建议额外记录 `render_engine` 与 `render_authority`，例如 `word_native`、`wps_native`、`word_web`、`pdf_export_snapshot`
- 对 `shape_rendered` 图件，`assets_manifest.json` 应允许同时登记“页面渲染证据”和“审计衍生资产”，而不是假装它们来自 `word/media`

Markdown 台账继续保留，但默认只承担执行面，不再兼任结构化数据库。

## 4. `process_projection`

如果项目跨越多线程、多代理、多工具或多轮交接，就补一个统一接手面：`notes/process_projection.md`。

最小字段固定为：`goal / actions / findings / decisions / artifacts / status / next_step`。

它是过程投影，不是真源；作用只是降低接手和恢复成本。不要把 `next_step` 直接当作“已经放行到下一阶段”的依据。

另补三个 machine-readable 锚点：

- `governance/review-workspace-pack/workflow.state.json`
- `governance/review-workspace-pack/workflow.events.jsonl`
- `evidence/review-verdict.json`

`notes/legacy-review-manifest.json` 仍保留 thesis-specific 补充字段，但不再是长期唯一 runtime 真源。

## 5. 默认读取顺序

接手时优先按这个顺序：

1. 原始论文和当前底稿
2. 对象层
3. `governance/review-workspace-pack/`
4. `evidence/review-verdict.json`
5. `notes/legacy-review-manifest.json`
6. 审阅对象冻结说明
7. 版本冻结与依赖回归台账
8. `评审闭环与放行判断.md`
9. 审阅工作流和执行状态页
10. 证据型台账
11. HTML、导师摘要和其他展示页

如果项目已经漂移，先判断哪些入口还可信，再按这个顺序读。

## 6. 最小工具链

当前最小推荐组合：

1. `textutil + nl + rg`
   - 建文本底稿和快速定位
2. `scripts/render_docx_with_word.py`
   - 在 macOS 上优先调用 `Word` 原生 PDF 导出，再用 `gs` 固化到 `assets/page_renders/`
   - 默认通过常驻 daemon 复用同一个 `Word` 控制进程，降低重复授权和重复冷启动成本
   - 这是当前默认的稳健路线
3. `scripts/extract_docx_media.py`
   - 只从 `DOCX word/media` 抽取 `docx_media` 图件，并回写带 `source_kind = docx_media` 的资产清单
4. `scripts/extract_docx_tables.py`
   - 从 `DOCX` 抽表到 `assets/tables/docx_csv` 并回写 `objects/tables.json`
5. `scripts/extract_docx_citations.py`
   - 从 `DOCX` 抽取正文引用锚点与参考文献条目映射，并回写 `objects/citations.json`
6. `scripts/check_review_workspace.py`
   - 检查工作区合同、模板污点和 `READY / PARTIAL / BLOCKED` gate
7. `scripts/scan_stale_paths.py`
   - 扫旧绝对路径和迁移漂移
8. `scripts/evaluate_review_toolchain.py`
   - 量化单篇论文的对象层、图表资产、表格可抽取性、引文可抽取性、接手面和路径漂移状态

如果这些工具不可用，也要尽量保留同样的结构合同，而不是直接退回纯聊天记忆。

## 7. 轻量效果评估

结构或工具升级后，只需回看三件事：准备时间是否下降、接手恢复是否更快、图表/表格/结论覆盖率与漂移发现率是否上升。

如果这些指标没有明显改善，就不要把新增文件和脚本当成有效升级。
