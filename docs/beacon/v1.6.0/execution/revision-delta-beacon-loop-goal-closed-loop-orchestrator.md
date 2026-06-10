# Beacon Revision Delta

- feature: `beacon-loop-goal-closed-loop-orchestrator`
- version: `v1.6.0`
- revision_id: `R3`
- source_revision_id: `R2`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `11`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `AC-024` **TC-049**
- `AC-025` **TC-051**
- `AC-026` **TC-052**
- `AC-028` **TC-053**
- `AC-027` **TC-054**
- `AC-029` **Parent failure backoff（继承 parent）**：`implement_loop` 复用 parent orchestrator AC-019：agent-reported failure 立即下一轮；retryable hard error 指数退避；连续失败达上限 abort；no-op iteration 计为 failure。
- `AC-010` **AC-044** implement_loop worker
- `AC-008` **AC-045** output-schema + strict parse
- `AC-011` **AC-048** stage worker routing
- `AC-007` **AC-043** agent surface / using-beacon
- `AC-009` **AC-046** runner prompt template
