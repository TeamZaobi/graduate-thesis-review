# 方向与边界锚点

这个文件是 `workflow/skill-maintenance` governed pack 的边界入口。
先读它，再读 `WORKFLOW.md`、`workflow.contract.json`、`rules.contract.json` 和 `objects/`。

## 首批真实使用场景 [scenarios]

- 维护者需要改 skill 自身的 workflow、脚本、入口文档或 release 资产时，必须走独立维护流程，而不是混入论文审查 runtime。
- 审计者需要判断某轮仓库修改是否具备足够的 audit/design/regression 证据，才允许进入 release。
- 新接手维护工作的人，需要快速看清这个 pack 管的是 skill 维护，不是单篇论文评审。

## 首批交付物 [deliverable]

- 一套用于 skill 自身维护与发版的 governed pack，包含边界入口、维护/放行 workflow 合同、rules 合同、agent 合同和 objects 合同。

## 用户故事 [user_stories]

### 用户故事 US-1

- 谁在用：维护 `graduate-thesis-review` skill 的人或代理。
- 在什么场景下：需要改 repo truth、工具链或入口文档，但不能让维护动作污染论文审查主流程。
- 他/她现在想完成什么：确认本轮修改应该走 maintenance workflow，并留下足够的 audit 证据。
- 为什么这件事对当前阶段重要：如果维护流程和业务流程混层，仓库会再次失去稳定入口。
- 这次完成后，用户应该看到什么变化：repo 级维护与论文级 review runtime 被明确区分。
- 这次明确不包含什么：不要求这里处理单篇论文的 evidence、verdict 或导师建议。

### 用户故事 US-2

- 谁在用：负责 release gate 和发版说明的人。
- 在什么场景下：需要判断当前维护修改能否进入 release，而不是继续停留在 audit/design 阶段。
- 他/她现在想完成什么：确认维护证据已经齐备，release 只在受控条件下发生。
- 为什么这件事对当前阶段重要：如果没有独立 release workflow，仓库维护会继续靠对话记忆和临时判断推进。
- 这次完成后，用户应该看到什么变化：release 决策建立在 maintenance 证据之上，而不是自由讨论之上。
- 这次明确不包含什么：不要求这个 pack 直接产出用户面向的论文审查结果。

### 用户故事 US-3

- 谁在用：回归和治理工具链维护者。
- 在什么场景下：需要验证 skill-maintenance truth pack 仍能被 validator 校验，并作为 repo 级维护边界入口。
- 他/她现在想完成什么：确保边界说明、用户故事、测试用例和验收责任人进入正式 pack，而不是停留在 release note。
- 为什么这件事对当前阶段重要：如果入口边界不进 pack 根目录，长期维护时最先漂移的就是维护流程本身。
- 这次完成后，用户应该看到什么变化：skill-maintenance pack 可被独立校验，并持续承担 repo 级维护入口角色。
- 这次明确不包含什么：不要求这里覆盖全部未来维护分支或复杂发布策略。

## 测试用例 [test_cases]

### 测试用例 TC-1

- 对应故事：US-1
- 前提：维护者只打开 `workflow/skill-maintenance/` 根目录。
- 当：先读 `BOUNDARY.md`，再读 `WORKFLOW.md` 与 `workflow.contract.json`。
- 那么：应能明确知道这个 pack 管 skill 维护，不管论文评审 runtime。
- 通过条件：不看仓库历史，也能分清 maintenance workflow 与 review workflow 的边界。
- 这次明确不要求：不要求仅靠 `BOUNDARY.md` 理解所有 release 对象字段。
- 失败/越界边界：如果读者仍把这个 pack 理解成论文评审流程入口，说明维护边界没有立住。

### 测试用例 TC-2

- 对应故事：US-2
- 前提：维护节点与 release 节点都已在 workflow 合同中声明。
- 当：检查 `workflow.contract.json`、`rules.contract.json` 与 `objects/`。
- 那么：应能看到 release 只能在 maintenance evidence 准备好之后发生。
- 通过条件：不存在“无 audit evidence 直接 release”的合同形状。
- 这次明确不要求：不要求在这个 pack 中引入额外多分支发布策略。
- 失败/越界边界：如果 release 能绕过 maintenance 证据直接发生，说明治理边界失效。

### 测试用例 TC-3

- 对应故事：US-3
- 前提：pack 被上游 `validate_governance_assets.py` 校验。
- 当：运行 validator。
- 那么：应能通过边界入口、workflow/rules/agent/object 合同的最小要求。
- 通过条件：缺少边界入口、故事、测试或验收责任人时失败；当前 pack 完整时通过。
- 这次明确不要求：不要求这个 pack 直接携带 runtime state 实例。
- 失败/越界边界：如果缺 `BOUNDARY.md` 或测试边界不完整仍然通过，说明 maintenance workflow 没有正式入轨。

## 非目标 [non_goals]

- 不把 skill-maintenance pack 写成论文审查运行包。
- 不在这里承载单篇论文的 evidence workspace 或 outputs。
- 不让 `BOUNDARY.md` 取代维护 workflow 合同、rules 合同或 objects 合同。

## 质量参考对象 [quality_references]

- 质量标准是“一个能稳定承接 repo 级维护与 release 证据的 maintenance workflow truth pack”，而不是“把所有治理讨论都堆进入口页”。
- 这个 pack 的入口解释应始终服务于 repo maintenance / audit / release 三件事，不反向污染 review runtime。

## 验收责任人 [acceptance_owner]

- `graduate-thesis-review` 仓库维护者，或任何负责判断 skill-maintenance truth pack 是否仍可作为官方维护流程入口的人。
