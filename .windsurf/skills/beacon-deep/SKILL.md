---
name: beacon-deep
description: Use when Beacon should run deep analysis as a support surface for complex business risk, test-delta derivation, cross-stage routing, and release supplement closure without adding a new lifecycle stage.
---

# Beacon Deep

## Overview

This skill routes deep analysis work through Beacon's `deep` support surface.

`deep` analyzes frozen requirement truth, derives routeable findings and test deltas, and writes support evidence. It does not become a parallel truth or QA stage.
It is not a primary lifecycle stage.

## When to Use

- high-risk trigger and low-risk skip decisions
- state-machine, fact-source, invariant, and consistency-chain analysis
- deep test delta derivation before QA
- structural QA feedback review when P0/P1/P2 defects expose modeling gaps
- release supplement evidence for deep closure, waiver, backlog, or skip decisions

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen PRD, user-story, or test-case truth directly

## Workflow / Decision Loop

- analyze frozen truth and structural evidence
- derive findings, deltas, and route decisions
- route requirement gaps to `change/refreeze`
- route acceptance gaps to `test-case`
- route implementation gaps to `implement`
- route QA evidence gaps to supplemental `qa`
- route release risks to closure, waiver, or backlog decision

## Common Rationalizations

- “deep 发现的问题可以直接写回 truth。” -> 不允许；只能 route
- “这已经相当于做完 QA 了。” -> 不允许；deep 不代替验证
- “既然是高风险分析，deep 自己可以下最终 gate verdict。” -> 不允许；只能投影回 gate 影响

## Red Flags

- findings 没有 route target
- 结论只停在分析文字，没有 test delta / risk / closure impact
- `deep` 被当成新 stage，而不是 support analysis surface

## Verification

- findings are classifiable and routeable
- test delta and release supplement outputs are auditable
- accepted deep conclusions still need existing truth/execution/gate surfaces to close the loop

## Evidence Produced

- deep analysis report
- state machine report
- deep test delta
- risk register
- deep loop trace
- deep closure brief
- optional skip evidence

## State Updated

- deep transaction/read model artifacts

## Gate Impact

- no direct gate verdict
- can increase or reduce gate confidence by binding findings back to `test-case`, `qa`, or `release`

## Operator rule

Prefer:

- `beacon deep run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh deep run ...`

Keep toolkit internals hidden behind `beacon-deep` unless the user explicitly asks for implementation details.

## Examples

- 适用例：
  - “这条 feature 风险很高，我想先做更深的状态机、约束链和测试增量分析。”
  - “QA 暴露了结构性问题，我想知道这到底该回 `change`、`test-case`，还是 `implement`。”
  - “release 前需要补一层深分析证据，但不想新增主 stage。”
- 不适用例：
  - “我已经明确要改 frozen truth。” -> 应回 `beacon-change`
  - “我现在只是要正式执行验证。” -> 应优先去 `beacon-qa`

## Cold-start anchors

- `deep` 是 support analysis surface，不是新的主流程阶段。
- 它的价值是产出可路由的发现、delta 和 closure evidence，不是直接改 truth 或代替 QA。
- deep 结论只有在被现有 truth/execution/release surface 吸收后，才真正进入主闭环。
