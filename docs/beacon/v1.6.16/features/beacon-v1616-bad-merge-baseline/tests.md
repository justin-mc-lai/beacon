---
slug: beacon-v1616-bad-merge-baseline
version: v1.6.16
materials_status: current
---

# Tests: beacon-v1616-bad-merge-baseline

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1616_bad_merge_baseline.py -k collect` | exit 0：统计合并到 main 的提交 + revert（git 分析）|
| TC-002 | AC-002 | `python3 tests/test_v1616_bad_merge_baseline.py -k rate` | exit 0：bad-merge 率 = revert/合并（按时间窗）|
| TC-003 | AC-003 | `python3 tests/test_v1616_bad_merge_baseline.py -k report` | exit 0：产出基线报告（合并数/revert/比率/时间窗/置信度）|
| TC-004 | AC-004 | `python3 tests/test_v1616_bad_merge_baseline.py -k no_change` | exit 0：统计不改变合并行为；数据不足标低置信度 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1616_bad_merge_baseline.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1616_bad_merge_baseline.py -k fsm` | exit 0：合法路径 scaffold→collected→computed→reported/warned 全走 |
| TC-ILLEGAL | AC-004 | `rg -n -e "数据不足仍硬算" -e "revert 误判" docs/beacon/v1.6.16/features/beacon-v1616-bad-merge-baseline/truth.md` | illegal（无置信度/数据失真均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1616_bad_merge_baseline.py` 真实断言）。
