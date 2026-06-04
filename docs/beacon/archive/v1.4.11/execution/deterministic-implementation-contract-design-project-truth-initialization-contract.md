# Deterministic Implementation Contract

- feature: `design-project-truth-initialization-contract`
- version: `v1.4.11`
- revision_id: `R4`
- review_status: `accepted`
- approved_by: `codex-implement-design-project-truth-initialization`
- reviewed_at: `2026-05-27T06:46:30Z`

## Git
- base_branch: `main`
- target_branch: `main`
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
- `Implementation is scoped to explicit PRODUCT.md and DESIGN.md initialization.`
- `No release gate behavior or lifecycle stage change is allowed.`
