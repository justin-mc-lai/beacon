---
slug: beacon-loop-native-runner-and-automation-retirement
version: v1.6.0
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md
  user_story: docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md
  test_case: docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# 需求真相：Beacon Loop Native Runner and Automation Retirement

## 概述

`beacon-loop-native-runner-and-automation-retirement` 定义 Beacon v1.6.0 的长任务执行架构调整：

```text
beacon       -> Python governance kernel: truth, delivery, QA, release
beacon-loop  -> TypeScript native runner: long loop, agent process, git/worktree, resume
```

目标是移除旧 `beacon automation` 业务代码，把长任务保活、agent loop、分支/worktree、resume、iteration commit 和 stop condition 从 Beacon 内核移到同仓库的外置 CLI `beacon-loop`。

Beacon 继续作为唯一 requirement truth、delivery evidence、QA 和 release gate 内核。`beacon-loop` 只能执行长任务并产出 implementation evidence candidate，不能自证完成，不能给 QA/release verdict。

## Scope Mode

本 feature 的 `scope_mode` 为 **`full_parity`**：

- **gnhf**（`https://github.com/kunchenguid/gnhf`）：长跑 agent orchestrator 的完整 runner 语义（多轮 loop、commit/rollback/repair、resume/stop、caps、多 agent、exit summary）。
- **manage-oss-sync**：成熟本地 harness 模式（统一 CLI、`--json`、SQLite/索引层、query/show、diagnose 分桶、runtime 追踪、站外 analyze/learn），**不**复制 OSS 镜像库业务（scan/import/sync 镜像仓库）。

实现与验收必须走 Beacon 真相生命流程：

```text
truth (frozen) -> beacon-loop goal -> runtime evidence -> import-evidence -> beacon qa -> beacon release
```

任何从 `full_parity` 到 MVP 的降级必须进入 `Deferral Ledger` 并获用户显式接受。本 change 仅接受 D-005..D-008（见下）为显式 defer。

## 背景

Beacon 当前存在 `automation` support surface：

```text
beacon/commands/automation.py
beacon/utils/automation_*.py
automation/jobs/
automation/launchd/
automation/beacon-automation-queue.json
automation/README.md
```

该面以 queue、shell job 和 host scheduler 为核心，适合定时 status、QA summary、repair window 等任务，但不适合承担长时间 agent loop 保活。

新的架构必须把长跑执行外置到 `beacon-loop`，同时保留 Beacon truth/gate 作为闭环 authority。

## Lifecycle Boundary

本 feature 不改变 Beacon v1.6.0 的 human-facing lifecycle：

```text
plan -> truth -> generate -> evaluate -> release
```

`beacon-loop` 不是新的主生命周期阶段。它是外置 execution runner，位置在 `generate` 的实现执行面之下，并通过 Beacon 的 evidence import、QA 和 release gate 回到主链。

## Command Naming

正式入口必须是：

```bash
beacon-loop goal "<goal>"
```

`goal` 表示用户提交的是目标，不是 frozen feature truth、不是 implementation closure、不是 QA pass、不是 release readiness。

禁止暴露以下入口：

```bash
beacon-loop lfg "<goal>"
```

不得保留 `lfg` alias、deprecated alias、compatibility route、help hint、文档推荐或测试容忍项。

## Repository Shape

Beacon 仓库必须整理为双 CLI monorepo：

```text
beacon/
  beacon/
  packages/beacon-loop/
    src/
      cli.ts
      runner/
      git/
      agents/
      beacon/
      evidence/
      ledger/
      templates/
    tests/
  docs/beacon/v1.6.0/
  tests/
```

安装后应有两个独立 CLI：`beacon` 与 `beacon-loop`。

## Automation Retirement

旧 `automation` 业务面必须退役（AC-001）。如需过渡，只允许极薄 blocking stub：`automation retired; use beacon-loop goal`。

## State Model

`state_machine_required`: **true**

长跑 run 的状态机是 requirement truth 的一部分，不是实现注释。

### States

| State | 含义 |
|-------|------|
| `preflight_blocked` | resolver / git / dirty worktree 阻断 |
| `run_initialized` | run-package 已写，尚未进入 agent |
| `iterating` | agent 子进程活跃 |
| `iteration_success_commit` | 本轮 commit 成功 |
| `iteration_fail_rollback` | 本轮 rollback 完成 |
| `repair_required` | commit failure，保留未提交工作区 |
| `waiting_backoff` | 可重试硬错误指数退避 |
| `graceful_stop_pending` | 等待当前 iteration 结束 |
| `force_stopped` | 立即终止 |
| `cap_reached` | max-iterations / max-tokens / stop-when 触发 |
| `implementation_candidate` | 可 import 的 runtime evidence |
| `evidence_imported` | Beacon implement import 完成 |
| `qa_pending` | 等待 Beacon QA |
| `release_pending` | 等待 Beacon release |
| `terminal_closed` | QA/release accept（仅 Beacon 裁决） |

### Allowed Transitions

```text
preflight_blocked -> run_initialized | terminal_closed(abort)
run_initialized -> iterating
iterating -> iteration_success_commit | iteration_fail_rollback | repair_required | force_stopped | cap_reached
iteration_success_commit -> iterating | cap_reached | graceful_stop_pending
iteration_fail_rollback -> iterating | waiting_backoff | terminal_closed(consecutive_failures_abort)
repair_required -> iterating(resume) | force_stopped
waiting_backoff -> iterating
graceful_stop_pending -> cap_reached | force_stopped
implementation_candidate -> evidence_imported
evidence_imported -> qa_pending
qa_pending -> release_pending | repair_required(route change)
release_pending -> terminal_closed
```

### Invalid Transitions

- `implementation_candidate` -> `terminal_closed`（禁止 loop 自证完成）
- `iterating` -> `qa_pending`（禁止跳过 evidence import）
- 任意状态 -> `terminal_closed` 且未经过 Beacon evaluator/release

### Recovery / Resume / Rollback

- `repair_required` + `beacon-loop resume <run-id>` -> 继续 `iterating`，iteration 编号递增
- `iteration_fail_rollback` -> `git reset --hard` 到 iteration 前 HEAD（commit failure 除外）
- `resume` 必须复用既有 run metadata、`notes.md`、branch/worktree，不得新建无关 run

### Terminal States

`preflight_blocked`、`cap_reached`（abort 变体）、`terminal_closed`（仅 Beacon QA/release）

### Side Effects

| Transition | Artifacts |
|------------|-----------|
| `run_initialized` | `.beacon/loop/runs/<id>/run-package.json`, `prompt.md`, `notes.md`, `output-schema.json` |
| `iterating` | `iteration-<n>.jsonl`, `iteration-<n>-result.json`, optional debug log |
| `iteration_success_commit` | `commits.json` 追加, `notes.md` 追加 |
| `repair_required` | `repair-state.json` |
| `cap_reached` | `summary.md`, exit summary stdout |
| `evidence_imported` | Beacon feature `evidence.md` 候选条目（非 verdict） |

## Source Capability Inventory

### gnhf（agent orchestrator）

| 能力 | 源证据 | Beacon 落点 |
|------|--------|-------------|
| 多轮 iteration loop | `gnhf/src/core/orchestrator.ts` | `packages/beacon-loop/src/runner/orchestrator.ts` |
| 多 agent backend | `gnhf/src/core/agents/*` | `packages/beacon-loop/src/agents/*` |
| worktree / current-branch / push | gnhf README | `packages/beacon-loop/src/git/*` |
| notes 跨轮记忆 | `templates/iteration-prompt.ts` | `templates/iteration-prompt.ts` |
| commit / rollback / repair | orchestrator + git | runner + git |
| caps + stop-when | RunLimits | CLI flags + run-package |
| graceful + force stop | interrupt-state | stop 子命令 + signal handling |
| exit summary + review | exit-summary | `review`, `summary.md` |
| config.yml | `~/.gnhf/config.yml` | `~/.beacon-loop/config.yml` 或 project-local |
| debug JSONL | `.gnhf/runs/<id>/gnhf.log` | `.beacon/loop/runs/<id>/beacon-loop.log` |

### manage-oss-sync（harness 模式，非 OSS 业务）

| 能力 | 源证据 | Beacon 落点 |
|------|--------|-------------|
| 统一 CLI + `--json` | `manage_oss_sync.py` | `beacon-loop` 全子命令 |
| SQLite 机器层 | `oss-sync.db` | `.beacon/loop/ledger/loop-runs.db` |
| query / show | query, show | `beacon-loop runs query`, `runs show` |
| sync-diagnose 分桶 | sync-diagnose | `beacon-loop runs diagnose` |
| analyze / learn 站外 | `index/analysis`, `index/learning` | `.beacon/loop/index/analysis|learning/` |
| runtime-set/list/remove | runtime-* | `beacon-loop runtime-set|list|remove` |
| planner inventory 衔接 | `beacon/utils/oss_sync_inventory.py` | planner source-parity 只读；loop 不复制 |

## Parity Matrix

| Source capability | Target truth | Target tests | Target evidence | Status | Deferral |
|-------------------|--------------|--------------|-----------------|--------|----------|
| automation retirement | AC-001 | TC-001, TC-002 | python tests | covered | none |
| independent CLI package | AC-002 | TC-003 | npm build | covered | none |
| goal-only entry (no lfg) | AC-003 | TC-004, TC-005 | CLI help | covered | none |
| resolver preflight | AC-004, AC-005 | TC-006, TC-007 | resolve.ts | covered | none |
| runtime package artifacts | AC-006 | TC-008 | run dir | partial | none |
| git isolation | AC-007 | TC-009 | git tests | partial | none |
| commit/rollback/repair | AC-008 | TC-010 | runner tests | partial | none |
| true resume | AC-009, AC-017 | TC-011, TC-018 | resume | **missing** | none |
| evidence import | AC-010 | TC-012 | importer | partial | none |
| no QA/release verdict | AC-011 | TC-013 | payloads | covered | none |
| goal naming docs | AC-012 | TC-014 | rg | covered | none |
| test suite | AC-013 | TC-015 | pytest/npm | partial | none |
| runtime ≠ truth | AC-014 | TC-016 | artifacts | covered | none |
| doctor | AC-015 | TC-017 | doctor | partial | none |
| multi-iteration orchestrator | AC-016 | TC-019 | orchestrator | **missing** | none |
| notes injection | AC-020 | TC-020 | prompt template | **missing** | none |
| graceful/force stop | AC-018 | TC-021 | stop + signals | **missing** | none |
| failure backoff / consecutive cap | AC-019 | TC-022 | orchestrator | **missing** | none |
| exit summary richness | AC-021 | TC-023 | summary | **missing** | none |
| run ledger query/show | AC-022 | TC-024, TC-025 | ledger | **missing** | none |
| runs diagnose | AC-023 | TC-026 | diagnose | **missing** | none |
| runtime tracking | AC-024 | TC-027 | runtime-* | **missing** | none |
| analyze/learn 站外 | AC-025 | TC-028 | index/ | **missing** | none |
| branch modes + invalid combos | AC-026 | TC-029 | git | **missing** | none |
| config file | AC-027 | TC-030 | config | **missing** | none |
| multi-agent adapters | AC-028, AC-029 | TC-031, TC-032 | agents/ | **missing** | Phase B |
| closed-loop E2E | AC-030 | TC-033 | E2E | **missing** | none |
| TUI / telemetry / prevent-sleep | — | — | — | out of scope | D-005..D-007 accepted |

## Deferral Ledger

| deferral_id | capability | reason | impact | user_decision | expiry_or_revisit | recommended_route |
|-------------|------------|--------|--------|---------------|-------------------|---------------------|
| D-005 | TUI / live terminal title | 非闭环关键路径；gnhf 体验增强 | 无 TUI 状态条 | accepted | v1.6.x patch | defer |
| D-006 | Anonymous telemetry | Beacon 治理边界外 | 无远程统计 | accepted | v1.6.x patch | defer |
| D-007 | prevent-sleep OS hook | 可选运维能力 | 长跑可能受系统睡眠影响 | accepted | v1.6.x patch | defer |
| D-008 | stdin prompt 交互 | 需 TTY 冲突处理 | 仅 CLI 参数 goal | accepted | v1.6.x patch | defer |

未列入 deferral 的 gnhf / harness 能力均视为 **in-scope**，不得再以「第一版」静默裁剪。

## Delivery Phases

实现可按 phase 交付，但 **truth/tests 一次性冻结 full parity**；phase 只影响实现顺序，不缩小 AC。

| Phase | 范围 | AC 子集 |
|-------|------|---------|
| A | Orchestrator 多轮、caps、真 resume/stop、notes、exit summary、codex 真跑 | AC-016..AC-021, AC-008..AC-009 加强 |
| B | Run ledger、query/show/diagnose、runtime 追踪、analyze/learn | AC-022..AC-025 |
| C | 额外 agent adapters（claude、acp 最小）、branch modes、config | AC-026..AC-029 |
| D | Closed-loop E2E（goal -> import -> qa 契约测试） | AC-030 |

## Beacon Integration Contract

`beacon-loop goal "<goal>"` 启动前必须通过 Beacon CLI 读取 resolver-selected truth：

```bash
beacon truth-map resolve "<feature-or-goal-slug>" --project . --version v1.6.0 --json
```

resolver blocked 时 fail closed，路由 `beacon-gen-change`。

Runtime package 根目录：

```text
.beacon/loop/runs/<run-id>/
  run-package.json
  prompt.md
  notes.md
  output-schema.json
  iteration-<n>.jsonl
  iteration-<n>-result.json
  commits.json
  repair-state.json
  beacon-loop.log
  evidence.json
  summary.md
```

Run ledger（harness 层，非 requirement truth）：

```text
.beacon/loop/ledger/loop-runs.db
.beacon/loop/index/analysis/
.beacon/loop/index/learning/
```

## Closed Loop Contract

```text
1. beacon-loop goal "<goal>"
2. beacon-loop resolves Beacon truth
3. beacon-loop runs iterative implementation in branch/worktree
4. beacon-loop writes runtime evidence candidate
5. beacon-loop import-evidence -> beacon implement import-evidence
6. beacon qa run
7. beacon release create/check
8. only Beacon evaluator/release surfaces mark closure
```

## CLI Surface

```bash
beacon-loop goal "<goal>"
beacon-loop status [run-id]
beacon-loop stop <run-id> [--force]
beacon-loop resume <run-id>
beacon-loop review <run-id>
beacon-loop import-evidence <run-id>
beacon-loop doctor [--diagnose] [--json]
beacon-loop runs query [--status <s>] [--json]
beacon-loop runs show <run-id> [--json]
beacon-loop runs diagnose [--json]
beacon-loop analyze <run-id> [--json]
beacon-loop learn <run-id> [--json]
beacon-loop runtime-set <run-id> --status <running|stopped|error|degraded|starting> [--port N] [--notes <text>]
beacon-loop runtime-list [--status <s>] [--json]
beacon-loop runtime-remove <run-id>
```

默认策略：`--branch-mode worktree`、`--push false`、`--agent codex`、`--max-iterations` 必填或配置、`--stop-when` 必填或从 tests 派生、dirty worktree 默认阻断。

## Agent Adapter Boundary

Phase A 必须完成 **codex** 真多轮 adapter。Phase C 至少再完成 **claude** 与 **acp:&lt;target&gt;** 两个 adapter。每个 adapter 输出 structured iteration result：`success`, `summary`, `key_changes_made`, `key_learnings`, optional stop signal, token usage。

## Non-goals

- 重写 Beacon truth-map resolver
- 改变 v1.6.0 lifecycle
- `beacon-loop` 直接给 QA/release verdict
- `beacon-loop lfg` alias
- 旧 automation queue/launchd 业务
- Mastra / VoltAgent / LangGraph 作为主 runtime
- **manage-oss-sync 的 OSS 镜像业务**（scan/import/sync 第三方仓库)
- **D-005..D-008** 所列 TUI / telemetry / prevent-sleep / stdin UX（已 defer）

## Acceptance Criteria

| AC ID | Acceptance Criteria |
|---|---|
| AC-001 | `beacon automation` 业务代码退役，不再作为 active command surface 暴露或执行旧 queue/job/launchd 业务。 |
| AC-002 | 仓库包含 `packages/beacon-loop`，并能独立构建出 `beacon-loop` CLI。 |
| AC-003 | `beacon-loop goal "<goal>"` 是唯一 goal entrypoint；不存在 `beacon-loop lfg` alias、deprecated alias、compatibility route 或 help hint。 |
| AC-004 | `beacon-loop goal` 启动前调用 `beacon truth-map resolve ... --json` 并记录 resolver refs。 |
| AC-005 | resolver blocked、feature package 缺失或 truth/test gap 存在时，`beacon-loop` fail closed，并推荐 `beacon-gen-change`。 |
| AC-006 | resolver pass 时，`beacon-loop` 创建完整 runtime package（含 iteration logs、`evidence.json`、`summary.md`）。 |
| AC-007 | runner 默认使用 branch/worktree isolation，dirty worktree 下 fail closed，除非显式 controlled mode。 |
| AC-008 | 成功 iteration 自动 commit；失败 iteration rollback；commit failure 进入 repair state，且 resume 可继续。 |
| AC-009 | `beacon-loop resume <run-id>` 从既有 run metadata、notes 和 branch/worktree 状态恢复，而不是创建无关新运行。 |
| AC-010 | `beacon-loop import-evidence <run-id>` 调用 Beacon implementation evidence import。 |
| AC-011 | Beacon QA/release 仍然是唯一 closure verdict；`beacon-loop` output 不得声明 QA pass、release ready 或 feature complete。 |
| AC-012 | docs、help、tests、command catalog 和 skill routing 全部使用 `goal` 命名，不出现 active `lfg` route。 |
| AC-013 | 旧 automation tests 被删除或重写为 retirement negative tests；新增 `beacon-loop` CLI/package/runner/evidence/ledger tests。 |
| AC-014 | runtime artifacts 明确标记为 runtime process record，不是 requirement truth，不写 `.machine` requirement projection。 |
| AC-015 | `beacon-loop doctor` 检查 Beacon CLI、Node runtime、agent backend、git/worktree 和 evidence import prerequisites；`--diagnose` 输出可行动分桶。 |
| AC-016 | orchestrator 支持多轮 iteration，直到 `--max-iterations`、`--max-tokens` 或 `--stop-when` 触发 `cap_reached`。 |
| AC-017 | `resume` 继续下一轮 iteration 编号（N+1），复用同一 run-id 与 worktree/branch。 |
| AC-018 | graceful stop 等待当前 iteration 结束；`--force` 立即进入 `force_stopped`。 |
| AC-019 | agent-reported failure 立即下一轮；retryable hard error 指数退避；连续失败达上限 abort；no-op iteration 计为 failure。 |
| AC-020 | 每轮 iteration prompt 注入累积 `notes.md` 上下文。 |
| AC-021 | exit summary / `summary.md` 含 elapsed time、branch、iteration/token totals、artifact paths、后续 review/import/qa 命令。 |
| AC-022 | `.beacon/loop/ledger/loop-runs.db` 记录 run 索引；`runs query` / `runs show` 提供 `--json` 机器可读输出。 |
| AC-023 | `runs diagnose` 将 blocked/dirty/missing-backend/never-started 等状态分桶，并给出 repair route。 |
| AC-024 | `runtime-set` / `runtime-list` / `runtime-remove` 追踪活跃 loop 进程状态，与 ledger 关联。 |
| AC-025 | `analyze` / `learn` 在 `.beacon/loop/index/` 生成站外分析/学习笔记，不污染 requirement truth。 |
| AC-026 | 支持 `worktree`、`current-branch`、`beacon-loop/<run-id>` branch 模式；禁止非法组合（如 current-branch + worktree）。 |
| AC-027 | 支持 `~/.beacon-loop/config.yml`（或 project-local）配置默认 agent、path override；CLI flags 覆盖 config。 |
| AC-028 | Phase A 完成 codex 真多轮 adapter（非仅 fixture 单次）。 |
| AC-029 | Phase C 至少完成 claude 与 `acp:<target>` adapter，输出同一 structured schema。 |
| AC-030 | E2E 契约：`goal` -> 多轮 candidate -> `import-evidence` -> `beacon qa run` 可被自动化测试驱动（qa verdict 仍由 Beacon 产出）。 |

## Source Advisory

| Artifact | Role |
|----------|------|
| `docs/beacon/v1.6.0/research/beacon-loop-native-runner-and-automation-retirement.md` | 初始 support_advisory（已 promoted） |
| `docs/beacon/v1.6.0/change/beacon-loop-native-runner-and-automation-retirement.md` | R2 change record（full parity reopen） |
| `/Users/apple/Developer/Personal/oss-sync/agents/agent-systems/gnhf` | gnhf source mirror |
| `manage-oss-sync` skill | harness pattern reference |

本文件为 package-authoritative requirement truth。
