# PRD: Explicit Version Canonical Branch Worktree Preflight Gate

**Feature**: `explicit-version-canonical-branch-worktree-preflight-gate`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## Overview

This feature strengthens Beacon implement preflight so an explicitly supplied Beacon version cannot be reduced to a generic protected-branch or `origin/master` ancestry check. Version-specific canonical branch and worktree material must be resolved first and enforced before code is edited or committed.

## 1. Problem

The current execution path can validate that a feature branch has absorbed `origin/master` while failing to validate that the branch is the canonical branch for the explicitly requested Beacon version.

In Rolo, Beacon `v2.0.0` execution materials already stated that `marketing_sys` and `marketing_primary_fe` must use `feature/v2.0.0-all` worktrees. The implementation nevertheless first committed on `feature/v1.3.5-truth-engine-cutover`. That required cherry-pick correction and reset before UAT delivery.

The missing behavior is a deterministic version-to-canonical-branch/worktree gate that executes before any code edit or commit.

## 2. Goals

- AC-001: When an explicit Beacon version is supplied, implement resolves execution materials from `docs/beacon/<version>/execution/` before code edit or commit.
- AC-002: Implement reads branch governance, git workflow, and deterministic implementation contract materials when present.
- AC-003: Implement validates canonical branch and canonical worktree per target service.
- AC-004: `expected_branch=per-service` is resolved through the service branch/worktree map and is never treated as a literal branch.
- AC-005: Branch/worktree mismatch hard-stops before code edit, commit, push, UAT merge, or delivery.
- AC-006: `origin/master` ancestry validation remains required but cannot independently satisfy implement preflight.
- AC-007: The Rolo v2.0.0 marketing service mismatch is covered by regression tests.
- AC-008: The gate emits actionable reason codes and recommendations that name the expected canonical branch and worktree.

## 3. Design Principles

### 3.1 Version truth before branch hygiene

Generic branch hygiene answers whether a branch is current against the protected baseline. It does not answer whether the branch is the right lane for the requested Beacon version. The requested version must be resolved first.

### 3.2 Per-service maps are first-class

Multi-service projects can use different branches and worktrees for different services in the same version. Beacon must validate the target service against its own map entry.

### 3.3 Fail before mutation

The failure must occur before code edit and before commit. A gate that detects the mismatch after local commits already exist is too late.

## 4. Scope

### In Scope

- Implement preflight version material loading.
- Branch governance, git workflow, and deterministic implementation contract parsing sufficient to resolve canonical service branch/worktree maps.
- Current repo/worktree branch validation for each target writable service.
- Hard-stop status, reason codes, and recommended remediation commands.
- Regression tests for Rolo-style multi-service per-service branch maps.

### Out Of Scope

- Rolo service code edits.
- Automatic wrong-branch commit recovery.
- Rewriting historical friction records.
- Replacing Rolo's delivery workflow or `rolo-dev`.
- New public lifecycle stages.

## 5. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | If the user supplies an explicit version, implement must load `docs/beacon/<version>/execution/` before it permits code edits or commits. |
| FR-002 | AC-002 | The loader must consider `branch-governance-*.md`, `git-workflow-*.md`, and `deterministic-implementation-contract-*.md` as branch/worktree contract sources. |
| FR-003 | AC-003 | For each target service, implement must verify the current checkout or worktree path is the service's canonical worktree and branch. |
| FR-004 | AC-004 | `expected_branch=per-service` must resolve to a service branch map. Missing or ambiguous map entries must block. |
| FR-005 | AC-005 | Any branch/worktree mismatch must set preflight `blocked=true` before code edit, commit, push, UAT merge, or delivery can proceed. |
| FR-006 | AC-006 | `origin/master` ancestry checks must run only after or inside the canonical branch/worktree preflight, and their pass result must not override canonical mismatch. |
| FR-007 | AC-007 | Tests must model Rolo v2.0.0 with `marketing_sys` and `marketing_primary_fe` on `feature/v1.3.5-truth-engine-cutover` while expected worktrees are `feature/v2.0.0-all`. |
| FR-008 | AC-008 | Blocked output must include reason codes such as `explicit_version_canonical_branch_mismatch` and expected branch/worktree recommendations. |

## 6. Success Metrics

- A version-explicit implement run cannot start code editing from a non-canonical branch.
- Rolo v2.0.0 marketing service mismatch blocks with a recommendation to use `feature/v2.0.0-all` worktrees.
- `origin/master` ancestry pass is visible as a sub-check, not as the overall implement gate pass.
- Per-service branch maps are preserved in machine and human preflight evidence.

## 7. Boundary

This feature changes requirement and implementation gate behavior only. It does not grant `beacon-change-refreeze`, `friction-intake`, or `rolo-dev` authority to execute implementation, QA, release, or direct repository repair.
