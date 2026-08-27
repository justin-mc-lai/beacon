---
slug: beacon-v1616-failure-mode-expansion
version: v1.6.16
materials_status: current
---

# Tests: beacon-v1616-failure-mode-expansion

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1616_failure_mode_expansion.py -k count` | exit 0：目录条目 ≥ 20（从 5 扩到 20+）|
| TC-002 | AC-002 | `python3 tests/test_v1616_failure_mode_expansion.py -k source` | exit 0：每条带 source_ref（v1.6.13-15 真实失败记录）|
| TC-003 | AC-003 | `python3 tests/test_v1616_failure_mode_expansion.py -k rubric` | exit 0：每条含完整 rubric（症状/判定/通过/拦截）|
| TC-004 | AC-004 | `python3 tests/test_v1616_failure_mode_expansion.py -k adversarial` | exit 0：目录可作为对抗式审查翻车点输入 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1616_failure_mode_expansion.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1616_failure_mode_expansion.py -k fsm` | exit 0：合法路径 scaffold→collected→authored→verified→cataloged 全走 |
| TC-ILLEGAL | AC-002 | `rg -n -e "编造条目" -e "缺 rubric" docs/beacon/v1.6.16/features/beacon-v1616-failure-mode-expansion/truth.md` | illegal（无来源/缺 rubric 均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1616_failure_mode_expansion.py` 真实断言）。
