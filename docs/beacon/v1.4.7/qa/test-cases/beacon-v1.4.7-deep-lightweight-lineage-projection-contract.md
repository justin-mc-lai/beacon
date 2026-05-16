# Test Cases: beacon-v1.4.7-deep-lightweight-lineage-projection-contract

## Overview

**Feature**: `beacon-v1.4.7-deep-lightweight-lineage-projection-contract`
**Version**: `v1.4.7`
**Status**: `freeze-ready`

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion |
| --- | --- | --- | --- | --- |
| AC-001 | TC-DL47-001 | contract | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "deep_artifacts_expose_lineage_projection"` | deep artifacts expose lineage mode, source truth refs, candidate parent refs, route target, truth impact, and promotion flag |
| AC-002 | TC-DL47-002 | contract | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "source_bound_lineage_accepts_file_level_refs"` | L0 source-bound lineage is valid with file-level PRD/user-story/test-case refs only |
| AC-003 | TC-DL47-003 | contract | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "machine_inferred_refs_are_marked_non_canonical"` | L1 inferred parent refs include confidence and `inferred=true` |
| AC-004 | TC-DL47-004 | boundary | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "missing_inferred_parent_ids_do_not_block_deep"` | missing exact US/AC/TC refs does not block deep findings, risks, or deltas |
| AC-005 | TC-DL47-005 | integration | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "adoption_required_mode_is_set_for_current_closure_impacts"` | closure supplements, test-case deltas, acceptance deltas, and requirement meaning deltas set L2 adoption-required |
| AC-006 | TC-DL47-006 | routing | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "adoption_routes_to_truth_surface_for_trace_strengthening"` | L2 adoption routes to test-case or change/refreeze instead of writing canonical trace from deep |
| AC-007 | TC-DL47-007 | gate | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "canonical_promoted_trace_only_comes_from_truth_surfaces"` | L3 canonical trace is emitted only by PRD/user-story/test-case truth surfaces |
| AC-008 | TC-DL47-008 | gate | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "qa_release_do_not_trust_l0_l1_as_closure_truth"` | QA and release gates do not treat L0/L1 lineage as canonical closure truth |
| AC-009 | TC-DL47-009 | regression | `python3 -m pytest -q tests/test_v147_deep_lightweight_lineage_projection.py -k "lineage_projection_preserves_deep_support_boundary"` | lineage projection does not make deep a truth source, gate source, or new lifecycle stage |

## Required Scenario Families

1. L0 source-bound finding
2. L1 machine-inferred candidate refs
3. Missing candidate parent refs
4. L2 adoption-required test delta
5. Requirement meaning delta routes to change/refreeze
6. Canonical L3 trace only after truth-surface promotion
7. QA/release gate rejects L0/L1 as closure truth

## Boundary and Negative Coverage

- deep must not require manual US/AC/TC maintenance during discovery
- deep must not write canonical trace
- inferred lineage must not be release-grade evidence
- route pressure must not become a new lifecycle stage

## QA Verification Note

This document defines coverage truth for the implemented package. The executable matrix is backed by `tests/test_v147_deep_lightweight_lineage_projection.py`.
