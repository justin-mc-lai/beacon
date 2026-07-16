# Beacon Revision Delta

- feature: `beacon-harness-program-plan-v161`
- version: `v1.6.1`
- revision_id: `R4`
- source_revision_id: `R3`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `1`
- added_requirement_count: `0`

## Removed Requirement Surfaces
- `AC-001` 对接 `beacon-loop-goal-closed-loop-orchestrator-v161` R1（AC-072..075；upstream v1.6.0 R10）：`--mode program` 嵌套 per-lake delivery 不得破坏 AC-068 `truth_freeze_gate`；eval supplement opt-in 不得 gate qa/release。

## Added Requirement Surfaces
- none
