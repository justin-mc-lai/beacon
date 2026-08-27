---
slug: beacon-v1614-fsm-mermaid-validate
version: v1.6.14
materials_status: current
task_source: acceptance_criteria
---

# Tasks: beacon-v1614-fsm-mermaid-validate

## Task Ledger

- [ ] TASK-001 Implement AC-001: truth 生成/冻结时，FSM 段自动附带 `stateDiagram-v2` mermaid 块（状态+转移），文档可渲染。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-001.json`
- [ ] TASK-002 Implement AC-002: FSM 机器校验：校验器可解析 truth FSM 表，检查 状态存在 / 转移合法 / illegal 转换被拒，输出结构化 findi... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-002.json`
- [ ] TASK-003 Implement AC-003: FSM 行为变化可检测：同一 FSM 的 states/transitions 变化产生不同 behavior digest，仅措辞变化不... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-003.json`
- [ ] TASK-004 Implement AC-004: FSM 校验进入 freeze 门禁：FSM 不合法（如非法转移未声明）→ freeze fail-closed（reason_code ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-004.json`
- [ ] TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/GATES.json`
- [ ] TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/QA-MATRIX.json`

## Boundary

Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).
