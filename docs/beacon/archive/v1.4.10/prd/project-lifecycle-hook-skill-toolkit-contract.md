# PRD: Project Lifecycle Hook Skill Toolkit Contract

**Feature**: `project-lifecycle-hook-skill-toolkit-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Overview

- Research: `docs/beacon/archive/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
- Source architecture: `docs/beacon/archive/v1.4.10/source-architecture/project-lifecycle-hook-skill-toolkit-contract.md`
- Related P0 foundation: `docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md`

## 1. Problem

Beacon supports a stable requirement-to-release lifecycle, but real projects often need project-specific delivery actions between stages:

1. Beacon release may need local CLI and global agent skill installation after release evidence is accepted.
2. Rolo implementation may need a UAT pipeline delivery before formal QA.
3. Rolo QA may need Debug Lab diagnostics when UAT evidence or environment admission is blocked.

Without a governed project-level hook contract, these actions become manual memory, hidden automation, or ad hoc skill calls. That creates ambiguous evidence, silent failure routes, and risk that hook success is mistaken for QA or release success.

## 2. Goals

- AC-001: Define project-level hook truth under `docs/beacon/hooks/<hook-id>.md`, not version-level hook truth.
- AC-002: Define a single-file Markdown hook contract with frontmatter fields and human-readable sections.
- AC-003: Restrict hooks to a finite hook code taxonomy.
- AC-004: Provide admission rules for manual confirmation, dry-run, skill availability, command template safety, and failure routing.
- AC-005: Store hook run evidence and latest read models without making them requirement truth.
- AC-006: Define human-facing toolkit behavior for listing, planning, dry-running, confirmed running, disabling, and explaining hooks.
- AC-007: Provide fixture coverage for Beacon post-release install, Rolo post-implement UAT, and Rolo QA Debug Lab.
- AC-008: Preserve lifecycle authority boundaries: hooks cannot replace implement, QA, release, change, or gate verdicts.
- AC-009: Keep hidden auto-run, arbitrary shell hooks, and project-specific defaults out of the frozen P1 scope.

## 3. Design Principles

### 3.1 Hooks are project-level extensions

Hook definitions live at `docs/beacon/hooks/<hook-id>.md`. Version lines may freeze requirements about hook behavior, but they do not own hook truth.

### 3.2 Hooks open only at finite lifecycle boundaries

The first contract supports only:

- `post_implement_pre_qa`
- `qa_diagnostics`
- `post_qa_pre_release`
- `post_release`

### 3.3 Manual confirmation is the default safety model

High-side-effect actions such as UAT deploy, global install, pipeline triggering, notification, and diagnostics must require an explicit operator confirmation. Dry-run and plan are always allowed when admission passes.

### 3.4 Evidence is not truth

Hook evidence may support implementation, QA, or release decisions. It cannot rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate truth.

## Scope

### In Scope

- Hook Markdown contract fields and sections.
- Hook code taxonomy and lifecycle boundary mapping.
- Hook admission validation.
- Hook evidence and read model paths.
- Human-facing `beacon-project-hooks` skill / `beacon hooks` toolkit behavior.
- Fixture hook contracts:
  - `beacon-post-release-local-install`
  - `rolo-post-implement-uat`
  - `rolo-qa-debuglab`
- Help/status/release support summaries for hook evidence and blockers.

### Out Of Scope

- Hidden automatic hook execution.
- Arbitrary shell hooks.
- Project-specific commands hard-coded into Beacon core defaults.
- Version-scoped hook definitions.
- Hook execution during refreeze.
- Any hook authority over requirement, QA, release, or gate truth.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must discover hook contracts from `docs/beacon/hooks/<hook-id>.md` and must not require or create canonical hook truth under `docs/beacon/<version>/hooks/`. |
| FR-002 | AC-002 | A hook contract must be a single Markdown file with frontmatter for hook id, hook code, project, enabled state, trigger policy, skill, command template, evidence outputs, and failure route. |
| FR-003 | AC-003 | Beacon must reject hook codes outside `post_implement_pre_qa`, `qa_diagnostics`, `post_qa_pre_release`, and `post_release`. |
| FR-004 | AC-004 | Hook admission must validate enabled state, lifecycle binding, project applicability, skill availability, trigger policy, required evidence declaration, and failure route. |
| FR-005 | AC-004 | Hook commands with side effects must require `manual_confirmed`; dry-run must not execute side-effect commands. |
| FR-006 | AC-005 | Hook runs must write runtime evidence under `.beacon/state/hooks/<hook-id>/<run-id>.json` and a latest read model under `docs/beacon/.machine/hooks/<hook-id>.latest.json`. |
| FR-007 | AC-006 | The human-facing toolkit must support list, plan, run dry-run, run confirmed, disable, and status/explain behavior. |
| FR-008 | AC-007 | Fixture coverage must include Beacon post-release local install, Rolo post-implement UAT delivery, and Rolo QA Debug Lab hook contracts without making them global defaults. |
| FR-009 | AC-008 | Hook output must be marked as support/runtime evidence and must not claim PRD, user-story, test-case, QA verdict, release verdict, gate verdict, or freeze authority. |
| FR-010 | AC-009 | Hidden auto-run, arbitrary shell hook, and unbounded hook code attempts must fail closed with explicit reason codes. |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `business-flow`
- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `hook_contract_state`
- `hook_admission_state`
- `trigger_policy_state`
- `hook_run_state`
- `hook_evidence_state`
- `failure_route_state`
- `truth_authority_boundary`

### 6.3 Propagation Contract

Hook planning and evidence may be surfaced in help/status/release support summaries. They must remain separate from canonical requirement truth and formal lifecycle verdicts.

## 7. Freeze Deliverables

- `docs/beacon/archive/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/source-architecture/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/change/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/prd/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/user-story/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/qa/test-cases/project-lifecycle-hook-skill-toolkit-contract.md`

## 8. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hook becomes a shadow lifecycle stage | Main Beacon lifecycle becomes ambiguous | Keep finite hook codes and preserve implement/QA/release as authority surfaces. |
| Hook success is treated as release success | False closure | Mark hook output as support evidence only and require formal QA/release verdicts. |
| Project-specific command becomes global default | Cross-project breakage | Keep fixture hooks as examples/admission cases, not core defaults. |
| Hidden auto-run triggers high-side-effect commands | Data or deployment risk | Require manual confirmation and fail closed on hidden auto-run. |
| Hook truth duplicates across versions | Drift | Keep hook definitions in `docs/beacon/hooks/` only. |

## 9. Success Metrics

- Hook contracts are discoverable from `docs/beacon/hooks/`.
- Invalid hook codes and hidden auto-run requests fail closed.
- Dry-run creates plan/evidence without side effects.
- Confirmed run records hook evidence and failure route.
- Help/status can surface hook blockers without changing lifecycle verdicts.
- Fixture hooks validate Beacon/Rolo scenarios without becoming global defaults.
