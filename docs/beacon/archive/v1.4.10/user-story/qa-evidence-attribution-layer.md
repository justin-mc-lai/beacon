# User Story: QA Evidence Attribution Layer

**Feature**: `qa-evidence-attribution-layer`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-25`

## Story

As a Beacon operator reviewing QA results, I want Beacon to classify why QA evidence failed before recommending the next route, so that truth drift, implementation gaps, coverage gaps, runner blockers, QA execution lapses, and Beacon skill defects do not contaminate each other's repair paths.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | finite taxonomy | QA attribution uses only the supported failure families: `implementation_gap`, `truth_drift`, `coverage_gap`, `execution_lapse`, `skill_defect`, `runner_admission_blocker`, and `evidence_insufficient`. |
| AC-002 | evidence binding | Each attribution includes affected AC IDs and current evidence refs; runner blockers may omit AC IDs only when AC evaluation was not reached. |
| AC-003 | deterministic route | Each failure family maps to the correct route recommendation: implement, change, test-case, QA rerun/continue, blocked, or research/change proposal. |
| AC-004 | fail closed | Ambiguous or missing evidence cannot pass release readiness and must fail closed as insufficient evidence or a proven blocker. |
| AC-005 | skill defect boundary | Skill defects create research/change proposal input only and never auto-modify Beacon skills or requirement truth. |
| AC-006 | authority boundary | Attribution output cannot claim PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority. |
| AC-007 | release consumption boundary | Release readiness consumes attribution only through formal QA closure; raw attribution remains support evidence. |

## Non Goals

- This story does not replace `beacon qa`.
- This story does not create a release verdict.
- This story does not automatically patch Beacon skills.
- This story does not add a lifecycle stage.
- This story does not execute hooks, Ralph checkpointing, or project skill injection.

## Boundary

QA attribution is a pre-verdict classification and routing aid. It strengthens formal QA by making failure causes explicit, but formal QA and release gates remain authoritative.
