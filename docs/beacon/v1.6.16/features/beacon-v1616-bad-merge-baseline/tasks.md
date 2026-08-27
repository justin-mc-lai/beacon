---
slug: beacon-v1616-bad-merge-baseline
version: v1.6.16
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1616-bad-merge-baseline

## Task Ledger

- [ ] TASK-001 Implement AC-001: collected 阶段：统计 v1.6.15 以来合并到 main 的提交数及 revert 数（git 分析）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-001.json`
- [ ] TASK-002 Implement AC-002: computed 阶段：计算 bad-merge 率（revert 数 / 合并数，按时间窗）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-002.json`
- [ ] TASK-003 Implement AC-003: reported 阶段：产出可对比基线报告（合并数/revert 数/比率/时间窗/置信度）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-003.json`
- [ ] TASK-004 Implement AC-004: warned 判定：统计不改变自动合入行为，数据不足标低置信度；数据不足时标低置信度不硬算。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-bad-merge-baseline/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
