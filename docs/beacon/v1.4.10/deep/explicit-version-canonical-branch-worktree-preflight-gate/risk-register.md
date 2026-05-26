# Risk Register

- schema_version: `1.0`
- feature: `explicit-version-canonical-branch-worktree-preflight-gate`
- feature_slug: `explicit-version-canonical-branch-worktree-preflight-gate`
- version: `v1.4.10`
- generated_at: `2026-05-25T06:56:05.993511+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "user_story": "docs/beacon/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md"
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
    "classification": "order_or_transaction_flow",
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
    "summary": "order_or_transaction_flow reviewed by deep loop",
    "source": "order",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
        "docs/beacon/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md",
        "docs/beacon/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md"
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
