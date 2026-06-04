# Deep Test Delta

- schema_version: `1.0`
- feature: `qa-evo-deep-and-skill-eval-kit-v1410`
- feature_slug: `qa-evo-deep-and-skill-eval-kit-v1410`
- version: `v1.4.10`
- generated_at: `2026-05-23T09:00:22.151664+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
  "user_story": "docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
  "test_case": "docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
    "scenario": "Cover cross_surface_consistency_chain across explicit state/fact-source boundaries",
    "source_family": "cross_surface_consistency_chain",
    "state_axes": [
      "qa_deep_output_status",
      "qa_round_memory_role",
      "skill_eval_case_state",
      "regression_core_status",
      "authority_boundary"
    ],
    "existing_case_refs": [
      "TC-QAED-001",
      "TC-QAED-002",
      "TC-QAED-003",
      "TC-QAED-004",
      "TC-QAED-005",
      "TC-SKEV-001",
      "TC-SKEV-002",
      "TC-SKEV-003"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
    "state_axes": [
      "qa_deep_output_status",
      "qa_round_memory_role",
      "skill_eval_case_state",
      "regression_core_status",
      "authority_boundary"
    ],
    "existing_case_refs": [
      "TC-QAED-001",
      "TC-QAED-002",
      "TC-QAED-003",
      "TC-QAED-004",
      "TC-QAED-005",
      "TC-SKEV-001",
      "TC-SKEV-002",
      "TC-SKEV-003"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
    "delta_id": "DTD-003",
    "scenario": "Cover release_blocking_risk across explicit state/fact-source boundaries",
    "source_family": "release_blocking_risk",
    "state_axes": [
      "qa_deep_output_status",
      "qa_round_memory_role",
      "skill_eval_case_state",
      "regression_core_status",
      "authority_boundary"
    ],
    "existing_case_refs": [
      "TC-QAED-001",
      "TC-QAED-002",
      "TC-QAED-003",
      "TC-QAED-004",
      "TC-QAED-005",
      "TC-SKEV-001",
      "TC-SKEV-002",
      "TC-SKEV-003"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
    "delta_id": "DTD-004",
    "scenario": "Cover state_machine_workflow across explicit state/fact-source boundaries",
    "source_family": "state_machine_workflow",
    "state_axes": [
      "qa_deep_output_status",
      "qa_round_memory_role",
      "skill_eval_case_state",
      "regression_core_status",
      "authority_boundary"
    ],
    "existing_case_refs": [
      "TC-QAED-001",
      "TC-QAED-002",
      "TC-QAED-003",
      "TC-QAED-004",
      "TC-QAED-005",
      "TC-SKEV-001",
      "TC-SKEV-002",
      "TC-SKEV-003"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
