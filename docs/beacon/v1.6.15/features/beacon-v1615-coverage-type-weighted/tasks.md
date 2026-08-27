---
slug: beacon-v1615-coverage-type-weighted
version: v1.6.15
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1615-coverage-type-weighted

## Task Ledger

- [ ] TASK-001 Implement AC-001: `coverage_rate` 按类型族加权：required_families 缺一类 → 状态 assessed 时 rate < 1... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-001.json`
- [ ] TASK-002 Implement AC-002: 非浏览器（contract/docs/unit）场景在 weighted 阶段展开类型 family（默认 happy+negative+... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-002.json`
- [ ] TASK-003 Implement AC-003: coverage 输出在 reported 阶段列出 missing_families（缺哪类），供 QA 与自动合入门禁审计。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-003.json`
- [ ] TASK-004 Implement AC-004: 兼容既有 lake：已通过 QA 的 lake 语义不变，仅覆盖计算方式变化（gated 判定更新），不引入新命令面。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-coverage-type-weighted/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
