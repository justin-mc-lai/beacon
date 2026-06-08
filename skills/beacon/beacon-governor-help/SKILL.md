---
name: beacon-governor-help
description: Beacon v1.6.0 governor skill migrated from `beacon-help`. Use when the user asks what Beacon should do next, is blocked in the Beacon lifecycle, or needs stage-aware guidance through Beacon's current guidance surface.
---

# Beacon Governor Help

## Overview

This skill routes next-step guidance through Beacon's `help` support surface.

It explains where the user is in the current loop and which mainline surface should run next. It does not redefine truth or act as a release gate.

## When to Use

- "what next?"
- "where am I in Beacon?"
- blocked workflow progression
- stage-aware resume guidance
- frozen feature change-loop guidance
- requirement gap, supplement, and re-freeze routing

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for PRD, story, QA, or release decisions

## Workflow / Decision Loop

- inspect current workflow/read-model state
- explain current blockers, missing proof, or missing requirement closure
- route to `brainstorm`, `change`, `user-story`, `test-case`, `implement`, `qa`, or `release` as appropriate
- stop at guidance; do not self-author canonical truth

## Common Rationalizations

- “help 都说清楚了，就不用回主链了。” -> 不允许；它只解释和 route
- “卡住时先讲内部 lane 细节给用户。” -> 不允许；先给低摩擦 next-step guidance
- “状态有点乱，help 直接替我改掉就行。” -> 不允许；修复要去 `doctor` 或 truth surface

## Red Flags

- next-step guidance 没有明确 surface
- requirement gap 已经明确，但仍停留在泛泛建议
- 用 `help` 代替正式 `change` / `qa` / `release` 判断

## Verification

- guidance outputs current status, blocker, next step, and fallback route
- frozen-feature change scenarios route to `beacon-change`
- open gap but unchanged truth routes to read-only convergence first when appropriate

## Evidence Produced

- route recommendation
- blocked reason digest
- layered verdict summary when available

## State Updated

- none by default
- may project support/read-model state only

## Gate Impact

- no direct gate verdict
- can stop premature progression by routing back to the right mainline surface

## Operator rule

Prefer:

- `beacon help ...`
- or `beacon help ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh help ...`)

Use `beacon-governor-help` before exposing low-level machine lanes or asking the user to reason about Beacon internals.
When the user is changing a frozen feature, prefer routing to `beacon-change` rather than explaining hidden `reopen/freeze` mechanics directly.
When a gap is still open but frozen truth is unchanged, prefer `beacon-brainstorm` for read-only convergence and then route to `beacon-user-story` or `beacon-test-case` for补料.

## Examples

- 适用例：
  - “我现在该做什么？”
  - “我被卡住了，但不知道是该回 story、test-case、qa 还是 change。”
- 不适用例：
  - “我已经明确知道要执行哪条主链动作。” -> 直接去对应 surface


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
- 来源迁移：`beacon-help` -> `beacon-governor-help`。
- 主要作用：下一步指导。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-help` -> `beacon-governor-help`。
- 主要作用：下一步指导。
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
