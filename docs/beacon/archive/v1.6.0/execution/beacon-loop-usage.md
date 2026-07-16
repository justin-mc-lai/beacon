# beacon-loop 使用指南（v1.6.0 / v1.6.1 止血）

Canonical operator doc for the native long-loop entrypoint. Automation queue/job/launchd assets are retired; use `beacon-loop` instead.

**v1.6.1 止血（R10）** 在默认 `goal → beacon-run` 路径上补齐三件事：

1. **Worktree 不断链**：agent 与 harness 的 `project-root` / cwd 对齐到同一 worktree，避免主仓 `sync-materials` 误伤。
2. **State spine 查询**：不用手拼四份 state 文件；一条命令看进度（见 §2.1）。
3. **Stop-when 可验证**：`--stop-when` 不能靠 agent 自说自话结束；须 harness 或 `--stop-check-cmd` exit 0（见 §3）。

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

### 2.1 查进度（state spine）

不用打开 `beacon-phase.json`、`run-package.json`、ledger 四处找——用 spine：

```bash
# 最新 run
beacon-loop spine show --project . --json

# 指定 run
beacon-loop spine show --run-id <id> --project . --json

# 等价别名
beacon-loop status --spine --project . --json
```

JSON 含 `phase`、`phases_completed`、`phase_promoted`、`next_harness`、`next_action`、`authoritative_paths[]`、`run_id`。

字段语义与权威文件清单见 [`beacon-loop-state-spine.md`](./beacon-loop-state-spine.md)。

## 3. 常用参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--project` | cwd | 项目根 |
| `--version` | `auto` | Beacon docs 版本，如 `v1.6.0` |
| `--feature` | 自动推断 | feature slug；推断失败会 `feature_slug_required` |
| `--agent` | `codex` | `codex` / `claude` / `acp:...` |
| `--max-iterations` | `8` | **总迭代上限**（绝对计数，非「再跑 N 轮」） |
| `--max-tokens` | `0` | `0` = 不限制 |
| `--stop-when` | — | 自然语言停止条件（**须**配合外部验证，见下） |
| `--stop-check-cmd` | — | shell 命令；exit 0 才允许因 stop-when 停迭代（AC-071） |
| `--branch-mode` | `worktree` | `worktree` / `current-branch` / `run-branch` |
| `--mode` | `delivery` | `delivery` / `execute-only` / `intent-only` / `review-only` |
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

### Stop-when：写代码的人不能给自己打分 done

Loop Engineering 对齐：**agent 结构化输出里写「stop-when matched」不算完成**。

每轮 agent 之后至少要有一种 **外部可验证** 的检查通过：

| 方式 | 何时生效 |
|------|----------|
| 阶段 harness | 默认：`beacon qa run` / phase 对应 gate exit 0 |
| `--stop-check-cmd` | 你显式给的 shell（如 `npm test`、`go test ./...`）exit 0 |
| Terminal harness | lifecycle 已到 qa/release evaluator |

仅 agent 自报 → `reason_code=stop_when_unverified`，**继续下一 iteration**，不会 silent done。

```bash
beacon-loop goal "修完 login 空邮箱 bug 且单测全绿" \
  --feature auth-login-fix \
  --stop-when "login 空邮箱用例通过" \
  --stop-check-cmd "cd services/auth && go test ./... -run TestLoginEmptyEmail" \
  --max-iterations 8
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `BEACON_RUN_CLI` | 显式指定 `beacon-run` 的 `cli.mjs` 路径 |
| `BEACON_LOOP_IMPLEMENT_RUNNER` | 默认 implement runner |

## 4. 示例一览（从小到大）

下面四条是**同一套 CLI**、不同目标粒度。共性：

- 默认 **`delivery`**：intent → truth → generate → qa → release harness。
- 默认 **`worktree`**：改代码在隔离 worktree，主分支保持干净。
- **`--feature`** 尽量显式写 slug（推断失败会 `feature_slug_required`）。
- 大任务提高 **`--max-iterations`**（绝对计数，不是「再跑 N 轮」）。

意图分类（deterministic，见 truth AC-032）会从 goal 文案里读信号：

| 你写的关键词 | 典型 `scope_mode` / class |
|--------------|---------------------------|
| 修 bug / hotfix / 修复 | `patch` |
| 完整复刻 / 全量 / parity | `full_parity` |
| 调研 / 探索 | `research`（不进 implement） |
| frozen + 只跑实现 | `execute_bound` → 用 `--mode execute-only` |

---

### 示例 1 — 修一个已知问题（最小）

**场景**：生产上「空邮箱登录返回 500」，truth 可能还没有，或已有 frozen patch feature。

**路径 A — 从零走闭环（推荐首次）**

```bash
cd /path/to/your-app

beacon-loop goal "修复 auth 登录：email 为空时返回 400 而不是 500，补单测" \
  --project . \
  --version v1.6.0 \
  --feature auth-login-empty-email-fix \
  --agent codex \
  --max-iterations 10 \
  --stop-when "空邮箱登录用例通过" \
  --stop-check-cmd "cd services/auth && go test ./... -run TestLoginEmptyEmail"
```

**路径 B — truth 已 frozen，只跑实现 + QA**

```bash
beacon-loop goal "按 features/auth-login-empty-email-fix/truth.md 实现并过 QA" \
  --mode execute-only \
  --feature auth-login-empty-email-fix \
  --project . \
  --version v1.6.0 \
  --max-iterations 8
```

**你会看到什么**：worktree 里改 `services/auth/` → harness 跑 test/qa → spine 里 `phase` 从 `generate` 走向 `qa`。

**查进度**：

```bash
beacon-loop spine show --project . --json | jq '{phase, next_action, phase_promoted}'
```

---

### 示例 2 — 局部重构（中等）

**场景**：把 `payment` 模块从 handler 里抽成 service 层，接口行为不变，测试不回归。

```bash
cd /path/to/your-app

beacon-loop goal "重构 payment 模块：提取 PaymentService，handler 只编排；行为不变，现有测试全绿" \
  --project . \
  --version v1.6.0 \
  --feature payment-service-extraction \
  --agent codex \
  --max-iterations 20 \
  --stop-check-cmd "npm test -- payment"
```

**要点**：

- goal 里写清 **边界**（只动 payment、不改 API 契约）比写「重构一下」省迭代。
- `--stop-check-cmd` 绑在你已有的 payment 测试套件上，避免 agent 自报「重构完成」。
- 若 truth 里 `scope_mode` 是 `mvp`，freeze gate 走 smoke 路径；全量 parity 会走 `sync-materials` 链（更慢但更严）。

---

### 示例 3 — 接手现有项目，加一块能力（中偏大）

**场景**：brownfield——已有电商后台，要加 OAuth2 登录，不动订单核心。

```bash
cd /path/to/ecommerce-admin

# 首次接入 Beacon 上下文（一次性）
beacon init --apply
beacon doctor setup-context --project-root .
beacon doctor verify-context --project-root . --strict

beacon-loop goal "在现有 admin 加 OAuth2 登录（Google/GitHub），保留邮箱密码登录；文档写进 features/oauth-login/truth.md" \
  --project . \
  --version v1.6.0 \
  --feature oauth-login \
  --agent codex \
  --max-iterations 35
```

**要点**：

- 先说 **保留什么、新增什么**（intent contract 会记 verbatim utterance）。
- 大改动默认 worktree；合并前在主仓 review worktree diff。
- QA/release verdict 仍以 `beacon qa` / `beacon release check` 为准，不是 loop stdout。

---

### 示例 4 — 复刻 / 对标开源项目（最大）

**场景**：对标 `https://github.com/todosaurus/todo-api`（示例名），在本仓 `examples/todo-api/` 做 **full parity** 最小可运行版 + Beacon truth + QA。

```bash
cd /path/to/greenfield-or-examples-repo

beacon init --apply
beacon doctor setup-context --project-root .

beacon-loop goal "完整复刻 todosaurus/todo-api 的核心 REST API（CRUD + 健康检查），代码落在 examples/todo-api，不要 MVP 裁剪，truth 与 tests 对齐开源行为" \
  --project . \
  --version v1.6.0 \
  --feature todo-api-parity \
  --agent codex \
  --max-iterations 50 \
  --stop-check-cmd "cd examples/todo-api && go test ./... && curl -sf http://127.0.0.1:8080/health"
```

**要点**：

- goal 里 **「完整复刻 / full parity / 不要 MVP」** 会推高 `scope_mode`，freeze gate 走 full sync 链。
- 迭代预算给足（30–50+）；中途用 spine 看卡在哪一 phase。
- 可选 **dry-run** 先看委托命令：

```bash
beacon-loop goal "..." --feature todo-api-parity --dry-run --json | jq .beacon_run_command
```

- Beacon 仓内回归夹具（worktree + smoke）：`--feature go-todo-crud-smoke` + utterance 含 `examples/go-todo-crud`（见 truth R5/R6）。

---

### 示例对照表

| 级别 | 目标类型 | 建议 `--mode` | 典型 `--max-iterations` | 是否建议 `--stop-check-cmd` |
|------|----------|---------------|-------------------------|----------------------------|
| 1 小 | 单 bug / hotfix | `delivery` 或 `execute-only`（truth 已冻） | 8–12 | **强烈建议** |
| 2 中 | 模块重构 | `delivery` | 15–25 | **建议** |
| 3 中大 | brownfield 新能力 | `delivery` | 25–40 | 可选（用模块测试） |
| 4 大 | 开源复刻 / full parity | `delivery` | 40–60+ | 可选（集成测试/health） |

---

## 5. 其它典型场景

### A. 在业务项目里跑 smoke / drill

```bash
cd /path/to/examples/go-todo-crud

beacon-loop goal "完成 go-todo-crud smoke：truth frozen 后实现并通过 native QA" \
  --project . \
  --version v1.6.0 \
  --feature go-todo-crud-smoke \
  --max-iterations 30
```

Worktree 一般在 `../beacon-gnhf-worktrees/<slug>-*` 或 `<repo>-gnhf-worktrees/*` 一类路径。

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

## 6. 辅助命令（loop ledger）

默认 `goal → beacon-run` 路径以 **`.gnhf/runs/<id>/beacon-phase.json`** 为主进度；legacy loop 账本在 `.beacon/loop/runs/`。

| 命令 | 用途 |
|------|------|
| `beacon-loop spine show [--run-id]` | **推荐** — operator 进度 spine（AC-070） |
| `beacon-loop status --spine` | 同上 |
| `beacon-loop status [run-id]` | 查看 loop run 状态 |
| `beacon-loop resume <run-id>` | 恢复 legacy loop run |
| `beacon-loop stop <run-id> [--force]` | 停止 run |
| `beacon-loop runs query [--status s]` | 查询历史 run |
| `beacon-loop runs show <run-id>` | 详情 |
| `beacon-loop import-evidence <run-id>` | 导入证据到 Beacon |
| `beacon-loop review <run-id>` | 打印 `summary.md` |
| `beacon-loop analyze / learn <run-id>` | harness 分析/学习 |

## 7. Legacy delivery（R3 FSM）

```bash
beacon-loop goal "..." \
  --legacy-delivery \
  --mode delivery \
  --agent implement-harness \
  --max-iterations 1
```

走 `packages/beacon-loop/src/delivery/*` 状态机（intent → review → truth_fill → implement → qa → release invoke）。

v1.6.0 主路径已迁到 **beacon-run + phase harness**；legacy 仅用于兼容与对照。

## 8. 排错速查

| 现象 | 原因 | 处理 |
|------|------|------|
| `beacon_run_cli_missing` | 找不到 `beacon-run` | build `packages/beacon-run`；或设 `BEACON_RUN_CLI` |
| `feature_slug_required` | 无法推断 feature | 加 `--feature <slug>` |
| goal 秒退、exit 0 | lifecycle 已完成 | 正常；换 feature 或新 worktree |
| harness repair 循环 | infra/QA 失败 | 看 `beacon-phase.json` 的 `last_harness_exit`；修 gate/QA 后 resume |
| TUI 乱码/无交互 | 非 TTY 环境 | 在真实终端跑；CI 用 pipe 模式 |
| `--max-iterations` 太小 | 绝对计数已耗尽 | 设更大值（≥ 已跑迭代数） |
| `stop_when_unverified` | agent 自报 stop 但检查未过 | 加/修 `--stop-check-cmd` 或等 phase harness |
| `test_case_sync_failed`（worktree） | harness 对主仓 sync | 确认 v1.6.1+；harness cwd 应对齐 worktree |
| `revision_not_frozen` 空转 | generate 在 draft truth 上跑 | 等 truth phase freeze；看 spine `phase_promoted` |

### 建议诊断顺序

```bash
beacon-loop doctor --project . --diagnose --json
beacon-loop spine show --project . --json
beacon doctor verify-context --project-root . --strict
beacon truth-map resolve <feature> --project . --version v1.6.0 --json
beacon status --verbose
# worktree 内
cat .gnhf/runs/*/beacon-phase.json
```

## 9. 与 Beacon 其它面的关系

```text
Operator
  → beacon-loop goal
    → beacon-run --beacon
      → truth phase (agent)     → features/<slug>/truth.md
      → generate phase (agent)  → repo / worktree code
      → qa harness              → .beacon/qa evidence
      → release harness         → release-gate-report.json
```

- **需求真相**：`docs/beacon/archive/v1.6.0/features/<slug>/truth.md`（resolver-first）
- **人工干预**：Cursor/Codex 里仍可用 `beacon-pln-review`、`beacon-gen-implement` 等 skills
- **Release 判定**：以 `beacon release check v1.6.0` / gate 为准，不是 loop stdout

## 10. 本机快速验证（beacon 仓）

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

- State spine：`docs/beacon/archive/v1.6.0/execution/beacon-loop-state-spine.md`
- Feature truth：`docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`
- Architecture：`docs/beacon/archive/v1.6.0/execution/architecture-blueprint.md`
- Automation retirement：`automation/README.md`
- Post-release install：`docs/beacon/hooks/beacon-post-release-local-install.md`
