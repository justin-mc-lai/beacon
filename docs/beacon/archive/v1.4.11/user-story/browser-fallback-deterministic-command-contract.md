# User Story: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer reducing legacy browser runner ambiguity, I want deterministic project commands to have a truthful current name and evidence model, so that QA and release can distinguish browser-agent execution from deterministic command execution without losing compatibility for old `--fallback-cmd` usage.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | current syntax | Browser adapter current syntax exposes `--deterministic-command` or `--explicit-project-command`. |
| AC-002 | compat alias | Legacy `--fallback-cmd` remains callable as a compatibility alias. |
| AC-003 | execution mode | Deterministic project command execution records `execution_mode=deterministic_command`. |
| AC-004 | evidence split | Evidence records browser agent availability separately from deterministic command execution. |
| AC-005 | no false browser success | Evidence does not claim browser-agent success when only deterministic command execution happened. |
| AC-006 | compat evidence | `--fallback-cmd` usage records compatibility evidence bound to `browser-fallback-command-name`. |
| AC-007 | generated commands | Current QA/browser command templates prefer deterministic command naming over legacy fallback naming. |
| AC-008 | fail closed | Missing browser agent and missing deterministic command fail closed with clear reason code. |
| AC-009 | no unrelated behavior | Tests prove no prototype/design, QA mirror, PRD mirror, implement package, memory, intent, or test marker behavior changes. |
| AC-010 | repair route | Help/status/report or evidence readout distinguishes browser setup repair from deterministic command setup repair. |

## Explicit Non Coverage

- This story does not reopen prototype behavior.
- This story does not modify `beacon-design`.
- This story does not migrate memory or intent behavior.
- This story does not relayer test markers.
- This story does not remove `--fallback-cmd`.
- This story does not create a release verdict by itself.

## Traceability

- Research: `docs/beacon/archive/v1.4.11/research/browser-fallback-deterministic-command-contract.md`
- PRD: `docs/beacon/archive/v1.4.11/prd/browser-fallback-deterministic-command-contract.md`
- Test cases: `docs/beacon/archive/v1.4.11/qa/test-cases/browser-fallback-deterministic-command-contract.md`
