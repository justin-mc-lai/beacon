# Beacon Revision Delta

- feature: `beacon-global-workspace-git-admission-v162`
- version: `v1.6.2`
- revision_id: `R4`
- source_revision_id: `R3`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `3`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-017` GIT_ADMISSION preamble 含「implement 前 merge main」步骤（**Must**，文档层）
- `AC-018` implement/qa/release/change 保持 Tier A worktree（**Must**）
- `AC-016` `beacon-gen-truth` 不在 Tier A（降级 C），truth 在 main 编写不进 worktree（**Must**）
