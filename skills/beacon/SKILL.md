---
name: beacon
description: Use when you need Beacon's evidence-first workflow as the host-level meta-protocol for deciding which truth, execution, gate, or support surface should run next.
metadata:
  author: Beacon CLI
  version: "1.4.0"
  organization: Beacon
  date: May 2026
  abstract: Compact meta-protocol for Beacon's human-facing workflow surface. It classifies the current decision surface, preserves hard boundaries, and routes to the right child skill without exposing runtime internals by default.
---

# Beacon Skill

This package is the canonical `skills/beacon/` wrapper for Codex and Claude.

Beacon is not just a command catalog. It is a truth-and-delivery meta-protocol:

- classify the current decision surface
- preserve stable boundaries that must not drift
- route to the right truth, execution, gate, or support skill
- keep support capability wide without expanding the public mainline

## Meta-Protocol

Always start with one question:

> 当前问题属于哪个决策面: truth、execution、verification/gate，还是 support?

Route by decision surface, not by tool familiarity, internal runtime mechanics, or which command name looks closest.

The public Codex / Claude surfaces are:

- host entry:
  - `using-beacon`
- truth:
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  - `beacon-change`
- execution:
  - `beacon-prototype`
  - `beacon-implement`
- gate:
  - `beacon-qa`
  - `beacon-release`
- support:
  - `beacon-brainstorm`
  - `beacon-deep`
  - `beacon-ceo-review`
  - `beacon-design-review`
  - `beacon-context-engineering`
  - `beacon-source-driven`
  - `beacon-doubt-review`
  - `beacon-security-review`
  - `beacon-performance-review`
  - `beacon-documentation-adr`
  - `beacon-debug-recovery`
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`
  - `beacon-learn`
  - `beacon-archive`
  - `beacon-real-project-validation`
  - `beacon-friction-intake`

## Current v1.3.9 Additions

Legacy compatibility anchors that should remain discoverable from the packaged host skill:

- `beacon-deep` remains a deep analysis support surface
- `beacon-friction-intake` remains available through `beacon friction-intake run ...`
- historical host-pack tests may still look for named support surfaces from earlier packaged lines

## Stable Rules

These rules should remain true even when runtime details evolve:

- main chain stays compact: `prd -> user-story -> test-case -> implement -> qa -> release`
- `prototype` is conditional, not a mandatory new stage for every feature
- support surfaces stay advisory and do not become truth sources
- support surfaces are not gate sources
- support surfaces are not new lifecycle stages
- canonical truth remains versioned under `docs/beacon/<version>/`
- QA prompt contract must follow first principles and bind claims back to evidence
- if a scorecard or gate path says `stop_for_repair`, route to repair or truth recovery before continuing
- browser-admitted or compatibility paths such as `browser-use` remain optional capability planes, not default lifecycle requirements

## Route-Back Rules

Use these defaults:

- promise, scope, ambiguity, or acceptance still open -> `beacon-prd`, `beacon-user-story`, or `beacon-test-case`
- frozen truth must change -> `beacon-change`
- coding or implementation execution against frozen truth -> `beacon-implement`
- evidence closure, verification depth, or acceptance proof -> `beacon-qa`
- release readiness, blocker judgment, or go/no-go -> `beacon-release`
- blocked, unsure next step, or resume guidance -> `beacon-help` or `beacon-status`
- package drift, docs drift, environment drift, or context corruption -> `beacon-doctor`

If any support surface changes accepted scope or promise, it must route back through `beacon-change`.

## Support Surface Constitution

Support surfaces exist to widen judgment, not to replace the mainline.

They may:

- challenge framing
- expose uncertainty or drift
- improve evidence quality
- strengthen implementation method
- explain route and fallback

They may not:

- freeze canonical truth by default
- claim implementation completion
- issue release verdicts by default
- silently replace `change`, `implement`, `qa`, or `release`

`beacon-deep` remains the deep analysis support surface for high-risk structural review and test-delta derivation.

## Human vs Machine Readout

Human-facing output should stay concise:

- current status
- blocker if any
- recommended next surface
- fallback or repair route

Machine-facing output should stay complete:

- reason codes
- evidence refs
- artifact paths
- diagnostics
- runtime or transaction metadata

Beacon should absorb complexity into machine-readable surfaces first, then project only the minimum useful action layer to humans.

## Current Anchors

Keep only the minimum current anchors here:

- current package version: `1.4.6`
- current public runtime/docs line: `docs/beacon/v1.4.6/`
- current planning line for this evolution theme: `docs/beacon/v1.4.7/`
- if a target project pins another docs line, follow the pinned local truth instead of silently overriding it

## Lightweight References

When the user needs fast human-readable judgment support, start with:

- [`references/usage-rules.md`](./references/usage-rules.md)
- [`references/support-surface-routing-cheatsheet.md`](./references/support-surface-routing-cheatsheet.md)
- [`references/requirement-closure-checklist.md`](./references/requirement-closure-checklist.md)
- [`references/freeze-readiness-checklist.md`](./references/freeze-readiness-checklist.md)
- [`references/qa-layer-checklist.md`](./references/qa-layer-checklist.md)
- [`references/release-blocker-taxonomy.md`](./references/release-blocker-taxonomy.md)
- [`references/external-lifecycle-mapping.md`](./references/external-lifecycle-mapping.md)
- [`references/research-closure-checklist.md`](./references/research-closure-checklist.md)
- [`references/business-flow-checklist.md`](./references/business-flow-checklist.md)
- [`references/state-machine-checklist.md`](./references/state-machine-checklist.md)

These references are non-canonical support material. They help humans scan and decide faster, but they do not replace versioned truth.

For complex features, the minimum freeze-facing requirement chain remains:

`research -> prd -> user-story -> test-case -> requirement_clarity -> freeze`

## Deep References

When versioned delivery context is needed, read progressively:

1. [`../../docs/beacon/v1.4.6/SUMMARY.md`](../../docs/beacon/v1.4.6/SUMMARY.md)
2. [`../../docs/beacon/v1.4.6/execution/index.md`](../../docs/beacon/v1.4.6/execution/index.md)
3. [`../../docs/beacon/v1.4.6/release/v1.4.6.md`](../../docs/beacon/v1.4.6/release/v1.4.6.md)
4. [`../../docs/beacon/v1.4.7/SUMMARY.md`](../../docs/beacon/v1.4.7/SUMMARY.md)

Do not treat this wrapper as the full runtime manual or release note.

## Lifecycle Navigation Rules

- `beacon help --project-root . --json` is the default recovery route when the next surface is unclear.
- If frozen truth is stale, do not push through execution. Reopen through `beacon-change`.
- If verification reveals drift or weak evidence, return to the right truth or execution surface instead of hand-waving through gate.
- If support output is only advisory, say so explicitly and route back.
- Support surfaces such as `beacon-friction-intake` may run host-visible commands like `beacon friction-intake run ...`, but they still do not become truth or gate stages.

## Examples

- 适用例：
  - “我想用 Beacon 作为总入口，但先要判断现在属于哪种决策面。”
  - “我需要一个稳定的元协议，把 truth、execution、qa、release 和 support surface 路由清楚。”
  - “我知道 Beacon 很严谨，但这轮到底该先走主链还是先走 support？”
- 不适用例：
  - “我已经明确知道要进哪条具体子 skill，而且只想看那条 skill 的边界。” -> 直接进入对应子 skill

## Cold-start anchors

- 主 `beacon` skill 的职责是路由和边界，不是总 runbook。
- 好的入口不是把所有命令都摊开，而是先判断当前问题属于哪个决策面。
- Beacon 的 support 面可以更强，但主链不应因此继续膨胀。
