# Beacon v1.3.0 Team Runtime 使用指南

> 这份文档只回答一件事：  
> **如何在 `v1.3.0` 中使用 `implement-team` / `qa-team` 的多角色 runtime、tmux 执行和 HUD 展示。**

---

## 1. 当前已落地范围

`v1.3.0` 当前已经落地的 team runtime 能力包括：

- `implement team-plan`
- `implement team-run --runtime file|tmux|auto`
- `qa team-plan`
- `qa team-run --runtime file|tmux|auto`
- `team worker-run`
- `team hud`
- `team page`

当前最稳定、已实机验证的路径是：

```bash
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
```

这条路径会生成：

- team manifest
- tmux session / pane 映射
- role reports
- team HUD JSON
- team HUD HTML 页面

---

## 2. 运行模式

### `file`

适合：

- 本地快速验证
- CI
- 不需要 live pane 展示

特点：

- 多角色仍然成立
- 但不启动 tmux
- HUD 仍会生成

### `tmux`

适合：

- 本地真实观察多角色 implement / qa
- 需要 session / pane 级可视执行

特点：

- 启动真实 tmux session
- 给 worker 分配 pane
- 写回 pane/session mapping
- 生成稳定 HUD 页面

### `auto`

当前先回退为 `file`。

后续可以扩成：

- 本地默认 tmux
- 非交互环境默认 file

---

## 3. implement-team 使用方式

如果前置 gate 已全部准备好，可直接使用：

```bash
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
```

如果 feature 已 frozen，但希望 Beacon 自动补 implementation plan / git workflow contract / branch preflight，再进入开发，推荐使用：

```bash
beacon implement dev-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
```

如果你只想先把当前 feature/version 的 branch/worktree/service-directory 约束固化进版本物料，可先执行：

```bash
beacon implement sync-git-workflow "<feature>" --project . --version v1.3.0 --json
```

这条命令的语义是：

- 读取当前可用 seed（通常来自 `beacon.config`）
- materialize 为 versioned git workflow contract
- 后续 `check-branch` / `gate` / `doctor` 都优先读取该 contract

### 3.1 先生成计划

```bash
beacon implement team-plan "<feature>" --project . --version v1.3.0 --json
```

### 3.2 file 模式

```bash
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime file --json
```

### 3.3 tmux 模式

```bash
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
```

返回中重点关注：

- `team_execution.runtime`
- `team_execution.tmux_session`
- `team_execution.role_reports`
- `team_execution.hud.json`
- `team_execution.hud.html`

---

## 4. qa-team 使用方式

### 4.1 先生成 QA 计划

```bash
beacon qa team-plan "<feature>" --project . --version v1.3.0 --json
```

### 4.2 file 模式

```bash
beacon qa team-run "<feature>" --project . --version v1.3.0 --runtime file --json
```

### 4.3 tmux 模式

```bash
beacon qa team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
```

---

## 5. HUD / 页面怎么查看

### JSON HUD

```bash
beacon team hud --team "<team-name>" --project . --json
```

### HTML 页面路径

```bash
beacon team page --team "<team-name>" --project .
```

典型页面位置：

```text
docs/beacon/archive/v1.3.0/execution/codex-subagents/<feature-slug>/<run-id>/index.html
docs/beacon/archive/v1.3.0/execution/qa-team/<feature-slug>/<run-id>/index.html
```

---

## 6. 运行产物在哪里

### implement-team

- manifest:
  - `.beacon/team/implement-team-<run-id>/manifest.json`
- runtime HUD:
  - `.beacon/state/team-hud/implement-team-<run-id>.json`
- role reports:
  - `docs/beacon/archive/v1.3.0/execution/codex-subagents/<feature>/<run-id>/`
- worker runtime state:
  - `.beacon/subagents/implement-team-<run-id>/workers/`

### qa-team

- manifest:
  - `.beacon/team/qa-team-<run-id>/manifest.json`
- runtime HUD:
  - `.beacon/state/team-hud/qa-team-<run-id>.json`
- role reports:
  - `docs/beacon/archive/v1.3.0/execution/qa-team/<feature>/<run-id>/`

---

## 7. 当前角色配置

角色配置现在已经外置，不再只写死在代码里：

- implement:
  - `beacon/team_roles/implement-team.json`
- qa:
  - `beacon/team_roles/qa-team.json`

当前默认角色：

- implement-team:
  - `planner`
  - `implementation-architect`
  - `implementer`
  - `reviewer`
  - `tester`
- qa-team:
  - `verifier`
  - `repair-handoff-writer`

---

## 8. 当前边界

虽然 tmux runtime + HUD 已经落地，但 `v1.3.0` 仍保持以下边界：

- Beacon 仍然是 stage owner
- 正式 writeback 仍由 Beacon 主命令负责
- gate / release 仍读取 formal artifacts
- 不允许递归 worker 再开 worker
- implement / qa 仍必须上下文隔离
- `implementation-architect` 只允许写 execution-scoped architecture note，不允许直接改 frozen PRD/story/test-case/architecture-blueprint
- git branch / worktree / service-directory 应优先来自当前版本线的 execution materials，不应只藏在全局 `beacon.config`

## 8.1 Config 与 versioned contract 的主从关系

当前推荐原则：

1. `beacon.config` 中的 `implementation.branch_guard` 只作为 seed / fallback
2. `implement plan` / `implement sync-git-workflow` / `implement dev-run` 会生成 versioned git workflow contract
3. 一旦 contract 已存在，后续 branch/worktree gate 应优先读取 versioned contract
4. 只有 contract 缺失时，才允许退回 config seed

---

## 9. 最推荐的最短路径

```bash
beacon freeze "<feature>" --project . --version v1.3.0 --json
beacon implement team-plan "<feature>" --project . --version v1.3.0 --json
beacon implement team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
beacon review quality "<feature>" --project . --version v1.3.0 --json
beacon review accept "<feature>" --project . --version v1.3.0 --reviewer qa --json
beacon qa team-run "<feature>" --project . --version v1.3.0 --runtime tmux --json
beacon gate check release --project-root . --version v1.3.0 --json
```
