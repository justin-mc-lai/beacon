# PRD: Implement Mode Human Playbooks And Routing Contract

**Feature**: `implement-mode-human-playbooks-and-routing-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Overview

- Research: `docs/beacon/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`
- Source architecture: `docs/beacon/v1.4.10/source-architecture/implement-mode-human-playbooks-and-routing-contract.md`
- Related execution surface: `skills/beacon/beacon-implement/SKILL.md`

## 1. Problem

Beacon implementation currently has three runtime modes: `single`, `team`, and `ralph`. The runtime model is useful, but the human-facing surface can be misread as one vague command or as three potential new skills.

Without a frozen mode playbook contract, operators may ask agents to invent `beacon-implement-team` or `beacon-implement-ralph`, support skills may overstep by directly choosing execution behavior, and Skill Eval Kit cannot reliably test route stability for implementation prompts.

## 2. Goals

- AC-001: Preserve `beacon-implement` as the only public implementation skill.
- AC-002: Provide human-facing playbooks for `single`, `team`, and `ralph`.
- AC-003: Define mode admission and recommendation rules.
- AC-004: Clarify Ralph as a closure controller that routes next action, not a QA or release verdict.
- AC-005: Ensure help/status mode recommendations include a reason and the exact `beacon implement run ... --mode <mode>` command.
- AC-006: Add Skill Eval Kit route-stability cases for implement mode prompts.
- AC-007: Fail closed on attempts to route to nonexistent public implement mode skills.
- AC-008: Preserve truth and verdict boundaries for change, PRD, user-story, test-case, QA, release, and gate.

## 3. Design Principles

### 3.1 One public implementation entrypoint

The public human skill remains `beacon-implement`. Mode playbooks are references and route contracts, not new skills.

### 3.2 Modes explain execution shape

- `single`: small, low-risk, clearly scoped implementation.
- `team`: complex implementation requiring role separation or parallel evidence.
- `ralph`: closure controller used when team/complex implementation needs multi-round repair routing toward review, QA, or release.

### 3.3 Recommendation is not execution authority

Help/status and support analysis can recommend a mode. They cannot execute implementation, rewrite frozen truth, or claim QA/release closure.

### 3.4 Ralph routes closure

Ralph may connect implementation, review, QA, and release next actions. It does not replace formal QA, release, or gate verdicts.

## Scope

### In Scope

- Playbook files or equivalent human-facing references for all three modes.
- Updates to `beacon-implement` skill guidance.
- Help/status mode explanation and route recommendation wording.
- Route-stability eval cases for prompts that mention normal implementation, team/subagents, or Ralph closure.
- Boundary and fail-closed behavior for nonexistent public implement mode skills.

### Out Of Scope

- New public implementation skills.
- New lifecycle stages.
- Full Ralph Task Loop checkpoint/recovery controller.
- Auto-running QA or release from Ralph.
- Project lifecycle hooks.
- `beacon learn` project skill injection.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | The skill catalog and agent surfaces must keep `beacon-implement` as the only public implementation skill. |
| FR-002 | AC-002 | Human-facing mode playbooks must define purpose, admission conditions, command form, produced evidence, and boundary for `single`, `team`, and `ralph`. |
| FR-003 | AC-003 | Mode recommendation must distinguish low-risk single work, complex/team work, and closure-control Ralph work. |
| FR-004 | AC-004 | Ralph guidance must state that Ralph routes next action and evidence, but cannot replace QA, release, gate, or frozen truth. |
| FR-005 | AC-005 | Help/status output that recommends an implementation mode must include the reason and the canonical `beacon implement run "<feature>" --project . --version <version> --mode <mode>` command. |
| FR-006 | AC-006 | Skill Eval Kit must include route-stability cases for single/team/ralph prompts and expected route metadata. |
| FR-007 | AC-007 | Attempts to route to `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph` as public skills must fail closed or redirect to `beacon-implement` with mode explanation. |
| FR-008 | AC-008 | No mode playbook or route recommendation may modify PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze state. |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `business-flow`
- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `implement_request_state`
- `mode_resolution_state`
- `mode_admission_state`
- `implementation_evidence_state`
- `ralph_closure_route_state`
- `truth_authority_boundary`

### 6.3 Propagation Contract

Mode playbooks influence implement route explanation, help/status recommendations, and Skill Eval Kit route checks. They do not become separate lifecycle truth or replace formal QA/release evidence.

## 7. Freeze Deliverables

- `docs/beacon/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/source-architecture/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/change/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/prd/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/user-story/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/qa/test-cases/implement-mode-human-playbooks-and-routing-contract.md`

## 8. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Mode playbooks become new public skills | Lifecycle and routing ambiguity | Keep one public skill and eval against nonexistent mode-skill routing. |
| Ralph is mistaken for QA/release | False closure | Explicitly mark Ralph as next-action controller only. |
| Support skills execute implementation directly | Boundary violation | Require route recommendation only; execution stays in `beacon-implement`. |
| Mode recommendation hides its reason | Poor operator trust | Help/status must show reason and command. |

## 9. Success Metrics

- Operators can distinguish `single`, `team`, and `ralph` without seeing three public skills.
- Help/status recommends mode with a clear reason.
- Skill Eval Kit route-stability cases pass for implement mode prompts.
- Nonexistent public mode skill routes fail closed or redirect to `beacon-implement`.
- Ralph recommendations never claim QA, release, or gate authority.
