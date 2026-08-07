---
slug: beacon-test-modernization-v1612
version: v1.6.12
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-test-modernization-v1612

## Task Ledger

- [ ] TASK-001 Implement AC-001: 分类清单中 20 个 fix_upstream_first 条目修复后，其所属测试文件不再出现级联失败，批次从 implementing ... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-001.json`
- [ ] TASK-002 Implement AC-002: 466 个 migrate_assert 条目全部改为现行规范断言并随文件一起通过，批次进入 next_batch · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-002.json`
- [ ] TASK-003 Implement AC-003: 206 个 fixture 条目按 TestDriftBatch 处置完成：迁移后通过，或显式归档（LegacyArchive）并更新清单状态 · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-003.json`
- [ ] TASK-004 Implement AC-004: v1.0–v1.5 历史线测试移入 tests/legacy/（LegacyArchive），默认 pytest 收集不再包含 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-004.json`
- [ ] TASK-005 Implement AC-005: 默认测试套件（不含 legacy）全量通过后进入 current_line_green，beacon doctor diagnose 无存... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-005.json`
- [ ] TASK-006 Implement AC-006: v2.x 4 个 defer 条目在 FillBatchQueue 记录 reason_code 与复核计划，不混入现行线验收 · ac=AC-006 · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/AC-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-test-modernization-v1612/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
