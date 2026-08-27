---
slug: beacon-v1615-automerge-gate
version: v1.6.15
materials_status: current
---

# Tests: beacon-v1615-automerge-gate

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1615_automerge_gate.py -k three_conditions` | exit 0：三条件任一不达标 → fail-closed stop_for_repair |
| TC-002 | AC-002 | `python3 tests/test_v1615_automerge_gate.py -k regression_hit` | exit 0：失败模式回归命中 > 0 → 合并被拦 |
| TC-003 | AC-003 | `python3 tests/test_v1615_automerge_gate.py -k adversarial` | exit 0：对抗审查缺清单/证据 → 合并被拦 |
| TC-004 | AC-004 | `python3 tests/test_v1615_automerge_gate.py -k human_gate` | exit 0：release 人类 gate 不变（不自动 tag/部署）|
| TC-EXEC | AC-001..004 | `python3 tests/test_v1615_automerge_gate.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1615_automerge_gate.py -k fsm` | exit 0：合法路径 qa_passed→coverage_checked→regression_checked→adversarial_checked→merged 全走（域 FSM legal walk）|
| TC-ILLEGAL | AC-001 | `rg -n -e "覆盖不足仍合并" -e "回归库命中仍合并" -e "对抗审查缺失仍合并" docs/beacon/v1.6.15/features/beacon-v1615-automerge-gate/truth.md` | illegal（gate 绕过/安全网失效均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1615_automerge_gate.py` 真实断言）。
