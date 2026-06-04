# User Story: QA Evo Deep And Skill Eval Kit v1.4.10

**Feature**: `qa-evo-deep-and-skill-eval-kit-v1410`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Story

As a Beacon operator preparing a feature for implementation and release, I want deep QA exploration and skill/harness regression checks to produce governed, routeable evidence, so that requirement certainty, implementation certainty, and acceptance certainty can improve without turning support surfaces into truth sources.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | QA evo-deep output | Beacon defines a governed QA evo-deep output contract with source refs, finding type, risk, affected ACs, route recommendation, blocked admissions, and release supplement input. |
| AC-002 | round memory boundary | QA evo-deep records prior QA round memory as advisory influence only and never counts it as current pass evidence. |
| AC-003 | deep coverage taxonomy | QA evo-deep supports state-machine, business-flow, scenario-combination, permission-boundary, data-source-consistency, cross-surface-closure, and repeated-failure finding families. |
| AC-004 | write topology | QA evo-deep detailed output writes to `docs/beacon/<version>/qa/evo-deep/<feature>.md`; research stores only index or design-input summaries. |
| AC-005 | eval case schema | Skill Eval Kit defines auditable cases with id, prompt, expected route, boundary expectations, source anchors, tags, split, expected evidence, and scoring dimensions. |
| AC-006 | regression core | Skill Eval Kit defines optimization and holdout splits plus a small regression core that can be run before skill or harness release. |
| AC-007 | evidence boundary | Skill Eval Kit run outputs are runtime or machine evidence only and do not become requirement truth. |
| AC-008 | route stability | Skill Eval Kit includes route-stability cases for ordinary support skills, `beacon-deep`, `beacon-learn`, and `beacon-implement --mode single/team/ralph`. |
| AC-009 | authority gate | Requirement clarity or release readiness fails closed if QA evo-deep or Skill Eval output claims PRD, user-story, test-case, QA verdict, release verdict, or freeze authority. |

## Non Goals

- This story does not implement Ralph Task Loop.
- This story does not implement project lifecycle hooks.
- This story does not implement automatic `beacon learn` skill injection.
- This story does not split `beacon-implement` into multiple public skills.
- This story does not execute implementation, QA, or release.

## Boundary

QA evo-deep and Skill Eval Kit remain governed support and evidence surfaces. They can create findings, blockers, route recommendations, and harness quality evidence, but only PRD, user-story, test-case, requirement clarity, and freeze define requirement truth.
