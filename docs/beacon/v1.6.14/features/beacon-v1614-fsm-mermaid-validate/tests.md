---
slug: beacon-v1614-fsm-mermaid-validate
version: v1.6.14
materials_status: current
---

# Tests: beacon-v1614-fsm-mermaid-validate

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -n "stateDiagram-v2" docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md` | mermaid 状态图存在 |
| TC-002 | AC-002 | `python3 tests/test_v1614_fsm_validate.py -k validator` | exit 0：校验器解析 FSM，非法转移被拒 |
| TC-003 | AC-003 | `python3 tests/test_v1614_fsm_validate.py -k digest` | exit 0：行为变化 digest 不同，措辞变化 digest 相同 |
| TC-004 | AC-004 | `python3 tests/test_v1614_fsm_validate.py -k freeze_gate` | exit 0：FSM 不合法 → freeze 拦截（truth_fsm_invalid） |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1614_fsm_validate.py` | exit 0：全断言通过 |
| TC-ILLEGAL | AC-002,AC-004 | `rg -n -e "跳过校验冻结" -e "校验绕过" docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md` | illegal（跳校验/绕过 gate 均被拒） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1614_fsm_validate.py` 真实断言）。
