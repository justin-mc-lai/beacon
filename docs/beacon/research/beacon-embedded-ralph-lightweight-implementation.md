# Design Note: Beacon 内置 Ralph 的轻量稳定实现

**Date**: 2026-04-15  
**Purpose**: 基于 `oss-sync/ralph` 里的 Ralph 家族开源项目，对照 Beacon 当前 `implement / qa / ralph / subagent` 结构，收敛出一份适合 Beacon 内置的 Ralph 轻量稳定实现方案。  
**结论定位**: 这不是“把 Beacon 改造成 Ralph 平台”，而是把 Ralph 压缩成 Beacon 内部的闭环控制器，用最小新增复杂度增强 `implement + qa`。

---

## 1. 一句话判断

> Beacon 内置 Ralph 的正确实现，不是新建一个独立执行器，而是做一个包在现有 `implement + review + qa + gate` 外层的薄控制器。

这意味着：

1. Ralph 不拥有任务真相
2. Ralph 不直接执行编码
3. Ralph 不解析自由文本来判停
4. Ralph 只消费 Beacon 现有正式阶段的结构化输出

如果把这件事做厚，Beacon 会变成另一个 `ralph-orchestrator`。  
如果把这件事做薄，Beacon 才能既保留自己的主链，又得到 Ralph 的“持续推进直到可交付”能力。

---

## 2. 现有 Beacon 的起点

Beacon 当前已经有 Ralph 的雏形，而且并不弱：

### 已有基础

1. `implement --mode ralph`
2. `.beacon/ralph/<feature>.json` 状态文件
3. `single / team / ralph` execution family 语义
4. `review quality`
5. `qa` 结构化 scorecard / repair handoff / continue decision
6. `gate release`
7. `help/status` 中的 Ralph phase / stop state 暴露

### 现有实现的优点

1. Ralph 已经被定义成 `closure controller`，不是新执行器
2. stop states 已冻结为：
   - `release_ready`
   - `human_blocked`
   - `budget_exhausted`
3. preflight 依赖：
   - requirement materials
   - implementation plan
   - git workflow contract
   - QA baseline bundle
   都已经存在

### 现有实现的主要问题

当前 `implement --mode ralph` 仍然有一个结构性问题：

> Ralph 外层闭环和 `auto_qa` 内层多轮闭环耦合过深，形成了“控制器包控制器”的嵌套。

具体表现是：

1. `implement --mode ralph` 会自动开启 `auto_qa`
2. `auto_qa_follow_handoff = true`
3. `auto_qa_max_rounds >= 3`

这会导致：

1. Ralph 还没决定是否进入下一轮，QA 内层已经在自己循环
2. 控制权不够清晰
3. 每轮边界不够纯粹
4. 状态与预算不好解释

所以，Beacon 内置 Ralph 的第一修正方向不是“加更多能力”，而是：

> **把 Ralph 的外层闭环和 QA 的内层多轮逻辑拆开，让 Ralph 成为唯一 outer loop。**

---

## 3. Ralph 家族开源项目的可借鉴点

## 3.1 `snarktank/ralph`

### 值得借

1. 最小心智模型
   - 一个 `prd.json`
   - 一个 `progress.txt`
   - 一个 loop
2. fresh instance per iteration
3. 一轮只做一件事
4. 完成后再做下一轮

### 不值得直接照搬

1. `<promise>COMPLETE</promise>` 这种文本信号
2. 由 agent 自己维护 `passes: true`
3. 由 prompt 约定承担全部真相治理

### 对 Beacon 的启发

Beacon 应保留它的“每轮只推进一个明确 repair/closure 动作”的轻量感，  
但不要把 `progress.txt + prd.json` 搬进来，因为 Beacon 已经有更强的正式工件链。

---

## 3.2 `ralph-loop-agent`

### 值得借

1. outer loop / inner tool loop 两层分离
2. `verifyCompletion` 作为独立判停器
3. stop conditions 明确参数化：
   - iteration
   - token
   - cost

### 不值得直接照搬

1. 通用 library 抽象过强
2. 成本/token 级 stop condition 对 Beacon 当前不是核心

### 对 Beacon 的启发

Beacon 最适合吸收的是：

> Ralph 的核心不是“再调用一次模型”，而是“在每轮 formal outputs 之后运行一个独立 closure evaluator”。

也就是说，Beacon 的 `verifyCompletion` 不应去看原始模型输出，而应去看：

1. review 结果
2. QA scorecard
3. gate 结果

---

## 3.3 `ralph-claude-code`

### 值得借

1. circuit breaker
2. rate limit / timeout / resume 的运维意识
3. “显式判停 + 显式继续”的防无限循环机制

### 不值得直接照搬

1. 大量 shell + 文本解析
2. host-specific behavior 直接内嵌到闭环逻辑
3. `STATUS/EXIT_SIGNAL` 的 prompt 耦合

### 对 Beacon 的启发

Beacon 应借的是控制原则：

1. 防空转
2. 防同一 blocker 重复
3. 防无限消耗

但 **不要** 借文本解析实现。  
Beacon 应该用结构化 artifacts 做 circuit breaker，而不是 grep 输出。

---

## 3.4 `ralphex`

### 值得借

1. plan-driven execution
2. task-level freshness
3. review pipeline
4. worktree isolation
5. progress / dashboard / status 设计

### 不值得直接照搬

1. 自己完整重建 plan/task/runtime world
2. 把 review / task parser / web dashboard 都做进核心

### 对 Beacon 的启发

`ralphex` 证明了一件事：

> 一轮执行的最稳定单元不是“整件事”，而是“计划里的一段明确 task + validation”。

对 Beacon 来说，对应物不是重新发明 `plan.md`，而是复用现有：

1. `implementation-plan-<slug>.json`
2. `git-workflow-<slug>.json`
3. `qa baseline bundle`

---

## 3.5 `ralph-orchestrator`

### 值得借

1. workspace-scoped control plane
2. 事件流与 dashboard
3. runtime / task / memory 的分层治理

### 不值得直接照搬

1. hat system
2. MCP / bot / API / web 全家桶
3. 让 Ralph 成为平台核心

### 对 Beacon 的启发

Beacon 只需要吸收一句话：

> Ralph 的 durable state 必须是 workspace scoped、feature scoped、可恢复的。

但不需要把整套 orchestrator runtime 搬进来。

---

## 3.6 `ralph-tui`

### 值得借

1. session persistence
2. 可视化执行
3. subagent tracing
4. headless / UI 双模式

### 不值得直接照搬

1. plugin system
2. remote instances
3. TUI 成为主产品面

### 对 Beacon 的启发

Beacon 内置 Ralph 的 HUD 不需要终端 UI，
但应该保留：

1. round summary
2. current phase
3. current blocker
4. recommended next action

也就是说，Beacon 更适合：

- `JSON + Markdown + help/status`

而不是先做 TUI。

---

## 3.7 `ralphy`

### 值得借

1. 多引擎 adapter 思路
2. prompt / PRD / YAML / JSON 多输入源

### 不值得直接照搬

1. 把 Beacon 做成多 agent engine 抽象层

### 对 Beacon 的启发

Beacon 当前应坚持单宿主判断，不应扩成 `ralphy` 这种多引擎调度入口。  
适合作为未来 host adapter 的参考，不适合进当前轻量 Ralph 核心。

---

## 4. 对 Beacon 来说，什么是“轻量稳定”

一个适合 Beacon 的内置 Ralph，必须同时满足四条：

### 4.1 轻量

1. 不引入新的公开一级命令
2. 不引入新的独立任务格式
3. 不引入新的独立 memory plane
4. 不引入新的 dashboard / TUI runtime

### 4.2 稳定

1. 所有判停都基于正式 artifacts
2. 每轮输入固定
3. 每轮输出固定
4. stop states 固定

### 4.3 可恢复

1. state durable
2. next action clear
3. round artifact 可追

### 4.4 贴合 Beacon

1. requirement truth 继续由 `prd / user-story / test-case` 持有
2. 实现继续由 `implement` 持有
3. 验收继续由 `qa` 持有
4. 放行继续由 `gate / release` 持有
5. Ralph 只做闭环控制

---

## 5. 推荐的 Beacon 内置 Ralph 架构

## 5.1 设计原则

### 核心原则

> Ralph = 薄控制器，不是执行器，不是真相层，不是平台。

### 技术原则

1. single owner of truth
2. outer loop only once
3. fresh execution per round
4. structured closure evaluation
5. bounded rounds

---

## 5.2 组件划分

推荐把 Beacon 内置 Ralph 收敛成 5 个薄组件。

### 1. Preflight Gate

输入：

1. requirement clarity
2. implementation plan
3. git workflow contract
4. QA baseline bundle
5. branch preflight
6. team/subagent readiness（若 executor=team）

输出：

- `pass`
- `human_blocked`
- `recommended_command`

### 2. Round Executor

只负责触发一轮正式阶段：

1. implement round
2. review quality
3. qa run
4. gate release（必要时）

注意：

> QA 在 Ralph 中每轮只跑一次，不允许再自行多轮闭环。

这意味着：

1. `auto_qa_max_rounds` 应在 Ralph 模式下被压成 `1`
2. `follow_handoff` 逻辑回归到 Ralph 自己处理

### 3. Closure Evaluator

输入：

1. review payload
2. qa scorecard
3. gate payload
4. failure streak / no-delta streak

输出：

1. `release_ready`
2. `human_blocked`
3. `budget_exhausted`
4. `next_action`
5. `recommended_command`

### 4. Ralph State Store

继续使用：

- `.beacon/ralph/<feature>.json`

但建议扩出更清晰的字段：

```json
{
  "schema_version": "1.1",
  "feature": "...",
  "version": "...",
  "mode": "ralph",
  "executor": "single|team",
  "phase": "preflight|implement_round|review_gate|qa_round|closure_evaluate|completed",
  "status": "active|waiting|completed",
  "round_count": 0,
  "failure_streak": 0,
  "no_delta_streak": 0,
  "stop_state": "",
  "current_blocker": "",
  "next_action": "",
  "recommended_command": "",
  "last_round_ref": "",
  "rounds": []
}
```

### 5. Round Artifact Writer

新增一层非常薄的 round artifact：

- `docs/beacon/<version>/execution/ralph-rounds/<feature>/round-001.json`
- `docs/beacon/<version>/execution/ralph-rounds/<feature>/round-001.md`

每轮只记录：

1. round id
2. executor
3. implementation summary ref
4. review ref
5. qa ref
6. gate ref
7. continue decision
8. repair handoff ref

这比引入 event bus 或 dashboard 轻得多，但已经足够稳定排查。

---

## 5.3 推荐状态机

```text
start
→ preflight
→ implement_round
→ review_gate
→ qa_round
→ closure_evaluate
→ continue_loop | stop
```

### 关键约束

1. `implement_round` 一次只运行一个 executor
2. `qa_round` 一次只运行一个 QA round
3. `closure_evaluate` 是唯一决定“是否下一轮”的地方

这三条是轻量稳定的核心。

---

## 5.4 命令面

推荐保持人类面极简：

```bash
beacon implement run "<feature>" --mode ralph --executor single
beacon implement run "<feature>" --mode ralph --executor team --runtime tmux
```

不建议新增：

1. `beacon ralph run`
2. `beacon ralph resume`
3. `beacon ralph loop`

原因很简单：

Beacon 全局约束已经冻结了：

> `implement` 和 `qa` 是唯一执行入口。

所以 Ralph 只应该是 `implement` 下的一种执行模式。

---

## 5.5 每轮算法

推荐的内置 Ralph 每轮算法：

### Round 0

1. preflight
2. 失败则：
   - `human_blocked`
   - 退出

### Round N

1. 运行 `implement` 一轮
2. 运行 `review quality` 一轮
3. 若 review 阻断：
   - 进入 `closure_evaluate`
4. 否则运行 `qa run` 一轮
5. 若 QA 给出 `ready_for_release`：
   - 运行 `gate check release`
6. 进入 `closure_evaluate`
7. 由 evaluator 决定：
   - `release_ready`
   - `human_blocked`
   - `budget_exhausted`
   - 或进入下一轮

### 关键点

下一轮的唯一输入不是整段历史，而是：

1. frozen materials
2. latest implementation summary
3. latest review findings
4. latest QA repair handoff
5. latest round summary

这就是 Beacon 版的 `fresh context per iteration`。

---

## 6. 绝不建议做的事

为了让 Beacon 内置 Ralph 保持轻量稳定，下面这些一定不要做：

### 6.1 不要新建独立 PRD/task 格式

Beacon 已经有：

1. `prd`
2. `user-story`
3. `test-case`
4. `.machine/execution/implementation-plan-*.json`

再引入 `prd.json` 或 `progress.txt` 会制造双真相。

### 6.2 不要依赖文本输出判停

不要学：

1. `<promise>COMPLETE</promise>`
2. `EXIT_SIGNAL`
3. grep completion keywords

Beacon 有正式 scorecard，比文本强得多。

### 6.3 不要把 QA 也做成内部无限循环

Ralph 已经是 outer loop，就不要让 `auto_qa` 再做自己的 long loop。

否则你会得到：

- 外层 Ralph
- 内层 QA loop
- 双层 budget
- 双层 stop condition

这会显著降低稳定性。

### 6.4 不要把 worktree / dashboard / TUI 做成前置依赖

它们可以是增强项，但不应成为 Ralph MVP 的前提。

---

## 7. 一份适合 Beacon 的 MVP

如果只做一个真正能进 Beacon 的 MVP，我建议收敛成下面这版。

## MVP 范围

### 必做

1. Ralph 外层 loop 独立于 `auto_qa`
2. QA 单轮执行
3. closure evaluator 基于结构化 outputs
4. `.beacon/ralph/<feature>.json` 扩充 round/failure/no-delta 字段
5. round summary JSON/MD artifact
6. `help/status` 暴露：
   - executor
   - round_count
   - phase
   - stop_state
   - next_action

### 可暂缓

1. worktree isolation
2. TUI / dashboard
3. cost-based stop conditions
4. remote control
5. multi-host adapters

---

## 8. 建议的代码落点

在 Beacon 代码里，最适合的落点是：

### 继续保留

1. `beacon/utils/ralph_runtime.py`
   - state helpers
2. `beacon/commands/implement.py`
   - 人类入口仍然在这里

### 建议新增

1. `beacon/utils/ralph_controller.py`
   - 外层 round orchestration
2. `beacon/utils/ralph_evaluator.py`
   - closure evaluation 纯函数
3. `beacon/utils/ralph_artifacts.py`
   - round summary writer

### 不建议新增

1. 新 top-level `ralph` command
2. 新 task parser
3. 新 dashboard runtime

---

## 9. 推荐实现顺序

### Slice 1: 拆 loop

目标：

- 让 Ralph 成为唯一 outer loop

做法：

1. `implement --mode ralph` 不再把 QA 当成内层多轮
2. QA 每轮只执行一次

### Slice 2: 做 evaluator

目标：

- 把判停逻辑从命令面拆出来

做法：

1. 引入纯函数 evaluator
2. 明确输入输出 schema

### Slice 3: 做 round artifacts

目标：

- 让每轮可追踪

做法：

1. JSON/MD round summary
2. `help/status` 挂接

### Slice 4: 做 failure/no-delta guardrails

目标：

- 稳定停止，不空转

做法：

1. no-delta streak
2. same-blocker streak
3. max rounds

---

## 10. 最终方案总结

最适合 Beacon 的 Ralph，不是：

1. `snarktank/ralph` 那种最小脚本本体
2. `ralph-claude-code` 那种 host-specific shell 产品
3. `ralph-orchestrator` 那种完整 orchestrator 平台
4. `ralph-tui` 那种交互操作台

而是它们共同压缩出来的这一层：

> **一个读取正式工件、控制每轮 implement/review/qa/gate、并稳定给出 stop state 的薄闭环控制器。**

Beacon 已经有 70% 的基础能力。  
真正要做的不是“把 Ralph 加进来”，而是：

1. 把外层 loop 做纯
2. 把判停做结构化
3. 把每轮状态做薄而稳定

如果按这个方向做，Beacon 的内置 Ralph 会有三个优点：

1. **轻**
   - 不扩命令面
   - 不扩任务格式
   - 不扩平台层
2. **稳**
   - 全靠正式 artifacts，不靠 grep 文本
3. **像 Beacon**
   - 继续围绕 requirement truth、execution family、QA closure、release gate

这才是 Beacon 最值得内置的 Ralph。  
