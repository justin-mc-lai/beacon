# Beacon Git Workflow Contract

- feature: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- version: `v1.3.6`
- mode: `single-repo`
- expected_branch: `beacon/v1.3.6`
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
- Before implementation, verify the current branch is beacon/v1.3.6.
- If a branch switch is needed and the worktree is dirty, stop and clean or stash first.
