# Test Cases: beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning

## Overview

**Feature**: `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`  
**Version**: `v1.4.5`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-GUIDE45-001 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "guidance_family_members_are_frozen"` | guidance surface family contains `ceo-review`, `brainstorm`, `design-review`, and `deep` |
| AC-002 | TC-GUIDE45-002 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "guidance_surfaces_are_non_truth_non_gate"` | guidance surfaces are explicitly non-truth and non-gate |
| AC-003 | TC-GUIDE45-003 | docs | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "shared_decision_loop_is_documented"` | shared loop `define -> challenge -> freeze -> execute -> verify -> learn` is documented |
| AC-004 | TC-GUIDE45-004 | docs | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "software_lifecycle_is_materialization"` | software lifecycle is documented as one materialization of the shared loop |
| AC-005 | TC-GUIDE45-005 | integration | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "non_software_scenarios_route_through_guidance"` | non-software scenarios can route through guidance surfaces |
| AC-006 | TC-GUIDE45-006 | regression | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "route_explainability_is_consistent"` | route explainability remains consistent across guidance surfaces |
| AC-007 | TC-GUIDE45-007 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "skill_philosophy_is_strategy_tool_fact_first"` | guidance-family skills prioritize strategy philosophy, minimum complete tools, and necessary factual grounding |
| AC-008 | TC-GUIDE45-008 | contract | `python3 -m pytest -q tests/test_v145_guidance_family.py -k "route_explainability_ac_should_not_be_classified_as_ui or qa9_generation_should_not_widen_to_functional"` | support-surface requirement semantics stay in deterministic non-browser QA mapping unless UI/browser interaction is explicit |
