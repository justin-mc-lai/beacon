---
schema_version: "1.0"
project_root: "/Users/apple/Developer/Personal/products/beacon"
topology_kind: "single_repo"
default_execution_service: "beacon"
transaction_id: "tx-project-governance-4e79744af696ead5"
committed_at: "2026-06-23T06:45:02.656000+00:00"
source_hash: "4e79744af696ead54d5d51cdfe1259f926040bfcd1d5bda5cfc8bf558d08d5f7"
event_type: "worktree-resync"
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

### v1.6.2
- participating_services: `beacon`
- branch_guard_mode: `strict`
- validation_state: `active`
- per_service_canonical_branch:
  - `beacon`: `beacon/v1.6.2`
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `pre-main`
- next_version_feature_branch: `beacon/v1.6.2/<feature-slug>`
- worktree_mode: `dedicated`
- worktree_path: `.beacon/worktrees/v1.6.2`
- require_workspace_admission: `true`
- admission_invalidation: `dirty_only`
