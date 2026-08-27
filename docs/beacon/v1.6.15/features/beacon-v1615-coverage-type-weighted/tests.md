---
slug: beacon-v1615-coverage-type-weighted
version: v1.6.15
materials_status: current
---

# Tests: beacon-v1615-coverage-type-weighted

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1615_coverage_type_weighted.py -k weighted_rate` | exit 0：只测 happy → rate < 1.0（类型加权生效）|
| TC-002 | AC-002 | `python3 tests/test_v1615_coverage_type_weighted.py -k non_browser_families` | exit 0：非浏览器场景展开 happy+negative+boundary |
| TC-003 | AC-003 | `python3 tests/test_v1615_coverage_type_weighted.py -k missing_families` | exit 0：输出列出 missing_families |
| TC-004 | AC-004 | `python3 tests/test_v1615_coverage_type_weighted.py -k compat` | exit 0：既有 lake 语义兼容、无新命令面 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1615_coverage_type_weighted.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1615_coverage_type_weighted.py -k fsm` | exit 0：合法路径 weighted→assessed→reported→gated 全走（域 FSM legal walk）|
| TC-ILLEGAL | AC-001,AC-002 | `rg -n -e "数量全绿仍报" -e "primary-only" docs/beacon/v1.6.15/features/beacon-v1615-coverage-type-weighted/truth.md` | illegal（类型缺口被掩盖/跳过均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1615_coverage_type_weighted.py` 真实断言）。
