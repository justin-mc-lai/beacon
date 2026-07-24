---
slug: workspace-clean-exit-gate-v1610
version: v1.6.10
materials_status: current
task_source: acceptance_criteria
---

# Tasks: workspace-clean-exit-gate-v1610

## Task Ledger

- [x] TASK-001 Implement AC-WC-001: 提供 `verify_clean_workspace`（或等价）统一出口 gate，读取完整 `git status --porcelai... · ac=AC-WC-001 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-001.json`
- [x] TASK-002 Implement AC-WC-002: dirty manifest 至少区分 `canonical_truth`、`formal_evidence`、`machine_proj... · ac=AC-WC-002 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-002.json`
- [x] TASK-003 Implement AC-WC-003: formal evidence manifest 仅可包含 tracked、branch-carried、hash-valid 的正式证据... · ac=AC-WC-003 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-003.json`
- [x] TASK-004 Implement AC-WC-004: tasks.md 中 checked evidence path 必须要求 evidence 文件存在、可解析、tracked/promo... · ac=AC-WC-004 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-004.json`
- [x] TASK-005 Implement AC-WC-005: agent_trace 写入前必须执行 redline/allowlist gate，禁止 `full_chat`、非空 `chat_bo... · ac=AC-WC-005 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-005.json`
- [x] TASK-006 Implement AC-WC-006: raw `.beacon/traces/**` 默认分类为 `runtime_private`；正式证据只能使用脱敏 digest，dig... · ac=AC-WC-006 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-006.json`
- [x] TASK-007 Implement AC-WC-007: `beacon-post-release-local-install` 默认在临时 git worktree 或等价隔离区执行 proje... · ac=AC-WC-007 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-007.json`
- [x] TASK-008 Implement AC-WC-008: `quiet-worktree`/skip-worktree 只能作为开发者降噪；`verify-clean-workspace --st... · ac=AC-WC-008 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-008.json`
- [x] TASK-009 Implement AC-WC-009: host projection 必须二选一：local-only ignore/skip 策略，或 deterministic `surf... · ac=AC-WC-009 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-009.json`
- [x] TASK-010 Implement AC-WC-010: truth/freeze/qa/release/post-release 出口都必须调用 clean-workspace gate 或记录... · ac=AC-WC-010 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-010.json`
- [x] TASK-011 Implement AC-WC-011: pre-push/main-push profile 必须阻断 generator dirty 与 unclassified dirty，... · ac=AC-WC-011 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-011.json`
- [x] TASK-012 Implement AC-WC-012: release human gate 保持最高边界；clean-workspace pass 不等于 release pass，post-... · ac=AC-WC-012 · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/AC-WC-012.json`
- [x] TASK-013 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/GATES.json`
- [x] TASK-014 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/workspace-clean-exit-gate-v1610/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
