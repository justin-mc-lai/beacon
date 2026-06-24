# Beacon Git Workflow Contract

- feature: `beacon-global-workspace-git-admission-v162`
- version: `v1.6.2`
- mode: `single-repo`
- expected_branch: `beacon/v1.6.2`
- branch_prefix: `beacon/`
- base_branch: `beacon/v1.6.2`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon/.beacon/worktrees/v1.6.2/beacon-global-workspace-git-admission-v162`
- source: `technical_review_contract`

## Service Directories
- `.`

## Direct Delivery Services
- `.`

## Implementation Preflight
- Before implementation, verify the target service belongs to: .
- Before implementation, verify the current branch is beacon/v1.6.2.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.
