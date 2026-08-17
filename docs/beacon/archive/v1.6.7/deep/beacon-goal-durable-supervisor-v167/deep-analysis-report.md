# Deep Analysis Report

- schema_version: `1.0`
- feature: `beacon-goal-durable-supervisor-v167`
- feature_slug: `beacon-goal-durable-supervisor-v167`
- version: `v1.6.7`
- generated_at: `2026-07-18T03:06:30.123553+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md",
  "user_story": "docs/beacon/archive/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md",
  "test_case": "docs/beacon/archive/v1.6.7/qa/test-cases/beacon-goal-durable-supervisor-v167.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_analysis_report`
- intent_snapshot: `Durable product-goal supervisor opt-in, heartbeat, resume-pack, tick execute; release human gate`
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
  "lineage_mode": "source_bound",
  "source_truth_refs": [
    "docs/beacon/archive/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md",
    "docs/beacon/archive/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md",
    "docs/beacon/archive/v1.6.7/qa/test-cases/beacon-goal-durable-supervisor-v167.md"
  ],
  "candidate_parent_refs": [],
  "route_target": "deep",
  "truth_impact": "none",
  "promotion_required": false,
  "canonical": false,
  "gate_trust": "canonical_only",
  "blocking": false
}
```

- status: `closed`
