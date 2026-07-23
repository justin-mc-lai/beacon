---
schema_version: "1.0"
project_root: "/Users/apple/Developer/Personal/products/beacon"
topology_kind: "single_repo"
default_execution_service: "beacon"
transaction_id: "tx-project-governance-e7e4654238d50b68"
committed_at: "2026-07-23T01:43:16.853414+00:00"
source_hash: "e7e4654238d50b68dcf85e0bd335c8d6a1615635cc0f56cfa5da97e8725879fb"
event_type: "freeze-version-contract"
parser_contract: "beacon-project-governance-v1"
---

# Project Version Governance

- project_root: `/Users/apple/Developer/Personal/products/beacon`
- topology_kind: `single_repo`
- default_execution_service: `beacon`

## Service Bindings
- `beacon` repo=`/Users/apple/Developer/Personal/products/beacon` role=`service` writable=`true` worktree_policy=`follow-repo-root`

## Version Contracts

### v1.5.0
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.5.0`
- branch_governance_template: `standard-feature`

### v1.5.1
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `main`
- branch_governance_template: `standard-feature`

### v1.5.2
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.5.2`

### v1.6.0
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.0`
- branch_governance_template: `standard-feature`

### v1.6.1
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `pre-main`
- branch_governance_template: `standard-feature`

### v1.6.10
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `main`
- truth_canonical: `main`
- branch_governance_template: `standard-feature`
- worktree_mode: `branch-only`
- merge_direction_policy: `master->main`
- merge_direction_policy: `main->uat`
- forbidden_directions: `uat->main`
- forbidden_directions: `uat_as_feature_base`

### v1.6.2
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `archived`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.2`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `pre-main`
- next_version_feature_branch: `beacon/v1.6.2/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.2`
- require_workspace_admission: `true`
- admission_invalidation: `dirty_only`

### v1.6.3
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.3`
- truth_canonical: `main`
- runtime_mirror: `beacon/v1.6.3`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `pre-main`
- next_version_feature_branch: `beacon/v1.6.3/<feature-slug>`

### v1.6.4
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.4`
- truth_canonical: `main`
- runtime_mirror: `beacon/v1.6.4`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v1.6.4/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.4`
- require_workspace_admission: `true`
- admission_invalidation: `dirty_only`

### v1.6.5
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.5`
- truth_canonical: `main`
- runtime_mirror: `beacon/v1.6.5`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v1.6.5/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.5`
- require_workspace_admission: `true`
- admission_invalidation: `dirty_only`

### v1.6.6
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.6`
- truth_canonical: `main`
- runtime_mirror: `beacon/v1.6.6`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v1.6.6/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.6`
- require_workspace_admission: `true`
- admission_invalidation: `dirty_only`

### v1.6.7
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.7`
- truth_canonical: `main`
- runtime_mirror: `beacon/v1.6.7`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v1.6.7/<feature-slug>`
- worktree_mode: `branch-only`
- worktree_path: `.beacon/worktrees/v1.6.7`
- require_workspace_admission: `false`
- admission_invalidation: `dirty_only`

### v1.6.9
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `main`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v1.6.9/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.9`

### v2.0.0
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `main`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `main`
- next_version_feature_branch: `beacon/v2.0.0/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v2.0.0`
