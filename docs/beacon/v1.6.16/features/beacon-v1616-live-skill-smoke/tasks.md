---
slug: beacon-v1616-live-skill-smoke
version: v1.6.16
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1616-live-skill-smoke

## Task Ledger

- [ ] TASK-001 Implement AC-001: executing 阶段：eval benchmark 在 local_admitted tier 下对 37 个 skill 全量执行 ... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-001.json`
- [ ] TASK-002 Implement AC-002: traced→passed 后：live_skill_pass 从 1/37 提升到 ≥ 30/37（真实执行通过率）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-002.json`
- [ ] TASK-003 Implement AC-003: traced 阶段：每个执行过的 skill 落盘 host_behavior 执行 trace（含 status/reason_code... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-003.json`
- [ ] TASK-004 Implement AC-004: failed 判定：执行结果不伪造，失败 skill 标 fail + reason_code，不折算为 pass。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1616-live-skill-smoke/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
