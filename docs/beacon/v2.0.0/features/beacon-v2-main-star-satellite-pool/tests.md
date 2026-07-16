---
slug: beacon-v2-main-star-satellite-pool
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-main-star-satellite-pool/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 Main-Star Satellite Worktree Pool

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-MSS-001 | TC-V2-MSS-001 | contract | `python3 -m pytest tests/test_v200_star_satellite.py::test_modes -q` | 双模式 |
| AC-V2-MSS-002 | TC-V2-MSS-002 | integration | `python3 -m pytest tests/test_v200_star_satellite.py::test_one_lake_one_satellite -q` | 一湖一卫星 |
| AC-V2-MSS-003 | TC-V2-MSS-003 | integration | `python3 -m pytest tests/test_v200_star_satellite.py::test_merge_to_star_only -q` | 只合主星 |
| AC-V2-MSS-004 | TC-V2-MSS-004 | negative | `python3 -m pytest tests/test_v200_star_satellite.py::test_satellite_cannot_write_truth -q` | 卫星禁写 truth |
