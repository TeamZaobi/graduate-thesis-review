# 方向与边界锚点

这个文件是 `workflow/review-workspace` governed pack 的边界入口。
先读它，再读 `WORKFLOW.md`、`workflow.contract.json`、`rules.contract.json` 和 `objects/`。

## 首批真实使用场景 [scenarios]

- 审查者需要一套受控 workflow，确保“先评审后导师建议”不再只是口头原则。
- 接手已有论文工作区的人，需要快速确认 runtime pack、evidence workspace、notes 和 outputs 的边界关系，而不是从历史对话猜 authority。
- 维护回归与工具链的人，需要一个可被 validator 和 workflow fixture 直接校验的 repo truth pack。

## 首批交付物 [deliverable]

- 一套可复制到单篇论文 runtime pack 的 review-workspace governed pack，包含边界入口、workflow 合同、rules 合同、agent 合同和 objects 合同。

## 用户故事 [user_stories]

### 用户故事 US-1

- 谁在用：首次接手论文审查工作区的人或代理。
- 在什么场景下：需要判断当前请求应留在评审层，还是已经满足进入导师层的前置条件。
- 他/她现在想完成什么：读完 pack 根目录就看清 workflow 的使命层级、主路径和禁止越权边界。
- 为什么这件事对当前阶段重要：如果 review/advice 边界不清，局部改写、导师摘要和学生执行包会继续偷跑到评审之前。
- 这次完成后，用户应该看到什么变化：只靠 pack 入口就能知道这是 review-first workflow，而不是并列的“评审模式 + 改稿模式”。
- 这次明确不包含什么：不要求这里完整展开论文级 notes、display 或所有领域知识细则。

### 用户故事 US-2

- 谁在用：维护 `check_review_workspace.py`、`evaluate_review_toolchain.py` 和 workflow fixtures 的人。
- 在什么场景下：需要确认 repo truth pack 与 paper runtime pack 的合同根是否稳定。
- 他/她现在想完成什么：把 workflow 边界、object refs 和 route/evidence/write/stop checks 固定在一个可回归入口里。
- 为什么这件事对当前阶段重要：如果 truth pack 根本边界不清，后续 drift 检查和 runtime snapshot 都会反复漂移。
- 这次完成后，用户应该看到什么变化：repo truth pack 可以被 validator 校验，并能为 runtime snapshot 提供稳定来源。
- 这次明确不包含什么：不要求这里代替论文级 evidence verdict 或 notes 补充信息。

### 用户故事 US-3

- 谁在用：负责导师层输出治理的人。
- 在什么场景下：需要明确 advisor outputs 只能在 review 完成后进入，并且受 output policy 约束。
- 他/她现在想完成什么：确认 workflow 合同中的 advice 节点、rollback 入口和关键 output refs 没有越权定义。
- 为什么这件事对当前阶段重要：如果高权威输出没有被 pack 边界约束，policy-driven authority 会重新滑回文案承诺。
- 这次完成后，用户应该看到什么变化：advisor outputs 被视为 review 之后的受控下游，而不是默认主路径。
- 这次明确不包含什么：不要求在这个 pack 里直接承载具体导师建议内容。

## 测试用例 [test_cases]

### 测试用例 TC-1

- 对应故事：US-1
- 前提：接手者只打开 `workflow/review-workspace/` 根目录。
- 当：先读 `BOUNDARY.md`，再读 `WORKFLOW.md` 与 `workflow.contract.json`。
- 那么：应能明确看出“先 review 后 advice”的主路径，以及 review/advice 不是并列入口。
- 通过条件：读者不依赖仓库历史，也能说清 workflow 的使命层级和主路径。
- 这次明确不要求：不要求仅靠 `BOUNDARY.md` 理解所有 object 字段语义。
- 失败/越界边界：如果读者仍把 advisor outputs 视为默认首层能力，说明入口边界失效。

### 测试用例 TC-2

- 对应故事：US-2
- 前提：repo truth pack 被用于 validator 和 runtime snapshot。
- 当：运行上游 `validate_governance_assets.py` 校验这个 pack。
- 那么：应能通过边界入口、workflow/rules/agent/object 合同的最小校验。
- 通过条件：缺少边界入口、故事、测试或验收责任人时必须失败；当前 pack 完整时应通过。
- 这次明确不要求：不要求这里直接模拟单篇论文 evidence workspace。
- 失败/越界边界：如果 pack 缺 `BOUNDARY.md` 或边界段落不完整仍然通过，说明边界入口没有进入机器回归。

### 测试用例 TC-3

- 对应故事：US-3
- 前提：pack 已声明 advice 节点、rollback 转移和 advisor/student output refs。
- 当：检查 `workflow.contract.json`、`rules.contract.json` 与 `objects/`。
- 那么：应能确认 advice 是 review 的下游节点，且 rollback 能把高风险建议退回 review。
- 通过条件：不存在把 advisor outputs 定义成独立主路径或绕过 review 的合同形状。
- 这次明确不要求：不要求这里定义论文级 verdict 或具体建议文本。
- 失败/越界边界：如果 advice 可以绕过 review 或没有 rollback 出口，说明 workflow 已越权扩张。

## 非目标 [non_goals]

- 不把 repo truth pack 写成单篇论文 runtime 实例。
- 不在这里承载论文级 notes、evidence verdict 或 display 投影。
- 不让 `BOUNDARY.md` 反过来代替 workflow 合同、rules 合同或 object 合同。

## 质量参考对象 [quality_references]

- 质量标准是“一个可被 validator 和 runtime snapshot 共同消费的 review workflow truth pack”，而不是“尽量把所有知识都塞进 pack 根目录”。
- 这个 pack 的入口解释应始终服务于 review-first、policy-driven outputs 和 runtime snapshot 一致性。

## 验收责任人 [acceptance_owner]

- `graduate-thesis-review` 仓库维护者，或任何负责判断 review-workspace truth pack 是否仍能作为官方 workflow 真源的人。
