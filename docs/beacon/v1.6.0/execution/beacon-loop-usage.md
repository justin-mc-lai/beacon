# beacon-loop 使用指南（v1.6.0）

Canonical operator doc for the native long-loop entrypoint. Automation queue/job/launchd assets are retired; use `beacon-loop` instead.

## 它是什么

`beacon-loop` 是 Beacon 的**长循环入口 CLI**（Node ≥ 20）。

在 **v1.6.0 默认路径**下，`beacon-loop goal` **不会**自己跑 R3 delivery FSM，而是**薄委托**给 `beacon-run`：

```text
beacon-loop goal "<目标>"
    └─► beacon-run "<目标>" --beacon --worktree --feature <slug> ...
            └─► truth → generate → qa → release（Beacon lifecycle harness）
```

旧版 R3 delivery 仍可用，需显式加 `--legacy-delivery`。

## 1. 安装与自检

### 依赖

| 组件 | 要求 |
|------|------|
| Node | ≥ 20 |
| Python Beacon CLI | `beacon --version` → `v1.6.0` |
| beacon-run | 与 `beacon-loop` 同 monorepo 或 PATH 上 |
| Agent | 默认 `codex`（也可 `claude` / `acp:<target>`） |
| git | 支持 worktree |

### 安装（Beacon 源码仓）

```bash
cd /path/to/beacon

# Python CLI + 可编辑安装
pip install -e ".[dev]"

# 构建 loop / run
npm --prefix packages/beacon-loop run build
npm --prefix packages/beacon-run run build

# 可选：全局 symlink
# ln -sf /absolute/path/to/beacon/packages/beacon-loop/dist/cli.js /usr/local/bin/beacon-loop
```

Post-release hook（`beacon-post-release-local-install`）会同步 agent surface 与 `beacon` CLI；**beacon-loop 需单独 build 并确保在 PATH 上**。

### 一键自检

```bash
cd /path/to/your/project

beacon-loop doctor --project . --json
```

检查项：`node_runtime`、`sqlite_cli`、`beacon_cli`、`git_worktree`、`implement_runner`、`agent_backend`、`evidence_import`。

## 2. 最常用：一条 goal 跑完整闭环

### 基本用法

```bash
cd /path/to/project

beacon-loop goal "实现 examples/go-todo-crud 的 CRUD API 并通过 QA" \
  --project . \
  --version v1.6.0 \
  --feature go-todo-crud-smoke \
  --agent codex \
  --max-iterations 25
```

### 实际发生的事

1. **解析 feature**：`--feature` 优先；否则从 goal 文本推断（路径/token 匹配 `docs/beacon/<version>/features/*/truth.md`）。
2. **解析 version**：`--version auto`（默认）读 `.beacon/state/project-onboarding.json` 或 `docs/beacon/` 最新版本。
3. **分支模式**（默认 `worktree`）：
   - 在主仓分支 → 创建 **git worktree** 隔离执行
   - 已在 `gnhf/*` 分支 → 自动切 **`current-branch`**（不再嵌 worktree）
4. **委托 beacon-run**（等价命令可用 `--dry-run` 预览）：

```bash
beacon-loop goal "..." --dry-run --json
# 输出 beacon_run_command 字段
```

典型形态：

```text
beacon-run "<goal>" --beacon --project-root . --beacon-version v1.6.0 \
  --feature <slug> --agent codex --max-iterations 25 --worktree
```

5. **生命周期阶段**（`beacon-phase.json`）：

| 阶段 | 执行者 | 做什么 |
|------|--------|--------|
| `truth` | Agent | 写/冻结 feature package truth |
| `generate` | Agent | 实现代码（需 truth frozen） |
| `qa` | Harness | `beacon qa` / auto-test 等 |
| `release` | Harness | `beacon release check` 等 |

Agent 阶段走 Codex/Claude；QA/Release 走 Beacon CLI harness，**不由 loop 自判 release verdict**。

## 3. 常用参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--project` | cwd | 项目根 |
| `--version` | `auto` | Beacon docs 版本，如 `v1.6.0` |
| `--feature` | 自动推断 | feature slug；推断失败会 `feature_slug_required` |
| `--agent` | `codex` | `codex` / `claude` / `acp:...` |
| `--max-iterations` | `8` | **总迭代上限**（绝对计数，非「再跑 N 轮」） |
| `--max-tokens` | `0` | `0` = 不限制 |
| `--stop-when` | — | agent 报告某条件后停止 |
| `--branch-mode` | `worktree` | `worktree` / `current-branch` / `run-branch` |
| `--isolated-worktree` | off | 强制 worktree |
| `--implement-runner` | 自动 | generate harness 用的 runner |
| `--truth-bootstrap` | `agent` | `agent` 或 `fallback`（模板链，一般不用） |
| `--dry-run` | — | 只打印将要执行的 `beacon-run` 命令 |
| `--json` | — | 机器可读输出 |
| `--legacy-delivery` | off | 启用 R3 delivery FSM（不推荐默认） |

### 配置文件（可选）

`~/.beacon-loop/config.yml` 或 `<project>/.beacon-loop/config.yml`：

```yaml
version: v1.6.0
feature: my-feature-slug
agent: codex
max_iterations: 12
branch_mode: worktree
```

CLI 显式 flag 会覆盖 config。

### 环境变量

| 变量 | 说明 |
|------|------|
| `BEACON_RUN_CLI` | 显式指定 `beacon-run` 的 `cli.mjs` 路径 |
| `BEACON_LOOP_IMPLEMENT_RUNNER` | 默认 implement runner |

## 4. 典型场景

### A. 在业务项目里跑 smoke / drill

```bash
cd /path/to/examples/go-todo-crud

beacon-loop goal "完成 go-todo-crud smoke：truth frozen 后实现并通过 native QA" \
  --project . \
  --version v1.6.0 \
  --feature go-todo-crud-smoke \
  --max-iterations 30
```

Worktree 一般在 `../beacon-gnhf-worktrees/<slug>-*` 一类路径。

### B. 已在 worktree / gnhf 分支上 resume

生命周期**已完成**时再跑 goal，可能立刻退出（`gnhf wrapped`、exit 0）——这是**正常**，不是失败。

要继续未完成的 run，使用 **beacon-run 自己的 resume**（在 run 目录或 gnhf 状态里），或提高 `--max-iterations` 使其 ≥ 当前已消耗迭代数。

### C. 只在当前分支跑（不建 worktree）

```bash
beacon-loop goal "..." \
  --branch-mode current-branch \
  --project .
```

### D. 预览不执行

```bash
beacon-loop goal "..." --dry-run --json | jq .beacon_run_command
```

### E. 直接调 beacon-run（跳过 loop 包装）

```bash
node packages/beacon-run/dist/cli.mjs \
  "你的目标" \
  --beacon --project-root . --beacon-version v1.6.0 \
  --feature <slug> --agent codex --worktree --max-iterations 25
```

## 5. 辅助命令（loop ledger）

这些主要服务 **R3 legacy delivery** 与 loop run 账本。默认 `goal` 委托路径以 **beacon-run 的 run 目录**为主（如 `.beacon/runs/`、`beacon-phase.json`）。

| 命令 | 用途 |
|------|------|
| `beacon-loop status [run-id]` | 查看 loop run 状态 |
| `beacon-loop resume <run-id>` | 恢复 legacy loop run |
| `beacon-loop stop <run-id> [--force]` | 停止 run |
| `beacon-loop runs query [--status s]` | 查询历史 run |
| `beacon-loop runs show <run-id>` | 详情 |
| `beacon-loop import-evidence <run-id>` | 导入证据到 Beacon |
| `beacon-loop review <run-id>` | 打印 `summary.md` |
| `beacon-loop analyze / learn <run-id>` | harness 分析/学习 |

## 6. Legacy delivery（R3 FSM）

```bash
beacon-loop goal "..." \
  --legacy-delivery \
  --mode delivery \
  --agent implement-harness \
  --max-iterations 1
```

走 `packages/beacon-loop/src/delivery/*` 状态机（intent → review → truth_fill → implement → qa → release invoke）。

v1.6.0 主路径已迁到 **beacon-run + phase harness**；legacy 仅用于兼容与对照。

## 7. 排错速查

| 现象 | 原因 | 处理 |
|------|------|------|
| `beacon_run_cli_missing` | 找不到 `beacon-run` | build `packages/beacon-run`；或设 `BEACON_RUN_CLI` |
| `feature_slug_required` | 无法推断 feature | 加 `--feature <slug>` |
| goal 秒退、exit 0 | lifecycle 已完成 | 正常；换 feature 或新 worktree |
| harness repair 循环 | infra/QA 失败 | 看 `beacon-phase.json` 的 `last_harness_exit`；修 gate/QA 后 resume |
| TUI 乱码/无交互 | 非 TTY 环境 | 在真实终端跑；CI 用 pipe 模式 |
| `--max-iterations` 太小 | 绝对计数已耗尽 | 设更大值（≥ 已跑迭代数） |

### 建议诊断顺序

```bash
beacon-loop doctor --project . --diagnose --json
beacon doctor verify-context --project-root . --strict
beacon truth-map resolve <feature> --project . --version v1.6.0 --json
beacon status --verbose
# worktree 内
cat beacon-phase.json
```

## 8. 与 Beacon 其它面的关系

```text
Operator
  → beacon-loop goal
    → beacon-run --beacon
      → truth phase (agent)     → features/<slug>/truth.md
      → generate phase (agent)  → repo / worktree code
      → qa harness              → .beacon/qa evidence
      → release harness         → release-gate-report.json
```

- **需求真相**：`docs/beacon/v1.6.0/features/<slug>/truth.md`（resolver-first）
- **人工干预**：Cursor/Codex 里仍可用 `beacon-pln-review`、`beacon-gen-implement` 等 skills
- **Release 判定**：以 `beacon release check v1.6.0` / gate 为准，不是 loop stdout

## 9. 本机快速验证（beacon 仓）

```bash
cd /path/to/beacon

beacon --version
beacon-loop doctor --project .

beacon-loop goal "smoke: verify beacon-loop delegates to beacon-run" \
  --dry-run --json \
  --feature beacon-loop-goal-closed-loop-orchestrator \
  --version v1.6.0
```

## 相关文档

- Feature truth：`docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- Architecture：`docs/beacon/v1.6.0/execution/architecture-blueprint.md`
- Automation retirement：`automation/README.md`
- Post-release install：`docs/beacon/hooks/beacon-post-release-local-install.md`
