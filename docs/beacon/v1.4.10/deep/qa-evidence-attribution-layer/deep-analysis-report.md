# Deep Analysis Report

- schema_version: `1.0`
- feature: `qa-evidence-attribution-layer`
- feature_slug: `qa-evidence-attribution-layer`
- version: `v1.4.10`
- generated_at: `2026-05-25T11:46:28.999338+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/qa-evidence-attribution-layer.md",
  "user_story": "docs/beacon/v1.4.10/user-story/qa-evidence-attribution-layer.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `qa-evidence-attribution-layer`
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
      "token": "score",
      "category": "ranking_or_scoring_flow"
    },
    {
      "token": "attribution",
      "category": "identity_or_attribution_binding"
    }
  ],
  "reason_code": "deep_high_risk_trigger_detected",
  "qa_structural_reopen": false
}
```

- finding_count: `2`
- test_delta_count: `2`
## lineage_projection
```json
{
  "lineage_mode": "machine_inferred",
  "source_truth_refs": [
    "docs/beacon/v1.4.10/prd/qa-evidence-attribution-layer.md",
    "docs/beacon/v1.4.10/user-story/qa-evidence-attribution-layer.md",
    "docs/beacon/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md"
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
      "ref_type": "TC",
      "ref_id": "TC-QA-ATTR-001",
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
