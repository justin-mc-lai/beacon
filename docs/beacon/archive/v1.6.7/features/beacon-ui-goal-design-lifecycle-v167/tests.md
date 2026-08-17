---
slug: beacon-ui-goal-design-lifecycle-v167
version: v1.6.7
status: frozen
parser_contract: beacon-feature-package-v2
---

# Tests: UI Goal Design Lifecycle v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-UIG-G01 | TC-UIG-G01 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_goal_inserts_design_stage_when_ux -q` | stages 含 design |
| AC-UIG-G02 | TC-UIG-G02 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_run_design_stage_writes_baseline -q` | baseline artifact 写出 |
| AC-UIG-G03 | TC-UIG-G03 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_existing_design_fine_tune -q` | 不覆盖 + proposal |
| AC-UIG-L01 | TC-UIG-L01 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_design_md_lint_writes_evidence -q` | lint 证据 JSON |
| AC-UIG-L02 | TC-UIG-L02 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_ship_blocks_on_lint_error -q` | ship blocked |
| AC-UIG-T01 | TC-UIG-T01 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_company_catalog_min_eight -q` | ≥8 templates |
| AC-UIG-T02 | TC-UIG-T02 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_company_auto_select -q` | auto reason |
| AC-UIG-I01 | TC-UIG-I01 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_implement_blocks_without_design -q` | implement precheck |
| AC-UIG-Q01 | TC-UIG-Q01 | unit | `python3 -m pytest tests/test_v167_ui_goal_design_lifecycle.py::test_scorecard_has_design_fields -q` | scorecard fields |

## Evidence Path

`.beacon/evidence/design-md-lint/` · `.beacon/state/product-goal/`
