---
slug: compat-debt-cut-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: compat-debt-cut-v1610

## Task Ledger

- [ ] TASK-001 Implement AC-CDC-001: `feature_package_authoritative` 对 v0.0.13/v1.4/v1.6 均为 True · ac=AC-CDC-001 · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/AC-CDC-001.json`
- [ ] TASK-002 Implement AC-CDC-002: `truth_source_model_for_version` 恒为 feature_package_authoritative · ac=AC-CDC-002 · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/AC-CDC-002.json`
- [ ] TASK-003 Implement AC-CDC-003: freeze 源码不含 `legacy_split_truth` skip · ac=AC-CDC-003 · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/AC-CDC-003.json`
- [ ] TASK-004 Implement AC-CDC-004: triptych-only / 缺四件套 package integrity 不得 status=skipped · ac=AC-CDC-004 · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/AC-CDC-004.json`
- [ ] TASK-005 Implement AC-CDC-005: v0.0.x 回归测试存在且通过 · ac=AC-CDC-005 · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/AC-CDC-005.json`
- [ ] TASK-006 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/GATES.json`
- [ ] TASK-007 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/compat-debt-cut-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
