# Test Cases: Implement Package Legacy Loader Retirement Contract

**Feature**: `implement-package-legacy-loader-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-IMPLEMENT-LOADER-001 | smoke | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "implement_public_entrypoint_remains_routeable"` | `beacon implement --help` remains routeable through the public app. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-001.json` |
| AC-002 | TC-IMPLEMENT-LOADER-002 | smoke | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "implement_public_subcommands_remain_routeable"` | Required public implement subcommands remain visible and callable. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-002.json` |
| AC-003 | TC-IMPLEMENT-LOADER-003 | contract | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "implement_package_exports_current_app"` | The implement package exports `app` and required helpers without dynamic sibling loading. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-003.json` |
| AC-004 | TC-IMPLEMENT-LOADER-004 | static | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "legacy_loader_function_is_absent"` | `_load_legacy_cli_module` is absent from current source. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-004.json` |
| AC-005 | TC-IMPLEMENT-LOADER-005 | static | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "legacy_dynamic_module_name_is_absent"` | `_implement_legacy_cli` dynamic module loading is absent from current source. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-005.json` |
| AC-006 | TC-IMPLEMENT-LOADER-006 | static | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "tests_do_not_depend_on_legacy_cli"` | Tests do not import, monkeypatch, or assert `_legacy_cli`. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-006.json` |
| AC-007 | TC-IMPLEMENT-LOADER-007 | registry | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "implement_loader_retirement_is_registry_bound"` | `implement-legacy-cli-loader` remains registered and points to this retirement feature. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-007.json` |
| AC-008 | TC-IMPLEMENT-LOADER-008 | regression | `python3 -m pytest -q tests/test_v1411_implement_package_legacy_loader_retirement.py -k "no_unrelated_retirement_in_implement_loader_slice"` | QA, PRD, prototype, browser, memory, intent, and command alias behavior are not changed by this slice. | `.beacon/evidence/test-results/implement-package-legacy-loader-retirement-contract/TC-IMPLEMENT-LOADER-008.json` |

## Explicit Non Coverage

- These tests do not require QA legacy mirror policy changes.
- These tests do not require PRD legacy mirror policy changes.
- These tests do not require prototype legacy inspector split.
- These tests do not require browser fallback rename.
- These tests do not require memory or intent behavior changes.
- These tests do not require command alias removal.
- These tests do not produce release pass or fail verdicts by themselves.
