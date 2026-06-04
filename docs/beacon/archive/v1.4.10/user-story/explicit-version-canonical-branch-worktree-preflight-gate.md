# User Story: Explicit Version Canonical Branch Worktree Preflight Gate

**Feature**: `explicit-version-canonical-branch-worktree-preflight-gate`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## Story

As a Beacon operator working in a multi-service project, I want an explicitly supplied Beacon version to force validation of that version's canonical branch and worktree before any code edit or commit, so that implementation cannot accidentally land on a branch from another version line even when the generic `origin/master` ancestry check passes.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | explicit version material load | When a user explicitly supplies a Beacon version, implement resolves `docs/beacon/<version>/execution/` materials before code edit or commit. |
| AC-002 | contract source coverage | Implement reads branch governance, git workflow, and deterministic implementation contract materials when present. |
| AC-003 | branch and worktree validation | Implement validates the target service's canonical branch and canonical worktree before allowing mutation. |
| AC-004 | per-service branch map | `expected_branch=per-service` resolves through the service branch/worktree map and never passes as a literal branch. |
| AC-005 | hard stop on mismatch | Branch/worktree mismatch blocks code edit, commit, push, UAT merge, and delivery. |
| AC-006 | ancestry gate ordering | `origin/master` ancestry validation remains required but cannot by itself satisfy implement preflight. |
| AC-007 | Rolo regression | A Rolo v2.0.0 scenario with `marketing_sys` and `marketing_primary_fe` on `feature/v1.3.5-truth-engine-cutover` blocks and recommends `feature/v2.0.0-all` worktrees. |
| AC-008 | actionable output | Blocked output includes reason codes and expected canonical branch/worktree recommendations. |

## Non Goals

- This story does not repair already-created wrong-branch commits.
- This story does not alter Rolo business functionality.
- This story does not replace formal `beacon qa` or `beacon release`.
- This story does not add a new Beacon lifecycle stage.

## Boundary

The gate is part of implement preflight. It protects execution before mutation; it does not become requirement truth, QA verdict, release verdict, or branch repair automation.
