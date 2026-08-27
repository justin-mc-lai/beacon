# Beacon Implementation Tasks Ledger

- feature: `beacon-v1615-automerge-gate`
- version: `v1.6.15`
- plan_id: `plan-beacon-v1615-automerge-gate-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: merge 回 main 前 gate 检查三条件（类型覆盖达标 + 失败模式回归命中 0 + 对抗式审查通过）；任一不达标 → cove... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.15/.machine/execution/implementation-plan-beacon-v1615-automerge-gate.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.15/.machine/execution/implementation-plan-beacon-v1615-automerge-gate.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: merge 回 main 前 gate 检查三条件（类型覆盖达标 + 失败模式回归命中 0 + 对抗式审查通过）；任一不达标 → cove... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-001.json`
  - tests=TEST-001,TC-001,TC-ILLEGAL | next
[ ] `ITASK-002` TASK-002 Implement AC-002: 失败模式回归库（v1.6.13 D3 已建）作为合并前置输入：在 regression_checked 阶段命中 > 0 → 合并被拦。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-002.json`
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: 对抗式审查（global-boundaries §5）作为合并前置：在 adversarial_checked 阶段缺翻车点清单/验证证据... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-003.json`
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: release 人类 gate 保持不变：auto-merge 不自动打 tag/部署/发布（merged 后仍须人类确认）；`manua... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-004.json`
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/QA-MATRIX.json`
  - depends_on=ITASK-005
