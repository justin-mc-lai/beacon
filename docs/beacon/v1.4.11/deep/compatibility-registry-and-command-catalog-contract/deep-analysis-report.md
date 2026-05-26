# Deep Analysis Report

- schema_version: `1.0`
- feature: `compatibility-registry-and-command-catalog-contract`
- feature_slug: `compatibility-registry-and-command-catalog-contract`
- version: `v1.4.11`
- generated_at: `2026-05-26T11:48:36.585328+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.11/prd/compatibility-registry-and-command-catalog-contract.md",
  "user_story": "docs/beacon/v1.4.11/user-story/compatibility-registry-and-command-catalog-contract.md",
  "test_case": "docs/beacon/v1.4.11/qa/test-cases/compatibility-registry-and-command-catalog-contract.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `compatibility-registry-and-command-catalog-contract`
## trigger
```json
{
  "status": "required",
  "deep_requirement_state": "required",
  "required": true,
  "recommended": false,
  "skipped": false,
  "skip_reason": "low-risk governance slice: compatibility registry and command catalog read-model only; no runtime behavior retirement; QA acceptance and regression evidence already passed",
  "triggers": [
    {
      "token": "migration",
      "category": "migration_or_cutover_flow"
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
    "docs/beacon/v1.4.11/prd/compatibility-registry-and-command-catalog-contract.md",
    "docs/beacon/v1.4.11/user-story/compatibility-registry-and-command-catalog-contract.md",
    "docs/beacon/v1.4.11/qa/test-cases/compatibility-registry-and-command-catalog-contract.md"
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
