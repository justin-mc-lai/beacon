---
slug: beacon-v1617-layering-audit
version: v1.6.17
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1617-layering-audit

## Task Ledger

- [x] TASK-001 Implement AC-001: scanned 阶段：生成 beacon/utils + commands 的 import 依赖图（模块 × 依赖列表）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-001.json`
- [x] TASK-002 Implement AC-002: sized 阶段：列出所有 >2000 行的 God Module（含行数）（含行数）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-002.json`
- [x] TASK-003 Implement AC-003: classified 阶段：识别越界引用（command 层 → 不应依赖的 utils）（command 层 → 不应依赖的 utils... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-003.json`
- [x] TASK-004 Implement AC-004: reported 阶段：产出可维护性风险判断（分层缺失/God Module 风险等级）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1617-layering-audit/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
