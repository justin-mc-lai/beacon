# User Story: Implement Mode Frozen Truth Requirement Contract

**Feature**: `implement-mode-frozen-truth-requirement-contract`
**Version**: `v1.4.11`
**Status**: `refreeze-input`
**Date**: `2026-05-29`

## Story

As a Beacon operator, I want implement mode to receive existing project-level product and design truth along with frozen requirement truth, so implementation does not drift from `PRODUCT.md`, `DESIGN.md`, or acceptance criteria before QA.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | design truth injection | The default implement task prompt includes existing root-level `DESIGN.md` as project-level design truth. |
| AC-002 | product truth injection | The default implement task prompt includes existing root-level `PRODUCT.md` as project-level product truth. |
| AC-003 | optional project truth | Missing `DESIGN.md` or `PRODUCT.md` does not block prompt generation. |
| AC-004 | truth separation | The prompt distinguishes project-level product/design truth from frozen PRD/user-story/test-case requirement truth. |
| AC-005 | AC matrix required | The prompt requires an AC coverage matrix before QA handoff. |
| AC-006 | AC statuses | The AC coverage matrix records each AC as `pass`, `partial`, or `blocked`. |
| AC-007 | AC evidence | Each AC coverage row includes evidence or a blocking note. |
| AC-008 | mode boundary | Simple, team, and ralph remain implement modes under `beacon-implement`; no new public implement mode skill is introduced. |
| AC-009 | regression coverage | Tests cover project truth injection and AC coverage matrix wording. |
| AC-010 | source-anchored scope | This change stays anchored to `build_default_task_prompt`; team-worker injection and ralph baseline hash enforcement are not included. |

## Test Story Map

| Test ID | Covers | Scenario |
| --- | --- | --- |
| TEST-001 | AC-001 | Build a prompt in a project containing `DESIGN.md` and assert the prompt references it as project-level design truth. |
| TEST-002 | AC-002 | Build a prompt in a project containing `PRODUCT.md` and assert the prompt references it as project-level product truth. |
| TEST-003 | AC-003 | Build a prompt in a project without project truth files and assert prompt generation succeeds. |
| TEST-004 | AC-004 | Inspect prompt sections and assert project-level truth and frozen requirement truth are separate. |
| TEST-005 | AC-005, AC-006, AC-007 | Inspect prompt wording and assert an AC coverage matrix with `pass`, `partial`, `blocked`, and evidence/note is required. |
| TEST-006 | AC-008, AC-010 | Assert no new public implement mode skill is added and existing mode topology remains under `beacon-implement`. |
| TEST-007 | AC-009 | Run focused regression tests for prompt truth injection and AC matrix wording. |
