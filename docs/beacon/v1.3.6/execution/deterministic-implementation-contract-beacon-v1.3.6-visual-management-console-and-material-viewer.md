# Deterministic Implementation Contract

- feature: `beacon-v1.3.6-visual-management-console-and-material-viewer`
- version: `v1.3.6`
- revision_id: `R1`
- review_status: `approved`
- approved_by: `codex`
- reviewed_at: `2026-04-21T14:47:22.020372+00:00`

## Git
- base_branch: `main`
- target_branch: `beacon/v1.3.6`
- branch_prefix: `beacon/`
- branch_strategy: `single-branch`

## Worktree
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

## Environment Isolation
- environment_mode: `local-dev`
- isolation_strategy: `repo-local implementation with fixture-backed UI read model`

## Service Directories
- `.`
- `beacon-console-ui`
- `beacon/commands`
- `docs/beacon/v1.3.6`
- `.beacon`

## Writable Services
- `beacon-console-ui`
- `beacon/commands`
- `docs/beacon/v1.3.6`
- `.beacon`

## Direct Delivery Services
- `beacon-console-ui`
- `docs/beacon/v1.3.6`
- `.beacon`

## Reference-only Services
- `docs/beacon/v1.3.5`
- `docs/beacon/global-boundaries.md`

## Protected Resources
- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/`

## Shared Schema Or Contracts
- `docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md`
- `docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- `docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md`

## Cross-service Change Order
- `Repair implement public command routing and branch truth before evidence generation.`
- `Bring beacon-console-ui to clean npm run build with all seven pages present.`
- `Update versioned docs, implementation evidence, and QA inputs in docs/beacon/v1.3.6 and .beacon.`
- `Rerun implement and QA surfaces only after revision freeze and contract materialization.`

## Boundary Principles
- `explicit_assumptions`: 显式假设与歧义管理
- `simplicity_first`: 简单优先
- `surgical_changes`: 外科手术式改动
- `goal_driven_execution`: 目标驱动验证闭环
- `trivial_task_exception`: trivial task 可以轻量处理，但不能越界

## Notes
- `This contract exists to unblock implement plan/status for the visual console feature.`
- `The UI uses realistic local fixtures until PocketBase and SQLite projection are formally wired into the same truth line.`
- `Host session visibility is limited to metadata references and linked run pointers.`
