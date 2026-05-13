# Test Cases: beacon-v1.4.5-docs-architecture-and-machine-truth-minimization

## Overview

**Feature**: `beacon-v1.4.5-docs-architecture-and-machine-truth-minimization`  
**Version**: `v1.4.5`  
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-DOCS45-001 | contract | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "new_docs_structure_contract_exists"` | `v1.4.5` freezes a new docs structure contract |
| AC-002 | TC-DOCS45-002 | docs | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "software_truth_maps_into_truth_layer"` | software truth surfaces map into `truth/` semantics |
| AC-003 | TC-DOCS45-003 | docs | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "guidance_outputs_do_not_mix_with_truth"` | guidance outputs are routed separately from truth |
| AC-004 | TC-DOCS45-004 | contract | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "delivery_and_evidence_are_separated"` | delivery and evidence layers are separated |
| AC-005 | TC-DOCS45-005 | regression | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "paired_human_machine_projection_not_default"` | paired human/machine artifacts are not defaulted when semantics are duplicated |
| AC-006 | TC-DOCS45-006 | contract | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "machine_layer_is_projection_only"` | `.machine` is treated as a projection layer with optional human companions |
| AC-007 | TC-DOCS45-007 | boundary | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "historical_versions_remain_compatible"` | historical versions remain valid while new versions follow the new contract |
| AC-008 | TC-DOCS45-008 | contract | `python3 -m pytest -q tests/test_v145_docs_architecture.py -k "directories_are_created_progressively"` | new docs structure is created progressively instead of fully materialized up front |
