# PRD: Beacon v1.4.6 automation jobs feedback loop and queue governance

**Feature**: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`  
**Version**: `v1.4.6`  
**Date**: `2026-05-14`  
**Status**: `freeze-ready`  
**Track**: `automation-governance + project-local-feedback-loop + executor-tiering`  
**Scenario**: `scheduled-qa-results-feeding-the-next-qa-and-gated-implement-window`

## Context

- Version summary: `docs/beacon/archive/v1.4.6/SUMMARY.md`
- Existing automation capability guide:
  - `docs/analysis/codex-automations-and-beacon-capability-guide.md`
- Existing project-local scheduler assets:
  - `automation/beacon-automation-queue.json`
  - `automation/jobs/`
  - `automation/codex/`
  - `automation/launchd/`
- Product tension:
  - Beacon already explains host-scheduled automation boundaries.
  - Beacon does not yet freeze the project-local feedback loop that lets one QA run feed the next scheduled QA or the next gated implement window in a governed way.

## 1. Overview

Beacon needs a frozen, project-local automation feedback loop contract so scheduled QA, queue governance, executor tiering, and scaffold generation can enter execution truth without relying on per-project shell invention.

## 1. 问题

Beacon 的 automation/jobs 目前更像 host wrapper 样例集，而不是正式冻结的 project-local automation contract。

这会导致三个实际缺口：

- 定时 QA 虽然能跑，但缺少正式 machine-readable feedback ledger
- 下一轮 QA 虽然能读取上一轮 feature QA status，但没有冻结 project-local automation queue update 规则
- gated implement 虽然能使用 queue，但 QA repair 结果还没有被正式提升成 queue-governed next-step automation intent
- 不同项目仍需要手工复制 `automation/` 目录，project-local bootstrap 还没有冻结成 Beacon public surface
- 对外容易误以为所有 agent 都能通过同一底层机制原生定时执行，但官方 runtime surfaces 实际并不对称

因此 Beacon 目前只具备：

- host-scheduled capability explanation
- queue validation
- thin wrappers

但还不具备正式冻结的：

- QA feedback ledger contract
- queue auto-update rule
- automation/jobs feedback loop truth for project-local scheduling

## 2. 目标

1. 冻结 Beacon automation/jobs 的 project-local feedback loop
2. 让 nightly QA 结果能 machine-readably feed the next QA or gated implement window
3. 保持 queue governance 显式化，不允许 opportunistic work creation
4. 把 automation/jobs 保持在 host plane，不侵入 Beacon core lifecycle
5. 让真实项目可以通过 Beacon public CLI 生成 project-local automation scaffold，而不是手工复制资产
6. 明确冻结“host-agnostic control plane + executor adapters”的能力边界，而不是虚假承诺所有 agent 原生等价执行

## 2. Scope

### In scope

- freeze the QA feedback ledger contract
- freeze queue update rules and shared automation summary schema
- expose `beacon automation init / summarize-qa / update-queue / validate-queue`
- generate project-local automation scaffold assets with executor-aware prompts and launchd examples
- preserve Beacon/host boundary and executor-tier capability truth

### Out of scope

- embed cron / launchd runtime into Beacon core lifecycle
- auto-rewrite requirement truth or auto-publish release claims
- claim native implement/qa execution parity for unsupported hosts

## 3. 设计原则

### 3.1 Feedback loop 必须是 project-local automation plane，不是新的 lifecycle stage

该能力只能增强 scheduler-adjacent execution governance，不能变成新的 Beacon 主阶段。

It is not a new lifecycle stage.

### 3.2 QA result writeback 只能更新 automation intent，不得重写 requirement truth

QA 结果可以：

- 移除已通过的 QA candidate
- 把 repair-needed candidate 提升到 implement queue
- 生成下一轮 QA 可复用的 feedback ledger

但不能：

- 改写 requirement truth
- 自动 reopen `change`
- 自动发布 release 结论

### 3.3 Queue update 必须是 explicit rule，不得让 wrapper 发明新工作

automation/jobs 只能按正式规则更新 queue：

- `passed` -> remove from QA queue
- `stop_for_repair` -> add to implement queue when repair route exists
- environment blocker remains evidence, not product-failure promotion

### 3.4 Beacon 应冻结 ledger 和 queue update entrypoints，而不是只保留 shell 脚本约定

该能力必须通过 Beacon public CLI 可发现、可测试、可验证。

### 3.5 多 agent automation 必须是 capability tiers，不是统一 runtime 幻觉

Beacon automation 可以统一：

- queue intent
- job contract
- artifact contract
- summary schema contract
- feedback loop
- next-route governance

但不能在 `v1.4.6` 里虚构所有宿主都拥有同等的：

- native scheduler
- public headless CLI
- public execution API
- Beacon `implement/qa` host-runtime admission

因此该补充必须冻结 executor tier 模型：

- `native`: Codex, Claude
- `supported-via-adapter`: Cursor
- `assisted`: Windsurf
- `experimental`: Trae

## 4. 范围

### In scope

- QA feedback ledger contract
- queue update contract
- shared automation summary schema contract
- Beacon automation CLI entrypoints for summarize/update
- automation/jobs wrapper integration
- v1.4.6 docs and tests for the automation/jobs feedback loop
- project-local automation scaffold generation surface
- executor capability matrix and scaffold tiering
- human-facing toolkit skill for automation bootstrap and maintenance

### Out of scope

- 直接内建 cron / launchd runtime
- 自动重写 requirement truth
- 自动触发 release write actions
- 任意未被官方证据证明的 agent-native execution claim

## 5. 功能需求

### FR-001 Beacon 必须冻结 project-local QA feedback ledger

Beacon 必须为 scheduled QA output 写出 canonical feedback ledger。

至少包含：

- feature
- run_id
- status
- evidence_done
- release_ready
- continue_decision
- stop_reasons
- repair_command
- targeted rerun hints

### FR-002 Beacon 必须暴露 feedback ledger 的 public CLI surface

至少提供：

- `beacon automation summarize-qa --project-root .`

### FR-003 Beacon 必须暴露 queue update 的 public CLI surface

至少提供：

- `beacon automation update-queue --project-root .`

### FR-004 Queue update 必须保持显式治理

Queue update 只能执行冻结规则，不得产生 opportunistic candidate selection。

### FR-005 Nightly QA wrapper 必须在 QA 后刷新 ledger 与 queue

`automation/jobs/beacon-qa-job.sh` 必须在 QA execution 结束后：

- refresh QA feedback ledger
- update automation queue

### FR-006 Gated implement wrapper 至少必须消费 queue update flow

`automation/jobs/beacon-gated-implement-job.sh` 必须能在 implement window 后刷新 queue state。

### FR-007 Capability reporting 必须披露 feedback loop surface

`beacon automation capabilities` 必须显示：

- feedback ledger path
- summarize entrypoint
- update entrypoint

### FR-008 该补充必须继续保持 Beacon/host boundary

该能力必须强化 host-scheduled workflow，但不得把 scheduler runtime 吸收到 Beacon core lifecycle。

### FR-009 Beacon 必须暴露 project-local scaffold generation entrypoint

至少提供：

- `beacon automation init --project-root .`

### FR-010 Scaffold output 必须是目标项目定制的可运行资产

至少生成：

- `automation/beacon-automation-queue.json`
- `automation/jobs/`
- `automation/codex/`
- `automation/launchd/`
- `automation/README.md`

并将其中的项目路径、queue 路径、输出目录、launchd label 定制到目标项目。

### FR-011 Scaffold overwrite 行为必须保守

默认不得覆盖项目已存在的 automation 文件；只有显式 `--force` 才允许刷新。

### FR-012 Beacon 必须冻结 executor capability matrix

至少区分：

- executor name
- tier
- whether Beacon `implement/qa` can execute through current host runtime
- whether execution is scaffold-only / adapter-only

### FR-013 Scaffold 必须支持 executor profile 生成

至少提供：

- `beacon automation init --project-root . --executor codex|claude|cursor|windsurf|trae`

并据此调整 queue target、prompt/spec 说明、以及对 native runtime 是否存在的提示。

### FR-014 Beacon 不得把 unsupported executor 伪装成当前可直接跑 implement/qa

在 `v1.4.6` 中：

- Codex / Claude 可作为 current Beacon runtime execution hosts
- Cursor 只能冻结为 adapter-capable, not yet Beacon-native implement/qa runtime
- Windsurf / Trae 只能冻结为 scaffold/rules/external-scheduler guidance until stronger public execution evidence exists

### FR-015 Beacon 必须冻结 shared automation summary schema

Beacon 必须为 automation/jobs 输出一套 transport-agnostic 的 summary schema，供：

- functional QA
- exception QA
- regression QA
- Beacon nightly strict QA
- 后续通知适配器

共同消费。

至少包含：

- `summary_kind`
- `project_root`
- `job`
- `layer`
- `status`
- `analysis.headline`
- `analysis.summary_line`
- `metrics.*`
- `features.all`
- `features.release_ready`
- `features.repair_needed`
- `artifacts.*`
- `notification.title`
- `notification.lines`

### FR-016 Beacon 必须暴露 shared summary 的 public CLI surface

至少提供：

- `beacon automation build-summary --project-root . --job <job> --layer <layer>`

### FR-017 Scaffolded wrapper 与通知 helper 必须消费同一 summary schema

`automation/jobs/beacon-qa-job.sh` 与 `automation/jobs/beacon-notify-feishu-post.py` 不得各自发明私有摘要协议。

至少要求：

- wrapper 通过 Beacon CLI 生成 summary JSON
- notifier 从 summary JSON 的 `notification` contract 渲染消息
- 真实项目不需要再手写一版重型 per-project 摘要拼接逻辑才能发通知

### FR-018 Beacon 必须暴露 human-facing automation toolkit surface

至少提供：

- `beacon-toolkit-automation`

用于：

- `beacon automation init`
- `beacon automation capabilities`
- `beacon automation validate-queue`
- `beacon automation summarize-qa`
- `beacon automation build-summary`
- `beacon automation update-queue`

的初始化、检查、维护路由。

## 6. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | Beacon freezes a project-local QA feedback ledger contract |
| AC-002 | Beacon exposes `beacon automation summarize-qa` as public CLI |
| AC-003 | Beacon exposes `beacon automation update-queue` as public CLI |
| AC-004 | queue update uses explicit pass/repair rules and does not create opportunistic work |
| AC-005 | nightly QA wrapper refreshes ledger and queue after QA execution |
| AC-006 | gated implement wrapper refreshes queue after implement execution |
| AC-007 | automation capability reporting exposes feedback loop surfaces |
| AC-008 | the automation/jobs supplement preserves Beacon core lifecycle boundaries |
| AC-009 | Beacon exposes `beacon automation init --project-root .` as a public scaffold bootstrap surface |
| AC-010 | scaffold output is project-local and rewrites paths/labels for the target repo |
| AC-011 | scaffold generation is conservative by default and refreshes only with explicit force |
| AC-012 | Beacon freezes a tiered executor capability matrix instead of claiming uniform native automation across all agents |
| AC-013 | scaffold generation supports executor profiles and reflects them in queue/spec outputs |
| AC-014 | unsupported executors are not represented as current Beacon-native implement/qa runtimes |
| AC-015 | Beacon freezes a shared automation summary schema that multiple QA layers and notification adapters can consume |
| AC-016 | Beacon exposes `beacon automation build-summary` as a public automation surface |
| AC-017 | scaffolded wrappers and notification helpers consume the same summary schema instead of project-specific summary formats |
| AC-018 | Beacon exposes a human-facing `beacon-toolkit-automation` support surface for project-local scheduled automation bootstrap and maintenance |
