# Beacon 调研：业务流程图与状态机文档设计

> 日期：2026-05-21
> 调研版本线：`v1.4.8`
> 状态：仅调研
> 范围：面向后续 `beacon-change -> prd -> user-story -> test-case` 的版本级人类可读 requirement projection（需求投影）
> 来源引用：
> - `docs/beacon/global-boundaries.md`
> - `skills/beacon/beacon-doubt-review/SKILL.md`
> - `skills/beacon/references/business-flow-checklist.md`
> - `skills/beacon/references/state-machine-checklist.md`
> - `docs/beacon/v1.4.7/research/beacon-vnext-ui-ux-externalization-and-version-requirement-visualization-analysis.md`
> - `docs/brainstorms/2026-05-21-beacon-brainstorm-vnext-externalize-ui-ux-and-add-version-level-requirement-visualization.md`

---

## 1. 调研目标

本文定义 Beacon 应如何设计两类缺失的版本级文档：

1. business flow documents（业务流程文档）
2. state-machine documents（状态机文档）

目标不是增加装饰性图表。
目标是定义面向 freeze 的人类可读 projection，让操作者不用逐行阅读所有 PRD、user-story、test-case 文件，也能理解一个完整版本包。

本文不是 canonical truth。
它是后续 `v1.4.8` 规划线中 `beacon-change` transaction 的上游调研补充。

## 2. Doubt Review（怀疑审查）起点

看起来很有吸引力但证明不足的主张是：

> 如果 Beacon 增加 business flow 和 state-machine 图，人类就能更好理解完整版本包。

这个主张方向上成立，但还不完整。

最弱的证明点在于：

- 图可能变成装饰，而不是 freeze-facing projection
- 图可能重复实现细节，而不是澄清业务闭环
- 图可能偏离 `prd / user-story / test-case`
- 图可能塞入过多细节，反而无法服务人类理解

因此问题不是“加图”。
真正的问题是“定义能显著改善 requirement closure 的图文档契约”。

## 3. Doubt Review（怀疑审查）最终结论

收敛判断是：

> Beacon 应该补充这两类图，但不能允许它们被随意绘制。

实现前必须先冻结三条设计原则：

1. 版本级业务流程图只解释业务闭环，不解释实现细节
2. 版本级状态机图只解释 stable closure states，不解释页面或 widget 交互细节
3. 每个图文档都必须声明 truth bindings，否则它只是 commentary，不是 freeze-facing projection

这三条原则是防止图表工作滑向模糊说明或重复噪声的最低边界。

## 4. 设计原则 1：业务流程图解释业务闭环

### 4.1 它们用来回答什么

Business flow（业务流程）文档应回答：

- 这个版本闭合了什么业务 / 问题循环
- 主要的 actor-facing path 是什么
- 关键分支与 handoff 出现在何处
- 什么状态算完成

### 4.2 它们不能变成什么

它们不能变成：

- implementation sequence charts
- internal module call graphs
- technical task checklists
- 完整异常百科

如果 flow 变得偏实现，它就不再服务版本级人类理解。

### 4.3 最低结构要求

每个版本级 business flow 文档应包含：

1. `purpose`
   - 用一句短话说明图为什么存在
2. `scope`
   - 覆盖版本包中的哪一部分
3. `actors`
   - 只列版本相关的最小 actor 或 system 集合
4. `start state`
   - flow 由什么触发
5. `main path`
   - 主要业务步骤序列
6. `major branches`
   - 只保留会实质改变 route、promise 或 completion 的分支
7. `terminal outcomes`
   - 对版本 closure 有意义的结束状态
8. `truth bindings`
   - 该 flow 投影自哪些 PRD / user-story / test-case artifact

### 4.4 压缩规则

Flow 应保持大纲层级。

推荐约束：

- 5 到 9 个 main path nodes
- 只保留最高价值的 branches
- 图后只附少量文字

如果需要更多细节，这些细节应回到 truth surfaces 或更低层补充文档，而不是塞进顶层版本业务流程图。

## 5. 设计原则 2：状态机图解释 Stable Closure States（稳定闭合状态）

### 5.1 它们用来回答什么

State-machine（状态机）文档应回答：

- closure object 可以处于哪些 stable states
- transition 如何发生
- 哪些 transition 被阻断或非法
- transition 边界上哪些 side effects 重要

### 5.2 它们不能变成什么

它们不能变成：

- page interaction state diagrams
- UI widget visibility charts
- transient action logs
- 把普通 workflow swimlane 伪装成 state machine

版本级 state machine 首先不是 UI 状态模型。
它首先是 requirement / business closure 的状态模型。

### 5.3 推荐状态对象

默认研究对象应是：

```text
version-level requirement closure object
```

这样可以让 state machine 与 Beacon 的核心身份保持一致。

### 5.4 候选 stable states

初始研究状态族为：

- `drafted`
- `prd_frozen`
- `user_story_frozen`
- `test_case_frozen`
- `requirement_clarity_pass`
- `freeze_pass`
- `implement_in_progress`
- `qa_blocked`
- `qa_pass`
- `release_blocked`
- `release_ready`
- `refreeze_required`
- `archived`

这些还不是 `v1.4.8` canonical truth。
它们只是最低研究候选集。

### 5.5 最低结构要求

每个版本级 state-machine 文档应包含：

1. `state object`
   - 状态到底属于什么对象
2. `stable states`
   - 只列命名状态，不允许隐藏隐含状态
3. `transition rules`
   - 什么导致状态迁移
4. `blocked / invalid transitions`
   - 什么必须 fail closed
5. `transition side effects`
   - 进入某状态的关键后果
6. `truth bindings`
   - 哪些 PRD / user-story / test-case artifact 支撑这个状态模型

### 5.6 压缩规则

不要把每个微小 transition 都塞进状态机。

判断标准是：

> 读完 state machine 后，操作者应知道版本现在在哪里、下一步安全 route 是什么、哪些跳转被禁止。

如果某个细节无法改善这个判断，它大概率应该放到其他地方。

## 6. 设计原则 3：每张图都必须声明 Truth Bindings（真相绑定）

这是最硬的边界，也是最重要的边界。

没有 truth bindings：

- 图只是 commentary
- drift 无法检查
- freeze-facing 价值很弱
- 操作者可能把视觉清晰误认为 requirement closure

因此每个 business flow 或 state-machine 文档都应包含固定区块：

```text
truth_bindings:
- prd_refs
- user_story_refs
- test_case_refs
- coverage_notes
- out_of_scope_notes
```

这既保留 Beacon 的单一 truth 模型，也允许图真正变得有用。

## 7. 与 PRD / User-Story / Test-Case 的关系

三类 truth surface 继续保持原有职责：

- PRD = promise / goals / scope / boundaries
- User Story = actor goals / scenarios / acceptance criteria
- Test Case = scenario coverage / verification contract

新增图文档不替代这个结构。
它们只是为了人类理解而投影这个结构。

关系应是：

```text
PRD
-> 解释为什么做、承诺什么

User Story
-> 解释谁在什么场景中需要什么结果

Test Case
-> 解释这些场景如何被验证

Business Flow
-> 解释版本级业务路径

State Machine
-> 解释版本级 closure 状态逻辑
```

## 8. 推荐文档形态

### 8.1 Business flow document（业务流程文档）

建议文件名模式：

```text
docs/beacon/<version>/research/<feature-or-version>-business-flow.md
```

建议章节：

- purpose
- scope
- actors
- main flow diagram
- branch notes
- terminal outcomes
- truth bindings

### 8.2 State-machine document（状态机文档）

建议文件名模式：

```text
docs/beacon/<version>/research/<feature-or-version>-state-machine.md
```

建议章节：

- state object
- state diagram
- transition rules
- blocked / invalid transitions
- transition side effects
- truth bindings

### 8.3 Requirement-map document（需求映射文档）

虽然本文重点是 flow 和 state，但如果后续配套一个 requirement map 文档，这些图会更易用：

- version feature list
- PRD / user-story / test-case ownership map
- projection coverage matrix

该文档值得推荐，但不是本文调研的必需项。

## 9. 成功标准

这些新文档只有在能让人类操作者回答以下问题时才算成功：

- 这个版本闭合了什么业务循环
- main path 是什么
- 主要 branches 在哪里
- 存在哪些 states
- 哪些 transitions 被阻断
- 哪些 truth artifacts 支撑了这张图

如果图无法回答这些问题，它还不是 freeze-facing projection。

## 10. 下一步路由

推荐下一跳：

1. `beacon-change`
2. 冻结以下文档契约：
   - business flow
   - state machine
   - truth bindings
3. 编译进入：
   - PRD
   - user-story
   - test-case

只有在这些 truth surfaces 存在之后，implementation 或 automation 才应消费新的 projection contract。
