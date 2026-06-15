# Beacon Git Workflow Contract

- feature: `beacon-truth-integrity-gates-v160`
- version: `v1.6.0`
- mode: `single-repo`
- expected_branch: `beacon/v1.6.0`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- worktree_root: `.`
- source: `version_default`

## Service Directories
- `.`

## Direct Delivery Services
- `.`

## Implementation Preflight
- Before implementation, verify the target service belongs to: ..
- Before implementation, verify every direct delivery service is on beacon/v1.6.0.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.

## Branch Governance

- toolkit: `beacon-toolkit-branch-governance`
- template_name: `standard-feature`
- template_source: `project_metadata`
- service_key: `beacon`
- repo_root: `/Users/apple/Developer/Personal/products/beacon`
- base_branch: `main`
- current_branch: `beacon/v1.6.0`
- target_branch: `beacon/v1.6.0`
- worktree_mode: `branch-only`
- worktree_path: `/Users/apple/Developer/Personal/products/beacon`
- evidence_contract_status: `pass`
- blocked_reason: ``
- recommended_action: ``

### Flow Diagram
```text
main
    -> beacon/v1.6.0 [current]
    -> uat
```

### Allowed Paths
- `base_branch->feature_branch`

### Forbidden Paths
- none

### Evidence Contract
- none
