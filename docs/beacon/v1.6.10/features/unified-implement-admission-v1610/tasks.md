---
slug: unified-implement-admission-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: unified-implement-admission-v1610

## Task Ledger

- [ ] TASK-001 Implement AC-UIA-001: 提供唯一 shared `ensure_implement_admission`（或等价单一入口），direct implement、go... · ac=AC-UIA-001 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-001.json`
- [ ] TASK-002 Implement AC-UIA-002: `require_workspace_admission=false`、`branch-only`、`skipped=true` 只能触发... · ac=AC-UIA-002 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-002.json`
- [ ] TASK-003 Implement AC-UIA-003: single-repo pass 必须绑定真实 leaf git worktree、governed feature branch、cle... · ac=AC-UIA-003 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-003.json`
- [ ] TASK-004 Implement AC-UIA-004: monorepo pass 必须为每个 participating 且 writable service 生成完整 `service_wo... · ac=AC-UIA-004 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-004.json`
- [ ] TASK-005 Implement AC-UIA-005: 每个 service worktree 必须由对应 child repo 的 `git worktree list` 证明，分支符合 pe... · ac=AC-UIA-005 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-005.json`
- [ ] TASK-006 Implement AC-UIA-006: version governance 是 branch/service/worktree facts 的最高项目权威；stale `bea... · ac=AC-UIA-006 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-006.json`
- [ ] TASK-007 Implement AC-UIA-007: implement write path 强制 strict branch/cwd/HEAD mismatch；诊断型 soft mism... · ac=AC-UIA-007 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-007.json`
- [ ] TASK-008 Implement AC-UIA-008: admission 在 worker dispatch 和第一次 implementation write 前执行；pre-commit/... · ac=AC-UIA-008 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-008.json`
- [ ] TASK-009 Implement AC-UIA-009: admission artifact 记录 parent truth reconcile、每个 child baseline reconc... · ac=AC-UIA-009 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-009.json`
- [ ] TASK-010 Implement AC-UIA-010: 真实 Git 回归覆盖 single-repo、nested child repos monorepo、direct/goal/team/... · ac=AC-UIA-010 · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/AC-UIA-010.json`
- [ ] TASK-011 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/GATES.json`
- [ ] TASK-012 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/unified-implement-admission-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
