# Deterministic Implementation Contract

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- revision_id: `R2`
- review_status: `approved`
- approved_by: `beacon-gen-implement`
- reviewed_at: `2026-06-10T08:35:00Z`

## Git
- base_branch: `main`
- target_branch: `beacon/v1.6.0`
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
- `Delivery orchestrator extends packages/beacon-loop only; parent runner remains frozen.`
- `Loop must not write package truth or formal QA/release verdicts.`
