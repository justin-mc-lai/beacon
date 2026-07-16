# Deep Test Delta

- schema_version: `1.0`
- feature: `beacon-agent-eval-v161`
- feature_slug: `beacon-agent-eval-v161`
- version: `v1.6.1`
- generated_at: `2026-06-15T11:33:26.413412+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.6.1/prd/beacon-agent-eval-v161.md",
  "user_story": "docs/beacon/archive/v1.6.1/user-story/beacon-agent-eval-v161.md",
  "test_case": "docs/beacon/archive/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md"
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
    "scenario": "Cover ranking_or_scoring_flow across explicit state/fact-source boundaries",
    "source_family": "ranking_or_scoring_flow",
    "state_axes": [],
    "existing_case_refs": [
      "TC-AE-001",
      "TC-AE-002",
      "TC-AE-003",
      "TC-AE-004",
      "TC-AE-005",
      "TC-AE-006",
      "TC-AE-007",
      "TC-AE-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.6.1/prd/beacon-agent-eval-v161.md",
        "docs/beacon/archive/v1.6.1/user-story/beacon-agent-eval-v161.md",
        "docs/beacon/archive/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md"
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
          "ref_id": "AC-018",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "TC",
          "ref_id": "TC-AE-001",
          "confidence": "high",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-AE-001",
          "confidence": "high",
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
