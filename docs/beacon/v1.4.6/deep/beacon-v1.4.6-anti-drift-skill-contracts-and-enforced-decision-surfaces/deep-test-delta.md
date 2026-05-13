# Deep Test Delta

- schema_version: `1.0`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- feature_slug: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- version: `v1.4.6`
- generated_at: `2026-05-13T14:41:24.917901+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md",
  "user_story": "docs/beacon/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md",
  "test_case": "docs/beacon/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- artifact_type: `deep_test_delta`
- qa_execution_owner: `qa`
- deep_execution_boundary: `deep derives deltas but does not execute QA`
## deltas
```json
[
  {
    "delta_id": "DTD-001",
    "scenario": "Cover cross_surface_consistency_chain across explicit state/fact-source boundaries",
    "source_family": "cross_surface_consistency_chain",
    "state_axes": [],
    "existing_case_refs": [
      "TC-ADRIFT46-001",
      "TC-ADRIFT46-002",
      "TC-ADRIFT46-003",
      "TC-ADRIFT46-004",
      "TC-ADRIFT46-005",
      "TC-ADRIFT46-006",
      "TC-ADRIFT46-007",
      "TC-ADRIFT46-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure"
  }
]
```
