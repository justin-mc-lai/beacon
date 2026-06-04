# Deterministic Implementation Contract

- feature: `read-only-support-research-write-topology-gate-contract`
- version: `v1.4.9`
- revision_id: `R3`
- review_status: `approved`
- approved_by: `codex`
- reviewed_at: `2026-05-23T06:56:14Z`

## Git
- base_branch: `main`
- target_branch: `beacon/v1.4.9`
- branch_prefix: `beacon/`
- branch_strategy: `single-branch`

## Worktree
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

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
- `Approved for scoped implementation of v1.4.9 read-only support research write topology gate.`
- `Writable scope is repo-local Beacon runtime, docs, and focused tests for this feature.`
