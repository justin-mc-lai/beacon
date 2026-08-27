---
slug: beacon-v1616-eval-external-anchor
version: v1.6.16
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1616-eval-external-anchor

## Task Ledger

- [ ] TASK-001 Implement AC-001: collected 阶段：benchmark 案例集引入外部来源案例（真实失败案例/社区标准），不再全内置。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-001.json`
- [ ] TASK-002 Implement AC-002: verified 阶段：每个外部案例带 source_ref，伪称来源被拒（可追溯来源），伪称外部来源的案例被拒。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-002.json`
- [ ] TASK-003 Implement AC-003: executed 阶段：外部案例可被 benchmark 执行（prompt + expected_route 完整）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-003.json`
- [ ] TASK-004 Implement AC-004: registered 兼容：系统内置案例保留（回归兼容），外部案例为增量。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-eval-external-anchor/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
