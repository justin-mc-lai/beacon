---
slug: beacon-v1614-fsm-test-generation
version: v1.6.14
materials_status: current
---

# Tests: beacon-v1614-fsm-test-generation

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1614_fsm_gen.py -k walk` | exit 0：从合法 FSM 生成 legal-walk 用例，可达状态全走 |
| TC-002 | AC-002 | `python3 tests/test_v1614_fsm_gen.py -k exec_tc` | exit 0：生成用例可执行（进 exec-layer TC） |
| TC-003 | AC-003 | `python3 tests/test_v1614_fsm_gen.py -k vertex_assert` | exit 0：每到达状态生成顶点断言 |
| TC-004 | AC-004 | `python3 tests/test_v1614_fsm_gen.py -k illegal_excluded` | exit 0：illegal 路径未被生成 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1614_fsm_gen.py` | exit 0：全断言通过 |
| TC-ILLEGAL | AC-004 | `rg -n -e "illegal 路径被生成" -e "跳过校验" docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md` | illegal（安全网失效被拒） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1614_fsm_gen.py` 真实断言）。
