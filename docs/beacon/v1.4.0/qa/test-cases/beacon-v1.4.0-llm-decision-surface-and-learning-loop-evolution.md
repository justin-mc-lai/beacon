# Test Cases: beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution

## Overview

**Feature**: beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution
**Test Type**: ALL
**Version**: v1.4.0
**Generated**: 2026-05-08 16:10
**Status**: `freeze-ready`
**Requested Mode**: auto
**Effective Mode**: requirement-freeze
**Fallback Reason**: implementation-and-machine-matrix-not-yet-materialized
**Memory Context**: v1.4.0 llm decision surface + governed ask + learning disclosure + diagram semantic reasoning + python dual-read
**Primary Truth**: docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md
**Upstream User Story**: docs/beacon/v1.4.0/user-story/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md
**Global Boundary Truth**: docs/beacon/global-boundaries.md
**AC Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.ac-test-matrix.json
**QA9 Matrix JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.qa9-matrix.json
**Story Scenario Map JSON**: docs/beacon/v1.4.0/.machine/qa/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.story-scenario-map.json
**Prototype Plan Present**: True
**Prototype Coverage Present**: True
**Prototype Navigation Contract**: True
**Prototype Interaction Contract**: True

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_v140_llm_skill_surface.py -k "core_skills_are_in_scope" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the six core skills are all covered by one thickening governance surface | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-001.json` |
| AC-002 | TC-002 | contract | `python3 -m pytest -q tests/test_v140_llm_skill_surface.py -k "stable_sections_present" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | each core skill exposes Inputs Contract, Decision Protocol, Anti-Inertia Notes, Learning Notes, and Backstop CLI | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-002.json` |
| AC-003 | TC-003 | integration | `python3 -m pytest -q tests/test_v140_llm_skill_surface.py -k "host_readable_contract" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the thickened skill surface can be consumed by the host without relying on hidden code-only fallback | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-003.json` |
| AC-004 | TC-004 | regression | `python3 -m pytest -q tests/test_v140_llm_skill_surface.py -k "skill_surface_cannot_write_truth" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | thickened skill surfaces do not become freeform frozen-truth write surfaces | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-004.json` |
| AC-101 | TC-005 | contract | `python3 -m pytest -q tests/test_v140_ask_governance.py -k "ask_is_real_public_surface" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Beacon formally treats `beacon ask` as an existing public route surface rather than a proposed future command | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-005.json` |
| AC-102 | TC-006 | regression | `python3 -m pytest -q tests/test_v140_ask_governance.py -k "ask_plan_only_default" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon ask` continues to default to plan-only mode | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-006.json` |
| AC-103 | TC-007 | integration | `python3 -m pytest -q tests/test_v140_ask_governance.py -k "ask_execute_is_bounded" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `ask --execute` can only route into existing legal Beacon surfaces and cannot bypass implement, qa, or gate | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-007.json` |
| AC-104 | TC-008 | regression | `python3 -m pytest -q tests/test_v140_ask_governance.py -k "ask_cannot_freeform_writeback" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `ask` cannot directly write frozen truth, gate verdict, or release state | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-008.json` |
| AC-201 | TC-009 | contract | `python3 -m pytest -q tests/test_v140_route_role_split.py -k "ask_role_is_route_preview_execute" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `ask` is classified as natural-language entry, route preview, and controlled execution surface | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-009.json` |
| AC-202 | TC-010 | contract | `python3 -m pytest -q tests/test_v140_route_role_split.py -k "brainstorm_is_read_only_convergence" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `brainstorm` is classified as read-only convergence, contradiction check, and route suggestion surface | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-010.json` |
| AC-203 | TC-011 | integration | `python3 -m pytest -q tests/test_v140_route_role_split.py -k "frozen_truth_changes_route_to_change" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | frozen-truth change requests route to the change loop instead of remaining in ask or brainstorm | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-011.json` |
| AC-204 | TC-012 | regression | `python3 -m pytest -q tests/test_v140_route_role_split.py -k "no_new_stage_confusion" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ask, brainstorm, and change are not presented as replacements for the seven-stage main lifecycle | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-012.json` |
| AC-301 | TC-013 | contract | `python3 -m pytest -q tests/test_v140_learning_disclosure.py -k "reuse_existing_learning_kernel" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | learning disclosure reuses the existing typed learning contract kernel rather than inventing a parallel system | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-013.json` |
| AC-302 | TC-014 | integration | `python3 -m pytest -q tests/test_v140_learning_disclosure.py -k "progressive_disclosure_order" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | learning hints can be disclosed in feature, host, runner, then domain order | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-014.json` |
| AC-303 | TC-015 | regression | `python3 -m pytest -q tests/test_v140_learning_disclosure.py -k "learning_is_hint_not_truth" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | learning hints influence routing or explanation but cannot define truth, gate verdict, or release-ready | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-015.json` |
| AC-304 | TC-016 | regression | `python3 -m pytest -q tests/test_v140_learning_disclosure.py -k "stale_and_superseded_learning_downgrade" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | stale or superseded learning notes downgrade cleanly instead of continuing to steer decisions as fresh evidence | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-016.json` |
| AC-401 | TC-017 | contract | `python3 -m pytest -q tests/test_v140_requirement_reasoning.py -k "diagram_trigger_blocks_template_fill" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | when diagram-truth complexity is present, requirement generation cannot fall back to shallow template fill | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-017.json` |
| AC-402 | TC-018 | integration | `python3 -m pytest -q tests/test_v140_requirement_reasoning.py -k "state_transition_reasoning_required" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | prd, user-story, and test-case generation explicitly reason about states, transitions, exceptional paths, and invariants | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-018.json` |
| AC-403 | TC-019 | integration | `python3 -m pytest -q tests/test_v140_requirement_reasoning.py -k "state_axis_is_reused_when_present" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | state-axis information is detected and reused when the problem exposes a stable state ladder | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-019.json` |
| AC-404 | TC-020 | regression | `python3 -m pytest -q tests/test_v140_requirement_reasoning.py -k "output_stays_consistent_with_diagram_truth" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | requirement outputs remain consistent with existing diagram truth artifacts | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-020.json` |
| AC-501 | TC-021 | contract | `python3 -m pytest -q tests/test_v140_semantic_requirement_alignment.py -k "semantic_trace_is_shared_input" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | semantic trace is treated as a shared input for requirement generation and validation | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-021.json` |
| AC-502 | TC-022 | integration | `python3 -m pytest -q tests/test_v140_semantic_requirement_alignment.py -k "official_vocabulary_is_reused" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | official state, action, module, and page terms are preferred over ad hoc wording | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-022.json` |
| AC-503 | TC-023 | regression | `python3 -m pytest -q tests/test_v140_semantic_requirement_alignment.py -k "semantic_trace_is_not_second_truth" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | semantic trace can validate wording but does not become a second truth root | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-023.json` |
| AC-504 | TC-024 | integration | `python3 -m pytest -q tests/test_v140_semantic_requirement_alignment.py -k "wording_drift_is_reduced" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | requirement wording drift against semantic trace is surfaced and reduced | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-024.json` |
| AC-601 | TC-025 | contract | `python3 -m pytest -q tests/test_v140_modeling_upgrade_strategy.py -k "reuse_diagram_and_semantic_first" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the first-stage modeling upgrade explicitly reuses diagram truth and semantic dictionary before adding new structures | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-025.json` |
| AC-602 | TC-026 | contract | `python3 -m pytest -q tests/test_v140_modeling_upgrade_strategy.py -k "minimal_extension_only" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | any addition of events, invariants, or entities remains minimal and justified by gaps in existing modeling | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-026.json` |
| AC-603 | TC-027 | regression | `python3 -m pytest -q tests/test_v140_modeling_upgrade_strategy.py -k "no_forced_business_model_five_folders" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature does not require a full new five-folder business-model truth structure as an entry condition | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-027.json` |
| AC-604 | TC-028 | integration | `python3 -m pytest -q tests/test_v140_modeling_upgrade_strategy.py -k "governance_before_expansion" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | governance closes around existing modeling before heavier structural expansion is allowed | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-028.json` |
| AC-701 | TC-029 | contract | `python3 -m pytest -q tests/test_v140_python_guardrail_split.py -k "python_four_duties_only" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Python responsibility converges on fact read, schema validation, contract write, and gate verdict write | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-029.json` |
| AC-702 | TC-030 | integration | `python3 -m pytest -q tests/test_v140_python_guardrail_split.py -k "explanation_moves_to_skill_surface" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | explanatory and decision-protocol content is promoted into skill surfaces instead of remaining hidden in Python fallback | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-030.json` |
| AC-703 | TC-031 | regression | `python3 -m pytest -q tests/test_v140_python_guardrail_split.py -k "python_remains_fail_closed_guardrail" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Python still enforces fail-closed behavior after explanation logic is migrated upward | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-031.json` |
| AC-704 | TC-032 | regression | `python3 -m pytest -q tests/test_v140_python_guardrail_split.py -k "not_a_language_migration_project" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature does not drift into a language-migration objective | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-032.json` |
| AC-801 | TC-033 | contract | `python3 -m pytest -q tests/test_v140_python_slimming_scope.py -k "four_heavy_modules_are_covered" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | qa, implement, prd, and release all enter the same slimming-governance scope | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-033.json` |
| AC-802 | TC-034 | contract | `python3 -m pytest -q tests/test_v140_python_slimming_scope.py -k "read_write_vs_judgment_classification" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | each target module separates fact-write logic from explanation-judgment logic | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-034.json` |
| AC-803 | TC-035 | integration | `python3 -m pytest -q tests/test_v140_python_slimming_scope.py -k "judgment_logic_migrates_first" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | migration prioritizes explanation and judgment logic before touching guardrail write paths | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-035.json` |
| AC-804 | TC-036 | regression | `python3 -m pytest -q tests/test_v140_python_slimming_scope.py -k "shared_governance_view_across_modules" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | all four modules share one slimming-governance standard rather than diverging into local heuristics | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-036.json` |
| AC-901 | TC-037 | contract | `python3 -m pytest -q tests/test_v140_dual_read_cutover.py -k "dual_read_required_before_cutover" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | no decision cutover occurs before dual-read comparison is available | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-037.json` |
| AC-902 | TC-038 | integration | `python3 -m pytest -q tests/test_v140_dual_read_cutover.py -k "reason_and_gate_consistency_checked" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | blocked reason, downgrade path, fallback path, and gate verdict consistency are all checked during dual-read | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-038.json` |
| AC-903 | TC-039 | regression | `python3 -m pytest -q tests/test_v140_dual_read_cutover.py -k "inconsistent_cutover_fails_closed" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | cutover remains blocked when dual-read consistency is insufficient | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-039.json` |
| AC-904 | TC-040 | regression | `python3 -m pytest -q tests/test_v140_dual_read_cutover.py -k "compatibility_window_retains_legacy_fallback" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | a compatibility window preserves legacy fallback even after primary cutover | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-040.json` |
| AC-1001 | TC-041 | contract | `python3 -m pytest -q tests/test_v140_skill_version_alignment.py -k "no_mixed_old_version_lines" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | core skills no longer present mixed v1.3.9, v1.3.12, and v1.4.0 storytelling drift | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-041.json` |
| AC-1002 | TC-042 | integration | `python3 -m pytest -q tests/test_v140_skill_version_alignment.py -k "operator_rule_matches_runtime_and_docs" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | operator-rule text matches the current runtime and docs reality | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-042.json` |
| AC-1003 | TC-043 | integration | `python3 -m pytest -q tests/test_v140_skill_version_alignment.py -k "runtime_docs_host_lines_are_consistent" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime, docs, and host-native version lines are internally consistent | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-043.json` |
| AC-1004 | TC-044 | regression | `python3 -m pytest -q tests/test_v140_skill_version_alignment.py -k "version_alignment_precedes_surface_thickening" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | version-surface alignment occurs before or alongside thickening rather than after it | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-044.json` |
| AC-1101 | TC-045 | integration | `python3 -m pytest -q tests/test_v140_support_route_explainability.py -k "route_reason_is_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | help, status, doctor, and ask can explain why a route is recommended | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-045.json` |
| AC-1102 | TC-046 | integration | `python3 -m pytest -q tests/test_v140_support_route_explainability.py -k "learning_hint_usage_is_visible" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | human-facing recommendation can indicate whether learning hints were used | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-046.json` |
| AC-1103 | TC-047 | integration | `python3 -m pytest -q tests/test_v140_support_route_explainability.py -k "brainstorm_vs_change_reasoning_is_clear" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the system can clearly explain when brainstorm is appropriate and when change is mandatory | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-047.json` |
| AC-1104 | TC-048 | regression | `python3 -m pytest -q tests/test_v140_support_route_explainability.py -k "action_reason_precedes_command_dump" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | default support output prioritizes action rationale over raw command dumping | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-048.json` |
| AC-1201 | TC-049 | contract | `python3 -m pytest -q tests/test_v140_prototype_handoff_contract.py -k "prototype_stage_is_conditionally_required_before_implement" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature formally treats prototype as a conditionally triggered stage before implement because a real UX/UI handoff surface exists | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-049.json` |
| AC-1202 | TC-050 | contract | `python3 -m pytest -q tests/test_v140_prototype_handoff_contract.py -k "route_surface_is_frozen_in_prototype_scope" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | prototype scope covers decision-surface route presentation for core skills and ask/brainstorm/change | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-050.json` |
| AC-1203 | TC-051 | integration | `python3 -m pytest -q tests/test_v140_prototype_handoff_contract.py -k "state_navigation_and_interaction_contracts_are_required" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | prototype handoff requires state visibility, navigation contract, and interaction contract | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-051.json` |
| AC-1204 | TC-052 | regression | `python3 -m pytest -q tests/test_v140_prototype_handoff_contract.py -k "cannot_claim_implement_ready_before_prototype_freeze" --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | the feature cannot be described as implement-ready before prototype freeze artifacts exist | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-052.json` |
| AC-1301 | TC-053 | contract | `python3 -m pytest -q tests/test_v13010_requirement_package_gates.py -k "human_docs_still_block"` | requirement gate still blocks when frozen human requirement truth is incomplete | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-053.json` |
| AC-1302 | TC-054 | regression | `python3 -m pytest -q tests/test_v13010_requirement_package_gates.py -k "missing_machine_projection_does_not_block"` | missing machine-side requirement projections no longer act as default hard gate blockers | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-054.json` |
| AC-1303 | TC-055 | integration | `python3 -m pytest -q tests/test_v13010_requirement_package_gates.py -k "feature_scope_does_not_inherit_sibling_drift"` | feature-level implement/qa gate does not inherit unrelated sibling feature drift from the same version line | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-055.json` |
| AC-1304 | TC-056 | regression | `python3 -m pytest -q tests/test_v13010_requirement_package_gates.py -k "freeze_receipt_drift_still_blocks"` | baseline hash / revision receipt drift remains a fail-closed blocker even after machine projection slimming | `.beacon/evidence/test-results/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution/TC-056.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-101 |
| TC-006 | Pending | from AC-102 |
| TC-007 | Pending | from AC-103 |
| TC-008 | Pending | from AC-104 |
| TC-009 | Pending | from AC-201 |
| TC-010 | Pending | from AC-202 |
| TC-011 | Pending | from AC-203 |
| TC-012 | Pending | from AC-204 |
| TC-013 | Pending | from AC-301 |
| TC-014 | Pending | from AC-302 |
| TC-015 | Pending | from AC-303 |
| TC-016 | Pending | from AC-304 |
| TC-017 | Pending | from AC-401 |
| TC-018 | Pending | from AC-402 |
| TC-019 | Pending | from AC-403 |
| TC-020 | Pending | from AC-404 |
| TC-021 | Pending | from AC-501 |
| TC-022 | Pending | from AC-502 |
| TC-023 | Pending | from AC-503 |
| TC-024 | Pending | from AC-504 |
| TC-025 | Pending | from AC-601 |
| TC-026 | Pending | from AC-602 |
| TC-027 | Pending | from AC-603 |
| TC-028 | Pending | from AC-604 |
| TC-029 | Pending | from AC-701 |
| TC-030 | Pending | from AC-702 |
| TC-031 | Pending | from AC-703 |
| TC-032 | Pending | from AC-704 |
| TC-033 | Pending | from AC-801 |
| TC-034 | Pending | from AC-802 |
| TC-035 | Pending | from AC-803 |
| TC-036 | Pending | from AC-804 |
| TC-037 | Pending | from AC-901 |
| TC-038 | Pending | from AC-902 |
| TC-039 | Pending | from AC-903 |
| TC-040 | Pending | from AC-904 |
| TC-041 | Pending | from AC-1001 |
| TC-042 | Pending | from AC-1002 |
| TC-043 | Pending | from AC-1003 |
| TC-044 | Pending | from AC-1004 |
| TC-045 | Pending | from AC-1101 |
| TC-046 | Pending | from AC-1102 |
| TC-047 | Pending | from AC-1103 |
| TC-048 | Pending | from AC-1104 |
| TC-049 | Pending | from AC-1201 |
| TC-050 | Pending | from AC-1202 |
| TC-051 | Pending | from AC-1203 |
| TC-052 | Pending | from AC-1204 |
| TC-053 | Pending | from AC-1301 |
| TC-054 | Pending | from AC-1302 |
| TC-055 | Pending | from AC-1303 |
| TC-056 | Pending | from AC-1304 |

---

## Freeze Gate Notes

- 当前 test-case 包把本特性的高风险点都编译成了正式验收对象，而不是停留在“方向正确”的抽象口号：
  - skill surface 厚化必须可验证
  - `ask --execute` 必须有边界阻断
  - learning 必须可降级且不能变成第二真相
  - requirement 深度思考必须消费 diagram 与 semantic 输入
  - Python 迁移必须 dual-read 后切主
  - skill version surface 必须先校准
  - support surface 必须能解释 route 推荐原因
  - prototype handoff 已冻结 route/state/navigation/interaction contract
- 当前文档声明的是 coverage freeze，不代表实现已完成，也不代表自动化测试已存在并执行通过。
- 如果后续实现无法同时满足以下约束，则本 feature 不应通过 gate：
  - `docs/beacon/<version>/**/*.md` 仍为唯一 frozen truth root
  - `implement` 仍为唯一实现入口
  - `qa` 仍为唯一验收入口
  - `gate` 仍是最终阻断与完成判定器
  - learning、semantic、support explainability 都不能反向越权为 truth 或 gate

## Diagram Truth

- `branch-flow`
  - 覆盖 `user prompt -> ask -> route preview / controlled execute -> skill surface -> python guardrail -> gate`
  - 覆盖 `diagram / semantic inputs -> requirement reasoning -> prd / user-story / test-case`
  - 覆盖 `learning hint -> progressive disclosure -> next run adjustment`
- `decision-priority`
  - `truth > compiled contract > gate verdict > skill decision surface > legacy python heuristics`
  - `reuse existing capability > invent new command > invent new truth system`
  - `fail-closed cutover > optimistic migration`
