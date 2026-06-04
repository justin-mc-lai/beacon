# User Story: Real Project QA Evidence Binding and Markdown Matrix Fail-Closed

**Feature**: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Story

As a Beacon operator validating a real project, I want implementation evidence, Markdown QA truth, project runner commands, and blocker taxonomy to stay aligned, so that QA and release do not produce false closure signals.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | implementation evidence | Implement completion or controlled `import-evidence` writes a QA-readable implementation evidence marker with feature, version, run/import id, source refs, changed files or service directories, summary ref, created_at, imported flag, and approved_by when imported. |
| AC-002 | markdown matrix | When Markdown QA has a parseable coverage matrix, `.machine/qa/<feature>.ac-test-matrix.json` preserves the original AC ID, TC ID, layer, command, assertion, and evidence path; parser failure blocks with diagnostics instead of fallback. |
| AC-003 | project runner | QA can resolve a Go + UniApp project runner profile with backend target tests, frontend type-check, miniapp build, and route check commands. |
| AC-004 | blocker taxonomy | QA distinguishes product_failed, test_failed, runner_admission_blocked, environment_blocked, auth_session_blocked, evidence_binding_missing, coverage_gap, and truth_projection_gap. |
| AC-005 | regression fixture | The BMTOP `rules-encyclopedia-admin-closure` case is captured as a regression fixture covering missing implementation marker, Markdown matrix fallback, project runner mismatch, unavailable frontend test script, and Docker/testcontainers environment blocker. |

## Non Goals

- No Better Harness acceptance criterion is defined in this P0 line; that remains future work.
- `qa-evo-deep` remains a future QA support/profile candidate and must not replace AC-001 through AC-005.

## Boundary

- This story does not authorize release pass.
- This story does not create a new lifecycle stage.
- This story does not allow support skills to modify frozen truth.
