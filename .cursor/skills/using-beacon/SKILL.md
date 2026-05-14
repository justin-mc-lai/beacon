---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user through Beacon's current human-facing surface instead of exposing the full CLI catalog.
---

# Using Beacon

## Overview

Use Beacon as the host-native route constitution for truth, execution, verification, gate, and support decisions.

The public surface follows Beacon's current human-facing runtime line. Route by decision surface, not by internal mechanism, and keep support surfaces from silently replacing truth or gate surfaces.

## When to Use

- Beacon should become the main workflow entrypoint in the host
- the user is not yet sure whether the current need is truth, execution, verification, or support
- the operator needs one stable human-facing surface instead of a raw CLI catalog

## Boundary

- this router does not freeze truth directly
- this router does not execute implementation by itself
- this router is not a release gate
- this router does not author canonical truth
- this router does not override release or QA verdicts
- internal team/runtime lanes stay hidden unless the user explicitly asks for internals
- external skill repos, plugins, or runtime packs are not Beacon's default prerequisite

## Workflow / Decision Loop

- identify whether the current need belongs to truth, execution, verification/gate, or support
- classify the request before naming tools:
  - truth = promised outcome, scope, ambiguity, acceptance, frozen package revision
  - execution = prototype handoff or implementation work against frozen truth
  - verification/gate = evidence closure, acceptance confidence, release judgment
  - support = challenge, convergence, diagnosis, method strengthening, route explanation
- route to `beacon-prd`, `beacon-user-story`, `beacon-test-case`, or `beacon-change` when the request is about truth
- route to `beacon-prototype` or `beacon-implement` when the request is about execution
- route to `beacon-qa` or `beacon-release` when the request is about evidence or gate judgment
- route to `beacon-brainstorm`, `beacon-ceo-review`, `beacon-design-review`, `beacon-deep`, `beacon-context-engineering`, `beacon-source-driven`, `beacon-doubt-review`, `beacon-security-review`, `beacon-performance-review`, `beacon-documentation-adr`, `beacon-debug-recovery`, `beacon-help`, `beacon-status`, or `beacon-doctor` only when support is the real need
- if a support surface changes accepted scope, promise, or acceptance assumptions, route back through `beacon-change`

## Common Rationalizations

- “先随便找个 support surface 进去，后面再补 route。” -> 不允许；先判断当前决策面
- “brainstorm 已经想清楚了，就当正式 requirement。” -> 不允许；正式 truth 仍要回主链
- “release 看起来差不多，直接放行。” -> 不允许；必须走 `beacon-qa` / `beacon-release`
- “support skill 很强，可以直接替代 implement / qa。” -> 不允许；support 只能 strengthen，不直接替代主链或 gate

## Red Flags

- 把 support surface 当成 truth source 或 gate source
- 因为工具名熟悉而按机制路由，而不是按当前决策面路由
- 在还没识别 scope / acceptance / evidence 所属面的前提下直接进入 `implement` 或 `release`
- route explanation 没说明哪些是 frozen truth、哪些只是 advisory hint

## Verification

- host 能明确分辨当前请求属于 truth、execution、verification/gate 或 support
- 路由建议不会把 support surface 误判成新的 lifecycle stage
- 变更 frozen scope 时会显式回到 `beacon-change`
- route explanation 能区分 frozen truth 与 learning hint

route explanation can distinguish frozen truth and learning hint.

## Evidence Produced

- host-visible route recommendation
- current-surface reasoning summary
- required follow-up surface when the current surface is only advisory
- optional reference pointer when a lightweight checklist can reduce ambiguity faster than free-form explanation

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
- `beacon-context-engineering`
- `beacon-source-driven`
- `beacon-doubt-review`
- `beacon-security-review`
- `beacon-performance-review`
- `beacon-documentation-adr`
- `beacon-debug-recovery`
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
- “scope 没想改，但当前实现上下文太乱，想先把上下文重排干净” -> `beacon-context-engineering`
- “truth 稳了，想确保实现和 review 时优先锚定 source 而不是自由发挥” -> `beacon-source-driven`
- “我怀疑方案在自我合理化，想有人专门帮我找盲区和证据洞” -> `beacon-doubt-review`
- “这轮要先看安全边界、暴露面、权限或输入风险” -> `beacon-security-review`
- “这轮要先看性能瓶颈、热点路径或可扩展性风险” -> `beacon-performance-review`
- “这轮要补 ADR、架构决策说明或文档闭环，但不想把它误当成 requirement truth” -> `beacon-documentation-adr`
- “我被实现/运行时异常卡住了，想先走恢复与调试支持面” -> `beacon-debug-recovery`
- “scope 要变，或者 freeze 后要补正式 truth” -> `beacon-change`
- “代码准备动了，直接进入执行” -> `beacon-implement`
- “我不知道现在下一步该去哪” -> `beacon-help` 或 `beacon-status`

## Cold-start anchors

- 优先先判断这是 truth、execution、verification，还是 support/guidance 问题
- 相似请求默认按“当前决策面”路由，不按内部实现机制或工具名路由
- 如果只是 challenge、explain、converge，就不要误送进 `implement` 或 `release`
- support skills 只增强判断与执行质量，不替主链写 truth，也不替 gate 写 verdict
