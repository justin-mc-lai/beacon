# Deep Analysis Report

- schema_version: `1.0`
- feature: `authority-vocabulary-and-baseline-inventory-contract`
- feature_slug: `authority-vocabulary-and-baseline-inventory-contract`
- version: `v1.4.11`
- generated_at: `2026-05-26T11:18:32.526601+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md",
  "user_story": "docs/beacon/archive/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md",
  "test_case": "docs/beacon/archive/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `authority-vocabulary-and-baseline-inventory-contract`
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
    "docs/beacon/archive/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md",
    "docs/beacon/archive/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md",
    "docs/beacon/archive/v1.4.11/qa/test-cases/authority-vocabulary-and-baseline-inventory-contract.md"
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
