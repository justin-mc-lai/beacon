# Beacon Git Workflow Contract

- feature: `beacon-v1613-d2-spend-ledger`
- version: `v1.6.13`
- mode: `single-repo`
- expected_branch: `beacon/v1.6.13`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `True`
- require_clean_worktree_for_switch: `True`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon`
- source: `version_governance`

## Service Directories
- `/Users/apple/Developer/Personal/products/beacon`

## Direct Delivery Services
- `beacon`

## Implementation Preflight
- Before implementation, verify the target service belongs to: ..
- Before implementation, verify every direct delivery service is on beacon/v1.6.13.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.

## Branch Governance

- toolkit: `beacon-toolkit-branch-governance`
- template_name: `standard-feature`
- template_source: `project_metadata`
- service_key: `beacon`
- repo_root: `/Users/apple/Developer/Personal/products/beacon`
- base_branch: `main`
- current_branch: `main`
- target_branch: `beacon/v1.6.13`
- worktree_mode: `dedicated-worktree`
- worktree_path: `/Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.13/beacon-v1613-d2-spend-ledger`
- evidence_contract_status: `pass`
- blocked_reason: `governance requires a dedicated worktree lane before implementation`
- recommended_action: `enter the governed worktree at /Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.13/beacon-v1613-d2-spend-ledger`

### Flow Diagram
```text
main [current]
    -> beacon/v1.6.13
    -> uat
```

### Allowed Paths
- `master->beacon/v1.6.13`
- `beacon/v1.6.13->uat`

### Forbidden Paths
- `uat->beacon/v1.6.13`
- `uat_as_feature_base`

### Evidence Contract
- none
