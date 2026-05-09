# Project Skill QA Evolution Blueprint

- version: `v1.4.1`
- feature: `beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure`
- status: `freeze-ready / implement-pending`

## Skill Surface Evolution

`v1.4.1` adds one support-facing capability family:

- human skill: `beacon-deep`
- preferred CLI entry: `beacon deep run`
- internal toolkit families:
  - `beacon-toolkit-deep-loop`
  - `beacon-toolkit-state-machine`
  - `beacon-toolkit-test-delta`
  - `beacon-toolkit-risk-register`

This does not alter the primary Beacon lifecycle. The support skill may analyze and route, but implementation still enters through `implement` and acceptance still enters through `qa`.

## QA Evolution

Deep analysis changes QA preparation, not QA ownership:

- before QA, deep can derive missing test deltas from PRD, user stories, state axes, fact-source maps, and existing test cases
- during QA, normal defects remain normal QA issues
- after QA, structural defects can re-enter deep only when they imply missing state, fact-source, consistency, or requirement coverage
- adopted deep deltas must be represented in `test-case` or supplemental QA artifacts

## Gate Evolution

Deep gate semantics are additive:

- high-risk features may require deep closure, waiver, or explicit skip evidence
- low-risk features may pass with explicit skip reason
- release-blocking findings must be closed or waived before release readiness
- backlog findings require explicit accepted backlog decision, but do not block by default

## Implementation Handoff

The frozen handoff consists of:

- `docs/beacon/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/user-story/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- `docs/beacon/v1.4.1/qa/test-cases/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- generated machine projections under `docs/beacon/v1.4.1/.machine/`
- requirement clarity and revision delta reports under `docs/beacon/v1.4.1/execution/`
