# Beacon v1.4.1 Execution Index

## Version Line

- version: `v1.4.1`
- status: `planning_only`
- theme: `deep analysis support surface and risk closure`
- runtime line: `v1.4.0` remains current runtime release

## Human Truth

- Summary: `docs/beacon/archive/v1.4.1/SUMMARY.md`
- PRD: `docs/beacon/archive/v1.4.1/prd/beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure.md`
- Research supplement: `docs/beacon/archive/v1.4.1/research/beacon-deep-capability-upgrade-research-supplement.md`

## Execution Boundary

`v1.4.1` introduces no new required human lifecycle stage.

The main lifecycle remains:

```text
prd
-> user-story
-> test-case
-> implement
-> qa
-> release
```

When UI handoff exists, `prototype` remains conditional between `test-case` and `implement`.

`deep` is a support/analysis/gate-supplement surface that can be triggered by high-risk feature attributes, QA findings, or explicit user request. It may propose requirement supplements and test deltas, but it cannot rewrite canonical truth without the normal change/refreeze path.

`deep` should be exposed as a human support skill/toolkit surface such as `beacon-deep`, not as a new lifecycle stage.

The preferred support loop is:

```text
scan_truth
-> model_business
-> challenge_gaps
-> derive_delta
-> classify_findings
-> route_repairs
-> verify_closure
```

The default closure target is one run per stable user intent. A new loop is justified when the user introduces a new feature, role, business process, state machine, or release-blocking evidence.

## Planned Artifact Families

Future implementation should converge on these human-facing artifacts:

- `docs/beacon/<version>/deep/<feature>-deep-analysis.md`
- `docs/beacon/<version>/deep/<feature>-state-machine.md`
- `docs/beacon/<version>/qa/test-cases/<feature>-deep-delta.md`
- `docs/beacon/<version>/deep/<feature>-risk-register.md`
- `docs/beacon/<version>/deep/<feature>-deep-loop-trace.md`
- `docs/beacon/<version>/execution/deep-closure-brief-<feature>.md`

These artifacts are recommendations and release-facing evidence until accepted through normal truth governance.
