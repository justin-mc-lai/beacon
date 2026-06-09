---
name: beacon-gov-automation
description: Beacon v1.6.0 governor skill migrated from `beacon-toolkit-automation`. Use when the user wants a human-facing Beacon toolkit surface to initialize, inspect, or maintain project-local scheduled automation assets without entering the main delivery workflow.
---

# Beacon Governor Automation

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


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-automation` -> `beacon-gov-automation`。
- 主要作用：自动化资产。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-automation` -> `beacon-gov-automation`。
- 主要作用：自动化资产。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
