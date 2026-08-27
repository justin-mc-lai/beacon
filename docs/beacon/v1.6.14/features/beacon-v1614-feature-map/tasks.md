---
slug: beacon-v1614-feature-map
version: v1.6.14
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1614-feature-map

## Task Ledger

- [ ] TASK-001 Implement AC-001: 每个 feature 有 `feature-map.md` 骨架：entry_points + verification_commands... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-001.json`
- [ ] TASK-002 Implement AC-002: 复现路由：map 含 `reproduce[]`（symptom_hint → 定位 steps），模糊 bug 描述可路由到对应 ent... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-002.json`
- [ ] TASK-003 Implement AC-003: agent 自验证：map 的 verification 命令可被 agent 执行（复用 code2truth 资产），输出可观测信号供断言。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-003.json`
- [ ] TASK-004 Implement AC-004: 单向投影：map 引用 truth（AC），不反向改 truth；不新增命令面；AC 变化时 map 漂移可检测。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-feature-map/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
