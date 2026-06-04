# Test Cases: Beacon v1.3.8 PRD Executable Diagram Truth Layer

**Feature**: `beacon-v1.3.8-prd-executable-diagram-truth-layer`  
**Version**: `v1.3.8`  
**Status**: `frozen`  
**Date**: `2026-04-24`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 复杂业务 feature 进入 PRD 阶段 | product | PRD 能正式承载 `branch-flow`、`state-machine`、`decision-priority`。 |
| TC-002 | AC-002 | 复杂业务 feature 需要表达多条状态轴 | product | user-story / PRD 能明确表达 state axis，而不是压缩成单字段语义。 |
| TC-003 | AC-003 | freeze readiness 检查一个 diagram 缺失的复杂 feature | integration | 系统给出明确 diagram truth layer 缺失提示或阻断。 |
| TC-004 | AC-004 | implementation plan 编译一个已具备 diagram truth layer 的 feature | integration | plan 吸收关键分支、状态节点、状态转移，生成 task / review gate。 |
| TC-005 | AC-005 | test-case / QA 生成一个具备 diagram truth layer 的 feature | integration | QA 覆盖骨架能追溯 diagram 的 branch / transition。 |

## Execution Notes

- version: `v1.3.8`
- admission correctness 与 downstream propagation 都必须验证。
