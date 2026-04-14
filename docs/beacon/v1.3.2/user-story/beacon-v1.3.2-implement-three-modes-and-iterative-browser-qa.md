# 用户故事：Beacon v1.3.2 implement 三模式与迭代浏览器 QA 闭环

**Feature**: `beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa`  
**Version**: `v1.3.2`  
**Date**: `2026-04-14`  
**Status**: `planning line`

## US-001：作为实现负责人，我希望 `implement` 有明确的 `single` 模式，以便小范围任务不必进入多代理执行

**验收标准**：

- 用户可以显式进入 `single` 模式
- `single` 只使用单进程执行面
- `single` 不创建 team worker lanes、tmux pane 或 HUD
- `single` 仍然对接正式 review / qa / gate

## US-002：作为实现负责人，我希望 `implement` 有明确的 `team` 模式，以便多文件 feature 可以使用 bounded 多代理并行分工

**验收标准**：

- 用户可以显式进入 `team` 模式
- `team` 进入 bounded multi-agent runtime
- `team` 支持 role reports、worker evidence、tmux / HUD
- `team` 的正式 writeback 仍由 Beacon stage owner 完成

## US-003：作为交付负责人，我希望 `ralph` 成为围绕 `implement + qa` 的持续闭环，而不是新的实现执行器

**验收标准**：

- `ralph` 不是第四种独立实现器
- `ralph` 驱动 `implement -> review -> qa -> gate -> repair`
- `ralph` 只围绕 `implement + qa` 推进，不直接改写 `prd / user-story / test-case`
- `ralph` 必须有明确终态

## US-004：作为 QA 负责人，我希望 `qa` 成为与 `implement` 对应的第二执行面，而不是一次性收尾动作

**验收标准**：

- `qa` 负责浏览器验收、边界发现、结构推演与 repair handoff
- `qa` 必须与 `implement` 共同构成闭环
- `qa` 的结果必须能影响下一轮 implement / ralph 决策

## US-005：作为 QA 负责人，我希望 QA 始终围绕冻结的 `prd / user-story / test-case` 顺序推进

**验收标准**：

- QA 的正式输入必须是冻结的 `prd / user-story / test-case`
- QA 推进顺序必须体现冻结材料的顺序关系
- QA 不得脱离冻结材料自由扩 scope

## US-006：作为 QA 负责人，我希望 Beacon 能围绕目标项目启动真实浏览器环境进行验收

**验收标准**：

- QA 必须支持浏览器原生执行
- 至少纳入 `browser-cli`、`agent-browser`、`pageagent`、`browser-use`
- 必要时可兼容 `playwright` / `cypress`
- QA 的产品语义应是“浏览器化项目验收”，而不是“runner 列表”

## US-007：作为 QA 负责人，我希望 QA 按轮次顺序迭代，而不是一次性把所有 case 粗暴跑完

**验收标准**：

- QA 必须支持顺序推进
- QA 必须支持多轮迭代
- 每轮可以根据上一轮发现调整下一轮验证重点
- 每轮必须保留自己的 summary 与 evidence

## US-008：作为 QA 负责人，我希望每一轮 QA 都带来新的 auto research 增量

**验收标准**：

- 每轮 QA 至少新增一种价值：
  - 新边界
  - 新异常路径
  - 新页面状态
  - 新结构推演
  - 新 coverage closure
  - 新 repair handoff
- 如果没有新增价值，该轮不应视为有效进展

## US-009：作为产品负责人，我希望 QA 能持续反馈边界信息和结构推演，帮助逐轮打磨功能产品

**验收标准**：

- QA 每轮都能反馈当前覆盖边界与未覆盖边界
- QA 每轮都能输出新的页面/流程结构推演
- 这些信息必须进入 QA evidence 或 repair handoff
- 目标是逐轮打磨功能正确性、验收完整性和产品边界清晰度

## US-010：作为运行负责人，我希望 `status/help` 明确显示当前 mode、轮次和 browser runner，以便我知道现在系统在做什么

**验收标准**：

- `status/help` 至少显示当前 mode
- `status/help` 至少显示当前轮次
- `status/help` 至少显示当前 browser runner / executor
- `status/help` 至少显示 blocker 与推荐下一步

## US-011：作为 Beacon 人类使用者，我希望 `v1.3.2` 继续沿袭极简心智工作流，而不是因为 subagent 能力增强被迫记更多命令

**验收标准**：

- 人类主流程仍然保持 `prd -> user-story -> test-case -> implement -> qa -> release`
- 不得因为 team/subagent 能力增强而新增新的公开一级主命令
- 人类不应被迫理解 team/subagent/precheck/runtime 细节才能继续主流程

## US-012：作为 Codex/Claude 宿主内的 Beacon 使用者，我希望 Beacon 作为 skill 调用宿主原生 subagent/team 能力，而不是自己桥接新的外部执行器

**验收标准**：

- Codex 路径必须使用 Codex 宿主原生 subagent/team 能力
- Claude 路径必须使用 Claude 宿主原生 subagent/team 能力
- `omx` 只作为设计借鉴，不作为 `v1.3.2` 正式目标运行时

## US-013：作为操作者，我希望 team subagent 的两段预检查默认内嵌在 `implement/qa` 里，而不是变成我要手动记住的额外步骤

**验收标准**：

- `runtime-readiness` 与 `delegation-readiness` 默认内嵌在 `implement/qa`
- `doctor` 只作为显式诊断与修复面
- 预检查失败时，应给出极简阻断原因与推荐下一步，而不是把内部复杂度直接暴露给人类

## US-014：作为平台维护者，我希望宿主上下文保持唯一，只判断“当前宿主能否稳定调用原生 subagent/team”，而不是引入多运行时选择叙事

**验收标准**：

- `v1.3.2` 只讨论当前宿主是否为 Codex 或 Claude
- 不讨论同一轮执行中在 Codex/Claude/OMX 之间做选择
- Beacon 不应扩展成多运行时桥接调度器

## Acceptance Criteria Matrix

| ID | Theme | Acceptance Criteria |
|----|-------|---------------------|
| AC-001 | implement-single | `implement` 必须支持显式 `single` 模式，单进程执行代码实现，不启动 team worker lanes、tmux pane 或 HUD，且仍进入正式 review / qa / gate。 |
| AC-002 | implement-team | `implement` 必须支持显式 `team` 模式，进入 bounded multi-agent runtime，生成 role reports、worker evidence、tmux / HUD，并保持正式 writeback 由 Beacon stage owner 完成。 |
| AC-003 | ralph-closure | `ralph` 必须只围绕 `implement + qa` 闭环推进，不得直接改写冻结的 `prd / user-story / test-case`，并具备明确终态。 |
| AC-004 | qa-execution-plane | `qa` 必须成为与 `implement` 对应的第二执行面，负责浏览器验收、边界发现、结构推演与 repair handoff，而不是一次性收尾动作。 |
| AC-005 | frozen-input-order | `qa` 必须围绕冻结的 `prd / user-story / test-case` 顺序推进场景执行，不得脱离冻结材料自由扩 scope。 |
| AC-006 | browser-family | `qa` 必须围绕目标项目启动真实浏览器环境，并正式纳入 `browser-cli`、`agent-browser`、`pageagent`、`browser-use` 这类 browser execution family。 |
| AC-007 | iterative-qa | `qa` 必须支持顺序推进和多轮迭代，每轮可根据上一轮发现调整下一轮 browser scenario 的优先级和执行重点。 |
| AC-008 | auto-research-delta | 每轮 `qa` 都必须带来新的 auto research 增量，例如新边界、新页面状态、新异常路径、新 coverage closure 或新的 repair handoff。 |
| AC-009 | boundary-feedback | `qa` 每轮必须输出边界信息、流程结构推演和未覆盖区域说明，这些信息必须进入 QA evidence、repair handoff 或 Ralph next-action 决策。 |
| AC-010 | product-polish-loop | 多轮 `qa` 的目标必须是逐轮打磨功能正确性、验收路径完整性和产品边界清晰度，而不是重复跑同一套页面脚本。 |
| AC-011 | ralph-stop-states | `ralph` 必须至少支持 `release_ready`、`human_blocked`、`budget_exhausted` 三类终态，并基于正式 review / qa / gate 结果决定是否继续。 |
| AC-012 | observability | `status/help` 必须显式显示当前 mode、当前轮次、当前 browser runner / executor、当前 blocker 与推荐下一步。 |
| AC-013 | minimal-human-surface | `v1.3.2` 必须继续沿袭极简人类主流程，保持 `prd -> user-story -> test-case -> implement -> qa -> release` 作为稳定主心智面。 |
| AC-014 | no-new-public-team-surface | 不得因 team/subagent 能力增强而新增新的公开一级主命令，也不得要求人类显式操作 team/subagent/precheck。 |
| AC-015 | host-native-subagents | Beacon 作为 skill 运行时，Codex/Claude 路径必须调用宿主原生 subagent/team 能力，`omx` 只作为借鉴样本，不作为正式目标运行时。 |
| AC-016 | embedded-prechecks | `runtime-readiness` 与 `delegation-readiness` 必须默认内嵌在 `implement/qa`，而不是成为人类主流程中的额外命令负担。 |
| AC-017 | minimal-human-output | precheck / delegation / blocker 对人类必须只输出极简原因、推荐下一步与 fallback；复杂细节应保留给机器输出。 |
| AC-018 | unique-host-context | `v1.3.2` 只讨论当前宿主是否支持原生 subagent/team，不引入多运行时选择或桥接叙事。 |
