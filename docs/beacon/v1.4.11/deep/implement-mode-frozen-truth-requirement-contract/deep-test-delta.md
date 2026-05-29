# Deep Test Delta

- schema_version: `1.0`
- feature: `implement-mode-frozen-truth-requirement-contract`
- feature_slug: `implement-mode-frozen-truth-requirement-contract`
- version: `v1.4.11`
- generated_at: `2026-05-29T13:17:06.841207+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md",
  "user_story": "docs/beacon/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md",
  "test_case": "docs/beacon/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md"
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
      "mode_selection",
      "simple",
      "team",
      "ralph",
      "truth_injection",
      "requirement_truth_only",
      "project_truth_present",
      "project_truth_absent"
    ],
    "existing_case_refs": [
      "TC-IMPL-TRUTH-001",
      "TC-IMPL-TRUTH-002",
      "TC-IMPL-TRUTH-003",
      "TC-IMPL-TRUTH-004",
      "TC-IMPL-TRUTH-005",
      "TC-IMPL-TRUTH-006",
      "TC-IMPL-TRUTH-007",
      "TC-IMPL-TRUTH-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md",
        "docs/beacon/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md",
        "docs/beacon/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md"
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
