---
slug: beacon-v1615-automerge-gate
version: v1.6.15
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1615-automerge-gate

## Task Ledger

- [x] TASK-001 Implement AC-001: merge 回 main 前 gate 检查三条件（类型覆盖达标 + 失败模式回归命中 0 + 对抗式审查通过）；任一不达标 → cove... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-001.json`
- [x] TASK-002 Implement AC-002: 失败模式回归库（v1.6.13 D3 已建）作为合并前置输入：在 regression_checked 阶段命中 > 0 → 合并被拦。 · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-002.json`
- [x] TASK-003 Implement AC-003: 对抗式审查（global-boundaries §5）作为合并前置：在 adversarial_checked 阶段缺翻车点清单/验证证据... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-003.json`
- [x] TASK-004 Implement AC-004: release 人类 gate 保持不变：auto-merge 不自动打 tag/部署/发布（merged 后仍须人类确认）；`manua... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1615-automerge-gate/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
