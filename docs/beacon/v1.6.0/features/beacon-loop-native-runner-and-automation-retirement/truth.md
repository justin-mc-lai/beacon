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

该面以 queue、shell job 和 host scheduler 为核心，适合定时 status、QA summary、repair window 等任务，但不适合承担长时间 agent loop 保活。原因：

- 它是调度器驱动，不是事件驱动的 agentic loop。
- 它缺少 per-iteration prompt、notes、commit、rollback、resume、stop condition 和 token cap 的统一协议。
- 它容易把长进程执行状态混入 Beacon governance 内核。
- 它把跨平台 process/signal/backend 兼容风险压到 Beacon Python CLI 内部。

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
    commands/
    utils/
  packages/
    beacon-loop/
      package.json
      src/
        cli.ts
        runner/
        git/
        agents/
        beacon/
        evidence/
        templates/
      tests/
  docs/beacon/v1.6.0/
  tests/
```

安装后应有两个独立 CLI：

```text
beacon
beacon-loop
```

`beacon-loop` 不得作为 `beacon automation` 的重命名实现，也不得隐藏在 Beacon Python subcommand 内。

## Automation Retirement

旧 `automation` 业务面必须退役：

- 删除 `beacon/commands/automation.py` 中的 automation business command surface。
- 删除或迁移 `beacon/utils/automation_*.py` 中只服务旧 automation queue/job 的业务逻辑。
- 删除 `automation/jobs/` 和 `automation/launchd/` 中的 host-scheduled job assets。
- 删除或停止维护 `automation/beacon-automation-queue.json`。
- 更新 `automation/README.md` 或删除旧 automation 文档，避免继续引导 queue/launchd 模式。
- 从 command catalog、CLI registration、help、intent routing、skill routing 和相关 tests 中移除 active `automation` surface。

如需短期过渡，只允许保留极薄 blocking stub：

```text
automation retired; use beacon-loop goal
```

stub 不得继续执行 queue runner、scheduler job、repair window 或 QA automation business logic。

## Beacon Loop Core Requirements

`beacon-loop` 必须吸收 gnhf 的关键 runner 能力，但以 Beacon 命名、目录、evidence contract 和 truth boundary 重新实现。

第一版核心能力：

- clean git preflight；
- branch/worktree isolation；
- run directory and resume；
- per-iteration prompt；
- `notes.md` cross-iteration memory；
- structured output schema；
- success commit；
- failure rollback；
- commit failure repair；
- max iterations / max tokens / stop condition；
- graceful stop and force stop；
- exit summary and review commands；
- multi-agent backend adapters。

第一版 runtime 应优先保持 Node 20-compatible TypeScript。Bun 可以作为开发、安装或打包加速，但核心 runtime 不得依赖 Bun-only API。

## Beacon Integration Contract

`beacon-loop goal "<goal>"` 启动前必须通过 Beacon CLI 读取 resolver-selected truth：

```bash
beacon truth-map resolve "<feature-or-goal-slug>" --project . --version v1.6.0 --json
```

如果 feature package 不存在、resolver blocked、truth 缺失或验收覆盖缺失，`beacon-loop` 必须 fail closed，并路由到：

```text
beacon-gen-change
```

不得在缺失 truth package 时直接启动 implementation loop。

当 resolver pass 时，`beacon-loop` 必须生成 runtime package：

```text
.beacon/loop/runs/<run-id>/
  run-package.json
  prompt.md
  notes.md
  output-schema.json
  iteration-001.jsonl
  iteration-001-result.json
  commits.json
  evidence.json
  summary.md
```

`run-package.json` 必须至少包含：

```json
{
  "schema_version": "1.0",
  "surface": "beacon-loop",
  "command": "goal",
  "goal": "<goal>",
  "feature": "<feature>",
  "version": "v1.6.0",
  "truth_refs": [],
  "test_refs": [],
  "task_refs": [],
  "evidence_refs": [],
  "agent": "codex",
  "branch_mode": "worktree",
  "stop_when": "<observable stop condition>",
  "beacon_commands": {
    "resolve_truth": "beacon truth-map resolve ...",
    "import_evidence": "beacon implement import-evidence ...",
    "qa": "beacon qa run ...",
    "release": "beacon release create ..."
  }
}
```

Runtime JSON 是 process record，不是 requirement truth。

## Closed Loop Contract

闭环必须是：

```text
1. beacon-loop goal "<goal>"
2. beacon-loop resolves Beacon truth
3. beacon-loop runs iterative implementation in branch/worktree
4. beacon-loop writes runtime evidence candidate
5. beacon-loop import-evidence calls Beacon implement evidence import
6. beacon qa run verifies against resolver-selected truth/tests
7. beacon release create/check performs release gate
8. only Beacon evaluator/release surfaces can mark closure
```

`beacon-loop` 的 success commit、exit summary 或 stop condition met 只能表示 implementation candidate，不得表示 Beacon closure。

## Minimum CLI Surface

第一版 `beacon-loop` 只暴露必要命令：

```bash
beacon-loop goal "<goal>"
beacon-loop status [run-id]
beacon-loop stop <run-id>
beacon-loop resume <run-id>
beacon-loop review <run-id>
beacon-loop import-evidence <run-id>
beacon-loop doctor
```

默认策略：

- `--branch-mode worktree`
- `--push false`
- `--agent codex`
- `--max-iterations` required or configured
- `--stop-when` required or generated from Beacon tests
- dirty worktree blocks unless an explicit controlled mode exists

## Agent Adapter Boundary

第一版至少支持 `codex` adapter。可扩展支持 `claude`、`opencode`、`aider` 或 `acp:<target>`，但 adapter 增加不得改变 Beacon integration contract。

每个 adapter 必须输出 structured iteration result，至少包含：

- `success`
- `summary`
- `key_changes_made`
- `key_learnings`
- optional stop-condition signal
- token usage when backend exposes it

## Non-goals

本 feature 不要求：

- 重写 Beacon truth-map resolver；
- 改变 v1.6.0 lifecycle；
- 让 `beacon-loop` 直接给 QA/release verdict；
- 保留 `beacon-loop lfg` alias；
- 继续维护旧 automation queue/launchd/hourly QA business logic；
- 在第一版引入 Mastra、VoltAgent 或 LangGraph 作为主 loop runtime。

## Acceptance Criteria

| AC ID | Acceptance Criteria |
|---|---|
| AC-001 | `beacon automation` 业务代码退役，不再作为 active command surface 暴露或执行旧 queue/job/launchd 业务。 |
| AC-002 | 仓库包含 `packages/beacon-loop`，并能独立构建出 `beacon-loop` CLI。 |
| AC-003 | `beacon-loop goal "<goal>"` 是唯一 goal entrypoint；不存在 `beacon-loop lfg` alias、deprecated alias、compatibility route 或 help hint。 |
| AC-004 | `beacon-loop goal` 启动前调用 `beacon truth-map resolve ... --json` 并记录 resolver refs。 |
| AC-005 | resolver blocked、feature package 缺失或 truth/test gap 存在时，`beacon-loop` fail closed，并推荐 `beacon-gen-change`。 |
| AC-006 | resolver pass 时，`beacon-loop` 创建 `.beacon/loop/runs/<run-id>/run-package.json`、`prompt.md`、`notes.md`、`output-schema.json`、iteration logs、`evidence.json` 和 `summary.md`。 |
| AC-007 | runner 默认使用 branch/worktree isolation，并在 dirty worktree 下 fail closed，除非显式 controlled mode 存在。 |
| AC-008 | 成功 iteration 自动 commit；失败 iteration rollback；commit failure 进入 repair state，且 resume 可继续。 |
| AC-009 | `beacon-loop resume <run-id>` 从既有 run metadata、notes 和 branch/worktree 状态恢复，而不是创建无关新运行。 |
| AC-010 | `beacon-loop import-evidence <run-id>` 调用 Beacon implementation evidence import，并把 runtime evidence candidate 接入 Beacon 可读实现证据面。 |
| AC-011 | Beacon QA/release 仍然是唯一 closure verdict；`beacon-loop` output 不得声明 QA pass、release ready 或 feature complete。 |
| AC-012 | docs、help、tests、command catalog 和 skill routing 全部使用 `goal` 命名，不出现 active `lfg` route。 |
| AC-013 | 旧 automation tests 被删除或重写为 retirement negative tests；新增 `beacon-loop` CLI/package/runner/evidence tests。 |
| AC-014 | runtime artifacts 明确标记为 runtime process record，不是 requirement truth，不写 `.machine` requirement projection。 |
| AC-015 | `beacon-loop doctor` 能检查 Beacon CLI 可用性、Node runtime、agent backend、git/worktree 能力和 evidence import prerequisites。 |

## Source Advisory

本需求由以下 `support_advisory` 晋升：

```text
docs/beacon/v1.6.0/research/beacon-loop-native-runner-and-automation-retirement.md
```

该 research 已由用户明确接受并要求冻结为需求真相。本文件成为 package-authoritative requirement truth。
