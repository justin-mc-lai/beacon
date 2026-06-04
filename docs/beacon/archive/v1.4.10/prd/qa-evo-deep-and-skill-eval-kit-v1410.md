# PRD: QA Evo Deep And Skill Eval Kit v1.4.10

**Feature**: `qa-evo-deep-and-skill-eval-kit-v1410`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Overview

- Research: `docs/beacon/archive/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
- Source architecture: `docs/beacon/archive/v1.4.10/source-architecture/qa-evo-deep-and-skill-eval-kit-v1410.md`
- Prior foundation: `docs/beacon/v1.4.9/research/read-only-support-research-write-topology-gate-contract.md`
- Related P1/P2 research inputs:
  - `docs/beacon/archive/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
  - `docs/beacon/archive/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`

## 1. Problem

Beacon can currently run QA and retain execution evidence, but deep acceptance still depends on whether the operator remembers to explore stateful and cross-flow risk. This produces two gaps:

1. QA closure may miss state transitions, business-flow combinations, permission boundaries, cross-surface consistency, data-source drift, and repeated failures across QA rounds.
2. Human-facing skills and harness routes can regress without a small, auditable regression suite that checks routing, boundary preservation, source anchoring, actionability, and closure quality.

## 2. Goals

- AC-001: Provide a governed QA evo-deep output contract for routeable findings.
- AC-002: Preserve QA round memory as advisory influence without converting it into pass verdicts.
- AC-003: Cover state-machine, business-flow, scenario-combination, permission, data-consistency, and cross-surface closure findings.
- AC-004: Keep QA evo-deep output in `docs/beacon/<version>/qa/evo-deep/<feature>.md`, with research storing only design input or index references.
- AC-005: Define Skill Eval Kit case schema, tags, splits, regression core, run output, and scorecard.
- AC-006: Ensure Skill Eval Kit results remain harness quality evidence and never become requirement truth.
- AC-007: Add route-stability and boundary-preservation eval cases for support skills and implement mode routing.
- AC-008: Fail closed when QA evo-deep or Skill Eval output attempts to bypass PRD, user-story, test-case, QA, or release authority.
- AC-009: Keep P1/P2 research inputs outside the frozen P0 scope unless they enter a later change/refreeze.

## 3. Design Principles

### 3.1 QA deep findings route; they do not pass release

`qa-evo-deep` can identify gaps and recommend routes. It cannot replace `beacon qa run`, cannot certify release readiness, and cannot rewrite QA verdicts.

### 3.2 Round memory is influence

Prior QA rounds, browser site memory, and repeated blocker patterns are used to select deeper scenarios. They are hints and risk signals, not acceptance evidence by themselves.

### 3.3 Eval cases are engineering assets

Skill Eval Kit cases must be small, tagged, replayable, and split into optimization and holdout sets. Regression core must be intentionally small and hard.

### 3.4 Markdown-first truth remains authoritative

PRD, user-story, test-case, requirement clarity, and freeze remain requirement truth. Machine eval runs, traces, and runtime state are evidence and read models only.

## Scope

### In Scope

- QA evo-deep Markdown output contract.
- QA evo-deep taxonomy and route recommendation fields.
- QA round memory schema and influence boundaries.
- Skill Eval Kit file layout and case schema.
- Eval tags, splits, regression core, scorecard, and run evidence.
- Route stability evals for support skill routing and `beacon-implement --mode single/team/ralph`.
- Requirement clarity diagnostics for authority bypass attempts.

### Out Of Scope

- Browser automation implementation details beyond QA round memory contract.
- Ralph Task Loop checkpoint controller.
- Project lifecycle hook runtime.
- Automatic context-to-project-skill injection.
- New public implement skill entrypoints.
- Any direct implementation, QA, or release execution.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must provide a QA evo-deep contract that records findings with source refs, finding type, risk, affected ACs, route recommendation, blocked admissions, and release supplement input. |
| FR-002 | AC-002 | QA evo-deep must distinguish historical QA round memory from current-run evidence and mark memory as advisory influence only. |
| FR-003 | AC-003 | QA evo-deep must support finding families for state machine, business flow, scenario combination, permission boundary, data-source consistency, cross-surface closure, and repeated failure. |
| FR-004 | AC-004 | QA evo-deep detailed output must be written under `docs/beacon/<version>/qa/evo-deep/<feature>.md`; research may only index or summarize it. |
| FR-005 | AC-005 | Skill Eval Kit must define a case format with id, prompt, expected route, boundary expectations, source anchors, tags, split, expected evidence, and scoring dimensions. |
| FR-006 | AC-005 | Skill Eval Kit must define optimization and holdout splits plus a regression core that can be run before skill or harness release. |
| FR-007 | AC-006 | Skill Eval Kit run outputs must be stored as runtime evidence under `.beacon/state/skill-eval/` or equivalent machine evidence paths and must not be treated as requirement truth. |
| FR-008 | AC-007 | Skill Eval Kit must include route stability cases for ordinary support skills, `beacon-deep`, `beacon-learn`, and `beacon-implement --mode single/team/ralph`. |
| FR-009 | AC-008 | Requirement clarity or release readiness must fail closed if QA evo-deep output or Skill Eval output claims PRD, user-story, test-case, QA verdict, release verdict, or freeze authority. |
| FR-010 | AC-009 | Ralph Task Loop, project lifecycle hooks, implement mode playbooks, and automatic learn injection must remain deferred research inputs until a later change/refreeze adopts them. |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `business-flow`
- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `qa_deep_output_status`
- `qa_round_memory_role`
- `skill_eval_case_state`
- `regression_core_status`
- `authority_boundary`

### 6.3 Propagation Contract

QA deep and Skill Eval evidence must stay explicit through requirement clarity, implementation planning, QA, and release readiness. Evidence can add repair routes or blockers, but cannot silently promote itself into frozen truth.

## 7. Freeze Deliverables

- `docs/beacon/archive/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
- `docs/beacon/archive/v1.4.10/source-architecture/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/change/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md`

## 8. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| QA evo-deep becomes a shadow QA gate | Release semantics drift | Require routeable findings only and prohibit pass verdicts. |
| Round memory overfits past failures | QA misses new risks | Mark memory as influence and require current source refs for findings. |
| Skill eval becomes another truth source | Requirement authority blurs | Store eval runs as runtime evidence only. |
| Regression core grows too large | Teams stop running it | Keep core small, tagged, and release-blocking only for skill/harness changes. |
| P1/P2 directions creep into P0 | Version scope overload | Keep Ralph, hooks, learn injection, and implement playbooks outside this frozen P0. |

## 9. Success Metrics

- QA evo-deep findings are discoverable from the governed QA evo-deep path.
- Every QA evo-deep finding has a route recommendation and affected requirement reference.
- QA round memory is visible as influence and never counted as pass evidence.
- Skill Eval Kit has replayable cases, tags, splits, regression core, and scorecard.
- Route-stability evals prevent support and implement mode routing drift.
- Requirement clarity blocks any attempt to treat QA deep or eval evidence as requirement truth.
