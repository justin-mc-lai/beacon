# User Story: QA Evo Deep Evidence-Bound AC-Aware Closure

**Feature**: `qa-evo-deep-evidence-bound-ac-aware-closure`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Story

As a Beacon operator preparing a feature for QA or release, I want QA evo-deep findings to be bound to frozen acceptance criteria and current QA evidence, so that a deep QA report cannot look complete while missing the business closure proof needed for downstream decisions.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | required source reads | QA evo-deep reads PRD, user-story, test-case, QA scorecard, and AC closure before producing a ready report. |
| AC-002 | finding evidence binding | Every ready finding includes non-empty `affected_ac_ids` and non-empty `current_evidence_refs`. |
| AC-003 | empty skeleton block | Empty skeleton findings fail closed unless represented as blocked admissions with explicit source gaps and route recommendations. |
| AC-004 | Skill Eval replay | Skill Eval Kit validates route decision, boundary preservation, and source anchoring through replay traces instead of schema-only checks. |
| AC-005 | formal QA absorption | QA scorecard records whether each deep finding was absorbed, deferred, blocked, or not applicable. |
| AC-006 | release supplement boundary | Release readiness treats only formally absorbed deep findings as release supplement input and keeps advisory-only or blocked findings out of pass evidence. |
| AC-007 | authority boundary | QA evo-deep and Skill Eval outputs cannot claim PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority. |

## Non Goals

- This story does not replace `beacon qa`.
- This story does not produce a release verdict.
- This story does not add browser automation.
- This story does not implement project hooks, Ralph checkpoint control, or project skill auto-injection.

## Boundary

QA evo-deep remains support analysis. Its output can create routeable, evidence-bound findings and release supplement input only through formal QA absorption. Canonical truth remains in PRD, user-story, test-case, requirement clarity, and freeze.
