---
name: beacon-truth
description: Use when the user wants Beacon's preferred v1.5.2+ truth umbrella for package-authoritative requirement definition, acceptance, coverage, or governed truth change routing.
---

# Beacon Truth

## Overview

`beacon-truth` is the preferred v1.5.2+ human-facing umbrella for Beacon feature truth work.

It is a routing and mode-selection surface, not a new authority. The authority remains the resolver-selected Markdown feature package:

- `features/<slug>/truth.md` for requirement definition and acceptance framing
- `features/<slug>/tests.md` for coverage truth
- `features/<slug>/tasks.md` for task ledger
- `features/<slug>/evidence.md` for evidence index

## Modes

- `truth.define`: define problem, scope, goals, boundaries, promised surface, and freeze readiness. Compatibility alias: `beacon-prd`.
- `truth.acceptance`: compile story intent and acceptance criteria into executable acceptance truth. Compatibility alias: `beacon-user-story`.
- `truth.coverage`: compile acceptance criteria into verifiable coverage rows in `features/<slug>/tests.md`. Compatibility alias: `beacon-test-case`.
- `truth.change`: route frozen truth changes through `beacon-change` or accepted post-freeze closure through `beacon-change-refreeze`.

These modes preserve distinct decision work. Do not flatten definition, acceptance, coverage, and change into one freeform truth surface.

## When To Use

- the user asks for the current Beacon truth surface under v1.5.2+
- the user is confused by old `prd`, `user-story`, or `test-case` names after package-authoritative cutover
- requirement work needs mode selection before implementation
- accepted support findings need routing back to truth or change

## Boundary

- not a truth authority
- not a truth source
- not a gate source
- not a new lifecycle stage
- not a lifecycle stage
- does not execute QA
- does not issue release verdicts
- does not make `brainstorm`, `change-refreeze`, QA, or release into truth authoring stages
- does not delete compatibility aliases such as `beacon-prd`, `beacon-user-story`, or `beacon-test-case`

## Workflow / Decision Loop

1. Resolve the feature truth map before reading or writing requirement material:

```bash
beacon truth-map resolve <feature> --project . --version v1.5.2 --json
```

2. Choose the narrow mode:

```text
truth.define      -> features/<slug>/truth.md
truth.acceptance  -> features/<slug>/truth.md
truth.coverage    -> features/<slug>/tests.md
truth.change      -> beacon-change / beacon-change-refreeze
```

3. Route through the compatibility alias when an existing skill is the more precise operator surface.
4. Preserve closure:

```text
support research
  -> truth.define
  -> truth.acceptance
  -> truth.coverage
  -> requirement_clarity
  -> freeze
  -> implement
  -> qa
  -> release
```

## Compatibility Aliases

- `beacon-prd` remains the compatibility alias for `truth.define`.
- `beacon-user-story` remains the compatibility alias for `truth.acceptance`.
- `beacon-test-case` remains the compatibility alias for `truth.coverage`.
- `beacon-change` remains the governed route for frozen truth changes.
- `beacon-change-refreeze` remains the support route for accepted post-freeze refreeze closure.

Use the new mode names when explaining lifecycle shape. Use the old skill names when invoking stable compatibility surfaces.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- resolver-selected `features/<slug>/truth.md`
- resolver-selected `features/<slug>/tests.md`
- resolver-selected `features/<slug>/tasks.md`
- resolver-selected `features/<slug>/evidence.md`
- support research when present

## Decision Protocol

- If problem, scope, goals, boundaries, or promised surface are open, choose `truth.define`.
- If acceptance criteria need to be compiled or sharpened, choose `truth.acceptance`.
- If coverage rows, negative paths, boundary cases, or regression proof are weak, choose `truth.coverage`.
- If frozen truth must change, choose `truth.change`.
- If the user only wants read-only challenge, route to `beacon-brainstorm` and require promotion back to truth before freeze.
- If the user asks for implementation, QA, or release, leave `beacon-truth` and route to `beacon-implement`, `beacon-qa`, or `beacon-release`.

## Anti-Inertia Notes

- `beacon-truth` is not permission to bypass resolver-first package truth.
- `truth.md` owns requirement and acceptance framing; it does not own executable coverage matrices.
- `features/<slug>/tests.md` owns coverage truth; generated QA JSON is projection state.
- Compatibility aliases are stable public surfaces, not legacy authority.
- Support output must be adopted into the package before it becomes requirement truth.

## Backstop CLI

- `beacon truth-map resolve <feature> --project . --version v1.5.2 --json`
- `beacon prd ...` for `truth.define` compatibility
- `beacon user-story ...` for `truth.acceptance` compatibility
- `beacon test-case ...` for `truth.coverage` compatibility
- `beacon change ...` for `truth.change`

## Examples

- “这个 feature 的 scope/promise 还没清楚。” -> `truth.define` / `beacon-prd`
- “我要把承诺面编译成 AC。” -> `truth.acceptance` / `beacon-user-story`
- “AC 有了，但测试覆盖不够。” -> `truth.coverage` / `beacon-test-case`
- “冻结后的承诺要变。” -> `truth.change` / `beacon-change`
- “只是想先 challenge 一下，不想写 truth。” -> `beacon-brainstorm`

## Cold-start Anchors

- v1.5.2+ preferred truth lifecycle is `truth.define -> truth.acceptance -> truth.coverage`.
- The Markdown feature package is the source of truth; `beacon-truth` is a route umbrella.
- Old public skill names remain compatibility aliases and must continue to work.
