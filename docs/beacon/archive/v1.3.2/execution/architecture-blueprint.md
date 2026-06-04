# Beacon v1.3.2 架构蓝图

`v1.3.2` 需要把 Beacon 的 `implement + qa` 执行面讲成一个清晰模型：

```text
implement stage owner
→ execution mode selector
→ single / team executor
→ run-scoped evidence
→ review / qa / gate
→ ralph closure loop（可选）
```

## 核心判断

Beacon 仍然不是通用多代理运行时。

Beacon 在这条线里要做的是：

1. 把 `implement + qa` 的执行方式明确成三种模式
2. 保持正式工件、formal writeback、gate、release 不变
3. 让 `ralph` 成为“持续推进”层，而不是新的 truth owner

## 三种模式的准确口径

### `single`

适用：

- 小改动
- 确定性任务
- 不需要并行分工的实现

语义：

- 单 owner
- 单执行上下文
- 不启动 worker lanes
- 仍需正式 review / qa / gate

### `team`

适用：

- 多文件、多子任务 feature
- 需要 planner / reviewer / tester 分工
- 需要 HUD、tmux、role reports 或 worktree 隔离

语义：

- Beacon 自己掌控的 bounded multi-agent runtime
- 当前稳定角色仍以：
  - `planner`
  - `implementation-architect`
  - `implementer`
  - `reviewer`
  - `tester`
  为主
- 正式 writeback 仍由 stage owner 完成
- 不允许 worker 递归再开 worker

### `ralph`

适用：

- 复杂 feature
- 多轮修复
- 目标不是“先跑一遍”，而是“推进到完整可交付”

语义：

- `ralph` 不是新的实现执行器
- `ralph` 是包在 `single` 或 `team` 外层的闭环控制器
- 它负责决定下一轮要继续 `implement`、进入 `review`、执行 `qa`、还是阻断并上升到人类处理

## 分层结构

### Layer A：Stage owner

仍然是：

- `implement`
- `review`
- `qa`
- `gate`
- `release`

这些命令继续持有：

- requirement truth
- canonical artifact writeback
- release decision ownership

### Layer B：Execution runtime

这里承载 `single` 与 `team` 两种执行模式，并同时作用于 `implement` 与 `qa`：

- `single`：最小执行面
- `team`：bounded worker lanes + tmux/HUD + run-scoped artifacts

### Layer C：Closure controller

这里由 `ralph` 持有：

- failure streak
- escalation level
- next action
- repair handoff
- stop condition

它不应直接持有 requirement truth，只应读取 stage outputs 和 control-plane state。

## 与当前代码基的对应关系

`v1.3.2` 不需要推翻当前实现，而是要把现有能力重新收口：

1. `native-single` 对应 `single`
2. `codex-subagents` / `implement-team` 对应 `team`
3. 当前 `qa run / qa team-run / qa evolve / qa session` 对应浏览器原生、迭代式 QA surface
4. 当前 `ralph-bridge` 与 exhaustion/checkpoint/control-plane 共同演进为 `ralph`

这意味着 `v1.3.2` 更接近“模式治理与命令面统一”，而不是“从零重写 runtime”。

## 从开源参考吸收什么

参考 `oh-my-codex` 这类开源实现，Beacon 最值得吸收的是：

1. 团队模式必须显式，而不是只靠隐式路由。
2. 持续推进模式必须是 loop contract，而不是一句口号。
3. worktree / 隔离执行是 team 模式的重要配套，而不是附属功能。
4. status / HUD / resume 必须是 durable artifact，而不是终端瞬时输出。

Beacon 不应吸收的是：

1. generic shell DAG
2. 任意递归代理
3. 第二套正式 truth plane

## 非目标

`v1.3.2` 不追求：

1. 让所有阶段都支持并行多代理
2. 把 team runtime 说成通用 agent platform
3. 让 Ralph 绕过 review / qa / gate
4. 把阶段命令再拆得更碎
