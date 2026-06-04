# Risk Register

- schema_version: `1.0`
- feature: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
- feature_slug: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
- version: `v1.4.8`
- generated_at: `2026-05-21T11:51:46.252490+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md",
  "user_story": "docs/beacon/archive/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md",
  "test_case": "docs/beacon/archive/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `risk_register`
## findings
```json
[
  {
    "finding_id": "DF-001",
    "classification": "migration_or_cutover_flow",
    "severity": "P3",
    "release_blocking": false,
    "state": "closed",
    "route_decision": {
      "route": "test-case delta",
      "target_surface": "test-case",
      "next_route": "beacon test-case"
    },
    "closure_decision": "closed",
    "backlog_decision": "",
    "summary": "migration_or_cutover_flow reviewed by deep loop",
    "source": "migration",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/archive/v1.4.8/prd/markdown-first-freeze-truth-and-minimal-machine-state-contract.md",
        "docs/beacon/archive/v1.4.8/user-story/markdown-first-freeze-truth-and-minimal-machine-state-contract.md",
        "docs/beacon/archive/v1.4.8/qa/test-cases/markdown-first-freeze-truth-and-minimal-machine-state-contract.md"
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

- orphan_finding_count: `0`
