# Beacon v1.3.2 Implement / QA 执行模式蓝图

## 目标

为 `implement + qa` 定义统一、稳定、可解释的三模式 contract：

- `single`
- `team`
- `ralph`

目标不是增加更多命令，而是把当前分散在 runner、team surface、bridge surface 里的能力收敛成一条人类可理解、源码可维护的执行主线。

## 当前问题

当前仓内已经存在以下事实：

1. `implement` 默认已经偏向 `codex-subagents`
2. `implement-team` / `qa-team` 的 bounded team runtime 已可用
3. tmux / HUD / role reports 已落地
4. `ralph-bridge` 仍主要是状态记录与 bridge 语义

但用户仍然很难明确回答：

1. 现在是单进程执行还是多代理执行？
2. `codex-subagents` 到底是 runner 名，还是产品模式？
3. Ralph 到底只是 bridge，还是持续穷尽交付模式？
4. QA 到底只是测试阶段，还是三模式中的正式浏览器执行面？

## 统一命令面

`v1.3.2` 推荐把人类可见主入口收敛为：

```bash
beacon implement run "<feature>" --mode single --project . --version v1.3.2 --json
beacon implement run "<feature>" --mode team --project . --version v1.3.2 --runtime tmux --json
beacon implement run "<feature>" --mode ralph --project . --version v1.3.2 --executor team --runtime tmux --json
```

其中：

- `--mode single|team|ralph` 是人类主语义
- `--runner ...` 继续作为兼容层或内部技术实现面
- `--runtime file|tmux|auto` 只描述 team executor 的运行后端
- `--executor single|team` 只在 `ralph` 模式下有效，用于决定每一轮实现执行采用哪种 executor

并且在 `ralph` 驱动下，`qa` 应被视为同一闭环中的正式执行面，而不是一次性收尾动作。

## 模式范围约束

三模式在 `v1.3.2` 中只正式适用于：

- `implement`
- `qa`

以下阶段继续保持单 owner 正式材料面：

- `think`
- `prd`
- `user-story`
- `test-case`

## 模式合同

### 1. `single`

#### 输入

- frozen requirement materials
- implementation plan
- git workflow contract

#### 执行

- 单进程
- 单 owner
- 不启动 worker specs
- 不生成 team HUD

#### 输出

- implementation summary
- technical archive
- story writeback
- verification refs

#### 适合条件

- 目标范围小
- 子任务少
- 不需要 reviewer/tester 并行 lane

### 2. `team`

#### 输入

- `single` 的全部输入
- team plan
- role registry
- team runtime config

#### 执行

- 使用 bounded worker lanes
- 允许 `file` 或 `tmux` runtime
- 生成 worker specs / worker results / HUD / role reports
- 可逐步接入 worktree isolation

#### 输出

- `single` 的全部输出
- team manifest
- HUD JSON / HTML
- role reports
- pane/session mapping

#### 适合条件

- feature 有明确子任务
- 需要 reviewer/tester 平行或半平行介入
- 需要更强可观测性

### 3. `ralph`

#### 输入

- `single` 或 `team` executor
- control plane
- review / qa / gate outputs
- repair handoff

#### 执行

`ralph` 每一轮只做一件事：

1. 运行一轮实现 executor
2. 读取正式 review / qa / gate 结果
3. 根据 closure contract 决定下一轮动作
4. 直到进入明确终态

#### 输出

- Ralph loop state
- per-round summary
- final delivery verdict
- stop reason / handoff

#### 终态

- `release_ready`
- `human_blocked`
- `budget_exhausted`

## QA 在三模式中的角色

### QA 不是旁路

在 `v1.3.2` 中，QA 必须被视为与 `implement` 对应的第二执行面：

- `implement` 负责代码与实现证据
- `qa` 负责浏览器验收、边界发现、结构推演与 repair handoff

### QA 的正式输入

QA 必须围绕冻结的：

- `prd`
- `user-story`
- `test-case`

进行顺序推进。

### QA 的正式执行口径

QA 必须围绕目标项目启动真实浏览器环境，并支持项目选定的 browser-capable runners，例如：

- `browser-cli`
- `agent-browser`
- `pageagent`
- `browser-use`

必要时也可以兼容 `playwright` / `cypress` 等 runner，但产品口径不应再只是“runner 选项列表”。

### QA 的迭代口径

QA 必须支持：

- 顺序推进
- 多轮迭代
- 每轮新增 auto research 增量
- 每轮产生新的边界反馈或结构推演

如果一轮 QA 没有新增发现、覆盖增强或 repair handoff，就不应被视为有效进展。

## Ralph 的关键约束

### Ralph 不做什么

Ralph 不应：

1. 直接改 requirement truth
2. 直接绕过 review / qa / gate
3. 成为新的实现执行器
4. 无界地自动循环

### Ralph 应该复用什么

当前仓内已有的：

- `failure_streak`
- `escalation_level`
- `required_next_action`
- `checkpoint`

这些控制面不应再另起一套，而应成为 Ralph 的核心状态 contract。

## 推荐状态机

```text
start
→ run executor(single|team)
→ formal review / qa / gate
→ evaluate closure
→ continue repair loop | stop
```

其中 `evaluate closure` 至少检查：

1. gate 是否通过
2. qa 是否达到 release-ready
3. qa 本轮是否产生新的边界/结构/coverage 增量
4. exhaustiveness / evidence 是否足够
5. 是否存在明确 repair handoff
6. failure streak 是否已达到上限

## 与现有命令的兼容映射

为降低迁移成本，`v1.3.2` 推荐如下映射：

- `beacon implement run --runner native-single`
  - 视为 `--mode single`
- `beacon implement run --runner codex-subagents`
  - 视为 `--mode team`
- `beacon implement team-run`
  - 视为 `beacon implement run --mode team`
- `beacon ralph-bridge`
  - 降级为兼容 alias 或内部 bridge，不再承担正式产品叙事

## 默认策略

推荐默认策略如下：

1. 若用户显式指定 `--mode`，严格按显式模式执行
2. 若未显式指定，`implement run` 默认优先 `team`
3. 若用户需要最小执行面，显式使用 `single`
4. 若用户目标是“直到完整可交付”，显式使用 `ralph`

这样可以同时满足：

- 与 `v1.3.0` team-first 语义保持连续
- 给用户一个稳定、简洁的单进程退路
- 避免 Ralph 被误用成默认模式

## 对开源参考的落地吸收

来自 `oh-my-codex` 的吸收点：

1. `team` 必须是显式团队执行模式
2. `ralph` 必须是持续推进 loop，而不是单次命令
3. 团队执行应配套 worktree / session / HUD
4. 状态必须可恢复、可回看、可继续

Beacon 在 `v1.3.2` 的落地方式应是：

1. 保持 Beacon stage owner 和 formal truth 不变
2. 借鉴其操作层 contract，而不是复制其全部 runtime 结构

## 分阶段落地建议

### P0

1. 增加 `implement --mode single|team|ralph`
2. 建立 runner 到 mode 的兼容映射
3. 把 `ralph` 提升为正式执行闭环 surface
4. 让 `status/help` 明确显示当前 mode
5. 让 `qa` 明确显示当前轮次、当前 browser runner 与本轮新增边界/coverage 增量

### P1

1. 为 `team` 增加 worktree isolation contract
2. 为 `ralph` 增加 per-round summary / stop-reason artifacts
3. 让 `qa` 输出更直接服务 Ralph closure decision
4. 把 `browser-cli / agent-browser / pageagent / browser-use` 收成统一 browser execution family

### P2

1. 再决定是否需要把 `team` 从 bounded runtime 继续推进到更原生的 child-agent runtime
2. 这个决策必须晚于 mode contract 稳定之后

