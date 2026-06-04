# Deep Test Delta

- schema_version: `1.0`
- feature: `authority-vocabulary-and-baseline-inventory-contract`
- feature_slug: `authority-vocabulary-and-baseline-inventory-contract`
- version: `v1.4.11`
- generated_at: `2026-05-26T11:18:32.526601+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md",
  "user_story": "docs/beacon/archive/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md",
  "test_case": "docs/beacon/archive/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_test_delta`
- qa_execution_owner: `qa`
- deep_execution_boundary: `deep derives deltas but does not execute QA`
## deltas
```json
[
  {
    "delta_id": "DTD-001",
    "scenario": "Cover migration_or_cutover_flow across explicit state/fact-source boundaries",
    "source_family": "migration_or_cutover_flow",
    "state_axes": [
      "authority_role",
      "compat_surface",
      "inventory_status"
    ],
    "existing_case_refs": [
      "TC-AUTH-INV-001",
      "TC-AUTH-INV-002",
      "TC-AUTH-INV-003",
      "TC-AUTH-INV-004",
      "TC-AUTH-INV-005",
      "TC-AUTH-INV-006",
      "TC-AUTH-INV-007",
      "TC-AUTH-INV-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md",
        "docs/beacon/archive/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md",
        "docs/beacon/archive/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md"
      ],
      "candidate_parent_refs": [
        {
          "ref_type": "AC",
          "ref_id": "AC-001",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-002",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-003",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-004",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-005",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-006",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-007",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-008",
          "confidence": "medium",
          "inferred": true
        }
      ],
      "route_target": "test-case",
      "truth_impact": "acceptance_delta",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": true
    }
  }
]
```
