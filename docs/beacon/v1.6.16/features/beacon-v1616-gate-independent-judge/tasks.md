---
slug: beacon-v1616-gate-independent-judge
version: v1.6.16
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1616-gate-independent-judge

## Task Ledger

- [ ] TASK-001 Implement AC-001: computed 阶段：coverage_rate 等关键 gate 值可由独立脚本重算（独立于系统判定逻辑）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-001.json`
- [ ] TASK-002 Implement AC-002: compared 阶段：独立判定与系统判定比对：一致 → 标记可信；不一致 → 暴露偏差。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-002.json`
- [ ] TASK-003 Implement AC-003: flagged 阶段：偏差记录可审计（gate/系统值/独立值/diff）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-003.json`
- [ ] TASK-004 Implement AC-004: verified 判定：独立裁判不改变 gate 业务规则，不判 pass/fail，只核验系统值可信度。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-gate-independent-judge/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
