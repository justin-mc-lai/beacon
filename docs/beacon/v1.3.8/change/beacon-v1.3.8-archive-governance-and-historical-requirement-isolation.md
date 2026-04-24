# Beacon Feature Change Document

- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- feature_slug: `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`
- version: `v1.3.8`
- run_id: `run-20260424T104600Z-v138-archive-governance`
- status: `completed`

## Scope
- Implemented the archive support command and governance helpers, then repaired release-gate scoping so v1.3.8 closes on current-version archive truth instead of cross-version drift.

## Added
- none

## Removed / Reduced
- none

## Fixed
- Updated `beacon/cli_factory.py`
- Updated `beacon/command_catalog.py`
- Updated `beacon/commands/archive.py`
- Updated `beacon/commands/gate.py`
- Updated `beacon/commands/qa.py`
- Updated `beacon/commands/release.py`
- Updated `beacon/utils/archive_governance.py`
- Updated `beacon/utils/intent_router.py`
- Updated `skills/beacon/beacon-archive/SKILL.md`
- Updated `docs/beacon/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Updated `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Updated `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Updated `docs/beacon/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`
- Updated `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/navigation-map.json`
- Updated `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/route-closure-contract.json`
- Updated `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/state-flow-map.json`
- Updated `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/page-specs/runtime-center.json`
- Updated `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/pages/runtime-center.md`
- Updated `tests/test_v138_archive_command.py`
- Updated `tests/test_gate_delivery_execution_artifacts.py`
- Updated `tests/test_v112_implementation_plan_runtime.py`
- Updated `tests/test_v131_cognitive_load_gates.py`

## Implementation Impact
- Changed file: `beacon/cli_factory.py`
- Changed file: `beacon/command_catalog.py`
- Changed file: `beacon/commands/archive.py`
- Changed file: `beacon/commands/gate.py`
- Changed file: `beacon/commands/qa.py`
- Changed file: `beacon/commands/release.py`
- Changed file: `beacon/utils/archive_governance.py`
- Changed file: `beacon/utils/intent_router.py`
- Changed file: `skills/beacon/beacon-archive/SKILL.md`
- Changed file: `docs/beacon/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Changed file: `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Changed file: `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md`
- Changed file: `docs/beacon/v1.3.8/research/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-analysis.md`
- Changed file: `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/navigation-map.json`
- Changed file: `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/route-closure-contract.json`
- Changed file: `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/state-flow-map.json`
- Changed file: `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/page-specs/runtime-center.json`
- Changed file: `docs/beacon/v1.3.8/prototype/beacon-v1-3-8-archive-governance-and-historical-requirement-isolation/pages/runtime-center.md`
- Changed file: `tests/test_v138_archive_command.py`
- Changed file: `tests/test_gate_delivery_execution_artifacts.py`
- Changed file: `tests/test_v112_implementation_plan_runtime.py`
- Changed file: `tests/test_v131_cognitive_load_gates.py`
- Module touched: `beacon/cli_factory.py`
- Module touched: `beacon/command_catalog.py`
- Module touched: `beacon/commands`
- Module touched: `beacon/utils`
- Module touched: `docs/beacon`
- Module touched: `skills/beacon`
- Module touched: `tests/test_gate_delivery_execution_artifacts.py`
- Module touched: `tests/test_v112_implementation_plan_runtime.py`
- Module touched: `tests/test_v131_cognitive_load_gates.py`
- Module touched: `tests/test_v138_archive_command.py`

## Verification Status
- passed: python3 -m pytest -q tests/test_v138_archive_command.py
- passed: python3 -m pytest -q tests/test_gate_delivery_execution_artifacts.py -k 'support_implementation_plan_marker'
- passed: python3 -m pytest -q tests/test_v112_implementation_plan_runtime.py -k 'cross_version_qa_status_and_fallback_to_current_revision'
- passed: python3 -m pytest -q tests/test_v131_cognitive_load_gates.py -k 'cross_version_qa_status_and_use_current_revision_feature'

## Traceability Refs
- `docs/beacon/v1.3.8/.machine/execution/implementation-summary-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.json`
- `docs/beacon/v1.3.8/.machine/execution/technical-implementation-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.json`
- `.beacon/implement/run-20260424T104600Z-v138-archive-governance/request.json`
- `.beacon/implement/run-20260424T104600Z-v138-archive-governance/result.json`
