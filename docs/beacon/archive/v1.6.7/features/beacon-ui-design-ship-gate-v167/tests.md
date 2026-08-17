---
slug: beacon-ui-design-ship-gate-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-ui-design-ship-gate-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: UI Design Philosophy Ship Gate v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-UID-001 | TC-UID-001 | contract | `python3 -m pytest tests/test_v167_ui_design_ship.py::test_matrix_schema -q` | matrix schema |
| AC-UID-002 | TC-UID-002 | negative | `python3 -m pytest tests/test_v167_ui_design_ship.py::test_missing_design_blocks_ship -q` | 缺 DESIGN 阻断 |
| AC-UID-003 | TC-UID-003 | contract | `python3 -m pytest tests/test_v167_ui_design_ship.py::test_scorecard_design_checks -q` | scorecard 含设计检查 |
| AC-UID-006 | TC-UID-004 | contract | `python3 -m pytest tests/test_v167_ui_design_ship.py::test_golden_has_matrix -q` | golden 含 matrix |

## Verification Notes

- Contract tests may land under `tests/test_v167_product_goal_domain.py` (or per-feature modules).
- Negative fixtures must fail closed (freeze or QA).
