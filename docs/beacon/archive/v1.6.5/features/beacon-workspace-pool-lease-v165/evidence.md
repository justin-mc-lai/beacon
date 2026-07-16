---
slug: beacon-workspace-pool-lease-v165
version: v1.6.5
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md
parser_contract: beacon-feature-package-v2
---

# Evidence Index: Workspace Pool Lease v1.6.5

## Authority Surface

| surface | authority | artifact |
|---|---|---|
| truth.md | requirement_truth | docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/truth.md |
| tests.md | test_truth | docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/tests.md |
| tasks.md | requirement_truth | docs/beacon/archive/v1.6.5/features/beacon-workspace-pool-lease-v165/tasks.md |

## Source Refs

- Program graph: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- Planner review: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/planner-review.md
- Research: docs/beacon/archive/v1.6.5/research/beacon-oss-borrow-hardening-v165-research.md

## Baseline

- Current command surface has `workspace admit` and `workspace validate`.
- Current admission invalidation is dirty-only.
- Current worktree mode compatibility must remain intact.

## Implementation Evidence

| Surface | Authority | Canonical Artifact | Status | Route |
|---|---|---|---|---|
| implementation | implementation_evidence | `beacon/utils/workspace_admission.py` | implemented | beacon-gen-implement |
| implementation | implementation_evidence | `beacon/commands/workspace.py` | implemented | beacon-gen-implement |
| tests | test_evidence | `tests/test_v165_workspace_pool_lease.py` | passing | beacon-eval-qa |
| regression | test_evidence | `tests/test_v162_workspace_admit.py`, `tests/test_v162_workspace_integration.py`, `tests/test_workspace_config_resolution.py` | passing | beacon-eval-qa |

Focused command: `python3 -m pytest tests/test_v162_workspace_admit.py tests/test_v162_workspace_integration.py tests/test_workspace_config_resolution.py tests/test_v165_workspace_pool_lease.py -q`
