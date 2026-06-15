---
slug: beacon-loop-native-runner-and-automation-retirement
version: v1.6.0
authority: support_advisory
status: promoted
source: beacon-pln-brainstorm
created: 2026-06-09
updated: 2026-06-09
truth_refs:
  - docs/beacon/v1.6.0/SUMMARY.md
  - docs/beacon/v1.6.0/execution/boundaries.md
source_refs:
  - beacon/commands/automation.py
  - automation/jobs/
  - automation/launchd/
  - /Users/apple/Developer/Personal/oss-sync/agents/agent-systems/gnhf
  - /Users/apple/Developer/Personal/personal-brain/sources/web/mp-weixin-qq-com-superpowers-ai-51-agent-35.md
evidence_refs:
  - /Users/apple/Developer/Personal/oss-sync/index/analysis/kunchenguid-gnhf.md
  - /Users/apple/Developer/Personal/personal-brain/sources/oss-sync-notes/kunchenguid-gnhf/2026-06-09-104020.md
  - /Users/apple/Developer/Personal/personal-brain/projects/notes/beacon/2026-06-09-104021.md
user_decision: accepted
promotion_ref: docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md
---

# Beacon Loop Native Runner and Automation Retirement Research

## Support Advisory Contract

- authority: `support_advisory`
- status: `promoted`
- feature_slug: `beacon-loop-native-runner-and-automation-retirement`
- outcome: 收敛 Beacon v1.6.0 后续 change 的方案边界：移除旧 automation 业务代码，引入 gnhf-derived `beacon-loop` TS native runner，并用 `beacon-loop goal "<goal>"` 作为一步到位长任务入口。
- lake_or_ocean: 海。它同时触及 CLI 拆分、旧 automation 退役、TS/Bun/Node runner、git/worktree、agent backend、Beacon truth/evidence/QA/release 接入和打包发布，必须拆成正式 feature package 后分层交付。
- truth_gap: 当前 `features/beacon-loop-native-runner-and-automation-retirement/{truth,tests,tasks,evidence}.md` 不存在；本文件不能替代 requirement truth。
- test_gap: 需要新增 deterministic CLI/package tests、runner unit tests、Beacon evidence import integration tests、automation retirement negative tests。
- implementation_risk: high，风险来自删除旧 automation 面、双 CLI packaging、长进程 signal/resume、跨平台 child process、git rollback 和 Beacon truth/gate 串接。
- verification_risk: high，长 loop 成功 commit 不能等同 Beacon QA/release pass，必须保留 Beacon evaluator/gate 作为唯一闭环裁决。
- recommended_route: 已通过 `beacon-gen-change` 晋升为正式 feature package；后续进入 `beacon-gen-implement`。
- promotion_ref: `docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md`

## Decision Summary

目标不是在 Beacon 内部继续强化 `beacon automation`，而是把保活执行从 Beacon 内核移出，形成同仓库、双 CLI、单 truth 的结构：

```text
beacon       -> Python governance kernel: truth, delivery, QA, release
beacon-loop  -> TypeScript native runner: long loop, agent process, git/worktree, resume
```

`beacon-loop` 运行在一个 Beacon project 内，但作为外置 CLI 执行长任务。它必须通过 Beacon CLI 读取 truth、导入 implementation evidence，并让 Beacon QA/release 做最终裁决。

## Naming Decision

废弃 `lfg` 作为 Beacon command name。`lfg` 是 Compound Engineering 的体验隐喻，但 Beacon 需要更精确的执行语义：

```bash
beacon-loop goal "<goal>"
```

`goal` 明确表示用户提交的是目标，不是已经闭环的 feature truth，也不是 QA/release verdict。

不保留 `beacon-loop lfg "<goal>"` alias、deprecated alias 或 compatibility route。正式文档、truth、tests 和 help 只使用：

```bash
beacon-loop goal "<goal>"
```

## Target Repository Shape

建议将 Beacon 仓库整理为双 CLI monorepo，而不是把 `beacon-loop` 做成 Beacon Python 子命令：

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

发布形态：

```text
beacon       # existing Python CLI
beacon-loop  # new TS CLI
```

## Retire Old Automation

旧 automation 是 host-scheduled support surface，不适合承载长 loop agent 保活。它目前集中在：

```text
beacon/commands/automation.py
beacon/utils/automation_*.py
automation/jobs/
automation/launchd/
automation/beacon-automation-queue.json
automation/README.md
```

问题：

- queue/launchd/shell job 适合定时 QA、status、repair window，不适合事件驱动的 agentic loop。
- 缺少 per-iteration prompt、notes、commit、rollback、resume 和 stop condition 协议。
- 调度状态和执行状态容易混入 Beacon governance 面。
- Beacon 内核会承担长进程和 agent backend 兼容性风险。

退役策略：

1. 正式 feature package 中标记 `automation` command 业务面 retirement。
2. 删除 automation 业务逻辑和 launchd/job assets。
3. 如需过渡，只保留极薄 stub，输出 `automation retired; use beacon-loop goal`，不能继续维护 queue runner。
4. 从 command catalog、help、skill routing 和 tests 中移除 automation 作为默认支持面。

## Beacon Loop Core

`beacon-loop` 吸收 gnhf 的关键能力，而不是直接把 gnhf 原样放入 Beacon 内核：

- clean git preflight
- branch/worktree isolation
- run directory and resume
- per-iteration prompt
- `notes.md` cross-iteration memory
- structured output schema
- success commit
- failure rollback
- commit failure repair
- max iterations / max tokens / stop condition
- graceful stop and force stop
- exit summary and review commands
- multi-agent backend adapters

建议第一版 runtime 选择：

```text
TypeScript + Node 20-compatible runtime
Bun optional for dev/install speed, not required for core APIs
```

原因是长进程 runner 对 `child_process`、signals、stdio、Windows/macOS/Linux 行为敏感，Node 兼容面应先稳定。

## Beacon Integration Contract

`beacon-loop goal "<goal>"` 启动前必须调用 Beacon truth resolver：

```bash
beacon truth-map resolve "<feature-or-goal-slug>" --project . --version v1.6.0 --json
```

如果 feature package 不存在或 truth gap 明显，`beacon-loop` 必须阻断并路由：

```text
recommended_route = beacon-gen-change
```

如果 resolver 可用，生成 runtime package：

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

## Closed Loop Contract

`beacon-loop` 不能自证完成。闭环必须是：

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

对应命令：

```bash
beacon-loop goal "<goal>" --project . --version v1.6.0 --agent codex
beacon-loop status <run-id>
beacon-loop review <run-id>
beacon-loop import-evidence <run-id>
beacon qa run "<feature>" --project . --version v1.6.0
beacon release create "<feature>" --project . --version v1.6.0
```

## Compound Loop Mapping

Compound Engineering 的一步到位体验可借鉴，但 Beacon 术语应保持治理精确：

| Compound loop | Beacon-loop route |
| --- | --- |
| 想点子 | read strategy/research/context; detect lake/ocean |
| 聊清楚 | resolve Beacon truth; block on truth gap |
| 写计划 | create run-package and iteration plan |
| 动手干 | run native long loop in branch/worktree |
| 找毛病 | run checks, review diff, collect findings |
| 打磨好 | bounded repair/polish iteration |
| 记下来 | notes, evidence candidate, optional memory record |
| 再来一轮 | resume or new `beacon-loop goal` from findings |

`再来一轮` 是 loop edge，不是 Beacon lifecycle stage。

## Minimum CLI Surface

第一版只保留必要命令，避免重建 automation 复杂面：

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
- dirty worktree blocks unless explicit controlled mode exists

## Acceptance Shape for Future Truth

如果用户接受本 research，正式 truth/tests 应至少覆盖：

1. `automation` business code retired and no longer exposed as active command surface.
2. `packages/beacon-loop` builds as an independent CLI.
3. `beacon-loop goal "<goal>"` creates a run package under `.beacon/loop/runs/<run-id>/`.
4. runner resolves Beacon truth before starting implementation.
5. missing truth package blocks with `beacon-gen-change` route.
6. successful iterations commit; failed iterations rollback or enter commit-failure repair.
7. resume continues from prior run metadata and notes.
8. evidence import uses Beacon `implement import-evidence`.
9. QA/release verdict remains owned by Beacon evaluator/release surfaces.
10. docs/tests use `goal` only; no `lfg` alias, deprecated alias, compatibility route, or help hint is exposed.

## Recommended Route

当前 artifact 已被用户接受，并通过 `beacon-gen-change` 晋升为 package-authoritative feature truth。

当前晋升引用：

```text
docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md
```

正式 feature package：

```text
docs/beacon/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/
  truth.md
  tests.md
  tasks.md
  evidence.md
```

之后再进入 `beacon-gen-implement`。不要从本 research 直接进入代码修改。
