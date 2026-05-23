# Project Skill QA Evolution Blueprint (v1.4.10)

## Intent

This blueprint defines how `v1.4.10` validates Beacon human-facing skill and harness evolution for the P0 feature:

```text
qa-evo-deep-and-skill-eval-kit-v1410
```

The narrow goal is: deep QA can produce routeable findings, and skill/harness routing can be regression-tested without turning support output into requirement truth.

## Required Skill QA Dimensions

QA for this version must verify:

- QA evo-deep writes detailed output to `docs/beacon/<version>/qa/evo-deep/<feature>.md`.
- QA evo-deep research records only index or design-input summaries.
- QA round memory is labeled advisory influence and cannot count as pass evidence.
- QA evo-deep finding families include state machine, business flow, scenario combination, permission boundary, data-source consistency, cross-surface closure, and repeated failure.
- Skill Eval Kit cases include id, prompt, expected route, boundary expectations, source anchors, tags, split, expected evidence, and scoring dimensions.
- Skill Eval Kit supports optimization and holdout splits plus a small regression core.
- Skill Eval Kit run outputs stay runtime or machine evidence only.
- Route-stability cases cover ordinary support skills, `beacon-deep`, `beacon-learn`, and `beacon-implement --mode single/team/ralph`.
- Requirement clarity or release readiness fails closed if QA evo-deep or Skill Eval output claims truth, QA verdict, release verdict, or freeze authority.

## Human-Facing Skill Material Effects

Relevant skill invocations must resolve to one of:

- `qa_evo_deep_finding_recorded`
- `qa_round_memory_influence_recorded`
- `skill_eval_case_recorded`
- `skill_eval_run_recorded`
- `regression_core_passed`
- `regression_core_failed`
- `route_stability_gap_found`
- `truth_reopen_required`
- `read_only_route_only`

Any invocation that cannot resolve to one of these effects is not gate-complete.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen PRD / user-story / test-case for `qa-evo-deep-and-skill-eval-kit-v1410`
- requirement clarity gate passing
- executable tests covering AC-001 through AC-009
- topology tests for QA evo-deep output
- schema tests for Skill Eval Kit cases and runs
- regression-core tests for splits and core membership
- route-stability tests for support and implement mode routing
- fail-closed tests for authority bypass
- release checklist updated from pending to actual observed results

## Current Status

The requirement package is frozen for implementation planning.

Runtime implementation, executable tests, QA evidence, and release promotion are not complete in this document.
