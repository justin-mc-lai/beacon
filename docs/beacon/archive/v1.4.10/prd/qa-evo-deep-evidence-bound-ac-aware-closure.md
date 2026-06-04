# PRD: QA Evo Deep Evidence-Bound AC-Aware Closure

**Feature**: `qa-evo-deep-evidence-bound-ac-aware-closure`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Overview

This feature strengthens the existing QA evo-deep support surface so it can support business closure rather than only emit a valid taxonomy skeleton. It keeps QA evo-deep as a support surface and makes its findings explicitly tied to frozen requirements and current QA evidence.

## 1. Problem

Current QA evo-deep output can be structurally valid while still failing the operator's deeper intent:

1. Findings can list all supported families without referencing affected acceptance criteria.
2. Findings can recommend `beacon qa supplement` without citing current evidence.
3. Skill Eval Kit can pass schema-level checks without replaying route behavior.
4. Formal QA and release readiness can remain unaware of whether deep findings were absorbed.
5. An empty skeleton can be mistaken for deep business closure.

## 2. Goals

- AC-001: QA evo-deep reads PRD, user-story, test-case, QA scorecard, and AC closure before producing a ready report.
- AC-002: Every ready finding binds to affected AC IDs and current evidence references.
- AC-003: Empty skeleton findings fail closed unless represented as blocked admissions with explicit source gaps.
- AC-004: Skill Eval Kit replays route decision, boundary preservation, and source anchoring.
- AC-005: QA scorecard records whether deep findings were formally absorbed by `beacon qa`.
- AC-006: Release supplement logic distinguishes absorbed deep findings from advisory-only or blocked deep findings.
- AC-007: QA evo-deep remains a support surface and cannot claim PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority.

## 3. Design Principles

### 3.1 Evidence-bound, not evidence-looking

A ready deep finding must name the affected AC and the current evidence that led to the finding. Generic family rows without AC or evidence binding are not deep QA closure.

### 3.2 Blocked admission is explicit

If PRD, user-story, test-case, QA scorecard, or AC closure cannot be read, QA evo-deep must report blocked admission. It must not emit a ready report with placeholder findings.

### 3.3 Replay beats schema validation

Skill Eval Kit must validate behavior through replay traces. A case is not passed only because its fields exist.

### 3.4 Formal QA remains authoritative

Deep findings can influence QA and release readiness only after formal QA records whether they were absorbed, deferred, or blocked.

## 4. Scope

### In Scope

- Source material readers for PRD, user-story, test-case, QA scorecard, and AC closure.
- Finding validation that requires `affected_ac_ids` and `current_evidence_refs` for ready findings.
- Blocked-admission validation and reason codes for missing source evidence.
- Human and machine report fields for `deep_absorption_status`.
- Skill Eval Kit replay traces for route decision, boundary preservation, and source anchoring.
- QA scorecard and release supplement signals for deep finding absorption.

### Out Of Scope

- Making QA evo-deep a formal QA verdict.
- Auto-fixing PRD, user-story, test-case, QA, or release evidence.
- Browser automation or visual QA execution.
- Project hook execution.
- Ralph long-task loop implementation.
- Project skill auto-injection.

## Scope Definition

The implementation scope is limited to the existing Beacon Python runtime and tests:

- `beacon qa evo-deep` source evidence loading, validation, report, and machine projection behavior.
- Skill Eval Kit runtime evidence and replay trace behavior.
- Formal QA scorecard deep absorption fields.
- Release scorecard summary fields for absorbed deep finding supplement eligibility.
- Regression tests for the frozen acceptance criteria.

The implementation must not add new public lifecycle stages, new implement skill entrypoints, browser automation, project hook execution, Ralph checkpoint control, or automatic project skill injection.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | `beacon qa evo-deep` must load the target feature PRD, user-story, test-case, QA scorecard, and AC closure before setting status `ready`. |
| FR-002 | AC-001 | Missing required source material must produce `status=blocked` with reason code `qa_evo_deep_source_evidence_missing`. |
| FR-003 | AC-002 | A ready finding must contain non-empty `affected_ac_ids` and non-empty `current_evidence_refs`. |
| FR-004 | AC-003 | A finding without AC or evidence binding must fail validation with reason code `qa_evo_deep_empty_skeleton_finding` unless it is a blocked admission. |
| FR-005 | AC-003 | Blocked admissions must include source refs, blocked reason codes, and recommended route. |
| FR-006 | AC-004 | Skill Eval Kit runs must produce replay traces that record expected route, actual route, boundary preservation, source anchor coverage, and pass/fail status. |
| FR-007 | AC-004 | Skill Eval Kit must fail a case when route decision, boundary preservation, or source anchoring cannot be replayed. |
| FR-008 | AC-005 | QA scorecard must record deep finding absorption status for each QA evo-deep finding: `absorbed`, `deferred`, `blocked`, or `not_applicable`. |
| FR-009 | AC-006 | Release readiness must only treat absorbed deep findings as release supplement input; advisory-only or blocked findings must remain non-verdict evidence. |
| FR-010 | AC-007 | QA evo-deep and Skill Eval outputs must fail closed if they claim canonical truth, formal QA verdict, release verdict, gate verdict, or freeze authority. |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `business-flow`
- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `source_evidence_state`
- `finding_binding_state`
- `blocked_admission_state`
- `skill_eval_replay_state`
- `deep_absorption_state`
- `release_supplement_state`
- `authority_boundary`

### 6.3 Propagation Contract

QA evo-deep findings flow into formal QA as evidence-bound support input. Formal QA records absorption status. Release readiness may summarize absorbed findings, but it must not promote advisory-only or blocked deep findings into release pass evidence.

## 7. Success Metrics

- Empty skeleton QA evo-deep reports are blocked.
- Every ready finding references at least one affected AC and one current evidence path.
- Missing source materials produce explicit blocked-admission findings.
- Skill Eval Kit replay traces can show route, boundary, and source anchor behavior.
- QA scorecard exposes deep finding absorption status.
- Release supplement input distinguishes absorbed findings from advisory-only findings.
