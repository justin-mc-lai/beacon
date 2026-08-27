---
slug: beacon-v1613-d2-spend-ledger
version: v1.6.13
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1613-d2-spend-ledger

## Task Ledger

- [x] TASK-001 Implement AC-001: goal run 状态含持久化 `spend_ledger`（已花回合数、每笔 SpendEntry 的 index/source/spe... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-001.json`
- [x] TASK-002 Implement AC-002: spend 仅在 validated writeback 之后发生一次（保留 `spend_guard`：writeback 未验证 → ... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-002.json`
- [x] TASK-003 Implement AC-003: quiet skip / dry-run / preflight 不 spend（`spend_ledger` 计数不变）。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-003.json`
- [x] TASK-004 Implement AC-004: spend 幂等：同一 index 重放不重复扣（CAS on index digest，conflict 即拒绝）。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-004.json`
- [x] TASK-005 Implement AC-005: 配额（`max_drive_turns`/quota_limit）耗尽 → 状态 `halt_budget` + reason_code ... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-005.json`
^- [x] TASK-006 Implement AC-006: 交接文本预算（handoff budget：16 行 / 1800 字符）保留且仍生效（回归）。 · ac=AC-006 · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/AC-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1613-d2-spend-ledger/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
