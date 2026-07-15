# Beacon Revision Delta

- feature: `beacon-loop-goal-v166`
- version: `v1.6.6`
- revision_id: `R4`
- source_revision_id: `R3`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `7`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-018` loop-goal 进入 implement 前必须验证 feature branch 包含 `truth_baseline_commit`；未合入时 fail-closed
- `AC-016` canonical truth/refreeze 只有在 main/master 提交后才可成为 loop-goal baseline；未提交 refreeze artifact 不得进入 implement
- `AC-021` standard execution flow 重复执行已完成步骤时必须返回 pass/up_to_date，不得再次 bump requirement revision 或产生 reason-only refreeze
- `AC-017` feature/dev worktree 中发现本地 `.machine` revision/projection dirty 或 feature-local refreeze 时，必须 scoped stash/archive 并记录 quarantine ref；不得采信为 requirement authority
- `AC-015` public SKILL.md 的 State Machine、Decision Tree、Skill Routing Matrix 必须显式包含 `standard_execution_precheck`，位于 `review_verify` 和 `implement_routing` 之间
- `AC-019` standard execution precheck 必须产出 verification bundle，至少包含 truth-map verify、verify-materials strict、git diff check、branch-governance verify、workspace admission 五类结果
- `AC-020` `implement check-branch` / workspace admission 必须 pass，并把 artifact ref 写入 loop-goal state outputs；缺失或 blocked 不得进入 implement
