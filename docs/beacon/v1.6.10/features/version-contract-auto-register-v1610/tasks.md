---
slug: version-contract-auto-register-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: version-contract-auto-register-v1610

## Task Ledger

- [ ] TASK-001 Implement AC-VCA-001: monorepo package `git_canonical_branch=beacon/vX/slug` 登记为 `feature/v... · ac=AC-VCA-001 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-001.json`
- [ ] TASK-002 Implement AC-VCA-002: freeze 成功路径调用 ensure_version_contract_from_feature_package 并输出 versio... · ac=AC-VCA-002 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-002.json`
- [ ] TASK-003 Implement AC-VCA-003: create_or_update_project_metadata / doctor --truth-canonical 可持久化 tru... · ac=AC-VCA-003 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-003.json`
- [ ] TASK-004 Implement AC-VCA-004: governance_md 权威且合同无 participating/branch map 时 implement preflight r... · ac=AC-VCA-004 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-004.json`
- [ ] TASK-005 Implement AC-VCA-005: 已登记但缺 truth_canonical 的版本 governance_precheck 默认 main 且 pass（truth_ca... · ac=AC-VCA-005 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-005.json`
- [ ] TASK-006 Implement AC-VCA-006: 回归套件 tests/test_version_contract_auto_register.py + test_v166_governa... · ac=AC-VCA-006 · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/AC-VCA-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/version-contract-auto-register-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
