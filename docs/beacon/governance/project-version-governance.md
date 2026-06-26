---
schema_version: "1.0"
project_root: "/Users/apple/Developer/Personal/products/beacon"
topology_kind: "single_repo"
default_execution_service: "beacon"
transaction_id: "tx-project-governance-b84ea5e95ac2ecbe"
committed_at: "2026-06-26T03:36:40.503433+00:00"
source_hash: "b84ea5e95ac2ecbec7c291dadbd977e8f5ead201267b4c5cb0a3a38b4031bad7"
event_type: "archive-version"
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
- branch_governance_template: `standard-feature`
- previous_version_baseline_branch: `pre-main`
- next_version_feature_branch: `beacon/v1.6.3/<feature-slug>`
