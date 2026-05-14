# Test Cases: beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces

## Overview

**Feature**: `beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces`  
**Version**: `v1.4.7`  
**Status**: `freeze-ready`

## First-Slice Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-META47-001 | contract | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "beacon_main_skill_is_meta_protocol_not_wrapper_sprawl"` | `skills/beacon/SKILL.md` acts as a compact meta-protocol centered on decision-surface classification, stable rules, and route-back boundaries |
| AC-002 | TC-META47-002 | contract | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "using_beacon_is_host_route_constitution"` | `using-beacon` explicitly separates truth, execution, verification, gate, and support routing and explains `change` escalation when support output changes accepted scope |
| AC-003 | TC-META47-003 | contract | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "first_wave_horizontal_support_skills_are_defined"` | Beacon defines first-wave support skills for context engineering, source-driven work, and doubt-driven review |
| AC-004 | TC-META47-004 | contract | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "horizontal_support_skills_remain_non_truth_non_gate_non_stage"` | new horizontal support skills are explicitly non-truth, non-gate, and non-stage surfaces and route back to canonical truth or delivery surfaces on drift |
| AC-005 | TC-META47-005 | docs | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "lightweight_reference_package_is_present_and_marked_non_canonical"` | first-wave lightweight references exist and are clearly presented as supporting human-readable materials rather than canonical truth |
| AC-006 | TC-META47-006 | docs | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "external_lifecycle_mapping_is_documented_without_mainline_expansion"` | Beacon documents how `agent-skills` and `gstack` lifecycle models map into Beacon without changing the main chain |
| AC-007 | TC-META47-007 | regression | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "support_surface_specialist_packaging_does_not_turn_into_command_sprawl"` | specialist packaging becomes clearer without exploding Beacon into a flat public command catalog |
| AC-008 | TC-META47-008 | docs | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "host_and_browser_tooling_story_is_more_readable_but_not_a_new_stage"` | host portability and browser/session/tooling support become more operator-readable without becoming new lifecycle stages or default prerequisites |
| AC-009 | TC-META47-009 | integration | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "route_explainability_distinguishes_truth_from_learning_hints"` | route explanations distinguish frozen truth from advisory learning hints and preserve support/advisory boundaries |
| AC-010 | TC-META47-010 | boundary | `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py -k "root_preservation_rules_hold_under_v147_surface_expansion"` | v1.4.7 preserves compact main chain, canonical truth, fail-closed QA/release, non-stage support surfaces, and philosophy-first skill design |

## First-Slice Coverage Notes

- The first slice is intentionally narrower than the full research backlog.
- It validates the entry contract, the host route contract, the first-wave support skill family, and the lightweight reference layer before broader support-surface expansion.
- Later waves may add:
  - `beacon-security-review`
  - `beacon-performance-review`
  - `beacon-documentation-adr`
  - `beacon-debug-recovery`
  but those are outside first-slice acceptance closure unless promoted by a later `change`.

## QA Execution Snapshot

- QA date: `2026-05-14`
- Verified command:
  - `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py tests/test_v131_host_skill_pack.py tests/test_v141_deep_skill_surface.py tests/test_v139_friction_intake.py tests/test_skill_standard_layout.py`
- Result:
  - `39 passed`
- QA verdict:
  - `pass_for_planning_line`

## Next-Slice Planned Coverage

The extended verification wave now covers:

- `beacon-security-review`
- `beacon-performance-review`
- `beacon-documentation-adr`
- `beacon-debug-recovery`
- `research-closure-checklist.md`
- `business-flow-checklist.md`
- `state-machine-checklist.md`

Those checks remain support-surface and lightweight-reference focused rather than runtime-promotion focused.

## Extended QA Execution Snapshot

- QA date: `2026-05-14`
- Verified command:
  - `python3 -m pytest -q tests/test_v147_meta_protocol_and_support_surfaces.py tests/test_v131_host_skill_pack.py tests/test_v141_deep_skill_surface.py tests/test_v139_friction_intake.py tests/test_skill_standard_layout.py`
- Result:
  - `42 passed`
- QA verdict:
  - `pass_for_planning_line`
