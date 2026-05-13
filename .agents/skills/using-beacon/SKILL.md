---
name: using-beacon
description: Use when Beacon should become the primary workflow router in Codex or Claude for requirements, implementation, QA, release readiness, or next-step guidance. Route the user through Beacon's current human-facing surface instead of exposing the full CLI catalog.
---

# Using Beacon

Use Beacon as a host-native human-facing workflow pack.

The public surface follows Beacon's current human-facing runtime line.

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

## Routing philosophy

Route by decision surface, not by internal mechanism.

- Requirement definition, ambiguity, or missing promise: `beacon-prd`
- Story and acceptance compilation: `beacon-user-story`
- Test and acceptance coverage: `beacon-test-case`
- Conditional UX/UI handoff before implementation: `beacon-prototype`
- Frozen truth reopening or supplement: `beacon-change`
- Read-only convergence, challenge, or evolution thinking: `beacon-brainstorm`
- Implementation execution: `beacon-implement`
- Verification and release confidence: `beacon-qa` or `beacon-release`
- Version-level scope or promise challenge: `beacon-ceo-review`
- UI/UX direction challenge: `beacon-design-review`
- Governed learning recall or audit: `beacon-learn`
- Blocked, lost, or next-step questions: `beacon-help`, `beacon-status`, or `beacon-doctor`
- Historical isolation or archive state: `beacon-archive`
- Project/version metadata or branch governance: toolkit support surfaces

Keep Beacon as the human-facing router even when project-local helpers exist inside implementation or QA loops.

## Examples

- “这个 feature 的承诺面还不清楚，PRD 需要先收口” -> `beacon-prd`
- “PRD 已经有了，但 acceptance criteria 还不够可执行” -> `beacon-user-story`
- “故事线没问题，但测试覆盖和 release proof 还不完整” -> `beacon-test-case` 或 `beacon-qa`
- “我不想改 frozen truth，只想继续 challenge 假设或收敛 gap” -> `beacon-brainstorm`
- “scope 要变，或者 freeze 后要补正式 truth” -> `beacon-change`
- “代码准备动了，直接进入执行” -> `beacon-implement`
- “我不知道现在下一步该去哪” -> `beacon-help` 或 `beacon-status`

## Cold-start anchors

- 优先先判断这是 truth、execution、verification，还是 support/guidance 问题。
- 相似请求默认按“当前决策面”路由，不按内部实现机制或工具名路由。
- 如果只是 challenge、explain、converge，就不要误送进 `implement` 或 `release`。

## Boundary

Do not treat these as public human entrypoints unless the user explicitly asks for internals:

- `team`
- `implement-team`
- `qa-team`
- auto research lanes beyond `beacon-learn`
