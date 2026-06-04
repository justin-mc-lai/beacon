# State Machine Report

- schema_version: `1.0`
- feature: `version-aggregate-projection-guard-contract`
- feature_slug: `version-aggregate-projection-guard-contract`
- version: `v1.4.11`
- generated_at: `2026-05-27T03:22:26.365956+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.11/prd/version-aggregate-projection-guard-contract.md",
  "user_story": "docs/beacon/archive/v1.4.11/user-story/version-aggregate-projection-guard-contract.md",
  "test_case": "docs/beacon/archive/v1.4.11/qa/test-cases/version-aggregate-projection-guard-contract.md"
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
  "version": "v1.4.11",
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
  "generated_at": "2026-05-27T03:22:26.365398+00:00",
  "feature": "version-aggregate-projection-guard-contract",
  "feature_slug": "version-aggregate-projection-guard-contract",
  "prd_ref": "docs/beacon/archive/v1.4.11/prd/version-aggregate-projection-guard-contract.md",
  "user_story_ref": "docs/beacon/archive/v1.4.11/user-story/version-aggregate-projection-guard-contract.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
