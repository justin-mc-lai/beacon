# Risk Register

- schema_version: `1.0`
- feature: `beacon-truth-map-center-and-package-cutover`
- feature_slug: `beacon-truth-map-center-and-package-cutover`
- version: `v1.5.2`
- generated_at: `2026-06-02T13:26:51.976186+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.5.2/prd/beacon-truth-map-center-and-package-cutover.md",
  "user_story": "docs/beacon/v1.5.2/user-story/beacon-truth-map-center-and-package-cutover.md",
  "test_case": "docs/beacon/v1.5.2/qa/test-cases/beacon-truth-map-center-and-package-cutover.md"
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
    "classification": "ranking_or_scoring_flow",
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
    "summary": "ranking_or_scoring_flow reviewed by deep loop",
    "source": "score",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.5.2/prd/beacon-truth-map-center-and-package-cutover.md",
        "docs/beacon/v1.5.2/user-story/beacon-truth-map-center-and-package-cutover.md",
        "docs/beacon/v1.5.2/qa/test-cases/beacon-truth-map-center-and-package-cutover.md"
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
