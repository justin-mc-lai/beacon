# Beacon Revision Delta

- feature: `beacon-loop-goal-v166`
- version: `v1.6.6`
- revision_id: `R5`
- source_revision_id: `R4`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `5`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-025` 必须提供 CLI 命令自跑 standard execution verification bundle（至少五类检查）并写 artifact；`record_standard_execution_precheck` 只接受带 CLI artifact ref 的结果，拒绝无 ref 的 agent 自报 pass（**Must**）
- `AC-024` `beacon-gen-truth` / `beacon-gen-change` / `beacon-gen-refreeze` 物化 skill 必须含 truth_canonical GIT_ADMISSION；`beacon-gen-implement` / qa / release / gov-branch 必须保留 worktree `workspace admit` preamble（**Must**）
- `AC-022` `beacon freeze` / `beacon reopen` / `beacon change --refreeze-chain` 在非 governance `truth_canonical` 分支必须 blocked，`reason_code=truth_canonical_branch_mismatch`（**Must**）
- `AC-023` 写 feature package requirement Markdown（`features/<slug>/{truth,tests,tasks,evidence}.md`）时：不在 `truth_canonical` → blocked；在 `truth_canonical` → **允许**，且不得因 `require_workspace_admission` 强制要求 feature worktree cwd（**Must**）
- `AC-026` public `beacon-loop-goal` SKILL.md Step 2 必须在进入 `beacon-gen-truth` 前校验当前分支为 `truth_canonical`，否则 route `beacon-gov-debug` + `truth_canonical_branch_mismatch`（**Must**）
