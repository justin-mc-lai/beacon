# Beacon Git Workflow Contract

- feature: `Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope`
- version: `v1.3.7`
- mode: `single-repo`
- expected_branch: `beacon/v1.3.7`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- worktree_root: `.`
- source: `technical_review_contract`

## Service Directories
- `.`

## Direct Delivery Services
- `.`

## Implementation Preflight
- Before implementation, verify the target service belongs to: .
- Before implementation, verify the current branch is beacon/v1.3.7.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.
