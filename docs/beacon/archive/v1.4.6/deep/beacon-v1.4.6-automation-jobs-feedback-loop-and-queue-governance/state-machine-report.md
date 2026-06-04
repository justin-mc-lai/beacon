# State Machine Report

- schema_version: `1.0`
- feature: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- feature_slug: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- version: `v1.4.6`
- generated_at: `2026-05-14T07:53:58.523241+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md",
  "user_story": "docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md",
  "test_case": "docs/beacon/archive/v1.4.6/qa/test-cases/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
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
  "version": "v1.4.6",
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
  "generated_at": "2026-05-14T07:53:58.522681+00:00",
  "feature": "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance",
  "feature_slug": "beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance",
  "prd_ref": "docs/beacon/archive/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md",
  "user_story_ref": "docs/beacon/archive/v1.4.6/user-story/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
