---
slug: beacon-v1616-eval-external-anchor
version: v1.6.16
materials_status: current
---

# Tests: beacon-v1616-eval-external-anchor

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1616_eval_external_anchor.py -k external` | exit 0：benchmark 案例集含外部来源案例（非全内置）|
| TC-002 | AC-002 | `python3 tests/test_v1616_eval_external_anchor.py -k provenance` | exit 0：外部案例带 source_ref，无来源冒充被拒 |
| TC-003 | AC-003 | `python3 tests/test_v1616_eval_external_anchor.py -k runnable` | exit 0：外部案例可执行（prompt+expected_route 完整）|
| TC-004 | AC-004 | `python3 tests/test_v1616_eval_external_anchor.py -k builtin` | exit 0：内置案例保留（回归兼容）|
| TC-EXEC | AC-001..004 | `python3 tests/test_v1616_eval_external_anchor.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1616_eval_external_anchor.py -k fsm` | exit 0：合法路径 scaffold→collected→registered→executed→verified 全走 |
| TC-ILLEGAL | AC-002 | `rg -n -e "无来源案例冒充" -e "外部案例不执行" docs/beacon/v1.6.16/features/beacon-v1616-eval-external-anchor/truth.md` | illegal（伪称来源/只登记不执行均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1616_eval_external_anchor.py` 真实断言）。
