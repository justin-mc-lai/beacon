---
slug: beacon-global-workspace-git-admission-v162
version: v1.6.4
status: frozen
revision_id: R7
language: zh
change_reason: R7 - nested aggregation branch vs child feature ref coexistence; stale per-feature execution contracts must not force program-level; doctor path-repair confirmed residual contract gap
source_revision_id: R6
canonical_refs:
  prd: docs/beacon/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
  user_story: docs/beacon/v1.6.4/features/beacon-global-workspace-git-admission-v162/truth.md
  test_case: docs/beacon/v1.6.4/features/beacon-global-workspace-git-admission-v162/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Workspace Admission Nested-Ref Coexistence R7

## Overview

R7 repairs a residual branch-governance gap left after R6 and after doctor path repair. R6 made program/lake aggregation branches first-class (`beacon/<version>` by default). In Beacon's own v1.6.4 delivery line, per-feature lanes already occupy child refs `beacon/v1.6.4/<feature-slug>`. Git cannot create the parent ref `beacon/v1.6.4` while those children exist, so `workspace admit` fails with nested-ref lock errors.

Doctor repaired Mac→current `project_root` / `worktree_root` drift. After that repair, five released QA lakes still resolve as `program-level` to `beacon/v1.6.4` with worktree at the primary checkout, then fail admission. Root causes that remain in requirement truth:

1. Default aggregation branch `beacon/<version>` collides with child feature refs.
2. Per-feature `deterministic-implementation-contract-*.md` with `target_branch` + `worktree_root` is treated as program-level even without explicit `branch_resolution_mode: program-level`, git-workflow, or frozen program topology.
3. Aggregation worktree may resolve to the primary repo root, which cannot be added as a dedicated worktree.

## User Intent

Keep program/lake aggregation admission, but make aggregation branch/worktree resolution coexist with per-feature child refs, refuse stale per-feature contracts as fake program-level authority, and fail closed with an explicit nested-ref reason code.

## Source Evidence

| Ref | Role |
|-----|------|
| doctor admit after path repair | `beacon-qa-chrome-extension-e2e-v164` blocked: `cannot lock ref 'refs/heads/beacon/v1.6.4': '.../beacon-global-workspace-git-admission-v162' exists` |
| `docs/beacon/v1.6.4/execution/deterministic-implementation-contract-beacon-qa-*-v164.md` | stale `single-branch` / `target_branch: beacon/v1.6.4` / absolute worktree root |
| `docs/beacon/governance/project-version-governance.md` | v1.6.4 canonical branch `beacon/v1.6.4` plus `next_version_feature_branch: beacon/v1.6.4/<feature-slug>` |
| R6 truth | prior aggregation authority UD-027..UD-031 / AC-023..AC-027 |
| planner review `pln-review-20260710t094854z` | branch/worktree governance review before doctor+change |

## User Decisions

| ID | Decision | Value |
|----|----------|-------|
| UD-027 | program/lake aggregation branch authority | Frozen program topology remains valid branch governance input for lake features. |
| UD-028 | shared resolver | QA, implement, release, workspace admit, and soft admission use `resolve_workspace_branch_targets`; no QA-only hard-code. |
| UD-029 | aggregation branch target | For a frozen program lake, target branch is the program aggregation branch. Default remains `beacon/<version>` only when that ref does not conflict with existing child refs. |
| UD-030 | per-feature compatibility | If no program-level contract/topology is present, default remains `beacon/<version>/<feature-slug>`. |
| UD-031 | fail-closed soft admission | `require_workspace_admission=false` still validates current branch against the resolved aggregation branch and blocks wrong branch with `branch_alignment_required`. |
| UD-032 | nested-ref coexistence | When any `refs/heads/beacon/<version>/*` child exists, resolver must not select bare `beacon/<version>` as aggregation branch. Default non-conflicting aggregation branch is `beacon/<version>/_agg` unless governance explicitly overrides `aggregation_branch`. |
| UD-033 | per-feature contract is not program-level | `deterministic-implementation-contract-<feature>.md` alone does not establish program-level resolution. Program-level requires explicit `branch_resolution_mode: program-level`, `git-workflow-*.md`, governance aggregation fields, or frozen program topology that includes the lake. |
| UD-034 | aggregation worktree never primary root | Aggregation `worktree_path` must resolve under governance `worktree_path` / `.beacon/worktrees/<version>` (or an explicit dedicated path). It must not use the primary checkout root as the aggregation worktree target. |
| UD-035 | nested-ref fail-closed reason | If aggregation still cannot be created/switched because of nested refs or invalid worktree target, admission blocks with `aggregation_branch_nested_ref_conflict` (not only opaque `workspace_admission_worktree_failed`). |

## Branch Governance Contract

Normative inputs, in priority order:

1. `docs/beacon/<version>/execution/git-workflow-*.md` with `branch_resolution_mode: program-level`.
2. `docs/beacon/governance/project-version-governance.md` fields such as `branch_resolution_mode: program-level`, `aggregation_branch`, `expected_branch`, `worktree_path`, or per-service canonical branch.
3. Frozen program topology under `docs/beacon/<version>/programs/<program>/` when the requested lake slug appears in `feature-graph.json` or `program-truth-freeze.json`.
4. Per-feature `deterministic-implementation-contract-*.md` may supply branch/worktree hints for that feature only; it does not promote program-level mode unless item 1–3 already established program-level authority or the contract explicitly sets `branch_resolution_mode: program-level`.

Normative output:

| Field | Program/Lake Value |
|-------|--------------------|
| `branch_resolution_mode` | `program-level` only under inputs 1–3 (or explicit program-level contract) |
| `feature_branch` | aggregation branch: `beacon/<version>` when no child refs conflict; otherwise `beacon/<version>/_agg` or governance override |
| `worktree_path` | dedicated aggregation worktree under version worktree root; never primary checkout root |
| `program_slug` | owning program slug from topology/git-workflow; not the per-feature contract filename |
| `material_path` | topology/governance material that established the contract |
| nested-ref block | `reason_code=aggregation_branch_nested_ref_conflict` when parent/child ref lock prevents admission |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-023 | program-topology-without-git-workflow | Program-level governance resolves a lake to the aggregation branch from program/lake topology when `git-workflow-*.md` is absent. |
| AC-024 | program-topology-with-git-workflow | Program-level governance still resolves through explicit `git-workflow-*.md` when present. |
| AC-025 | qa-run-aggregation-admission | `beacon qa run <lake>` accepts the aggregation branch after workspace admission and does not block with `branch_alignment_required`. |
| AC-026 | per-feature-default-preserved | Repos without program-level contract/topology continue to resolve `beacon/<version>/<feature-slug>`. |
| AC-027 | soft-admission-wrong-branch-blocks | Soft admission still blocks wrong current branch with `branch_alignment_required` using the shared resolved target. |
| AC-028 | nested-ref-aggregation-coexistence | When child refs `beacon/<version>/*` exist, resolver selects a non-conflicting aggregation branch (`beacon/<version>/_agg` by default or governance override) instead of bare `beacon/<version>`. |
| AC-029 | per-feature-contract-not-program-level | A per-feature deterministic implementation contract with `target_branch` + `worktree_root` but without explicit program-level authority resolves as `per-feature`, not `program-level`. |
| AC-030 | aggregation-worktree-not-primary-root | Program-level aggregation worktree resolves under `.beacon/worktrees/<version>` (or governance worktree path), never the primary repo checkout path. |
| AC-031 | nested-ref-reason-code | Admission failure caused by nested parent/child refs emits `aggregation_branch_nested_ref_conflict`. |

## Non-Goals

- Do not rewrite SidePilot history.
- Do not force every delivery repo to enable hard workspace admission.
- Do not add a QA-only branch bypass or special-case `sidepilot-pi-host`.
- Do not replace per-feature branch governance for repos without program topology.
- Do not delete existing remote feature branches as part of this requirement; cleanup remains operator/governance optional.

## Downstream Routes

| Stage | Route |
|-------|-------|
| Implement | `beacon-gen-implement` |
| QA | `beacon-eval-qa` |
| Release | `beacon-eval-release` |
