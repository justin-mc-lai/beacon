# Deep Analysis Report

- schema_version: `1.0`
- feature: `explicit-version-canonical-branch-worktree-preflight-gate`
- feature_slug: `explicit-version-canonical-branch-worktree-preflight-gate`
- version: `v1.4.10`
- generated_at: `2026-05-25T06:56:05.993511+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "user_story": "docs/beacon/archive/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "test_case": "docs/beacon/archive/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `explicit-version-canonical-branch-worktree-preflight-gate`
## trigger
```json
{
  "status": "required",
  "deep_requirement_state": "required",
  "required": true,
  "recommended": false,
  "skipped": false,
  "skip_reason": "",
  "triggers": [
    {
      "token": "order",
      "category": "order_or_transaction_flow"
    }
  ],
  "reason_code": "deep_high_risk_trigger_detected",
  "qa_structural_reopen": false
}
```

- finding_count: `1`
- test_delta_count: `1`
## lineage_projection
```json
{
  "lineage_mode": "machine_inferred",
  "source_truth_refs": [
    "docs/beacon/archive/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
    "docs/beacon/archive/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md",
    "docs/beacon/archive/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md"
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
  "route_target": "deep",
  "truth_impact": "none",
  "promotion_required": false,
  "canonical": false,
  "gate_trust": "canonical_only",
  "blocking": false
}
```

- status: `closed`
