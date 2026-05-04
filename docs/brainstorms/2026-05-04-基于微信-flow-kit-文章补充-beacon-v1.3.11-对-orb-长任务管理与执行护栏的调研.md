# Beacon Brainstorm

## prompt_summary
基于微信文章《每个ide都可以使用！！我融合了superpowers、OpenSpec、spec-kit、GSD、gstack、claude-task-master写一套可控Ai开发规范流程》，补充 Beacon v1.3.11 对 orb 方向的调研结论。目标不是把文章原样转存，而是提炼其中对 `Beacon requirement truth -> orb sibling runtime` 结构真正有价值的机制，尤其是长任务管理、执行护栏、change identity、fresh subagent、plan-check loop、老项目边界控制等内容。

- version: `v1.3.11`
- mode: `project-evolution`
- feature: ``

## 背景来源

- Beacon 当前版本材料：`docs/beacon/v1.3.11/`
- 外部文章：
  - 标题：`每个ide都可以使用！！我融合了superpowers、OpenSpec、spec-kit、GSD、gstack、claude-task-master写一套可控Ai开发规范流程`
  - 链接：`https://mp.weixin.qq.com/s/6NSD1WoKRXTHR0exWBKXtg`
  - 读取时间：`2026-05-04`

## 核心判断

这篇文章对 Beacon 本身的直接价值，不在于“再多一个 AI 工作流”，而在于它把几个不同开源体系的执行护栏明确化了。

对 `Beacon v1.3.11` 来说，这篇文章强化的是：

> Beacon 应继续作为 requirement truth authority，而未来 sibling runtime（如 orb）必须把长任务执行护栏、运行隔离和可管理性做成正式运行能力，而不是只靠 prompt 约束。

## 可吸收机制

### 1. CHANGE 作为一等公民

文章吸收 OpenSpec 的核心点是：

- 每次变更独立目录
- `propose -> apply -> archive`

对 Beacon 的启发：

- requirement truth 之外的执行层，不应把长任务理解为“继续对话”
- 更合理的对象是：`change / objective / run`
- 这强化了 Beacon 之前对 `ExecutionObjective` 与 `closure candidate` 的判断

### 2. context hygiene

文章反复强调：

- 阶段间清窗
- 工件驱动
- fresh context

对 Beacon 的启发：

- `implement / qa / release` 外侧的 runtime，不应依赖不断膨胀的单线程上下文
- 长任务必须有正式 `thread / run / workspace` 边界

### 3. fresh subagent

文章吸收了 GSD 的：

- 每任务一个 fresh subagent

对 Beacon 的启发：

- 后续 sibling runtime 不应只支持“一个 agent 一直聊到底”
- 任务拆解后，应默认具备执行隔离能力

### 4. plan-checker / verify loop

文章提到：

- AI 自检不通过就继续修，直到通过

对 Beacon 的启发：

- 长任务闭环不是单纯 `run completed`
- runtime 层需要支持 `verify / retry / repair / review` 的中间循环

### 5. 工具按需加载

文章吸收了 task-master 的：

- 工具分层加载

对 Beacon 的启发：

- 后续 orb 之类 runtime 的 tool profile 不应一股脑打开
- 更合理的是：
  - project policy
  - objective policy
  - task-scoped tool window

### 6. 老项目护栏

文章里最有价值的部分之一，是它给老项目加的 6 条护栏：

1. 入场扫描
2. 架构对齐
3. 边界约束
4. 破坏性变更门槛
5. 既有抽象复用扫描
6. 视觉语汇对齐

对 Beacon 的启发：

- 长任务可管理，不只意味着“看见 run 状态”
- 还意味着 runtime 能表达并执行这些 guardrail

## 对 Beacon v1.3.11 的更新结论

这篇文章不会改变 Beacon 的主定位，但会强化三条原结论：

### 1. Beacon 不应吞掉 runtime

这篇文章本身更像：

- Markdown workflow kit
- prompt + docs + guardrails

它不是 authoritative runtime state，也不是 operator plane。

所以它反而证明：

- Beacon 应继续守 truth
- runtime 层应独立建模

### 2. orb 的“长任务可管理”必须包含护栏

之前对 orb 的判断主要集中在：

- thread / run / workspace
- operator surface
- TypeScript first

这篇文章补充后，更完整的判断应是：

- orb 不只是 long-running run host
- orb 还应承接：
  - change identity
  - guardrail policies
  - verify loop
  - fresh worker isolation
  - destructive change gates

### 3. Beacon 与 orb 的桥接应更强调 contract + guardrail

未来 Beacon -> orb 的桥接不应只传：

- `RequirementPackageRef`
- `ExecutionObjective`

还应逐步考虑：

- project guardrails
- write boundary hints
- destructive change policies
- acceptance hook set

## 收敛结论

这篇微信文章对 Beacon v1.3.11 的价值，不在于让 Beacon 改做 `flow-kit`，而在于为 orb 方向补了一个重要维度：

> 长任务“可管理”不只是状态可见，而是执行护栏、验证循环、任务隔离和恢复动作都必须成为正式运行能力。

因此，Beacon 这边应保留的结论是：

1. Beacon 继续做 requirement truth authority
2. runtime sibling project 继续独立立项
3. orb 的 runtime substrate 除了 run/workspace 状态机，还应把 guardrail management 一并纳入
