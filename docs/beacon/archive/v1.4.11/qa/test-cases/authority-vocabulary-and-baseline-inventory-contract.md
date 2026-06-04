# Test Cases: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-AUTH-INV-001 | unit | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "artifact_roles_are_defined"` | Artifact roles include truth, projection, evidence, runtime state, compatibility mirror, and historical fixture. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-001.json` |
| AC-002 | TC-AUTH-INV-002 | static | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "forbidden_machine_truth_wording_is_rejected"` | Current-facing wording does not claim `.machine` or machine-readable artifacts are requirement truth. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-002.json` |
| AC-003 | TC-AUTH-INV-003 | contract | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "markdown_requirement_root_is_truth"` | Markdown requirement package under `docs/beacon/<version>/` is described as current requirement truth. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-003.json` |
| AC-004 | TC-AUTH-INV-004 | contract | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "machine_root_is_projection_not_truth"` | `.machine` remains available as projection, evidence, and read model. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-004.json` |
| AC-005 | TC-AUTH-INV-005 | artifact | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "baseline_inventory_artifacts_exist"` | Baseline inventory markdown and JSON artifacts are generated before behavior-changing cleanup. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-005.json` |
| AC-006 | TC-AUTH-INV-006 | schema | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "baseline_inventory_schema_is_complete"` | Each inventory row includes source file, symbol or function, surface category, current behavior, risk, proposed owner, proposed phase, and required evidence. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-006.json` |
| AC-007 | TC-AUTH-INV-007 | regression | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "compat_behavior_is_not_retired_by_this_slice"` | Compat commands, QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent legacy router remain behaviorally available. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-007.json` |
| AC-008 | TC-AUTH-INV-008 | regression | `python3 -m pytest -q tests/test_v1411_authority_vocabulary_and_inventory.py -k "required_hotspots_are_inventory_covered"` | Required known hotspots are present in the inventory coverage and forbidden wording cannot return silently. | `.beacon/evidence/test-results/authority-vocabulary-and-baseline-inventory-contract/TC-AUTH-INV-008.json` |

## Explicit Non Coverage

- These tests do not implement compatibility registry behavior.
- These tests do not remove legacy mirrors or fallback paths.
- These tests do not migrate implement loader behavior.
- These tests do not rename browser fallback runtime behavior.
- These tests do not produce release pass or fail verdicts.
