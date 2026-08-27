---
slug: beacon-v1614-feature-map
version: v1.6.14
materials_status: current
---

# Tests: beacon-v1614-feature-map

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -n "feature-map.md" docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md` | 骨架引用存在 + entry/verification 绑定 AC |
| TC-002 | AC-002 | `python3 tests/test_v1614_feature_map.py -k reproduce` | exit 0：模糊描述路由到 entry/verification |
| TC-003 | AC-003 | `python3 tests/test_v1614_feature_map.py -k self_verify` | exit 0：verification 命令可执行且信号可断言 |
| TC-004 | AC-004 | `python3 tests/test_v1614_feature_map.py -k one_way_projection` | exit 0：map 引用 truth 不反向改写；无命令面 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1614_feature_map.py` | exit 0：全断言通过 |
| TC-ILLEGAL | AC-004 | `rg -n "反向改写\|投影越权" docs/beacon/v1.6.14/features/beacon-v1614-feature-map/truth.md` | illegal（map 越权改 truth 被拒） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1614_feature_map.py` 真实断言）。
