---
slug: beacon-truth-fsm-terminal-unification
version: v1.6.18
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-truth-fsm-terminal-unification

## Task Ledger

- [ ] TASK-001 Implement AC-001: 生成器对自己的门禁封闭：`render_truth_package` 与 `render_intent_first_truth` 产出的骨... · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/AC-001.json`
- [ ] TASK-002 Implement AC-002: 单一规则一致：同一 truth 上 `check_b_fsm_audit(domain_required=True)["pass"] ==... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/AC-002.json`
- [ ] TASK-003 Implement AC-003: 终态按结构判定：目标状态无转出边且未显式声明时只产生 `terminal_undeclared` 告警且不阻断；转移缺目标时产生 `tra... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/AC-003.json`
- [ ] TASK-004 Implement AC-004: to` 表格行才形成机器边；含箭头的自然语言句子不形成机器边、不触发 `illegal_declared_as_legal`。 · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/AC-004.json`
- [ ] TASK-005 Implement AC-005: 投影可重算且无副作用：`attach_fsm_mermaid` 对过期投影返回 `mermaid_resynced` 并只改写 FSM 标... · ac=AC-005 · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/AC-005.json`
- [ ] TASK-006 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/GATES.json`
- [ ] TASK-007 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-truth-fsm-terminal-unification/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
