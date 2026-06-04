# Test Cases: Compatibility Registry and Command Catalog Contract

**Feature**: `compatibility-registry-and-command-catalog-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-COMPAT-REG-001 | schema | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "registry_schema_has_required_fields"` | The compatibility registry schema requires compat ID, surface, owner, reason, version range, default behavior, replacement, retirement route, and evidence. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-001.json` |
| AC-002 | TC-COMPAT-REG-002 | contract | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "registry_covers_required_baseline_inventory_surfaces"` | Required Phase 2+ baseline inventory compat IDs are present in the registry. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-002.json` |
| AC-003 | TC-COMPAT-REG-003 | schema | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "registry_entries_include_lifecycle_metadata"` | Each registry entry records owner, surface category, reason, current replacement, default behavior, allowed version range, retirement route, and required evidence. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-003.json` |
| AC-004 | TC-COMPAT-REG-004 | contract | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "command_catalog_layers_are_explicit"` | Command catalog entries can be classified into current, support, advanced, labs, compat, deprecated, or internal layers. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-004.json` |
| AC-005 | TC-COMPAT-REG-005 | regression | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "compat_and_deprecated_commands_remain_callable"` | Existing compat and deprecated command registration remains available during this slice. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-005.json` |
| AC-006 | TC-COMPAT-REG-006 | snapshot | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "default_routes_do_not_promote_compat_commands"` | Default help, status, or route guidance does not promote compat/deprecated commands as current mainline next route. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-006.json` |
| AC-007 | TC-COMPAT-REG-007 | negative | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "unregistered_compat_surface_fails_validation"` | Registry or catalog validation fails when a known compat, fallback, deprecated, or legacy surface is missing coverage. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-007.json` |
| AC-008 | TC-COMPAT-REG-008 | regression | `python3 -m pytest -q tests/test_v1411_compatibility_registry_and_command_catalog.py -k "no_behavior_retirement_in_registry_slice"` | QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent routing behavior are not changed by this slice. | `.beacon/evidence/test-results/compatibility-registry-and-command-catalog-contract/TC-COMPAT-REG-008.json` |

## Explicit Non Coverage

- These tests do not require command removal.
- These tests do not require legacy mirror policy changes.
- These tests do not require implement package migration.
- These tests do not require browser fallback rename.
- These tests do not produce release pass or fail verdicts.
