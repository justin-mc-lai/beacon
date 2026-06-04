# Test Cases: beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract

## Overview

**Feature**: `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
**Version**: `v1.4.8`
**Status**: `frozen`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-MATGATE48-001 | contract | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "execution_host_required_surfaces_are_declared"` | Beacon declares required execution host surfaces for execution-bound features |
| AC-002 | TC-MATGATE48-002 | gate | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "implement_blocks_on_missing_or_drifted_architecture_blueprint_projection"` | `implement` blocks when architecture blueprint projection is missing or drifted |
| AC-003 | TC-MATGATE48-003 | gate | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "delivery_facts_must_be_explicit_not_default_seeded"` | branch / service / worktree facts cannot rely only on default seeds |
| AC-004 | TC-MATGATE48-004 | contract | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "weak_fact_sources_do_not_unlock_implement"` | weak fact sources such as `version_default` or `project_config_seed` do not unlock implementation |
| AC-005 | TC-MATGATE48-005 | contract | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "subskill_material_effect_registry_covers_all_human_surfaces"` | material effect registry covers host, truth, execution, gate, support, toolkit, compatibility, and project-local skills |
| AC-006 | TC-MATGATE48-006 | contract | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "subskill_invocation_must_resolve_to_material_effect"` | every human-facing subskill invocation resolves to one allowed material effect |
| AC-007 | TC-MATGATE48-007 | workflow | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "accepted_support_finding_opens_material_update_or_obligation"` | accepted support finding becomes material update, release blocker, or artifact update obligation |
| AC-008 | TC-MATGATE48-008 | boundary | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "support_surfaces_remain_advisory_until_adopted"` | support surfaces do not become truth sources unless routed through governed adoption |
| AC-009 | TC-MATGATE48-009 | integration | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "branch_governance_updates_canonical_execution_and_metadata_surfaces"` | branch governance writes service / branch / worktree updates through canonical surfaces |
| AC-010 | TC-MATGATE48-010 | gate | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "qa_and_release_block_on_open_artifact_update_obligations"` | QA and release block while blocking artifact update obligations remain open |
| AC-011 | TC-MATGATE48-011 | diagnostics | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "gate_diagnostics_name_missing_material_and_repair_route"` | gate diagnostics name missing material, default-seeded field, unadopted finding, open obligation, and repair route |
| AC-012 | TC-MATGATE48-012 | regression | `python3 -m pytest -q tests/test_v148_material_gate_and_subskill_writeback.py -k "support_and_toolkit_do_not_become_new_lifecycle_stages"` | support and toolkit skills remain outside truth/gate authority and do not create new lifecycle stages |

## Coverage Focus

本 feature 的覆盖必须包括：

- execution host required file / section contract
- architecture blueprint projection drift
- branch / service / worktree explicit fact gate
- weak fact source rejection
- per-subskill material effect registry
- support finding adoption
- branch governance canonical writeback
- artifact update obligation blocking
- no silent pass diagnostics
- lifecycle boundary preservation

## Required Scenario Families

1. execution host material missing blocks implement
2. default-seeded branch / service / worktree facts block implement
3. support finding accepted and converted into material update or obligation
4. support finding not accepted remains read-only route-only
5. branch governance update writes canonical execution and metadata surfaces
6. QA / release block on open obligations
7. diagnostics explain missing material and repair route
8. support / toolkit surfaces do not become lifecycle stages

## Boundary and Negative Coverage

- Beacon must not treat missing material as `not needed`
- Beacon must not treat generated default as approved fact
- Beacon must not treat support report as truth writeback
- Beacon must not treat side dossier as canonical execution host
- Beacon must not treat status-only green signals as release proof

## QA Execution Snapshot

- QA date: `pending`
- Verified command:
  - `pending`
- Result:
  - `pending`
- QA verdict:
  - `pending_implementation`

## Findings

- Requirement package is frozen for implementation planning.
- Runtime tests are not implemented yet.
- Implementation must add the test file and make the AC matrix executable before QA can pass.
