# Test Cases: beacon-v1.4.5-governed-external-skill-sources-and-learning-composition

## Overview

**Feature**: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`  
**Version**: `v1.4.5`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-EXT45-001 | contract | `python3 -m pytest -q tests/test_v145_external_skills.py -k "external_sources_are_first_class_capabilities"` | external skill sources are modeled as first-class capability sources |
| AC-002 | TC-EXT45-002 | fixture | `python3 -m pytest -q tests/test_v145_external_skills.py -k "baoyu_skills_is_canonical_sample"` | `core-skills/baoyu-skills` is registered as canonical sample |
| AC-003 | TC-EXT45-003 | integration | `python3 -m pytest -q tests/test_v145_external_skills.py -k "business_goal_without_explicit_chain_is_supported"` | users can declare business goals without predeclaring full chains |
| AC-004 | TC-EXT45-004 | contract | `python3 -m pytest -q tests/test_v145_external_skills.py -k "capability_selection_and_composition_contract_exists"` | capability selection and composition semantics exist |
| AC-005 | TC-EXT45-005 | learning | `python3 -m pytest -q tests/test_v145_external_skills.py -k "success_failure_and_adoption_are_written_back"` | success, failure, fallback, and adoption outcomes are written back |
| AC-006 | TC-EXT45-006 | learning | `python3 -m pytest -q tests/test_v145_external_skills.py -k "task_type_to_chain_to_output_mapping_is_reusable"` | `task-type -> skill-chain -> output-shape` mapping is defined as reusable learning truth |
| AC-007 | TC-EXT45-007 | boundary | `python3 -m pytest -q tests/test_v145_external_skills.py -k "external_source_governance_preserves_boundaries"` | external source governance preserves truth, guidance, and runtime boundaries |
| AC-008 | TC-EXT45-008 | contract | `python3 -m pytest -q tests/test_v145_external_skills.py -k "philosophy_first_admission_preserves_strategy_tool_fact_layers"` | external skill admission preserves strategy philosophy, minimum complete tools, and necessary factual grounding |
