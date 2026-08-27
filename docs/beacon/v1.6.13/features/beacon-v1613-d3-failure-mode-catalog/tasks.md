---
slug: beacon-v1613-d3-failure-mode-catalog
version: v1.6.13
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1613-d3-failure-mode-catalog

## Task Ledger

- [ ] TASK-001 Implement AC-001: 建立失败模式目录 `beacon-qa/references/failure-mode-catalog.md`，每条含 模式/症状/判定规... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/AC-001.json`
- [ ] TASK-002 Implement AC-002: filled 状态要求：每个用例含 rubric（coordinator 判定标准：什么证据算通过、什么算拦截）。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/AC-002.json`
- [ ] TASK-003 Implement AC-003: filled 状态要求：用例可独立执行（命令 + 断言），且能在 CI/本地跑出确定结果。 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/AC-003.json`
- [ ] TASK-004 Implement AC-004: `wire_gate` 触发：QA/release 前的对抗式审查固定引用目录（从目录抽取 3-5 个翻车点），引用缺失时输出 advis... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/AC-004.json`
- [ ] TASK-005 Implement AC-005: `user_decides` 要求：手册输出为批判式意见（findings/evidence），不自动判 pass；最终 verdict ... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/AC-005.json`
- [ ] TASK-006 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/GATES.json`
- [ ] TASK-007 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1613-d3-failure-mode-catalog/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
