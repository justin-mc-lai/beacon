---
name: beacon-user-story
description: Use when the user wants to derive, refine, review, or freeze user stories and acceptance criteria from a Beacon PRD through Beacon's current v1.4.5 runtime surface.
---

# Beacon User Story

This skill routes story work through Beacon's `user-story` surface.

The host-readable contract is aligned to the current `v1.4.5` docs line.
Compatibility bridges may still exist, but the active requirement truth and acceptance framing should be read from `docs/beacon/v1.4.5/`.

## Use for

- story drafting
- acceptance criteria refinement
- story boundary clarification
- readiness checks before test-case or freeze
- truth-projected story generation from frozen `prd / user-story / qa/test-cases` materials

## Operator rule

Prefer:

- `beacon user-story ...`
- or `beacon user-story ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh user-story ...`)

Keep the human on the `user-story -> test-case` path. Treat internal critique and research as background machine support, not public stages.
When host-native runtime is available, `user-story` should first use the wrapper-provided bridge and project from requirement truth instead of falling back to a generic template.
If the PRD is still incomplete, surface supplement targets and re-freeze intent instead of pretending the story is done.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- upstream PRD truth
- existing story truth when revising
- semantic / diagram inputs when the feature exposes stable states, routes, or official vocabulary

## Decision Protocol

- Continue in `user-story` when the PRD is clear enough to compile roles, goals, and acceptance criteria.
- Route back to `prd` when problem statement, scope, or promised surface is still unstable.
- Route to `change` when the request modifies frozen acceptance truth.
- Require explicit state/transition reasoning when diagram truth is relevant.
- Prefer official states, actions, modules, and page names from semantic trace when available.
- For complexity-triggered features, acceptance criteria should stay aligned with research/business-flow/state-machine truth instead of inventing a second simplified narrative.

## Anti-Inertia Notes

- `user-story` is not just a PRD summary; it must compile to executable acceptance criteria.
- Acceptance criteria cannot be replaced by generic “done when implemented” wording.
- `brainstorm` may help resolve ambiguity, but it does not freeze acceptance truth.
- Do not invent a second terminology layer when semantic trace already provides official names.
- `user-story` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse prior story-level learning if it improves acceptance wording or route clarity.
- Treat learning as hint; it cannot override PRD or freeze acceptance by itself.
- Surface stale learning explicitly rather than silently carrying it forward.

## Backstop CLI

- `beacon user-story ...`
- `beacon prd ...` when upstream truth is incomplete
- `beacon change ...` for frozen-truth revisions

## Examples

- 适用例：
  - “PRD 已经有了，现在要把它编译成角色目标和 acceptance criteria。”
  - “我怀疑当前 story 只是 PRD 摘要，还不够可执行。”
- 不适用例：
  - “问题定义和 scope 还没清楚。” -> 应先回 `beacon-prd`
  - “我现在要把 AC 编译成可验证场景。” -> 应去 `beacon-test-case`

## Cold-start anchors

- `user-story` 不是 PRD 摘抄，而是把承诺面编译成可执行 acceptance truth。
- 如果上游 PRD 不稳定，story 不能假装已经完成。
- 如果官方术语、状态或页面名已经存在，应优先复用，而不是再造第二套命名。
