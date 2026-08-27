---
slug: beacon-v1616-live-skill-smoke
version: v1.6.16
materials_status: current
---

# Tests: beacon-v1616-live-skill-smoke

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1616_live_skill_smoke.py -k admission` | exit 0：local_admitted tier 下全量 skill 走 host_behavior |
| TC-002 | AC-002 | `python3 tests/test_v1616_live_skill_smoke.py -k host_behavior` | exit 0：live_skill_pass ≥ 30/37（真实执行通过率）|
| TC-003 | AC-003 | `python3 tests/test_v1616_live_skill_smoke.py -k host_behavior` | exit 0：每 skill 有 host_behavior 执行 trace（status/reason_code/route）|
| TC-004 | AC-004 | `python3 tests/test_v1616_live_skill_smoke.py -k no_fake` | exit 0：失败 skill 标 fail+reason_code，不折算 pass |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1616_live_skill_smoke.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1616_live_skill_smoke.py -k fsm` | exit 0：合法路径 scaffold→executing→traced→passed/failed 全走 |
| TC-ILLEGAL | AC-004 | `rg -n -e "执行失败仍标" -e "表面检查冒充" docs/beacon/v1.6.16/features/beacon-v1616-live-skill-smoke/truth.md` | illegal（伪造/冒充均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1616_live_skill_smoke.py` 真实断言）。
