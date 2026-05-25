---
name: beacon-qa-evo-deep
description: Use when the user wants deep QA support analysis for state, scenario, business-flow, permission, data-consistency, cross-surface, or repeated-round gaps without producing a formal QA or release verdict.
---

# Beacon QA Evo Deep

## Overview

This skill routes deep QA support analysis through Beacon's `qa evo-deep` surface.

`qa-evo-deep` reads frozen requirement truth, QA materials, and available evidence to produce routeable findings for deeper QA exploration. It is a support surface, not a formal QA verdict surface.
The active human-facing contract is aligned to the current `v1.4.10` docs line (`docs/beacon/v1.4.10/`).

## When to Use

- deep QA gap analysis before or after `beacon qa run`
- state-machine and business-flow scenario exploration
- scenario-combination, permission-boundary, data-consistency, and cross-surface closure review
- repeated QA round memory review when failures or blockers recur
- release supplement input that still needs formal QA/release absorption

## Boundary

- does not replace `beacon qa run`
- does not produce a formal QA pass/fail verdict
- does not produce a release verdict
- does not rewrite PRD, user-story, test-case, freeze state, QA verdict, or release verdict
- round memory is advisory influence only and never counts as current pass evidence

## Workflow / Decision Loop

- read frozen `prd / user-story / test-case` and QA evidence
- identify routeable deep QA findings
- route requirement truth drift to `beacon-change-refreeze`
- route coverage gaps to `beacon-test-case`
- route implementation gaps to `beacon-implement`
- route evidence gaps to `beacon-qa`
- route release supplement input to `beacon-release` only after formal QA evidence exists

## Command

Use the fixed entrypoint:

```bash
beacon qa evo-deep "<feature>" --project . --version <version>
```

Use JSON only when automation needs the machine projection:

```bash
beacon qa evo-deep "<feature>" --project . --version <version> --json
```

## Write Topology

- detailed human-readable findings: `docs/beacon/<version>/qa/evo-deep/<feature>.md`
- machine projection: `docs/beacon/<version>/.machine/qa/evo-deep/<feature>.json`
- research: index or design-input summary only; do not duplicate the detailed QA evo-deep report there

## Common Rationalizations

- “qa-evo-deep 已经分析很深了，可以算 QA 通过。” -> 不允许；必须回到 `beacon qa run`。
- “历史轮次都过了，这轮不用重新验。” -> 不允许；round memory 只能影响场景选择。
- “发现需求不对，直接在 qa-evo-deep 里改 PRD。” -> 不允许；truth drift 必须走 `change/refreeze`。

## Red Flags

- finding 没有 affected requirement 或 route recommendation
- 把 blocked admission 写成产品 fail
- 把 release supplement input 写成 release pass
- 详细报告写进 `research/<feature>.md` 造成重复 truth

## Verification

- output path is `docs/beacon/<version>/qa/evo-deep/<feature>.md`
- machine output is evidence/read-model only
- findings use supported families: state machine, business flow, scenario combination, permission boundary, data source consistency, cross-surface closure, repeated failure
- every finding remains routeable and does not claim forbidden authority

## Evidence Produced

- QA evo-deep report
- routeable findings
- blocked admission notes
- round-memory influence notes
- release supplement input for later formal absorption

## State Updated

- `docs/beacon/<version>/.machine/qa/evo-deep/<feature>.json`

## Gate Impact

- no direct gate verdict
- can block release indirectly by exposing QA evidence gaps, truth drift, or unresolved routeable findings

## Examples

- 适用例：
  - “QA 看起来过了，但我担心状态机和业务流程叠加场景没覆盖。”
  - “同一个 blocker 多轮出现，想让 QA 深挖一下路线和记忆。”
  - “release 前需要一份深 QA findings 作为补充输入。”
- 不适用例：
  - “我要正式验收通过。” -> 应运行 `beacon-qa`
  - “我要冻结新需求。” -> 应运行 `beacon-change-refreeze`
  - “我要直接修改 test-case truth。” -> 应运行 `beacon-test-case`

## Cold-start anchors

- `qa-evo-deep` 是深 QA 支持分析，不是正式 QA。
- 它只产出可路由发现，不改 truth，不下 release 结论。
- 详细结果固定写入 `docs/beacon/<version>/qa/evo-deep/<feature>.md`。
