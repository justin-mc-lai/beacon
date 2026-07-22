---
slug: compat-debt-cut-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-CDC-001 | AC-CDC-001 | `python3 -c "from beacon.utils.truth_map import feature_package_authoritative as f; assert f('v0.0.13')"` | True |
| TC-CDC-002 | AC-CDC-002 | `rg -n "return TRUTH_SOURCE_MODEL_AUTHORITATIVE" beacon/utils/truth_map.py` | 恒权威 |
| TC-CDC-003 | AC-CDC-003 | `rg -n "legacy_split_truth" beacon/commands/freeze.py` | 无命中 |
| TC-CDC-004 | AC-CDC-004 | `rg -n "legacy_split_truth" beacon/utils/truth_integrity.py` | 无 skip 理由 |
| TC-CDC-005 | AC-CDC-005 | `python3 -m pytest tests/test_v1610_compat_debt_cut.py -q` | pass |
| TC-CDC-006 | AC-CDC-004 | `rg -n "no_longer_skips|legacy_split_truth_no_longer" tests/test_truth_integrity.py` | 回归改名 |
| TC-CDC-007 | AC-CDC-003 | `rg -n "legacy_split_truth|Illegal" docs/beacon/v1.6.10/features/compat-debt-cut-v1610/truth.md` | no illegal skip path |
