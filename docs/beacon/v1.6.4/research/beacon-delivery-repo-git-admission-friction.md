# Research: Delivery-Repo Git Admission Friction (R5)

**Version**: v1.6.4  
**Feature**: `beacon-global-workspace-git-admission-v162` (R5 extension)  
**Date**: 2026-07-06  
**Friction refs**: `friction:73c1790d551e`, `friction:025cd2a6322f`, `friction:cd5f8a72940b`

## Outcome

SidePilot delivery repos use **program-level** branches (`beacon/v0.0.9`) and **custom dedicated worktrees** (`cloud-platform/`, sibling `selfmedia-sync-ai-v0.0.10/`). Beacon v1.6.2+ CLI assumed **per-feature** branches (`beacon/vX/<slug>`) and optional soft admission — causing branch drift when agents wrote from `main`.

## Root Cause

1. `require_workspace_admission=false` on delivery semver `< v1.6.2` made `workspace admit` a no-op (`skipped: true`).
2. `resolve_feature_branch` / `resolve_worktree_path` appended lake slug to worktree base.
3. `doctor branch-governance verify` did not surface `current_branch != target_branch`.
4. Cursor workspace root ≠ governed implement branch with no fail-closed gate.

## Remediation Layers

| Layer | Owner | Status |
|-------|-------|--------|
| SidePilot `project-version-governance.md` hard admission | Delivery | ✅ 2026-07-06 |
| SidePilot git-workflow `branch_resolution_mode=program-level` | Delivery | ✅ 2026-07-06 |
| Beacon R5 program-level resolve in `workspace admit` | Beacon CLI | ✅ implement |
| Beacon doctor branch mismatch reason_codes | Beacon CLI | ✅ implement |
| Soft admission branch alignment (UD-024) | Beacon CLI + skills | ✅ implement |

## Route Recommendation

- **Implement**: `beacon-global-workspace-git-admission-v162` R5 (AC-019–AC-022)
- **QA**: SidePilot fixture + unit tests in `test_v162_delivery_program_branch_r5.py`
- **Release**: v1.6.4 patch after QA pass

## Non-Goals

- Rewrite SidePilot git history
- Force all delivery repos to hard admission (SidePilot opted in explicitly)
