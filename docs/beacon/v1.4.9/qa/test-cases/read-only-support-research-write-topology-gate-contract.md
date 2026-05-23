# Test Cases: Read-Only Support Research Write Topology Gate Contract

**Feature**: `read-only-support-research-write-topology-gate-contract`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-ROSUP-001 | contract | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "ordinary_support_writes_feature_research"` | Ordinary support skills with explicit version+feature upsert their owned section in `docs/beacon/<version>/research/<feature>.md`. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-001.json` |
| AC-002 | TC-ROSUP-002 | contract | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "deep_writes_artifact_family_and_research_index"` | `beacon-deep` writes detailed artifacts under `deep/<feature>/` and research contains only `Deep Summary` index metadata. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-002.json` |
| AC-003 | TC-ROSUP-003 | contract | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "learn_writes_learning_audit_and_research_index"` | `beacon-learn` writes audit data to learning/transaction surfaces and research contains only learning influence summary. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-003.json` |
| AC-004 | TC-ROSUP-004 | gate | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "brainstorm_fallback_disallowed_for_version_feature"` | Explicit version+feature support analysis cannot default to `docs/brainstorms/`; violation blocks with topology diagnostics. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-004.json` |
| AC-005 | TC-ROSUP-005 | contract | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "same_version_clarification_upserts_rounds"` | Repeated clarification in one version updates rounds or supersedes owned sections in the same research file. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-005.json` |
| AC-006 | TC-ROSUP-006 | contract | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "cross_version_clarification_records_lineage"` | Cross-version clarification writes a new version research document with previous research, carried-forward findings, and superseded assumptions. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-006.json` |
| AC-007 | TC-ROSUP-007 | gate | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "topology_gate_reports_expected_and_actual_paths"` | Gate / requirement clarity reports invalid topology with source skill, expected path, actual path, feature, version, and repair route. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-007.json` |
| AC-008 | TC-ROSUP-008 | gate | `python3 -m pytest -q tests/test_v149_read_only_support_topology.py -k "pre_write_gate_blocks_unresolved_support_target"` | Support output is not persisted until the topology gate selects a governed target; unresolved route attempts fail closed without legacy fallback writes. | `.beacon/evidence/test-results/read-only-support-research-write-topology-gate-contract/TC-ROSUP-008.json` |

## Explicit Non Coverage

- These tests do not execute implementation, QA, or release.
- These tests do not promote support findings into canonical truth.
- These tests do not rewrite historical `docs/brainstorms/` files.
