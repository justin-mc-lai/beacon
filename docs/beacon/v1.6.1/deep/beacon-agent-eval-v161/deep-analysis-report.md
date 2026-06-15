# Deep Analysis Report

- schema_version: `1.0`
- feature: `beacon-agent-eval-v161`
- feature_slug: `beacon-agent-eval-v161`
- version: `v1.6.1`
- generated_at: `2026-06-15T11:33:26.413412+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.6.1/prd/beacon-agent-eval-v161.md",
  "user_story": "docs/beacon/v1.6.1/user-story/beacon-agent-eval-v161.md",
  "test_case": "docs/beacon/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `release closure for agent eval v1.6.1`
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
    "docs/beacon/v1.6.1/prd/beacon-agent-eval-v161.md",
    "docs/beacon/v1.6.1/user-story/beacon-agent-eval-v161.md",
    "docs/beacon/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md"
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
  "route_target": "deep",
  "truth_impact": "none",
  "promotion_required": false,
  "canonical": false,
  "gate_trust": "canonical_only",
  "blocking": false
}
```

- status: `closed`
