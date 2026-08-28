---
slug: beacon-v1617-layering-audit
version: v1.6.17
materials_status: current
---

# Tests: beacon-v1617-layering-audit

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1617_layering_audit.py -k graph` | exit 0：生成 import 依赖图（模块×依赖）|
| TC-002 | AC-002 | `python3 tests/test_v1617_layering_audit.py -k god` | exit 0：列出 >2000 行 God Module |
| TC-003 | AC-003 | `python3 tests/test_v1617_layering_audit.py -k violation` | exit 0：识别越界引用（command→utils 越界）|
| TC-004 | AC-004 | `python3 tests/test_v1617_layering_audit.py -k report` | exit 0：产出可维护性风险判断 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1617_layering_audit.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1617_layering_audit.py -k fsm` | exit 0：合法路径 scaffold→scanned→sized→classified→reported 全走 |
| TC-ILLEGAL | AC-004 | `rg -n -e "扫描不全仍 report" -e "越界引用不识别" docs/beacon/v1.6.17/features/beacon-v1617-layering-audit/truth.md` | illegal（数据不实/掩盖均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1617_layering_audit.py` 真实断言）。
