---
name: beacon-prd
description: Use when the user wants to draft, refine, clarify, or review a product requirements document through Beacon's current v1.4.3 runtime surface. Keep brainstorm embedded inside the PRD loop rather than sending the user to a standalone brainstorm stage unless explicitly requested.
---

# Beacon PRD

This skill routes requirement work through Beacon's `prd` surface.

The human-facing contract is aligned to the `v1.4.3` docs line (`docs/beacon/v1.4.3/`).
CLI compatibility may still preserve older runtime aliases, but operators and hosts should read this skill as the current `v1.4.3` decision surface.

## Use for

- PRD drafting
- requirement clarification
- missing points / open questions
- business ambiguity closure
- freeze-readiness before story generation

## Operator rule

Prefer Beacon's PRD surface first:

- `beacon prd ...`
- or `beacon prd ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh prd ...`)

Keep the human on the `prd -> user-story -> test-case` closure path. Use brainstorm only as a read-only gap sidecar when the PRD needs deeper convergence, and route frozen changes through `beacon-change`.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- upstream truth refs from `docs/beacon/<version>/prd/`
- related `user-story`, `test-case`, `global-boundaries`, and architecture refs when present
- host bridge or local context that explains the current requirement gap

## Decision Protocol

- Continue in `prd` when the user is still defining problem, scope, goals, boundaries, or promised surfaces.
- Route to `brainstorm` only for read-only convergence when truth is still open and the user needs help resolving ambiguity.
- Route to `change` when the request modifies already frozen truth.
- Block shallow template fill when the feature clearly needs state, transition, route, or semantic modeling.
- Prefer reusing official wording from current version truth over inventing parallel terms.
- For complexity-triggered features, require a human-readable closure package that covers research, architecture, business flow, and the relevant diagram truth before freeze.

## Anti-Inertia Notes

- `prd` is not a place to freeform rewrite unrelated frozen truth.
- `brainstorm` is not a new lifecycle stage and does not replace `prd`.
- `goal`, checkboxes, or temporary runtime notes do not define requirement truth.
- `prd` cannot rewrite frozen truth or override gate truth by itself.
- If UX/UI handoff is real, `prototype` may be triggered later; do not front-load visual polish into PRD text.

## Learning Notes

- Read learning as hint, not truth.
- Prefer `feature -> host -> runner -> domain` disclosure order when prior learning exists.
- Downgrade stale or superseded learning instead of forcing it into current requirement language.
- If learning conflicts with frozen truth, frozen truth wins.

## Backstop CLI

- `beacon prd ...`
- `beacon brainstorm ...` for read-only convergence
- `beacon change ...` for frozen-truth revision

## Examples

- 适用例：
  - “我还在定义这个 feature 到底解决什么问题、边界是什么、承诺面是什么。”
  - “需求里还有很多模糊点，需要先把问题 framing 和 scope 收口。”
- 不适用例：
  - “PRD 已经很清楚了，现在要把 acceptance criteria 编译出来。” -> 应去 `beacon-user-story`
  - “需求已经冻结，我要正式改写它。” -> 应去 `beacon-change`

## Cold-start anchors

- `prd` 解决的是问题定义、目标、边界和 promised surface。
- `brainstorm` 可以帮忙 challenge 和收敛，但不能代替 `prd` 冻结正式 truth。
- 不要在 `prd` 里提前做实现、视觉或 release 层判断。
- 复杂需求不能只靠文字段落冻结；缺少 research / business flow / state-machine / decision-priority 闭环时，应回补而不是假装 freeze-ready。
