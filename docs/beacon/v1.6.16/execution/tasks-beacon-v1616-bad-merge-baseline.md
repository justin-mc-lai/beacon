# Beacon Implementation Tasks Ledger

- feature: `beacon-v1616-bad-merge-baseline`
- version: `v1.6.16`
- plan_id: `plan-beacon-v1616-bad-merge-baseline-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: collected 阶段：统计 v1.6.15 以来合并到 main 的提交数及 revert 数（git 分析）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-bad-merge-baseline.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.16/.machine/execution/implementation-plan-beacon-v1616-bad-merge-baseline.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: collected 阶段：统计 v1.6.15 以来合并到 main 的提交数及 revert 数（git 分析）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-001.json`
  - tests=TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: computed 阶段：计算 bad-merge 率（revert 数 / 合并数，按时间窗）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-002.json`
  - tests=TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: reported 阶段：产出可对比基线报告（合并数/revert 数/比率/时间窗/置信度）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-003.json`
  - tests=TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: warned 判定：统计不改变自动合入行为，数据不足标低置信度；数据不足时标低置信度不硬算。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-004.json`
  - tests=TC-004,TC-ILLEGAL | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/QA-MATRIX.json`
  - depends_on=ITASK-005
