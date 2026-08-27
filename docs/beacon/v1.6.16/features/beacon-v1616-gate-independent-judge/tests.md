---
slug: beacon-v1616-gate-independent-judge
version: v1.6.16
materials_status: current
---

# Tests: beacon-v1616-gate-independent-judge

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1616_gate_independent_judge.py -k recalc` | exit 0：coverage_rate 可由独立脚本重算 |
| TC-002 | AC-002 | `python3 tests/test_v1616_gate_independent_judge.py -k compare` | exit 0：独立判定 vs 系统判定比对（一致/偏差）|
| TC-003 | AC-003 | `python3 tests/test_v1616_gate_independent_judge.py -k audit` | exit 0：偏差记录可审计（gate/系统值/独立值/diff）|
| TC-004 | AC-004 | `python3 tests/test_v1616_gate_independent_judge.py -k no_verdict` | exit 0：独立裁判不判 pass/fail，只核验可信度 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1616_gate_independent_judge.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1616_gate_independent_judge.py -k fsm` | exit 0：合法路径 scaffold→computed→compared→verified/flagged 全走 |
| TC-ILLEGAL | AC-002,AC-003 | `rg -n -e "偏差不暴露" -e "独立裁判缺数据" docs/beacon/v1.6.16/features/beacon-v1616-gate-independent-judge/truth.md` | illegal（掩盖/脑补均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1616_gate_independent_judge.py` 真实断言）。
