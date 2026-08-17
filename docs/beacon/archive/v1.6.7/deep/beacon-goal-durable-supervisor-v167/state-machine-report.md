# State Machine Report

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
- artifact_type: `state_machine_report`
## loop_states
```json
[
  "scan_truth",
  "model_business",
  "challenge_gaps",
  "derive_delta",
  "classify_findings",
  "route_repairs",
  "verify_closure"
]
```

## diagram_truth
```json
{
  "schema_version": "1.0",
  "version": "v1.6.7",
  "supported": true,
  "required": false,
  "ready": true,
  "diagram_types": [],
  "state_axes": [],
  "missing_diagram_types": [],
  "missing_state_axes": false,
  "complexity_signals": [],
  "review_gates": [],
  "qa_coverage_hints": [],
  "evidence_lines": {},
  "generated_at": "2026-07-18T03:06:30.123246+00:00",
  "feature": "beacon-goal-durable-supervisor-v167",
  "feature_slug": "beacon-goal-durable-supervisor-v167",
  "prd_ref": "docs/beacon/archive/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md",
  "user_story_ref": "docs/beacon/archive/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
