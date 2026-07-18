---
slug: loom-brand-surface
version: v2.0.0
status: frozen
revision_id: R1
---

# Tasks: loom-brand-surface

- [x] TASK-LOOM-BR-01 Freeze naming matrix (pip/CLI/skill/state)
- [x] TASK-LOOM-BR-02 Packaging sketch: loom wheel + `loom` console_script
- [x] TASK-LOOM-BR-03 Skill surface: skills/loom/loom-goal or alias route
- [x] TASK-LOOM-BR-04 Dual-install doctor check (no overwrite)
- [x] TASK-LOOM-BR-05 Examples + dual matrix checklist
- [x] TASK-LOOM-BR-06 Contract tests test_v200_loom_brand.py
- [x] TASK-LOOM-BR-07 State root isolation (.loom)


## Implementation note

2026-07-18 Product Goal pgr-51a763f2a691: Python parity + contract tests shipped (test_v200_*). Engine reuses v1.6.7 modules with v2 version support; Loom brand dual-install; subagent opt-in execute; driver→agent_trace hook; `beacon goal trace`.


- [x] TASK-LOOM-BR-08 Add support-only `skills/loom/loom-loop-goal` (Phase-1 route note)
- [x] TASK-LOOM-BR-09 Audit doc: v2 skill loom calling surface
