# Research: Beacon v1.3.2 职责优化与 execution family 收敛分析

**Date**: 2026-04-14  
**Method**: 基于职责 brainstorm 收敛到 `v1.3.2` 规划线  
**Purpose**: 把 `implement / qa / ralph` 的产品职责、运行时职责与 truth ownership 再讲清楚，避免 `v1.3.2` 被误读成“更通用的 agent runtime 扩张”。

---

## 1. Imported problem statement

围绕 `v1.3.2` 当前主题，真正需要优化的不是“新增多少 runner”，而是职责口径。

当前主要存在四类职责混淆：

1. **执行模式名词分裂**
   - `native-single`
   - `codex-subagents`
   - `team-run`
   - `ralph-bridge`

   这些名字分别带着实现细节、命令形态和历史桥接语义，用户难以直观看懂“现在到底是在单进程执行、team 执行，还是 Ralph 持续推进”。

2. **运行时职责与产品职责混叠**
   - 一部分语义在谈 runner
   - 一部分语义在谈 team surface
   - 一部分语义在谈持续交付闭环

   结果是源码知道自己在干什么，人类却不容易稳定复述系统职责。

3. **QA 容易被误解成附属测试步骤**
   - 实际上 QA 已经承担：
     - 浏览器原生验收
     - coverage / blocker 判断
     - repair handoff
     - autoresearch 增量
   - 但目前口径仍容易被理解成 “implement 后顺手跑一下测试”。

4. **Ralph 角色边界还不够清楚**
   - 它不应是新的 truth owner
   - 也不应是新的低层执行器
   - 它应是包在 `implement + qa` 外层的闭环控制器

因此，`v1.3.2` 应收敛的不是更多能力名词，而是：

> 让系统、文档和命令面都能统一回答：  
> Beacon 在这一条版本线上，谁持有 truth，谁负责执行，谁负责持续推进，谁负责学习回写。

---

## 2. 职责优化后的核心判断

`v1.3.2` 应明确冻结以下判断：

1. **Beacon 仍然不是通用多代理运行时。**
2. **三模式只正式作用于 `implement` 与 `qa`。**
3. **`single / team / ralph` 是同一 execution family 的三种模式，不是三套产品。**
4. **formal truth 仍由 stage owner 持有，而不下放给 worker 或 Ralph。**
5. **QA 是第二执行面，不是 implement 的附属尾步骤。**
6. **learning / memory / rewrite 仍是受控回写与判断增强面，不得变成第二套 truth plane。**

这意味着 `v1.3.2` 的主问题不是“如何更自动”，而是：

> 如何在不扩张产品边界的前提下，把 `implement + qa + ralph` 的职责重新切齐。

---

## 3. 建议分层：五层职责模型

建议把 `v1.3.2` 的职责口径统一成以下五层。

### Layer 1：Truth & governance owner

这一层继续由正式阶段持有：

- `think`
- `user-story`
- `prd`
- `test-case`
- `freeze`
- `review`
- `gate`
- `release`

它们负责：

- requirement truth
- frozen baseline
- canonical writeback
- release decision

它们**不负责**：

- 并行 worker 调度
- 持续穷尽 loop
- 浏览器执行细节

一句话：

> 这一层负责“什么算真相”，不负责“怎样跑得更快”。

---

### Layer 2：Execution family selector

这一层主要落在：

- `implement`
- `qa`

它们在 `v1.3.2` 中要做的，不只是发命令，而是**选择执行模式**：

- `single`
- `team`
- `ralph`

这里的职责是：

- 判断当前 feature 更适合哪种模式
- 物化 plan / contract / handoff / status 入口
- 明确下一步该进入哪个正式阶段

它们**不应该**：

- 直接充当 generic launcher shell
- 为 requirement 阶段扩出并行执行模式

一句话：

> 这一层负责“进入哪种执行模式”，不直接拥有 truth，也不应无限扩张命令面。

---

### Layer 3：Execution runtime

这一层承载 `single` 与 `team`：

#### `single`

- 单进程
- 单 owner
- 最小执行面
- 不开 worker lane

#### `team`

- bounded worker lanes
- planner / implementation-architect / implementer / reviewer / tester
- HUD / tmux / role reports / run-scoped artifacts
- implement / qa 上下文隔离

这一层负责：

- 执行
- 落 run-scoped evidence
- 形成 handoff 和 role artifacts

这一层**不负责**：

- 正式 writeback ownership
- release verdict
- recursive worker spawning

一句话：

> 这一层负责“怎么执行”，但不负责“最终什么算正式结果”。

---

### Layer 4：Closure controller

这一层由 `ralph` 持有。

`ralph` 的职责应被优化为：

- 读取 `implement / review / qa / gate` 的正式输出
- 决定下一轮动作：
  - 继续 implement
  - 进入 review
  - 继续 qa
  - 执行 repair handoff
  - 停止并升级到人类处理
- 持有 durable status / checkpoint / exhaustion / resume 语义

`ralph` **不应**：

- 直接改写 PRD / story / test-case
- 直接充当底层执行器
- 自己发明第二套 truth

一句话：

> Ralph 负责“把既有正式阶段串成持续推进闭环”，不是新的 owner，也不是新的 worker。

---

### Layer 5：Learning & recall plane

这一层主要包括：

- memory
- workflow memory
- QA calibration
- requirement rewrite inputs
- keep/discard ledger

它负责：

- recall 注入
- QA judgement 改进
- technical archive 到 rewrite input 的受控沉淀
- status / scorecard / evidence 对齐

它**不应**：

- 变成 semantic cache 平台
- 变成通用 retrieval kernel
- 变成所有 agent 共享的大脑

一句话：

> 这一层负责“让系统下一轮判断更好”，而不是再造第二个执行或真相平面。

---

## 4. 关键职责优化决策

## 4.1 `implement` 的职责优化

`implement` 在 `v1.3.2` 中的职责应收敛为：

1. 接受 frozen baseline
2. 编译 implementation plan
3. 选择 `single / team / ralph`
4. 产出实现证据
5. 进入 review / qa / gate

`implement` 不应继续承担的叙事负担：

- 用 runner 名称解释产品模式
- 暗示自己已经是通用 codex-native agent platform

因此建议口径：

- `native-single` → 对外叙事统一为 `single`
- `codex-subagents` / `implement-team` → 对外叙事统一为 `team`

runner 仍可保留在实现层，但不应继续成为人类主叙事。

---

## 4.2 `qa` 的职责优化

`qa` 应被正式提升为第二执行面，而不是附属尾步骤。

它的职责应统一为：

1. 围绕冻结的 `prd / user-story / test-case`
2. 启动目标项目浏览器环境
3. 按轮次顺序执行验收
4. 每轮产生新的边界发现、结构推演或 coverage closure
5. 生成 feature scorecard 与 repair handoff

它不应承担的职责：

- 自行改写 requirement truth
- 代替 release 判定
- 成为泛化“自动修 bug 平台”

这里最关键的职责优化是：

> QA 的主价值不再是“跑一次测试”，而是“围绕冻结材料做浏览器原生、顺序可迭代、带 autoresearch 增量的正式验收闭环”。

---

## 4.3 `team` 的职责优化

`team` 的职责应明确为：

- bounded multi-agent execution runtime
- HUD / tmux / pane / role report materialization
- worker role contract enforcement
- implement / qa 上下文隔离

它不应被解释为：

- 通用 agent OS
- 任意任务都能平行拆解的总平台

因此 `team` 的对外定位应是：

> Beacon 自己掌控的 execution mode，而不是开放式代理平台。

---

## 4.4 `ralph` 的职责优化

`ralph` 最需要优化的是“边界定义”。

建议冻结为：

- `ralph` = closure controller
- `single / team` = executor

也就是说：

```text
ralph
→ 调度 implement/review/qa/gate
→ 读取 handoff / scorecard / checkpoint
→ 决定继续、修复、阻断、升级
```

而不是：

```text
ralph
→ 自己实现
→ 自己写正式 truth
→ 自己替代 QA / gate
```

这样才能避免 Ralph 变成第三套 owner。

---

## 4.5 `memory / research / rewrite` 的职责优化

当前这部分能力已经存在，但口径容易漂。

建议在 `v1.3.2` 中统一为：

- `memory`：项目与流程记忆
- `research`：职责与模式的版本化分析材料
- `rewrite input`：从 technical archive / QA 结果提取下一轮 requirement or test rewrite 线索

它们共同的非目标是：

- semantic cache
- vector retrieval platform
- project-private execution wiki 的自由共享层

换句话说：

> 这些能力是 Beacon 的“判断增强和经验沉淀面”，不是新的 runtime 核心。

---

## 5. 命令与产品叙事的映射建议

为了让职责口径稳定，建议统一以下映射。

### 对外主叙事

- `implement --mode single`
- `implement --mode team`
- `implement --mode ralph`
- `qa --mode single|team|ralph`（或与 implement 对齐的等价入口）

### 对内兼容映射

- `native-single` → `single`
- `codex-subagents` → `team`
- `implement-team` / `qa-team` → `team` surface artifacts
- `ralph-bridge` + control-plane / exhaustion / checkpoint → `ralph`

### 这样做的收益

1. 人类不必理解内部 runner 名称
2. 文档、help、status 可以统一围绕“模式”解释
3. 代码仍能保留适配器层兼容旧实现

---

## 6. 明确禁止职责

`v1.3.2` 应明确禁止以下职责漂移：

1. 把 Beacon 扩成通用多代理操作系统
2. 把 worker 变成正式 writeback owner
3. 把 Ralph 变成新的 truth owner
4. 把 QA 变成无限自治修复平台
5. 把 memory / rewrite 平面扩成 semantic cache / retrieval platform
6. 把三模式默认扩展到 requirement 阶段
7. 让 implement 与 qa 共享私有上下文而不经正式 handoff

---

## 7. 对源码结构的直接优化启示

如果把这份职责分析落回代码层，`v1.3.2` 最值得优先优化的是：

### 7.1 优先统一“模式”而不是“runner”口径

优先改：

- help
- status
- SUMMARY / execution index
- implement / qa 对外输出

让模式名成为第一叙事层。

### 7.2 继续保持 truth/runtime 分层

继续坚持：

- frozen requirement materials
- run-scoped evidence
- formal writeback by stage owner

### 7.3 清理层间反向依赖

当前应重点避免继续扩大：

- utils 反向依赖 commands
- story/revision 等核心状态循环依赖

否则职责口径再清楚，源码层也会持续漏层。

### 7.4 learning plane 继续受控

允许：

- recall
- scorecard
- rewrite input
- QA calibration

不允许：

- 第二套 truth plane
- 泛化共享记忆池

---

## 8. Final conclusion

这份职责优化分析不会扩大 `v1.3.2` 的中心，反而会继续收口它。

它要冻结的最终判断是：

> Beacon `v1.3.2` 的正确方向，不是继续发明新的运行时名词，  
> 而是把 `implement + qa` 正式收敛成同一 execution family 下的 `single / team / ralph` 三模式，  
> 并把 truth owner、runtime executor、closure controller、learning plane 的职责重新切齐。

一句话版本：

> `v1.3.2` 应把 Beacon 讲成 **“truth-governed workflow kernel + bounded execution family + Ralph closure loop”**，而不是更通用的 agent platform。
