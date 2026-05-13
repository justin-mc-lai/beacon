---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user through Beacon's current human-facing surface instead of exposing the full CLI catalog.
---

# Using Beacon

## Overview

Use Beacon as the host-native router for requirement truth, execution, verification, release, and support guidance.

The public surface follows Beacon's current human-facing runtime line. Route by decision surface, not by internal mechanism, and keep support surfaces from silently replacing truth or gate surfaces.

## When to Use

- Beacon should become the main workflow entrypoint in the host
- the user is not yet sure whether the current need is truth, execution, verification, or support
- the operator needs one stable human-facing surface instead of a raw CLI catalog

## Boundary

- this router does not freeze truth directly
- this router does not execute implementation by itself
- this router is not a release gate
- internal team/runtime lanes stay hidden unless the user explicitly asks for internals
- external skill repos, plugins, or runtime packs are not Beacon's default prerequisite

## Workflow / Decision Loop

- identify whether the current need belongs to truth, execution, gate, or support
- route to `beacon-prd`, `beacon-user-story`, `beacon-test-case`, `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release` when the user is already on the mainline
- route to `beacon-brainstorm`, `beacon-ceo-review`, `beacon-design-review`, `beacon-deep`, `beacon-help`, `beacon-status`, or `beacon-doctor` only when challenge, explainability, diagnosis, or convergence is the real need
- if a support surface changes accepted scope or promise, route back through `beacon-change`

## Common Rationalizations

- “先随便找个 support surface 进去，后面再补 route。” -> 不允许；先判断当前决策面
- “brainstorm 已经想清楚了，就当正式 requirement。” -> 不允许；正式 truth 仍要回主链
- “release 看起来差不多，直接放行。” -> 不允许；必须走 `beacon-qa` / `beacon-release`

## Red Flags

- 把 support surface 当成 truth source 或 gate source
- 因为工具名熟悉而按机制路由，而不是按当前决策面路由
- 在还没识别 scope / acceptance / evidence 所属面的前提下直接进入 `implement` 或 `release`

## Verification

- host 能明确分辨当前请求属于 truth、execution、gate 或 support
- 路由建议不会把 support surface 误判成新的 lifecycle stage
- 变更 frozen scope 时会显式回到 `beacon-change`

## Evidence Produced

- host-visible route recommendation
- current-surface reasoning summary
- required follow-up surface when the current surface is only advisory

## State Updated

- none by default
- route state may be projected by Beacon runtime helpers, but this router does not author canonical truth

## Gate Impact

- no direct gate verdict
- influences which truth, execution, or gate surface must run next

## Public routing targets

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-prototype`
- `beacon-change`
- `beacon-brainstorm`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-ceo-review`
- `beacon-design-review`
- `beacon-learn`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`
- `beacon-archive`
- `beacon-toolkit-metadata`
- `beacon-toolkit-branch-governance`

## Examples

- “这个 feature 的承诺面还不清楚，PRD 需要先收口” -> `beacon-prd`
- “PRD 已经有了，但 acceptance criteria 还不够可执行” -> `beacon-user-story`
- “故事线没问题，但测试覆盖和 release proof 还不完整” -> `beacon-test-case` 或 `beacon-qa`
- “我不想改 frozen truth，只想继续 challenge 假设或收敛 gap” -> `beacon-brainstorm`
- “scope 要变，或者 freeze 后要补正式 truth” -> `beacon-change`
- “代码准备动了，直接进入执行” -> `beacon-implement`
- “我不知道现在下一步该去哪” -> `beacon-help` 或 `beacon-status`

## Cold-start anchors

- 优先先判断这是 truth、execution、verification，还是 support/guidance 问题
- 相似请求默认按“当前决策面”路由，不按内部实现机制或工具名路由
- 如果只是 challenge、explain、converge，就不要误送进 `implement` 或 `release`
