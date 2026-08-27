# Beacon Implementation Tasks Ledger

- feature: `beacon-v1614-fsm-mermaid-validate`
- version: `v1.6.14`
- plan_id: `plan-beacon-v1614-fsm-mermaid-validate-r1`
- revision_id: `R1`
- progress: `0/6`
- status: `planned`
- next_task: `ITASK-001` TASK-001 Implement AC-001: truth 生成/冻结时，FSM 段自动附带 `stateDiagram-v2` mermaid 块（状态+转移），文档可渲染。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-001.json`
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-fsm-mermaid-validate.progress.json`
- canonical_plan_json: `docs/beacon/v1.6.14/.machine/execution/implementation-plan-beacon-v1614-fsm-mermaid-validate.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[ ] `ITASK-001` TASK-001 Implement AC-001: truth 生成/冻结时，FSM 段自动附带 `stateDiagram-v2` mermaid 块（状态+转移），文档可渲染。 · ac=AC-001 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-001.json`
  - tests=TEST-001,TC-001 | next
[ ] `ITASK-002` TASK-002 Implement AC-002: FSM 机器校验：校验器可解析 truth FSM 表，检查 状态存在 / 转移合法 / illegal 转换被拒，输出结构化 findi... · ac=AC-002 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-002.json`
  - tests=TEST-002,TC-002 | depends_on=ITASK-001
[ ] `ITASK-003` TASK-003 Implement AC-003: FSM 行为变化可检测：同一 FSM 的 states/transitions 变化产生不同 behavior digest，仅措辞变化不... · ac=AC-003 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-003.json`
  - tests=TEST-003,TC-003 | depends_on=ITASK-002
[ ] `ITASK-004` TASK-004 Implement AC-004: FSM 校验进入 freeze 门禁：FSM 不合法（如非法转移未声明）→ freeze fail-closed（reason_code ... · ac=AC-004 · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/AC-004.json`
  - tests=TEST-004,TC-004 | depends_on=ITASK-003
[ ] `ITASK-005` TASK-005 Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/GATES.json`
  - depends_on=ITASK-004
[ ] `ITASK-006` TASK-006 Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`.beacon/evidence/implement/beacon-v1614-fsm-mermaid-validate/QA-MATRIX.json`
  - depends_on=ITASK-005
