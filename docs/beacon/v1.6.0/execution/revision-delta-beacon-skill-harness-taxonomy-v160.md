# Beacon Revision Delta

- feature: `beacon-skill-harness-taxonomy-v160`
- version: `v1.6.0`
- revision_id: `R5`
- source_revision_id: `R4`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `1`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-017` 每个 v1.6.0 host-visible skill 必须在共享 preamble 后注入 harness-specific `HARD GATE`，显式禁止跨 harness skill 调用、越权写 truth、越权 implementation、越权 QA/release verdict 和假交付闭环，并声明唯一允许产物；agent-surface verify 必须扫描并阻断缺失或不匹配的 gate。
