# PRD: QA Evidence Attribution Layer

**Feature**: `qa-evidence-attribution-layer`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Overview

This feature adds a formal attribution layer before QA route and verdict closure. It ensures Beacon classifies a QA evidence failure by evidence-chain breakpoint before recommending repair, blocked state, or continued QA.

The feature adopts the EmbodiSkill-style distinction between skill defect and execution lapse, and maps it to Beacon's truth, implementation, coverage, runner, and evidence boundaries. SkillEvolver-style patch generation remains future proposal work and is not part of this scope.

## 1. Problem

Beacon already has layered QA proof, AC/evidence binding, QA evo-deep support analysis, Skill Eval Kit, and route-back behavior. The remaining risk is misattribution:

1. A `truth_drift` can be repaired as an implementation bug.
2. A `coverage_gap` can be reported as product failure.
3. A `runner_admission_blocker` can become a false release blocker.
4. A QA execution lapse can be mistaken for a Beacon skill defect.
5. Support findings can be treated as formal QA or release verdicts.

These failures weaken requirement, implementation, acceptance, and evolution determinism.

## 2. Goals

- AC-001: QA attribution uses a finite failure taxonomy.
- AC-002: Each attribution binds to affected AC IDs and current evidence refs, except runner admission blockers where AC binding may be unavailable.
- AC-003: Each failure family maps to a deterministic route recommendation.
- AC-004: Attribution fails closed when evidence is insufficient or the failure family cannot be determined.
- AC-005: Skill defects produce research/change proposal input only and do not automatically patch Beacon skills.
- AC-006: Attribution output cannot claim canonical truth, QA verdict, release verdict, gate verdict, or freeze authority.
- AC-007: Formal release readiness consumes only QA evidence after attribution has been closed or explicitly blocked.

## 3. Failure Taxonomy

| Failure Family | Meaning | Route |
| --- | --- | --- |
| `implementation_gap` | Frozen truth is valid, but implementation evidence does not satisfy AC. | `beacon-implement` |
| `truth_drift` | Frozen truth no longer represents accepted requirement reality. | `beacon-change` |
| `coverage_gap` | Test-case or acceptance coverage is missing or too weak. | `beacon-test-case` |
| `execution_lapse` | QA procedure was valid, but this QA run did not follow it correctly. | `beacon-qa` |
| `skill_defect` | Beacon QA skill, checklist, or route rule is defective. | research/change proposal |
| `runner_admission_blocker` | Runner, credentials, environment, or admission precondition blocks evaluation. | `blocked` |
| `evidence_insufficient` | Evidence is too weak to pass, fail, or release. | `beacon-qa` |

## 4. Design Principles

### 4.1 Attribute before repairing

QA must classify the evidence-chain breakpoint before recommending implement, change, test-case, QA rerun, or blocked route.

### 4.2 Evidence-bound attribution

Attribution output must include affected AC IDs and current evidence refs. Runner admission blockers may omit affected AC IDs only when the runner did not reach AC evaluation.

### 4.3 Proposal, not automatic skill mutation

Skill defects may generate research or change proposal input. They must not silently edit Beacon skills, route rules, PRD, user-story, test-case, QA verdict, release verdict, or gate truth.

### 4.4 Formal QA remains authoritative

The attribution layer can feed formal QA decisions, but cannot replace `beacon qa run` or produce release readiness by itself.

## Scope

The implementation scope is limited to the existing Beacon Python runtime and tests:

- QA attribution schema, validation, route recommendation, and support evidence behavior.
- Formal QA and release-facing read models that may summarize attribution only as support evidence.
- Regression tests for the frozen acceptance criteria.

The implementation must not add new public lifecycle stages, auto-apply Beacon skill patches, mutate requirement truth from QA attribution, execute hidden side-effect hooks, or change release verdict rules directly.

### In Scope

- Attribution schema with `failure_family`, `affected_ac_ids`, `evidence_refs`, `route_recommendation`, `verdict_boundary`, and notes.
- Deterministic route matrix for each supported failure family.
- Validation that attribution remains evidence-bound and authority-bounded.
- QA scorecard or machine evidence support for attribution outputs.
- Regression tests for taxonomy, route mapping, evidence binding, blocked admission, skill defect boundary, and release boundary.

### Out Of Scope

- Auto-generating or auto-applying Beacon skill patches.
- Replacing QA evo-deep, formal QA, release, change, or test-case stages.
- Creating hidden side-effect automation.
- Changing release pass rules directly.
- Ralph Task Loop checkpoint/recovery.
- `beacon learn` project skill injection.

## 6. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must represent QA attribution with one of the finite failure families: `implementation_gap`, `truth_drift`, `coverage_gap`, `execution_lapse`, `skill_defect`, `runner_admission_blocker`, or `evidence_insufficient`. |
| FR-002 | AC-002 | Non-runner attribution must include at least one affected AC ID and one current evidence ref. |
| FR-003 | AC-002 | Runner admission blockers must include blocker reason, admission surface, and evidence refs; affected AC IDs may be empty only when AC evaluation was not reached. |
| FR-004 | AC-003 | `implementation_gap` routes to `beacon-implement`; `truth_drift` routes to `beacon-change`; `coverage_gap` routes to `beacon-test-case`; `execution_lapse` and `evidence_insufficient` route to `beacon-qa`; `runner_admission_blocker` routes to `blocked`. |
| FR-005 | AC-004 | Missing evidence or ambiguous attribution must fail closed as `evidence_insufficient` unless a more specific blocker is proven. |
| FR-006 | AC-005 | `skill_defect` output must be marked as research/change proposal input and must not mutate skill files or requirement truth. |
| FR-007 | AC-006 | Attribution output must fail closed if it claims PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority. |
| FR-008 | AC-007 | Release readiness may summarize attribution as support evidence only after formal QA records it; raw attribution cannot become pass evidence. |

## 7. Diagram Truth Layer

### 7.1 Diagram Types

- `decision-priority`
- `branch-flow`
- `state-machine`
- `business-flow`

### 7.2 State Axes

- `qa_evidence_state`
- `failure_family_state`
- `route_recommendation_state`
- `authority_boundary`
- `skill_evolution_proposal_state`
- `release_consumption_state`

### 7.3 Propagation Contract

QA evidence flows into attribution. Attribution produces a route recommendation and support evidence. Formal QA records whether the attribution is accepted, blocked, or superseded. Release consumes only formal QA closure and cannot treat attribution alone as pass evidence.

## 8. Success Metrics

- QA failures are consistently classified into the finite taxonomy.
- Route recommendations are stable and testable.
- Truth drift, implementation gaps, coverage gaps, runner blockers, skill defects, execution lapses, and insufficient evidence do not collapse into the same failure bucket.
- Skill improvement remains proposal-only unless a later governed change/refreeze accepts it.
- QA and release verdict boundaries remain intact.
