---
name: beacon-test-case
description: Use when the user wants to create, extend, or audit test cases and acceptance coverage for a Beacon feature through Beacon's current v1.4.6 runtime surface.
---

# Beacon Test Case

This skill routes acceptance coverage work through Beacon's `test-case` surface.

The active coverage contract is aligned to the current `v1.4.6` docs line.
Compatibility bridges may still resolve older entrypoints, but the truth package should be read from `docs/beacon/v1.4.6/`.

## Use for

- test-case generation
- acceptance coverage expansion
- boundary and regression coverage review
- QA preparation before implementation or verification
- truth-projected case generation from frozen `user-story / prd / qa/test-cases` materials

## Operator rule

Prefer:

- `beacon test-case ...`
- or `beacon test-case ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh test-case ...`)

The public goal is coverage readiness, not exposing internal QA lanes yet.
When host-native runtime is available, `test-case` should first use the wrapper-provided bridge and project from requirement truth or existing QA rows instead of emitting a generic placeholder matrix.
If coverage is incomplete, surface the supplement task and re-freeze transaction rather than treating the matrix as final.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- upstream `user-story` and `prd`
- existing `qa/test-cases` truth when revising
- diagram / semantic inputs when route, state, or invariant coverage is required

## Decision Protocol

- Continue in `test-case` when acceptance criteria are ready to compile into verifiable scenarios.
- Route back to `user-story` if acceptance criteria are still ambiguous.
- Route to `change` when frozen acceptance coverage must materially change.
- Keep `test-case` as the last truth surface before `requirement_clarity -> freeze`; do not treat coverage drafting as a side note that can be skipped before freeze.
- Require negative, boundary, recovery, and fallback coverage when the feature introduces blocked paths or guardrail behavior.
- If the feature has real UX/UI handoff, determine whether `prototype` should be conditionally triggered before implementation.
- When complexity-triggered human closure artifacts exist, compile coverage directly from business flow, state-machine, and decision-priority truth instead of only from happy-path acceptance bullets.
- For complexity-triggered features, ensure every upstream AC remains traceable in `test-case` truth before freeze; missing AC projection must route back for补料 instead of freezing shallowly.

## Anti-Inertia Notes

- A matrix of happy-path rows alone is not coverage closure.
- `test-case` does not make a feature implemented or accepted by itself.
- Prototype is conditional globally, but once UX/UI handoff is real it must not be skipped casually.
- Machine matrices are projections; they do not replace frozen requirement truth.
- `test-case` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse learning to improve scenario sharpness, especially around stale-data, downgrade, and recovery cases.
- Stale learning should produce cautionary scenarios, not silent assumptions.
- Learning cannot define pass/fail by itself.

## Backstop CLI

- `beacon test-case ...`
- `beacon user-story ...` when ACs are under-specified
- `beacon prototype ...` when real UX/UI handoff is present

## Examples

- 适用例：
  - “acceptance criteria 已经清楚，现在要把它们编译成可验证场景。”
  - “我想检查这条 feature 的 coverage 是不是只有 happy path，没有 boundary/recovery。”
- 不适用例：
  - “AC 还没写清楚。” -> 应回 `beacon-user-story`
  - “我现在是在执行测试，不是在设计测试 truth。” -> 应优先去 `beacon-qa`

## Cold-start anchors

- `test-case` 负责 coverage truth，不负责执行 verdict。
- 只有 happy-path 的矩阵不算 coverage closure。
- 如果 feature 有真实 UX/UI handoff，要显式判断 `prototype` 是否应先触发。
- `test-case` 不是 freeze 后补写的说明文档；它是 `research -> prd -> user-story -> test-case -> requirement_clarity -> freeze` 合同链的一环。
