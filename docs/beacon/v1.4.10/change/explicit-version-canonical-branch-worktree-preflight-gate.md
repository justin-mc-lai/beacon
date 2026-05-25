# Change: Explicit Version Canonical Branch Worktree Preflight Gate

**Feature**: `explicit-version-canonical-branch-worktree-preflight-gate`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## 1. Change Reason

Rolo P0 friction `friction:b0bf5951800d` showed that an implementation can pass the existing `origin/master` ancestry gate while still committing to a non-canonical Beacon version branch.

The concrete incident occurred after the operator explicitly specified Beacon `v2.0.0`. The target services `marketing_primary_fe` and `marketing_sys` first received implementation commits on `feature/v1.3.5-truth-engine-cutover`, while Rolo `docs/beacon/v2.0.0/execution/branch-governance-*.md`, `git-workflow-*.md`, and `deterministic-implementation-contract-*.md` already identified `feature/v2.0.0-all` worktrees as the canonical implementation lane.

## 2. Accepted Change

Freeze a v1.4.10 follow-up requirement that makes explicit Beacon version branch/worktree resolution a hard pre-code and pre-commit gate:

1. When a user explicitly supplies a Beacon version, implement must resolve that version's execution materials before any code edit or commit.
2. The gate must read `docs/beacon/<version>/execution/branch-governance-*.md`, `git-workflow-*.md`, and `deterministic-implementation-contract-*.md` when present.
3. The gate must verify the target service's canonical branch and worktree, including per-service maps where `expected_branch=per-service`.
4. A mismatch must hard-stop before code edit, commit, push, UAT merge, or delivery.
5. `origin/master` ancestry validation remains required, but it must run after or inside the canonical branch/worktree preflight and must not be treated as sufficient on its own.
6. Regression coverage must reproduce the Rolo v2.0.0 failure shape for `marketing_sys` and `marketing_primary_fe`.

## 3. Scope

### In Scope

- Beacon implement preflight behavior when `--version` or an equivalent explicit version is provided.
- Version-to-execution-material resolution for branch governance, git workflow, and deterministic implementation contracts.
- Per-service canonical branch and worktree validation.
- Fail-closed reason codes and human recommendations for switching to canonical worktrees.
- Regression test coverage for the Rolo v2.0.0 marketing service mismatch.

### Out Of Scope

- Executing code changes for Rolo.
- Changing Rolo business requirements.
- Replacing `rolo-dev` as the Rolo delivery surface.
- Removing `origin/master` ancestry checks.
- Automatically cherry-picking or repairing wrong-branch commits.
- Implementation, QA, release, or deployment of this Beacon feature.

## 4. Route Decision

- The source support finding `friction:b0bf5951800d` is accepted for requirement/change routing.
- This change freezes requirement truth only.
- Downstream implementation may start only after this refreeze transaction completes.

## 5. Source Evidence

- Rolo friction capture: `/Users/apple/Developer/Company/rolo/.beacon/debug/friction-captures/782652e26492.json`
- Rolo friction report: `/Users/apple/Developer/Company/rolo/.beacon/analysis/friction-intake-fit-20260525T040609Z.json`
- Rolo v2.0.0 branch governance:
  - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/branch-governance-msq-part1-dossier.md`
  - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/branch-governance-msq-questionnaire-revamp.md`
- Rolo v2.0.0 git workflow and deterministic contract:
  - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/git-workflow-msq-part1-dossier.md`
  - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/deterministic-implementation-contract-msq-part1-dossier.md`

## 6. Freeze Deliverables

- `docs/beacon/v1.4.10/change/explicit-version-canonical-branch-worktree-preflight-gate.md`
- `docs/beacon/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md`
- `docs/beacon/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md`
- `docs/beacon/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md`

## 7. Boundary

This change refreezes requirement truth only. It does not execute implementation, QA, release, commit repair, or direct writes to any Rolo service repository.
