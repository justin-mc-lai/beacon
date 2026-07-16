---
slug: beacon-global-workspace-git-admission-v162
version: v1.6.4
status: frozen
revision_id: R6
language: zh
change_reason: R6 - program/lake aggregation branch governance contract; SidePilot v0.0.12 QA admission friction friction:e3fe3b33ecf9
source_revision_id: R5
canonical_refs:
  prd: docs/beacon/archive/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
  user_story: docs/beacon/archive/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
  test_case: docs/beacon/archive/v1.6.4/features/beacon-global-workspace-git-admission-v162/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Workspace Admission Program/Lake Branch Governance R6

## Overview

R6 repairs the v1.6.4 workspace admission truth for program/lake topology. R5 accepted delivery repos that use program-level branches through `project-version-governance.md` and `git-workflow-*.md`. SidePilot v0.0.12 exposed the remaining gap: a frozen program can define lake feature packages through `program-manifest.md`, `feature-graph.json`, and `program-truth-freeze.json` while the version governance block is absent or lagging. `beacon qa run <lake>` then falls back to per-feature branch admission and blocks the valid aggregation branch `beacon/<version>` with `branch_alignment_required`.

The governance contract is now: when a lake belongs to a frozen program topology, the aggregation branch is first-class branch governance truth. `workspace admit`, soft admission validation, `beacon qa run`, implement, and release must resolve branch targets through the shared `resolve_workspace_branch_targets` contract instead of hard-coding a QA-only exception.

## User Intent

Let Beacon QA read program/lake topology and accept the program aggregation branch after admission, while preserving per-feature branch defaults and still blocking wrong branches under soft admission.

## Source Evidence

| Ref | Role |
|-----|------|
| `friction:e3fe3b33ecf9` | SidePilot v0.0.12 QA admission blocked on valid aggregation branch |
| `.beacon/debug/friction-captures/eec4092c3010.json` | capture showing `beacon qa run` expected `beacon/v0.0.12/<lake>` |
| `.beacon/analysis/friction-intake-fit-20260709T060148Z.md` | planner fit analysis |
| `docs/beacon/archive/v1.6.4/research/beacon-delivery-repo-git-admission-friction.md` | R5 delivery-repo branch admission research |
| `docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md` | source R5 truth authority |

## User Decisions

| ID | Decision | Value |
|----|----------|-------|
| UD-027 | program/lake aggregation branch authority | Frozen program topology (`program-manifest.md`, `feature-graph.json`, `program-truth-freeze.json`) is valid branch governance input for lake features. |
| UD-028 | shared resolver | QA, implement, release, workspace admit, and soft admission use `resolve_workspace_branch_targets`; no QA-only hard-code. |
| UD-029 | aggregation branch target | For a frozen program lake, target branch is the program aggregation branch, defaulting to `beacon/<version>` unless governance explicitly overrides it. |
| UD-030 | per-feature compatibility | If no program-level contract/topology is present, default remains `beacon/<version>/<feature-slug>`. |
| UD-031 | fail-closed soft admission | `require_workspace_admission=false` still validates current branch against the resolved aggregation branch and blocks wrong branch with `branch_alignment_required`. |

## Branch Governance Contract

Normative inputs, in priority order:

1. `docs/beacon/<version>/execution/git-workflow-*.md` with `branch_resolution_mode: program-level`.
2. `docs/beacon/governance/project-version-governance.md` fields such as `branch_resolution_mode: program-level`, `aggregation_branch`, `expected_branch`, `worktree_path`, or per-service canonical branch.
3. Frozen program topology under `docs/beacon/<version>/programs/<program>/` when the requested lake slug appears in `feature-graph.json` or `program-truth-freeze.json`.

Normative output:

| Field | Program/Lake Value |
|-------|--------------------|
| `branch_resolution_mode` | `program-level` |
| `feature_branch` | aggregation branch, default `beacon/<version>` |
| `worktree_path` | explicit governance worktree, current aggregation worktree when invoked there, or version worktree fallback |
| `program_slug` | owning program slug |
| `material_path` | topology/governance material that established the contract |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-023 | program-topology-without-git-workflow | Program-level governance resolves a lake to the aggregation branch from program/lake topology when `git-workflow-*.md` is absent. |
| AC-024 | program-topology-with-git-workflow | Program-level governance still resolves through explicit `git-workflow-*.md` when present. |
| AC-025 | qa-run-aggregation-admission | `beacon qa run <lake>` accepts the aggregation branch after workspace admission and does not block with `branch_alignment_required`. |
| AC-026 | per-feature-default-preserved | Repos without program-level contract/topology continue to resolve `beacon/<version>/<feature-slug>`. |
| AC-027 | soft-admission-wrong-branch-blocks | Soft admission still blocks wrong current branch with `branch_alignment_required` using the shared resolved target. |

## Non-Goals

- Do not rewrite SidePilot history.
- Do not force every delivery repo to enable hard workspace admission.
- Do not add a QA-only branch bypass or special-case `sidepilot-pi-host`.
- Do not replace per-feature branch governance for repos without program topology.

## Downstream Routes

| Stage | Route |
|-------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |
