---
slug: beacon-precheck-stage-and-bundle-freshness
version: v1.6.19
materials_status: current
---

# Tests: beacon-precheck-stage-and-bundle-freshness

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 -m pytest -q tests/test_standard_execution_precheck_stage_and_freshness.py -k stage --tb=no` | stage_scoped_release_docs |
| TC-002 | AC-002 | `python3 -m pytest -q tests/test_standard_execution_precheck_stage_and_freshness.py -k "digest or freshness" --tb=no` | bundle_content_addressed |
| TC-003 | AC-003 | `python3 -c "import inspect; from beacon.utils import loop_goal_state as m; s=inspect.getsource(m.record_standard_execution_precheck); assert 'bundle_is_fresh' in s and 'run_standard_execution_precheck' in s"` | stale_bundle_triggers_recompute |
| TC-EXEC-PYTEST | AC-001 | `python3 -m pytest -q tests/test_standard_execution_precheck_stage_and_freshness.py --tb=no` | precheck_fix_suite_green |

## Validation Note

TC-001/TC-002 are behavioural (stage-scoped requiredness; digest + freshness semantics). TC-003 asserts the auto-recompute wiring in the precheck consumer. TC-EXEC-PYTEST is the exec-layer TC required by the v1.6.10 Truth Review Gate Check C.
