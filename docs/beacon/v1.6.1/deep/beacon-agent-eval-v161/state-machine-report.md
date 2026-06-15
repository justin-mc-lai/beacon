# State Machine Report

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
  "version": "v1.6.1",
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
  "generated_at": "2026-06-15T11:33:26.412317+00:00",
  "feature": "beacon-agent-eval-v161",
  "feature_slug": "beacon-agent-eval-v161",
  "prd_ref": "docs/beacon/v1.6.1/prd/beacon-agent-eval-v161.md",
  "user_story_ref": "docs/beacon/v1.6.1/user-story/beacon-agent-eval-v161.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
