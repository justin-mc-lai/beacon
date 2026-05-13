# Test Cases: beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces

## Overview

**Feature**: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`  
**Version**: `v1.4.6`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-ADRIFT46-001 | contract | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "skill_anatomy_v2_is_frozen_for_key_surfaces"` | key host-visible skills freeze `Skill Anatomy v2` with boundary, workflow, rationalization, verification, evidence, state, and gate sections |
| AC-002 | TC-ADRIFT46-002 | contract | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "key_execution_and_entry_skills_require_anti_rationalization"` | `using-beacon`, `beacon-prd`, `beacon-change`, `beacon-brainstorm`, `beacon-implement`, `beacon-qa`, and `beacon-release` all declare anti-rationalization guidance |
| AC-003 | TC-ADRIFT46-003 | contract | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "support_surface_constitution_is_unified_and_bounded"` | `brainstorm`, `deep`, `ceo-review`, `design-review`, `help`, `status`, and `doctor` share one bounded constitution and remain non-truth, non-gate, and non-stage surfaces |
| AC-004 | TC-ADRIFT46-004 | integration | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "high_risk_challenge_outputs_bind_back_to_evidence_state_or_gate"` | challenge-style outputs cannot terminate as free-form commentary and must bind back to route, evidence, state, or gate impact |
| AC-005 | TC-ADRIFT46-005 | docs | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "public_surface_family_has_clear_handoff_boundaries"` | Beacon documents distinct truth, execution, support, and gate surface families with explicit escalation and handoff semantics |
| AC-006 | TC-ADRIFT46-006 | regression | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "anti_drift_contracts_are_machine_checkable"` | missing required contract sections, support-surface overreach, and unbound challenge outputs can be detected automatically |
| AC-007 | TC-ADRIFT46-007 | boundary | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "philosophy_first_contract_does_not_regress_to_step_scripts"` | v1.4.6 preserves philosophy-first skill design and does not regress into prescriptive operation scripts |
| AC-008 | TC-ADRIFT46-008 | boundary | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "external_skill_methods_are_absorbed_without_runtime_dependency"` | external workflow-skill methods are absorbed as internal contract design without creating a runtime dependency |
| AC-009 | TC-ADRIFT46-009 | contract | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "brainstorm_and_change_promotion_boundary_remains_explicit"` | `brainstorm` can sharpen options and framing, but only `change` can promote requirement truth for implementation and QA |
| AC-010 | TC-ADRIFT46-010 | regression | `python3 -m pytest -q tests/test_v146_anti_drift_skill_contracts.py -k "anti_drift_upgrade_does_not_create_a_new_lifecycle_stage"` | the anti-drift upgrade is expressed as stronger host-visible behavior and does not introduce a new lifecycle stage or replace existing truth, evidence, and gate governance |
