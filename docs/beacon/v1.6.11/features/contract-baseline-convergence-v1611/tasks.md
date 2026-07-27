---
slug: contract-baseline-convergence-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: contract-baseline-convergence-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-BAS-001: 版本上下文明确记录 runtime=v1.6.10、docs=v1.6.11 planning-only，且严格校验通过 · ac=AC-BAS-001 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-001.json`
- [ ] TASK-002 Implement AC-BAS-002: 基线固定 main commit、Plan/Goal/Truth 关键入口与历史真相引用 · ac=AC-BAS-002 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-002.json`
- [ ] TASK-003 Implement AC-BAS-003: 合同测试基线记录命令、通过数、失败数与逐项 disposition；不得用降低 gate 消除失败 · ac=AC-BAS-003 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-003.json`
- [ ] TASK-004 Implement AC-BAS-004: Truth refreeze 时旧 tests/tasks/evidence 被标 stale，禁止跨 revision 复用 · ac=AC-BAS-004 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-004.json`
- [ ] TASK-005 Implement AC-BAS-005: 旧 package、旧 Goal ledger、缺 Matrix/exec TC/`ac=`/`evidence=` 的 active s... · ac=AC-BAS-005 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-005.json`
- [ ] TASK-006 Implement AC-BAS-006: 旧冻结 Truth 保持只读 lineage；仍有效的语义只能通过 `parent_truth`/`inherited_contracts... · ac=AC-BAS-006 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-006.json`
- [ ] TASK-007 Implement AC-BAS-007: `beacon truth init`/等价 CLI 只负责确定性创建 `features/<slug>/{truth,tests,tas... · ac=AC-BAS-007 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-007.json`
- [ ] TASK-008 Implement AC-BAS-008: 旧 PRD/User Story semantic compiler、host-response/command-bridge/provi... · ac=AC-BAS-008 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-008.json`
- [ ] TASK-009 Implement AC-BAS-009: 每个 R2 freeze 必须绑定最终四文件 baseline hash、package-validation report/hash、T... · ac=AC-BAS-009 · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/AC-BAS-009.json`
- [ ] TASK-010 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/GATES.json`
- [ ] TASK-011 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/contract-baseline-convergence-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
