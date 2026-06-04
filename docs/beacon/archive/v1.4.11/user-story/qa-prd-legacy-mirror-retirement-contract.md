# User Story: QA and PRD Legacy Mirror Retirement Contract

**Feature**: `qa-prd-legacy-mirror-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer reducing legacy burden, I want QA and PRD legacy mirrors to remain readable as explicitly admitted compatibility evidence, so that current QA, PRD, and release decisions cannot be falsely closed by stale or legacy-only artifacts.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | QA canonical authority | Canonical QA status is the default current QA authority for v1.4.11+ flows. |
| AC-002 | QA legacy admission | Legacy QA status can be read only through explicit compatibility admission and must be labeled as historical evidence. |
| AC-003 | release fail closed | Release checks and scorecards cannot pass from legacy-only QA status. |
| AC-004 | PRD Markdown truth | Markdown PRD remains requirement truth and legacy PRD mirror cannot override it. |
| AC-005 | PRD projection blocking | Current PRD projection drift remains blocking when the current projection is stale or inconsistent. |
| AC-006 | PRD compat warning | Legacy PRD mirror mismatch is downgraded to compatibility warning by default. |
| AC-007 | registry binding | QA and PRD legacy mirror policies are bound to compatibility registry entries. |
| AC-008 | no unrelated retirement | Tests prove this slice does not delete legacy files or change implement, prototype, browser, memory, intent, or command behavior. |

## Non Goals

- This story does not delete legacy QA status files.
- This story does not delete legacy PRD mirror files.
- This story does not migrate implement package loading.
- This story does not change prototype legacy source behavior.
- This story does not rename browser fallback behavior.
- This story does not change memory migration behavior.
- This story does not change intent routing behavior.
- This story does not remove commands.
- This story does not create a new human lifecycle stage.
- This story does not produce QA or release verdicts.

## Boundary

This story changes authority policy for two registered compatibility mirrors only.

It makes current authority explicit before later v1.4.11 features remove or migrate deeper legacy behavior.
