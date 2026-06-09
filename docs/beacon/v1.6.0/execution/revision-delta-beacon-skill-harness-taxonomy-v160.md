# Beacon Revision Delta

- feature: `beacon-skill-harness-taxonomy-v160`
- version: `v1.6.0`
- revision_id: `R8`
- source_revision_id: `R7`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `3`
- added_requirement_count: `3`

## Removed Requirement Surfaces
- `AC-003` 每个 v1.6.0 host-visible skill 都使用 `beacon-<harness-code>-<function>`，其中 harness code 只能是 `pln/gen/eval/gov`。
- `AC-015` Research artifact 不能自动成为需求真相；只有 `user_decision=accepted/promoted` 且存在 `promotion_ref` 时，才能通过 `beacon-gen-change` 或 `beacon-gen-refreeze` 进入 package truth 并冻结。
- `AC-016` v1.6.0 skill 改名必须生成新 `beacon-<harness-code>-<function>` host-visible skill，更新 frontmatter/name/description/preamble/boundary，移除旧 host-visible aliases，并把旧名限制在 migration/archive/release notes。

## Added Requirement Surfaces
- `AC-003` 每个 v1.6.0 host-visible skill 都使用 `beacon-<harness-code>-<function-code>`，其中 harness code 只能是 `pln/gen/eval/gov`，并分别映射到 `planner/generator/evaluator/governor`。
- `AC-015` Research artifact 不能自动成为需求真相；只有 `user_decision=accepted/promoted` 且存在 `promotion_ref` 时，才能通过 `beacon-gen-change` 或 `beacon-gen-refreeze` 进入 package truth 并冻结。
- `AC-016` v1.6.0 skill 改名必须生成新 `beacon-<harness-code>-<function-code>` compact host-visible skill，更新 frontmatter/name/description/preamble/boundary，移除旧 host-visible aliases 和第一版完整 harness 长名 aliases，并把旧名限制在 migration/archive/release notes。
