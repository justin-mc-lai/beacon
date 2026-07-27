---
slug: convergence-verifier-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: convergence-verifier-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-CNV-001: ClosureMatrix 覆盖 intent/path/AC/state/task/evidence 六层并可双向追溯 · ac=AC-CNV-001 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-001.json`
- [ ] TASK-002 Implement AC-CNV-002: Goal pass 要求 must intents covered、required paths closed、AC verified、状... · ac=AC-CNV-002 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-002.json`
- [ ] TASK-003 Implement AC-CNV-003: 任一 Truth/graph/material/evidence stale 均阻断完成并给出重建 route · ac=AC-CNV-003 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-003.json`
- [ ] TASK-004 Implement AC-CNV-004: subagent/task executor 不能直接完成 GoalRun；只有 Goal owner 在 verifier pass 后... · ac=AC-CNV-004 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-004.json`
- [ ] TASK-005 Implement AC-CNV-005: fail verdict 必须列出最小未闭环集合及 recommended next-ready/replan/truth/qa route · ac=AC-CNV-005 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-005.json`
- [ ] TASK-006 Implement AC-CNV-006: GoalRun 必须持有 `run_id`、program slug、graph revision、truth revision set、... · ac=AC-CNV-006 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-006.json`
- [ ] TASK-007 Implement AC-CNV-007: L0–L8 只能映射到既有 goal→plan→truth→design?→implement→qa→release；不得新增 publi... · ac=AC-CNV-007 · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/AC-CNV-007.json`
- [ ] TASK-008 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/GATES.json`
- [ ] TASK-009 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/convergence-verifier-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
