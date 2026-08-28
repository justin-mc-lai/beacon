# Deterministic Implementation Contract

- feature: `beacon-v1617-live-benchmark-verify`
- version: `v1.6.17`
- revision_id: `R1`
- review_status: `approved`
- approved_by: `operator`
- reviewed_at: `2026-08-28T11:15:00+00:00`

## Git
- base_branch: `main`
- target_branch: `beacon/v1.6.17/beacon-v1617-live-benchmark-verify`
- branch_prefix: `beacon/`
- branch_strategy: `single-branch`

## Worktree
- use_git_worktree: `False`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon`
- workspace_root: `/Users/apple/Developer/Personal/products/beacon`

## Environment Isolation
- environment_mode: `local-dev`
- isolation_strategy: `repo-local isolation`

## Service Directories
- `.`

## Writable Services
- `.`

## Direct Delivery Services
- `.`

## Reference-only Services
- `docs`

## Boundary Principles
- `explicit_assumptions`: 显式假设与歧义管理
- `simplicity_first`: 简单优先
- `surgical_changes`: 外科手术式改动
- `goal_driven_execution`: 目标驱动验证闭环
- `trivial_task_exception`: trivial task 可以轻量处理，但不能越界

## Notes
- `This draft contract must be reviewed and approved before formal implementation.`
- `Fill approved_by/reviewed_at and update review_status to approved or accepted.`
