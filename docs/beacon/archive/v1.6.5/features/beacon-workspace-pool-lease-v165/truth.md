---
slug: beacon-workspace-pool-lease-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Workspace pool and durable lease semantics
canonical_refs:
  prd: docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md
  user_story: docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md
  test_case: docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Workspace Pool Lease v1.6.5

## Overview

Beacon currently creates governed worktree lanes through workspace admission, but the lane is treated as dedicated scratch. Repeated implement/QA rounds pay setup cost again, and there is no lease state that makes reuse, release, stale ownership, or corrupt state explicit.

This feature adds pooled worktree semantics while preserving the existing `dedicated-worktree` contract.

## User Intent

Reuse governed worktree lanes through durable leases so Beacon keeps isolation without recreating expensive execution context every time.

## User Intent Snapshot

- user_prompt: "v1.6.5 同版本交付全部 6 个 phase：workspace pool/lease..."
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- research_ref: docs/beacon/archive/v1.6.5/research/beacon-oss-borrow-hardening-v165-research.md
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Same-version delivery | accepted |
| UD-002 | Backward compatibility | keep `dedicated-worktree` behavior unchanged |
| UD-003 | Release semantics | return worktree to pool instead of deleting it |
| UD-004 | Unsafe reuse | stale or corrupt pool state fails closed |

## Problem Statement

1. `beacon workspace admit` has no pool entry, lease holder, lease timestamp, or release state.
2. Reusing a lane cannot be distinguished from accidentally writing in the wrong worktree.
3. There is no public `workspace release` command for returning a lane to reusable state.
4. Corrupt or stale pool state has no conservative recovery behavior.

## Non-Goals

- Do not remove or rename `dedicated-worktree`.
- Do not implement unsafe destroy or prune behavior.
- Do not make pool mode the default for older versions.
- Do not treat runtime pool JSON as requirement truth.

## Affected Surfaces

- `beacon/commands/workspace.py`
- `beacon/utils/workspace_admission.py`
- `beacon/utils/execution_branch_contract.py`
- `tests/test_v165_workspace_pool_lease.py`

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | pooled-contract | `worktree_mode=pooled` is accepted by metadata/admission resolution and resolves to `.beacon/worktrees/<version>/<feature>` unless an explicit worktree path is configured. |
| AC-002 | admit-reuse | `beacon workspace admit` creates a pool entry on first use and reuses the same worktree path after a successful release. |
| AC-003 | lease-schema | Pool entry records `state`, `feature_slug`, `branch`, `worktree_path`, `lease_holder`, `leased_at`, `released_at`, and `git_head`. |
| AC-004 | release-command | `beacon workspace release --version <v> --feature <slug>` changes a leased entry to released/available without deleting the worktree. |
| AC-005 | in-use-block | A second admit for an actively leased entry by a different holder blocks with reason_code `workspace_pool_lease_in_use`. |
| AC-006 | corrupt-state-safe | Unreadable or structurally invalid pool state blocks reuse with reason_code `workspace_pool_state_corrupt` until repaired. |
| AC-007 | dedicated-compat | Existing `dedicated-worktree` admission tests keep their current branch/worktree/artifact behavior. |

## State Model

```text
missing --admit--> leased
leased --release--> released
released --admit--> leased
leased --foreign admit--> blocked:workspace_pool_lease_in_use
corrupt --admit/release--> blocked:workspace_pool_state_corrupt
```

## Deferral Ledger

| ID | Capability | user_decision |
|---|---|---|
| UD-101 | Unsafe destroy/prune operations | accepted: excluded from this phase |

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: implement AC-001..007.
- `beacon-eval-qa`: validate pool lifecycle, corrupt state, and compatibility.
- `beacon-eval-release`: verify pooled mode does not break existing admission gates.
