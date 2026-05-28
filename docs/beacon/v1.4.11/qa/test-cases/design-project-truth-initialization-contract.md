# Test Cases: Design Project Truth Initialization Contract

**Feature**: `design-project-truth-initialization-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-DESIGN-TRUTH-001 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "default_write_does_not_create_project_truth"` | Default `--write` does not create root `PRODUCT.md` / `DESIGN.md`. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-001.json` |
| AC-002 | TC-DESIGN-TRUTH-002 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "include_project_truth_creates_product_md"` | Explicit include creates missing `PRODUCT.md`. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-002.json` |
| AC-003 | TC-DESIGN-TRUTH-003 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "include_project_truth_creates_design_md"` | Explicit include creates missing `DESIGN.md`. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-003.json` |
| AC-004 | TC-DESIGN-TRUTH-004 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "existing_project_truth_is_not_overwritten_without_force"` | Existing project truth is preserved without `--force`. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-004.json` |
| AC-005 | TC-DESIGN-TRUTH-005 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "force_overwrites_project_truth"` | Existing project truth may be overwritten with `--force`. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-005.json` |
| AC-006 | TC-DESIGN-TRUTH-006 | cli | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "write_status_is_auditable"` | JSON output reports statuses per path. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-006.json` |
| AC-007 | TC-DESIGN-TRUTH-007 | template | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "product_template_has_required_sections"` | `PRODUCT.md` template includes product truth sections. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-007.json` |
| AC-008 | TC-DESIGN-TRUTH-008 | template | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "design_template_has_required_sections"` | `DESIGN.md` template includes design truth sections. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-008.json` |
| AC-009 | TC-DESIGN-TRUTH-009 | projection | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "machine_projection_remains_projection_only"` | Machine design projection is projection-only. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-009.json` |
| AC-010 | TC-DESIGN-TRUTH-010 | boundary | `python3 -m pytest -q tests/test_v1411_design_project_truth_initialization.py -k "design_routes_remain_support_only"` | Design route payload remains support-only / non-truth / non-gate. | `.beacon/evidence/test-results/design-project-truth-initialization-contract/TC-DESIGN-TRUTH-010.json` |

## Explicit Non Coverage

- These tests do not execute implementation.
- These tests do not execute QA acceptance.
- These tests do not execute release.
- These tests do not promote design support output into truth.
- These tests do not require project truth initialization for non-UI features.
