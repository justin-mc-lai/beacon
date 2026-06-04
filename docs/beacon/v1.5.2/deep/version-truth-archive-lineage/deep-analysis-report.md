# Deep Analysis Report

- schema_version: `1.0`
- feature: `version-truth-archive-lineage`
- feature_slug: `version-truth-archive-lineage`
- version: `v1.5.2`
- generated_at: `2026-06-04T02:56:29.223491+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.5.2/prd/version-truth-archive-lineage.md",
  "user_story": "docs/beacon/v1.5.2/user-story/version-truth-archive-lineage.md",
  "test_case": "docs/beacon/v1.5.2/qa/test-cases/version-truth-archive-lineage.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `version-truth-archive-lineage`
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
    "docs/beacon/v1.5.2/prd/version-truth-archive-lineage.md",
    "docs/beacon/v1.5.2/user-story/version-truth-archive-lineage.md",
    "docs/beacon/v1.5.2/qa/test-cases/version-truth-archive-lineage.md"
  ],
  "candidate_parent_refs": [
    {
      "ref_type": "TC",
      "ref_id": "TC-001",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "AC",
      "ref_id": "AC-001",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "TC",
      "ref_id": "TC-002",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "AC",
      "ref_id": "AC-002",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "TC",
      "ref_id": "TC-003",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "AC",
      "ref_id": "AC-003",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "TC",
      "ref_id": "TC-004",
      "confidence": "high",
      "inferred": true
    },
    {
      "ref_type": "AC",
      "ref_id": "AC-004",
      "confidence": "high",
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
