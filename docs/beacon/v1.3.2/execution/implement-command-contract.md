# Beacon v1.3.2 Implement 命令合同

## 目标

把 `implement` 从“runner 名称集合”收敛成稳定的人类可理解合同：

- `single`
- `team`
- `ralph`

并把当前已经存在的：

- `run`
- `plan`
- `team-plan`
- `team-run`
- `dev-run`
- `sync-git-workflow`

统一解释到这套模式语义下。

## 当前代码面的真实情况

当前实现已经具备以下事实：

- `implement run` 是主入口
- `implement team-run` 是显式 implement-team surface
- `implement run` 仍以 `--runner` 作为底层实现选择
- `team-run` 当前固定映射到 `codex-subagents`
- `runtime` 目前仍是 `file|tmux|auto`

`v1.3.2` 不要求立刻删除这些命令，而是要先把它们讲清楚。

## 人类主合同

### 推荐主入口

```bash
beacon implement run "<feature>" --mode single --project . --version v1.3.2 --json
beacon implement run "<feature>" --mode team --project . --version v1.3.2 --runtime tmux --json
beacon implement run "<feature>" --mode ralph --project . --version v1.3.2 --executor team --runtime tmux --json
```

### 模式解释

#### `single`

- 单进程
- 单 owner
- 最小执行面
- 不创建 implement-team worker lanes

#### `team`

- bounded multi-agent runtime
- 可用 `file` 或 `tmux`
- 生成 role reports、worker evidence、HUD

#### `ralph`

- 闭环控制器
- 不是新的实现器
- 默认围绕 `implement + qa` 多轮推进

## 与现有命令的兼容映射

### 现有命令保留期映射

- `beacon implement run --runner native-single`
  - 等价于 `--mode single`
- `beacon implement run --runner codex-subagents`
  - 等价于 `--mode team`
- `beacon implement team-run`
  - 等价于 `beacon implement run --mode team`

### 现有规划命令映射

- `beacon implement plan`
  - 生成实现计划
- `beacon implement team-plan`
  - 生成 team-mode 优先的实现计划
- `beacon implement dev-run`
  - 在 frozen 前提下补 implementation plan / git workflow contract / branch preflight 后进入实现
- `beacon implement sync-git-workflow`
  - 将 branch/worktree/service-directory contract materialize 到版本物料

## 推荐语义

### `implement plan`

用于：

- 从冻结材料编译实现计划
- 生成 implementation tasks

### `implement team-plan`

用于：

- 显式编译 team-mode 执行方案
- 暴露 implement-team 角色拆解

### `implement run`

用于：

- 统一执行入口
- 在 `v1.3.2` 语义里承载 `single / team / ralph`

### `implement team-run`

用于：

- 兼容入口
- 显式进入 implement-team
- 在过渡期继续可用，但产品叙事不应再把它当第一主入口

### `implement dev-run`

用于：

- frozen feature 的安全前置准备
- 补 plan / git workflow contract / branch preflight

## 参数合同

### `--mode`

推荐新增并提升为人类主语义：

- `single`
- `team`
- `ralph`

### `--runner`

保留为兼容或技术实现面：

- `native-single`
- `codex-subagents`
- 其他 adapter runner

规则：

> 人类记住 mode，代码兼容 runner。

### `--runtime`

只描述 `team` executor 的运行后端：

- `file`
- `tmux`
- `auto`

### `--executor`

只在 `ralph` 下使用：

- `single`
- `team`

用于决定 Ralph 每一轮调用的实现执行器。

## 默认策略

推荐策略：

1. 用户显式指定 `--mode` 时，严格按显式模式执行
2. 未显式指定时，默认优先 `team`
3. 用户只要最小执行面时，应显式选择 `single`
4. 用户目标是持续推进到完整可交付时，应显式选择 `ralph`

## 输出合同

### `single`

必须至少输出：

- implementation summary
- technical archive
- story writeback refs

### `team`

必须额外输出：

- team manifest
- role reports
- worker evidence
- team HUD JSON / HTML
- tmux session / pane mapping

### `ralph`

必须额外输出：

- round summary
- stop reason
- final verdict
- next action decision

## Guardrails

1. `implement` 的正式 writeback ownership 仍属于 Beacon stage owner
2. `team` 不得递归 worker 再开 worker
3. `ralph` 不得绕过 review / qa / gate
4. `ralph` 不得直接改写冻结的 `prd / user-story / test-case`

