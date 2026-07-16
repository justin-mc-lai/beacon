# Change Record: Workspace Admission Program/Lake Branch Governance R6

**version**: `v1.6.4`  
**feature**: `beacon-global-workspace-git-admission-v162`  
**revision**: `R6`  
**reason**: `friction:e3fe3b33ecf9` showed `beacon qa run <lake>` still using per-feature branch admission for SidePilot v0.0.12, blocking the valid aggregation branch `beacon/v0.0.12`.

## Accepted Change

Program/lake topology is now a formal branch governance input. When a lake is part of a frozen program topology, Beacon resolves the workspace target to the program aggregation branch, defaulting to `beacon/<version>`, through the shared `resolve_workspace_branch_targets` contract.

## Scope

- program-level governance without `git-workflow-*.md`
- program-level governance with `git-workflow-*.md`
- `beacon qa run <lake>` accepts aggregation branch after admission
- per-feature default remains unchanged
- soft admission still blocks wrong branch with `branch_alignment_required`

## Non-Goals

- no QA-only bypass
- no SidePilot-specific hard-code
- no release or QA verdict from generator
