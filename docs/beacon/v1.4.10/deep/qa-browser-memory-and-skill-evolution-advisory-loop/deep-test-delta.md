# Deep Test Delta

- schema_version: `1.0`
- feature: `qa-browser-memory-and-skill-evolution-advisory-loop`
- feature_slug: `qa-browser-memory-and-skill-evolution-advisory-loop`
- version: `v1.4.10`
- generated_at: `2026-05-25T23:13:49.388662+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md",
  "user_story": "docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md"
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
    "scenario": "Cover identity_or_attribution_binding across explicit state/fact-source boundaries",
    "source_family": "identity_or_attribution_binding",
    "state_axes": [],
    "existing_case_refs": [
      "TC-QA-MEM-001",
      "TC-QA-MEM-002",
      "TC-QA-MEM-003",
      "TC-QA-MEM-004",
      "TC-QA-MEM-005",
      "TC-QA-MEM-006",
      "TC-QA-MEM-007",
      "TC-QA-MEM-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md",
        "docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md"
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
  },
  {
    "delta_id": "DTD-002",
    "scenario": "Cover ranking_or_scoring_flow across explicit state/fact-source boundaries",
    "source_family": "ranking_or_scoring_flow",
    "state_axes": [],
    "existing_case_refs": [
      "TC-QA-MEM-001",
      "TC-QA-MEM-002",
      "TC-QA-MEM-003",
      "TC-QA-MEM-004",
      "TC-QA-MEM-005",
      "TC-QA-MEM-006",
      "TC-QA-MEM-007",
      "TC-QA-MEM-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md",
        "docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md"
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
