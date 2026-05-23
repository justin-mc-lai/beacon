# Deep Test Delta

- schema_version: `1.0`
- feature: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- feature_slug: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- version: `v1.4.9`
- generated_at: `2026-05-22T06:42:55.481841+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
  "user_story": "docs/beacon/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
  "test_case": "docs/beacon/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md"
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
    "scenario": "Cover state_machine_workflow across explicit state/fact-source boundaries",
    "source_family": "state_machine_workflow",
    "state_axes": [
      "ui_ux_route",
      "adapter_binding",
      "requirement_visualization",
      "truth_binding"
    ],
    "existing_case_refs": [
      "TC-UXEXT-001",
      "TC-UXEXT-002",
      "TC-UXEXT-003",
      "TC-UXEXT-004",
      "TC-UXEXT-005",
      "TC-UXEXT-006",
      "TC-UXEXT-007",
      "TC-UXEXT-008"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
        "docs/beacon/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
        "docs/beacon/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md"
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
