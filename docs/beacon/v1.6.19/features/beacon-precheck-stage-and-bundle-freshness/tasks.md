---
slug: beacon-precheck-stage-and-bundle-freshness
version: v1.6.19
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-precheck-stage-and-bundle-freshness

## Task Ledger

- [ ] TASK-001 Implement AC-001: 阶段分级：`build_material_audit(stage="implement")` 中 `formal_release_pres... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-precheck-stage-and-bundle-freshness/AC-001.json`
- [ ] TASK-002 Implement AC-002: 判定内容寻址：precheck bundle 写入 `inputs_digest`；`precheck_inputs_digest` 在 ... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-precheck-stage-and-bundle-freshness/AC-002.json`
- [ ] TASK-003 Implement AC-003: 陈旧即重算：`record_standard_execution_precheck` 加载到的 CLI bundle 若 `bundle_... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-precheck-stage-and-bundle-freshness/AC-003.json`
- [ ] TASK-004 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-precheck-stage-and-bundle-freshness/GATES.json`
- [ ] TASK-005 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-precheck-stage-and-bundle-freshness/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
