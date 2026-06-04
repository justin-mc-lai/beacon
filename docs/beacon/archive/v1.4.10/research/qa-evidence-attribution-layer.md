# Research Closure: QA Evidence Attribution Layer

**Feature**: `qa-evidence-attribution-layer`  
**Version**: `v1.4.10`  
**Status**: `research-closure`  
**Date**: `2026-05-25`

## Truth Bindings

- prd_refs: `docs/beacon/archive/v1.4.10/prd/qa-evidence-attribution-layer.md`
- user_story_refs: `docs/beacon/archive/v1.4.10/user-story/qa-evidence-attribution-layer.md`
- test_case_refs: `docs/beacon/archive/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md`
- coverage_notes: The frozen coverage must verify failure taxonomy, AC/evidence binding, route matrix, fail-closed behavior, skill defect proposal-only behavior, authority boundary, and release consumption boundary.
- out_of_scope_notes: This closure does not implement SkillEvolver-style automatic skill mutation, does not replace formal QA, does not add a lifecycle stage, does not change release verdict rules directly, and does not execute hidden side-effect hooks.

## Source Anchors

- `docs/beacon/archive/v1.4.10/research/embodiskill-skillevolver-qa-attribution-foundation.md`
- `docs/beacon/archive/v1.4.10/research/qa-evo-deep-evidence-bound-ac-aware-closure.md`
- `docs/beacon/archive/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/global-boundaries.md`

## Architecture

`qa-evidence-attribution-layer` is a formal QA support component that sits before final QA route and verdict closure:

```text
formal QA evidence
  -> attribution layer
  -> failure_family + affected_ac_ids + evidence_refs
  -> route_recommendation
  -> formal QA closure
  -> release readiness consumes formal QA only
```

The layer adopts EmbodiSkill's core distinction between a defective skill and an execution lapse, then extends it to Beacon's requirement chain:

- `truth_drift`: requirement truth must reopen through `beacon-change`.
- `implementation_gap`: implementation must route to `beacon-implement`.
- `coverage_gap`: acceptance coverage must route to `beacon-test-case`.
- `execution_lapse`: QA must rerun or continue through `beacon-qa`.
- `skill_defect`: Beacon skill improvement must become research/change proposal input only.
- `runner_admission_blocker`: runner or environment admission must block without becoming product failure.
- `evidence_insufficient`: QA must continue gathering evidence and cannot pass release readiness.

The attribution layer writes support evidence only. It cannot write PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict.

## Business Flow

```text
1. Beacon operator runs or reviews QA.
2. QA evidence is incomplete, failed, or blocked.
3. Attribution validates current AC IDs and evidence refs.
4. Attribution chooses one failure family.
5. Attribution emits a deterministic route recommendation.
6. Formal QA records whether the attribution is accepted, blocked, or superseded.
7. Release readiness consumes only the formal QA closure, not raw attribution.
```

Failure routes:

| Failure Family | Route | Business Meaning |
| --- | --- | --- |
| `truth_drift` | `beacon-change` | Accepted truth is stale or wrong. |
| `implementation_gap` | `beacon-implement` | Implementation did not satisfy valid AC. |
| `coverage_gap` | `beacon-test-case` | Test-case truth is insufficient. |
| `execution_lapse` | `beacon-qa` | QA run failed to follow valid QA procedure. |
| `skill_defect` | research/change proposal | Beacon QA rule or skill needs governed improvement. |
| `runner_admission_blocker` | `blocked` | Environment or runner admission prevents evaluation. |
| `evidence_insufficient` | `beacon-qa` | Evidence is not enough to pass, fail, or release. |

## State Machine

```text
qa_evidence_collected
  -> attribution_pending
  -> attribution_ready
  -> formal_qa_records_attribution
  -> release_consumes_formal_qa
```

Blocked states:

- `source_evidence_missing`: AC or evidence refs are missing.
- `runner_admission_blocked`: runner never reached AC evaluation.
- `authority_boundary_violation`: attribution claims truth or verdict authority.
- `ambiguous_failure_family`: evidence cannot distinguish failure type.

Recovery:

- `source_evidence_missing` routes to `evidence_insufficient`.
- `runner_admission_blocked` routes to `blocked`.
- `authority_boundary_violation` fails closed and requires Beacon change/review.
- `ambiguous_failure_family` fails closed as `evidence_insufficient` unless a specific blocker is proven.

## Branch Flow

```text
QA evidence issue
  -> Does evidence show frozen truth is stale?
     -> yes: truth_drift -> beacon-change
  -> Does valid truth lack implementation proof?
     -> yes: implementation_gap -> beacon-implement
  -> Does acceptance/test coverage miss the case?
     -> yes: coverage_gap -> beacon-test-case
  -> Did QA procedure lapse while rule is valid?
     -> yes: execution_lapse -> beacon-qa
  -> Is Beacon QA skill or rule defective?
     -> yes: skill_defect -> research/change proposal
  -> Did runner/admission block evaluation?
     -> yes: runner_admission_blocker -> blocked
  -> Otherwise:
     -> evidence_insufficient -> beacon-qa
```

## Decision Priority

1. Authority boundary violation blocks first.
2. Proven `truth_drift` routes to `beacon-change`.
3. Proven `coverage_gap` routes to `beacon-test-case`.
4. Proven `implementation_gap` routes to `beacon-implement`.
5. Proven `runner_admission_blocker` routes to `blocked`.
6. Proven `execution_lapse` routes to `beacon-qa`.
7. Proven `skill_defect` becomes research/change proposal input only.
8. Unproven or ambiguous evidence becomes `evidence_insufficient`.
9. Release readiness consumes only formal QA closure after attribution is recorded.

## Conclusion

The first governed adoption from EmbodiSkill/SkillEvolver research should be a QA evidence attribution layer, not automatic skill evolution. This preserves Beacon's single truth chain while improving QA route determinism and future skill evolution discipline.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-25T11:46:29.005681+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.4.10/deep/qa-evidence-attribution-layer`
- machine_artifact_root: `docs/beacon/archive/v1.4.10/.machine/deep/qa-evidence-attribution-layer`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.4.10/.machine/deep/qa-evidence-attribution-layer/release-supplement.json`
- adoption_status: `route_only`
