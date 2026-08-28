---
slug: beacon-v1617-live-benchmark-verify
version: v1.6.17
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1617-live-benchmark-verify

## Task Ledger

- [x] TASK-001 Implement AC-001: materialized 阶段：34 个 live skill 的 prompt fixture 文件真实存在（非空、含 ROUTE: 行）。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-001.json`
- [x] TASK-002 Implement AC-002: resolved 阶段：skill surface 解析修正（mode 子能力映射到主 SKILL.md）：mode 子能力（如 beac... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-002.json`
- [x] TASK-003 Implement AC-003: executing 阶段：`beacon eval scorecard --runner live --live-tier local_a... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-003.json`
- [x] TASK-004 Implement AC-004: passed 判定：live_skill_pass ≥ 30/37（真实执行），失败 skill 有真实 reason_code（不折算 ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1617-live-benchmark-verify/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
