---
name: beacon-release
description: Use when the user wants Beacon to judge release readiness, inspect final blocking conditions, or run the last release-facing checks through Beacon's current v1.4.7 runtime surface.
---

# Beacon Release

## Overview

This skill routes final ship / release-readiness work through Beacon's `release` surface.

Release consumes layered QA proof and version-surface governance, then makes the go/no-go judgment. It does not invent acceptance truth or finish implementation.
The active human-facing contract is aligned to the current `v1.4.7` docs line (`docs/beacon/v1.4.7/`).
Compatibility bridges may still exist for older entrypoints or wrappers, but release judgment must bind to the current docs/runtime truth line.

## When to Use

- release readiness
- final go / no-go checks
- last-mile delivery confidence
- checking whether implementation and QA are sufficient to ship
- release proof chain validation

## Boundary

- `release` is not a place to finish implementation
- it does not rewrite frozen truth
- it does not bypass version-surface governance

## Workflow / Decision Loop

- continue in `release` only when implementation and QA have already produced enough evidence
- block on missing QA layers, unresolved truth drift, version-surface drift, or unresolved release blockers
- prefer explicit no-go over soft optimism when evidence is incomplete
- route backward when the missing condition belongs to `qa`, `implement`, or `change`

## Common Rationalizations

- “dashboard 看着都绿了，应该能发。” -> 不允许；要看证据链
- “real-project-validation 过了，其他层可以省。” -> 不允许；它是高权重层，不是唯一层
- “版本号差一点没关系，先发再说。” -> 不允许；version drift 必须阻断

## Red Flags

- QA 证据链未闭合，却已经寻求 go verdict
- docs/package/runtime version surfaces 不一致
- release 试图替 requirement truth 或 implementation gap 收尾

## Verification

- `skill-contract / scenario-suite / trace-scorecard / real-project-proof` 四层证明可追溯
- no-go blocker 和 reason code 明确
- docs/package/runtime version surfaces 一致

## Evidence Produced

- release readiness verdict
- final blocker list
- release-facing proof summary

## State Updated

- release scorecard / release-facing gate state

## Gate Impact

- direct go / no-go gate
- may block ship and route back to `qa`, `implement`, or `change`

## Inputs Contract

- `project-root`
- `version`
- `feature` or version release target
- layered QA proof
- release gate status
- version surface governance status

## Decision Protocol

- Continue in `release` only when implementation and QA have already produced sufficient evidence.
- Block on missing QA layers, unresolved truth drift, version-surface drift, or unresolved release gate blockers.
- Prefer explicit no-go verdicts over soft optimism when evidence is incomplete.
- Treat `real-project-validation` as highest proof, but still require the other layers.

## Anti-Inertia Notes

- `release` is not a place to finish implementation or invent acceptance truth.
- A green-looking dashboard without evidence chain is not release closure.
- Version drift across docs, package, and runtime surfaces must block ship.
- `release` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse prior release blockers as warning signals for current no-go checks.
- Learning may influence inspection order, but it does not override gate verdicts.
- Stale release learning should trigger re-check, not silent acceptance.

## Backstop CLI

- `beacon release ...`
- `beacon qa ...` when proof is incomplete
- `beacon doctor verify-version-surfaces --project-root . --strict`

## Supporting References

Use these lightweight references when the release conversation is blocked by human-readable ambiguity rather than missing commands:

- `../references/release-blocker-taxonomy.md`
- `../references/qa-layer-checklist.md`
- `../references/support-surface-routing-cheatsheet.md`

These references help classify blockers and route fallback correctly, but they do not replace release evidence or version-surface governance.

## Examples

- 适用例：
  - “这条 feature 的实现和 QA 都做完了，现在要判断能不能放行。”
  - “我要看最后的 release blocker 还剩什么。”
  - “我怀疑 dashboard 是绿的，但证据链未必真的闭合。”
- 不适用例：
  - “实现还没完成，只是想继续修功能。” -> 应回 `beacon-implement`
  - “acceptance proof 还没跑完整。” -> 应优先去 `beacon-qa`

## Cold-start anchors

- `release` 判断的是 go / no-go，不是补实现或补真相的地方。
- 绿色表象不等于 release closure，证据链和版本治理缺口都必须阻断。
- `real-project-validation` 是高权重证明，但不是唯一证明。
