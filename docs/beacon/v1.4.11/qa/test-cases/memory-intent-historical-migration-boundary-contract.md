# Test Cases: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-MEMORY-INTENT-001 | memory | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "old_memory_rows_remain_importable"` | Old memory rows can still be imported into `memory-v1`. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-001.json` |
| AC-002 | TC-MEMORY-INTENT-002 | evidence | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "first_migration_writes_transaction"` | First legacy memory migration writes an auditable migration transaction. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-002.json` |
| AC-003 | TC-MEMORY-INTENT-003 | memory | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "memory_v1_is_current_projection"` | `memory-v1` is the current memory projection after migration. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-003.json` |
| AC-004 | TC-MEMORY-INTENT-004 | guardrail | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "current_memory_write_does_not_write_legacy_projection_by_default"` | Current memory writes do not silently update legacy projection files. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-004.json` |
| AC-005 | TC-MEMORY-INTENT-005 | compatibility | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "legacy_projection_requires_explicit_compat_mode"` | Legacy projection writes require explicit compatibility mode or explicit migration/export command. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-005.json` |
| AC-006 | TC-MEMORY-INTENT-006 | intent | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "legacy_intent_router_is_compat_classified"` | Legacy intent router usage is marked as compatibility routing. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-006.json` |
| AC-007 | TC-MEMORY-INTENT-007 | compatibility | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "old_intent_api_remains_callable_with_compat_admission"` | Old intent APIs remain callable through explicit compatibility admission. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-007.json` |
| AC-008 | TC-MEMORY-INTENT-008 | intent | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "legacy_route_does_not_claim_current_route"` | Legacy router output is not claimed as current route evidence. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-008.json` |
| AC-009 | TC-MEMORY-INTENT-009 | registry | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "memory_registry_binding"` | Memory behavior binds to `memory-legacy-projection`. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-009.json` |
| AC-010 | TC-MEMORY-INTENT-010 | registry | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "intent_registry_binding"` | Intent behavior binds to `intent-legacy-router`. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-010.json` |
| AC-011 | TC-MEMORY-INTENT-011 | regression | `python3 -m pytest -q tests/test_v1411_memory_intent_historical_migration_boundary.py -k "no_unrelated_phase_behavior_changes"` | Prototype/design, browser, QA/PRD mirror, implement, command removal, release, and test marker behavior remain out of scope. | `.beacon/evidence/test-results/memory-intent-historical-migration-boundary-contract/TC-MEMORY-INTENT-011.json` |

## Explicit Non Coverage

- These tests do not cover prototype/design adapter behavior.
- These tests do not cover browser deterministic command behavior.
- These tests do not cover QA or PRD legacy mirror policy.
- These tests do not cover implement package behavior.
- These tests do not cover test marker relayering.
- These tests do not produce release pass/fail verdicts by themselves.

