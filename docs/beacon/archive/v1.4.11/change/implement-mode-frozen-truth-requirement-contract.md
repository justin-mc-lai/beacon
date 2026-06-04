# Change: Implement Mode Frozen Truth Requirement Contract

**Feature**: `implement-mode-frozen-truth-requirement-contract`
**Version**: `v1.4.11`
**Status**: `refreeze-input`
**Date**: `2026-05-29`

## 1. Change Reason

Beacon implement currently relies on frozen PRD, user-story, and test-case files, but the default implementation prompt does not inject existing project-level `PRODUCT.md` or `DESIGN.md`.

This creates a practical drift path: an implementation agent can satisfy generic requirement text while ignoring project product/design truth. The confirmed friction source is `friction:7f8df1217a82`, where implement did not verify alignment against requirement truth, and the related process drift where implement ignored `DESIGN.md` / `PRODUCT.md` when they existed.

## 2. Accepted Change

Freeze a small source-anchored contract for `beacon-implement`:

1. `build_default_task_prompt` must include existing root-level `PRODUCT.md` and `DESIGN.md` as project-level product/design truth inputs.
2. Missing `PRODUCT.md` or `DESIGN.md` must not block non-design or legacy projects.
3. The implement prompt must distinguish project-level product/design truth from frozen PRD/user-story/test-case requirement truth.
4. The implement prompt must require an AC coverage matrix before QA handoff.
5. The AC matrix must report each acceptance criterion as `pass`, `partial`, or `blocked` with evidence or a blocking note.
6. The scope remains inside existing `beacon-implement` modes; no new public implement mode skill or lifecycle stage is introduced.

## 3. Source Evidence

- Research: `docs/beacon/archive/v1.4.11/research/implement-mode-frozen-truth-requirement-contract.md`
- Source architecture: `docs/beacon/archive/v1.4.11/source-architecture/implement-mode-frozen-truth-requirement-contract.md`
- Prompt builder: `beacon/utils/implement_adapters.py`
- Implement command orchestration: `beacon/commands/implement/commands.py`
- Prompt boundary utility: `beacon/utils/implement_prompt_boundary.py`
- Mode playbooks: `beacon/utils/implement_mode_playbooks.py`
- Skill surface: `skills/beacon/beacon-implement/SKILL.md`

## 4. Scope

### In Scope

- Default implement task prompt truth injection.
- Existing `PRODUCT.md` and `DESIGN.md` discovery at project root.
- AC-by-AC implementation self-verification wording.
- Regression coverage proving the prompt contains project truth refs and structured AC matrix requirements.
- Preservation of simple, team, and ralph as modes under the existing `beacon-implement` surface.

### Out Of Scope

- No new implement lifecycle stage.
- No new public implement subskill for simple, team, or ralph.
- No mandatory creation of `PRODUCT.md` or `DESIGN.md`.
- No per-worker team-mode truth injection in this change.
- No ralph baseline hash enforcement in this change.
- No QA verdict automation change beyond prompt contract and regression coverage.

## 5. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/change/implement-mode-frozen-truth-requirement-contract.md`
- `docs/beacon/archive/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md`

## 6. Boundary

This change updates implement's frozen truth consumption contract. It does not redefine design truth, product truth, QA acceptance, release behavior, or Beacon lifecycle topology.
