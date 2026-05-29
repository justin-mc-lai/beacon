# PRD: Implement Mode Frozen Truth Requirement Contract

**Feature**: `implement-mode-frozen-truth-requirement-contract`
**Version**: `v1.4.11`
**Status**: `refreeze-input`
**Date**: `2026-05-29`

## Overview

Beacon implement must consume the same frozen truth that downstream QA expects it to satisfy. The current implementation prompt injects PRD, user-story, and test-case files, but it does not inject existing project-level `PRODUCT.md` or `DESIGN.md`, and it only asks for free-form verification.

This feature freezes a narrow implement contract: include existing project product/design truth in the default task prompt and require AC-by-AC implementation self-verification before QA handoff.

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.4.11/SUMMARY.md`
- Research: `docs/beacon/v1.4.11/research/implement-mode-frozen-truth-requirement-contract.md`
- Source architecture: `docs/beacon/v1.4.11/source-architecture/implement-mode-frozen-truth-requirement-contract.md`
- Primary source: `beacon/utils/implement_adapters.py`

## 1. 问题

Source-driven research confirmed that `build_default_task_prompt` in `beacon/utils/implement_adapters.py` includes frozen PRD, user-story, and test-case paths but does not mention `PRODUCT.md` or `DESIGN.md`.

The implement design truth gate in `beacon/commands/implement/commands.py` is prototype-adapter oriented; it does not protect project-level design/product truth. The prompt boundary utility also focuses on PRD/user-story/test-case conflict patterns, not project truth files.

As a result, an implementation can drift from product/design truth while still appearing to follow frozen requirement files.

This is a 分层 gap: requirement truth exists in PRD/user-story/test-case, while project-level product/design truth exists in root files and version design contracts. Implement currently consumes only one layer.

## 2. 目标

- AC-001: The default implement task prompt includes existing root-level `DESIGN.md` as project-level design truth.
- AC-002: The default implement task prompt includes existing root-level `PRODUCT.md` as project-level product truth.
- AC-003: Missing `DESIGN.md` or `PRODUCT.md` does not block prompt generation.
- AC-004: The prompt distinguishes project-level product/design truth from frozen PRD/user-story/test-case requirement truth.
- AC-005: The prompt requires an AC coverage matrix before QA handoff.
- AC-006: The AC coverage matrix records each AC as `pass`, `partial`, or `blocked`.
- AC-007: Each AC coverage row includes evidence or a blocking note.
- AC-008: Simple, team, and ralph remain implement modes under `beacon-implement`; no new public implement mode skill is introduced.
- AC-009: Regression tests cover project truth injection and AC coverage matrix wording.
- AC-010: Scope stays source-anchored to `build_default_task_prompt`; team-worker injection and ralph baseline hash enforcement are excluded from this change.

## 3. 设计原则

### 3.1 边界

`PRODUCT.md` and `DESIGN.md` are project-level truth inputs when present. They do not replace frozen PRD, user-story, or test-case truth, and implement must route requirement conflicts back to change/refreeze.

### 3.2 分层

The prompt must name two layers separately:

- frozen requirement truth: PRD, user-story, test-case;
- project-level truth: `PRODUCT.md`, `DESIGN.md`.

### 3.3 恢复

If project-level truth files are absent, implement remains usable and continues with frozen requirement truth. Absence is a non-blocking state, not a crash path.

### 3.4 风险与缓解

Risk: implementation may again drift from design/product truth.
Mitigation: prompt injection plus regression tests make project truth references explicit.

Risk: AC verification may remain free-form.
Mitigation: require AC-by-AC matrix rows with status and evidence/note before QA handoff.

## 4. 范围

### In Scope

- Project-root `PRODUCT.md` and `DESIGN.md` discovery for prompt construction.
- Prompt text that separates project-level truth from frozen requirement truth.
- Prompt text that requires AC-by-AC matrix output before QA handoff.
- Regression coverage against the prompt builder.
- Keeping mode behavior inside existing `beacon-implement`.

### Out Of Scope

- No new lifecycle stage.
- No new public implement mode skill.
- No mandatory creation of `PRODUCT.md` or `DESIGN.md`.
- No per-worker truth injection for team mode.
- No ralph baseline hash enforcement.
- No broad QA gate rewrite.
- No migration of historical implementation outputs.

## 5. 功能需求

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Discover project-root `DESIGN.md` and include it in the default implement prompt when present. |
| FR-002 | AC-002 | Discover project-root `PRODUCT.md` and include it in the default implement prompt when present. |
| FR-003 | AC-003 | Preserve prompt generation when either project truth file is absent. |
| FR-004 | AC-004 | Label project-level truth separately from frozen requirement truth. |
| FR-005 | AC-005, AC-006, AC-007 | Require AC-by-AC implementation self-verification with `pass`, `partial`, or `blocked` status plus evidence or note. |
| FR-006 | AC-008 | Preserve simple, team, and ralph as modes under the existing `beacon-implement` route. |
| FR-007 | AC-009 | Add focused tests for prompt truth refs and coverage matrix requirements. |
| FR-008 | AC-010 | Keep unsupported mode-specific mechanisms out of the current implementation scope. |

## 6. Source Contract

Implementation should update the default task prompt path rather than introducing a separate lifecycle route.

Primary source anchor:

```text
beacon/utils/implement_adapters.py
  build_default_task_prompt
```

Related surfaces:

```text
skills/beacon/beacon-implement/SKILL.md
.agents/skills/beacon-implement/SKILL.md
beacon/utils/implement_mode_playbooks.py
beacon/utils/implement_prompt_boundary.py
beacon/commands/implement/commands.py
```

## 7. State Axes

| Axis | States | Meaning |
| --- | --- | --- |
| `mode_selection` | `simple`, `team`, `ralph` | Implement mode selection remains existing behavior. |
| `truth_injection` | `requirement_truth_only`, `project_truth_present`, `project_truth_absent` | Whether project truth files are injected in addition to frozen requirement truth. |
| `ac_verification` | `not_reported`, `pass`, `partial`, `blocked` | AC-level implementation self-verification status. |
| `design_alignment` | `not_applicable`, `aligned`, `partial`, `blocked` | Implementation relationship to project design truth. |

## 8. 验收标准

- AC-001: Prompt includes `DESIGN.md` as project-level design truth when present.
- AC-002: Prompt includes `PRODUCT.md` as project-level product truth when present.
- AC-003: Prompt generation succeeds when either project truth file is absent.
- AC-004: Prompt separates project-level truth from frozen requirement truth.
- AC-005: Prompt requires AC coverage matrix before QA handoff.
- AC-006: Prompt requires each AC row to use `pass`, `partial`, or `blocked`.
- AC-007: Prompt requires evidence or blocking note per AC row.
- AC-008: No new public implement mode skill is introduced.
- AC-009: Regression tests cover prompt truth injection and AC matrix wording.
- AC-010: Implementation scope stays limited to the default prompt contract.

## 9. Non Goals

- Do not turn `PRODUCT.md` or `DESIGN.md` into mandatory files for every Beacon project.
- Do not make implement responsible for freezing design truth.
- Do not allow implement to override PRD, user-story, or test-case truth.
- Do not hide requirement changes inside implementation work.

## 10. Success Metrics

- A prompt built in a project with `PRODUCT.md` and `DESIGN.md` references both files explicitly.
- A prompt built without those files still succeeds.
- Implement output expectations include a per-AC matrix with status and evidence/note.
- Tests fail if the prompt drops project truth injection or AC matrix wording.

## 11. Diagram Truth Layer

### 11.1 Diagram Types
- `branch-flow`
- `state-machine`
- `decision-priority`

### 11.2 State Axes
- `mode_selection`
- `truth_injection`
- `ac_verification`
- `design_alignment`

### 11.3 Propagation Contract
- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.
- State axes must not be silently compressed into one implicit status field.
