---
name: beacon-toolkit-automation
description: Use when the user wants a human-facing Beacon toolkit surface to initialize, inspect, or maintain project-local scheduled automation assets without entering the main delivery workflow.
---

# Beacon Toolkit Automation

This skill routes scheduled-automation setup and maintenance through Beacon's `automation` support surface.

## Use for

- initialize project-local automation scaffold for a target repo
- inspect executor tiers, queue/governance boundaries, and supported wrappers
- validate or refresh the automation queue contract
- generate the shared automation summary schema consumed by notifications
- prepare recurring QA or gated implement jobs before enabling host schedulers

## Operator rule

Keep automation bootstrap and scheduler maintenance outside the main workflow by default.

Prefer:

- `beacon automation init --project-root ...`
- `beacon automation capabilities --project-root ...`
- `beacon automation validate-queue --project-root ...`
- `beacon automation summarize-qa --project-root ...`
- `beacon automation build-summary --project-root ...`
- `beacon automation update-queue --project-root ...`

Default expectations:

- treat `automation` as the human-facing deterministic scheduler toolkit
- keep queue state and summary artifacts on Beacon's canonical contract
- let host schedulers own timers and notification transport
- let `implement` and `qa` consume the same queue-governed automation truth instead of per-project shell inventions

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the scheduler result into the main Beacon workflow.

## Examples

- 适用例：
  - “我要给一个真实项目快速初始化 Beacon 定时 QA / implement 资产。”
  - “我想看这个项目当前 automation queue、summary schema、executor tier 是否可用。”
- 不适用例：
  - “我现在已经明确要推进某个 feature 的实现或验收。” -> automation 初始化结束后应回主链 surface

## Cold-start anchors

- `automation` 是 project-local scheduler toolkit，不是新的主生命周期 stage。
- scheduler runtime 和通知传输仍属于 host plane，Beacon 只冻结 queue、summary schema、feedback loop 与 gate contract。
- 先让 queue 和 scaffold 合法，再考虑 launchd / Codex / Claude 等宿主触发。
