---
slug: beacon-v1617-live-benchmark-verify
version: v1.6.17
materials_status: current
---

# Tests: beacon-v1617-live-benchmark-verify

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 tests/test_v1617_live_benchmark.py -k fixtures` | exit 0：34 skill 的 prompt fixture 存在且含 ROUTE: |
| TC-002 | AC-002 | `python3 tests/test_v1617_live_benchmark.py -k surface` | exit 0：mode 子能力解析到主 SKILL.md（无 skill_surface_missing）|
| TC-003 | AC-003 | `python3 tests/test_v1617_live_benchmark.py -k surface` | exit 0：live scorecard 跑通，每 skill 有 host_behavior trace |
| TC-004 | AC-004 | `python3 tests/test_v1617_live_benchmark.py -k fixtures` | exit 0：live_skill_pass ≥ 30/37（真实执行）|
| TC-EXEC | AC-001..004 | `python3 tests/test_v1617_live_benchmark.py` | exit 0：全断言通过 |
| TC-FSMW | AC-001..004 | `python3 tests/test_v1617_live_benchmark.py -k fsm` | exit 0：合法路径 scaffold→materialized→resolved→executing→traced→passed/failed |
| TC-ILLEGAL | AC-004 | `rg -n -e "执行失败仍标" -e "fixture 缺失仍执行" docs/beacon/v1.6.17/features/beacon-v1617-live-benchmark-verify/truth.md` | illegal（伪造/占位冒充均被拒）|

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1617_live_benchmark.py` 真实断言）。
