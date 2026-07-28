# Beacon Revision Delta

- feature: `design-craft-absorption-v1611`
- version: `v1.6.11`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `8`

## Removed Requirement Surfaces
- `AC-001` Acceptance criteria TBD

## Added Requirement Surfaces
- `AC-003` craft 输出必须标记 `support_only=true` 且 `truth_source=false`；缺省或伪造权限字段时路由/校验失败。
- `AC-006` craft finding 若改变产品承诺/AC/状态，只能推荐 `prototype_adapt` 或 `change_refreeze`，不能直接升格 truth。
- `AC-002` 四个 module（baseline/a11y/motion/improve）均有 Beacon-owned progressive reference，并可被 design craft router 选中。
- `AC-008` SEO/metadata 与 ui-skills 其余 registry skill **明确 defer**，本包不实现、不假装覆盖。
- `AC-005` improve finding 必须同时具备 contract/runtime/correction 三门证明，否则不得进入 plan。
- `AC-001` Beacon 仅通过 `beacon-design` public harness 暴露 craft；不新增 1+6 public skill，不新增主生命周期 stage。
- `AC-007` router 默认选择 ≤2 个 module；无 utterance/feature 上下文时不得静默全开 4 个 craft。
- `AC-004` improve 在产品源上只读；计划只写入受控 craft plan 根目录；试图改产品源必须被拒绝。
