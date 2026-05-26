# State Machine Report

- schema_version: `1.0`
- feature: `qa-browser-memory-and-skill-evolution-advisory-loop`
- feature_slug: `qa-browser-memory-and-skill-evolution-advisory-loop`
- version: `v1.4.10`
- generated_at: `2026-05-25T23:13:49.388662+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md",
  "user_story": "docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md"
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
  "version": "v1.4.10",
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
  "generated_at": "2026-05-25T23:13:49.388100+00:00",
  "feature": "qa-browser-memory-and-skill-evolution-advisory-loop",
  "feature_slug": "qa-browser-memory-and-skill-evolution-advisory-loop",
  "prd_ref": "docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md",
  "user_story_ref": "docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
