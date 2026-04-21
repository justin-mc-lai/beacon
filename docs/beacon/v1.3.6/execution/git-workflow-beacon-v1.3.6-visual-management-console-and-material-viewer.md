# Beacon Git Workflow Contract

- feature: `beacon-v1.3.6-visual-management-console-and-material-viewer`
- version: `v1.3.6`
- mode: `workspace`
- expected_branch: `beacon/v1.3.6`
- branch_prefix: `beacon/`
- base_branch: `main`
- use_git_worktree: `False`
- require_clean_worktree_for_switch: `True`
- worktree_root: `.`
- source: `technical_review_contract`

## Service Directories
- `.`
- `beacon-console-ui`
- `beacon/commands`
- `docs/beacon/v1.3.6`
- `.beacon`

## Direct Delivery Services
- `beacon-console-ui`
- `docs/beacon/v1.3.6`
- `.beacon`

## Implementation Preflight
- Before implementation, verify the target service belongs to: beacon-console-ui, docs/beacon/v1.3.6, .beacon
- Before implementation, verify the current branch is beacon/v1.3.6.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.
