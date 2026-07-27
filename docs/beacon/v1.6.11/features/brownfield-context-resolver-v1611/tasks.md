---
slug: brownfield-context-resolver-v1611
version: v1.6.11
materials_status: current
task_source: acceptance_criteria
---

# Tasks: brownfield-context-resolver-v1611

## Task Ledger

- [ ] TASK-001 Implement AC-CTX-001: ContextEnvelope 同时绑定 commit、Truth revision、代码入口、测试基线、历史 Change · ac=AC-CTX-001 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-001.json`
- [ ] TASK-002 Implement AC-CTX-002: resolver 从用户目标反向定位相关 service/module/test，而非要求用户手工列全 · ac=AC-CTX-002 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-002.json`
- [ ] TASK-003 Implement AC-CTX-003: Truth、代码、测试语义冲突时进入 awaiting_human，并列出候选权威与影响 · ac=AC-CTX-003 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-003.json`
- [ ] TASK-004 Implement AC-CTX-004: 任一基线引用变化都会使下游 intent/diff/task graph 标记 stale · ac=AC-CTX-004 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-004.json`
- [ ] TASK-005 Implement AC-CTX-005: ContextEnvelope 必须解析 `parent_truth` 与 `inherited_contracts`，并把既有 Goal... · ac=AC-CTX-005 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-005.json`
- [ ] TASK-006 Implement AC-CTX-006: resolver 必须返回 host subagent runtime 可用性、truth canonical、implementatio... · ac=AC-CTX-006 · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/AC-CTX-006.json`
- [ ] TASK-007 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/GATES.json`
- [ ] TASK-008 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/brownfield-context-resolver-v1611/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
