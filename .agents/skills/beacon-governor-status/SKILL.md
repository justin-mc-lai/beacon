---
name: beacon-governor-status
description: Beacon v1.6.0 governor skill migrated from `beacon-status`. Use when the user wants a board, current stage snapshot, or overall lifecycle state for a Beacon feature through Beacon's current visibility surface.
---

# Beacon Governor Status

## Overview

This skill routes status inspection through Beacon's `status` support surface.

It provides lifecycle/read-model visibility without changing requirement truth or execution state by itself.

## When to Use

- current board view
- current stage snapshot
- lifecycle progress overview
- quick state checks without changing delivery truth
- revision-aware frozen/reopened/re-frozen inspection
- supplement jump visibility for `user-story` and `test-case`
- acceptance kit layered verdict visibility

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for PRD, QA, or release decisions

## Workflow / Decision Loop

- inspect lifecycle state and layered verdict projections
- show where the feature is, what is blocked, and which route is implied next
- pair with `beacon-change` when frozen features need scope adjustment

## Common Rationalizations

- “status 看着差不多，就算通过。” -> 不允许；status 不是 verdict
- “有 board 了，就不需要 requirement/gate surface 了。” -> 不允许；status 只读
- “revision 乱了，status 直接帮我改。” -> 不允许；状态修复要回 `doctor` 或 truth surface

## Red Flags

- board/snapshot 被当成正式 acceptance 或 release 结论
- 生命周期状态和下一跳完全脱节
- 状态展示掩盖了 frozen/reopened 差异

## Verification

- current stage, blockers, and next-step visibility are explicit
- frozen/reopened/re-frozen state remains distinguishable
- no status payload is mistaken for formal truth mutation

## Evidence Produced

- board/snapshot projection
- lifecycle and layered-verdict visibility

## State Updated

- none by default
- read-model visibility only

## Gate Impact

- no direct gate verdict
- can prevent misrouting by revealing missing closure or blocker state

## Operator rule

Prefer:

- `beacon status ...`
- or `beacon status ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh status ...`)

Use status for visibility, not as a substitute for PRD, story, QA, or release decisions.
When status shows a frozen feature that now needs scope adjustment, pair it with `beacon-change`.

## Examples

- 适用例：
  - “我想看这条 feature 现在在哪个阶段、卡在哪里。”
  - “先给我一个 board / snapshot，不要改任何 truth。”
- 不适用例：
  - “我要正式判断 release readiness 或改 requirement truth。” -> 应去对应主链 surface


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
- 来源迁移：`beacon-status` -> `beacon-governor-status`。
- 主要作用：状态和看板可见性。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-status` -> `beacon-governor-status`。
- 主要作用：状态和看板可见性。
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
