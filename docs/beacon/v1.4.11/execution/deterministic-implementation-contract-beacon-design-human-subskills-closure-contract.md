# Deterministic Implementation Contract

- feature: `beacon-design-human-subskills-closure-contract`
- version: `v1.4.11`
- revision_id: `R3`
- review_status: `accepted`
- approved_by: `codex-implement-beacon-design-human-subskills-closure`
- reviewed_at: `2026-05-29T04:00:00Z`

## Git
- base_branch: `main`
- target_branch: `beacon/v1.4.11`
- branch_prefix: `beacon/`
- branch_strategy: ``

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
- `R3 scope: add simplify route to beacon/utils/design_contract.py DESIGN_ROUTES dict.`
- `R3 scope: create skills/beacon/beacon-design-simplify/SKILL.md.`
- `R3 scope: update skills/beacon/beacon-design/SKILL.md to mention simplify route.`
- `R3 scope: update tests to cover simplify route.`
- `No new CLI route, prototype adapter change, or release verdict change.`
- `Simplify route has no upstream dependency (Beacon-native).`
