---
schema_version: "1.0"
project_root: "/Users/apple/Developer/Personal/products/beacon"
topology_kind: "single_repo"
default_execution_service: "beacon"
transaction_id: "tx-project-governance-ca056180d70b2e88"
committed_at: "2026-06-15T06:03:54.557989+00:00"
source_hash: "ca056180d70b2e88ffaba3a9b3803989e502e5fe50df46c8b7e1a66f4de9267a"
event_type: "update"
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
