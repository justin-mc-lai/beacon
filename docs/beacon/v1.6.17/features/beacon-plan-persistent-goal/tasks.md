---
slug: beacon-plan-persistent-goal
version: v1.6.17
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-plan-persistent-goal

## Task Ledger

- [ ] TASK-001 Implement AC-001: plan 阶段：`build_plan_artifact(utterance)` 产出 `persistent_goal{objectiv... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/AC-001.json`
- [ ] TASK-002 Implement AC-002: goal 运行时：`create_goal_run` 将 `persistent_goal` 写入 `payload{goal_objec... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/AC-002.json`
- [ ] TASK-003 Implement AC-003: 续跑：`goal_steering.render_steering` 在 `halt_budget=false` 时选 `continua... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/AC-003.json`
- [ ] TASK-004 Implement AC-004: 预算收尾：`goal_steering.select_template_id(halt_budget=true)` 选 `budget_l... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/AC-004.json`
- [ ] TASK-005 Implement AC-005: 边界：`beacon-plan` 仅产 `programs/<slug>/` 咨询产物，不写 `features/<slug>/truth... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/AC-005.json`
- [ ] TASK-006 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/GATES.json`
- [ ] TASK-007 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-plan-persistent-goal/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
