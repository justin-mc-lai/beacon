# Beacon Revision Delta

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- revision_id: `R11`
- source_revision_id: `R10`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `8`

## Removed Requirement Surfaces
- `AC-020` 六能力 surface + legacy removal + progressive disclosure + BranchContext + TraceSpine + canonical truth branch

## Added Requirement Surfaces
- `AC-020` 六能力 surface + legacy removal + progressive disclosure + BranchContext + TraceSpine + canonical truth branch + standard execution flow
- `AC-133` **：canonical refreeze 只有在 canonical branch 提交后才成为可消费 baseline；未提交 refreeze artifact 不得被 feature branch、loop、implement、qa-evidence 或 release 采信。
- `AC-134` **：feature worktree 中发现 stale feature-local refreeze/projection dirty 时，必须 scoped stash/archive 并记录引用；不得作为 requirement authority commit/merge。
- `AC-135` **：feature/dev branch 进入 implement 前必须包含 canonical `truth_baseline_commit`，且不得有违反 dirty policy 的工作区状态；否则 blocked。
- `AC-138` **：标准执行流通过六 public skill 的 progressive examples 暴露，不得新增第七个 public skill 或绕过 Harness Boundary。
- `AC-136` **：标准流 admission evidence bundle 必须包含 truth-map verify、verify-materials strict、git diff check、branch-governance verify、workspace admission 五类结果；缺任一项不得进入 implement。
- `AC-137` **：标准流必须可 idempotent resume；已对齐步骤重复执行时返回 `up_to_date` / `pass`，不得因重复执行产生新的 requirement revision。
- `AC-031` R8 refreeze：将 canonical truth author/refreeze/commit -> feature worktree reconcile -> governance verify -> workspace admission -> implement resume 固化为 Standard Execution Flow；新增 baseline commit、stale feature-local refreeze quarantine、verification bundle 与 idempotent resume contract（AC-138–144）
