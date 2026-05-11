# Beacon Git Workflow Contract

- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- version: `v1.4.2`
- mode: `single-repo`
- expected_branch: `beacon/v1.4.2`
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
- Before implementation, verify the current branch is beacon/v1.4.2.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.
