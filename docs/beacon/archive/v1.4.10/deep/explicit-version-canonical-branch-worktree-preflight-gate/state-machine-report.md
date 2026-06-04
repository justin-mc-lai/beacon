# State Machine Report

- schema_version: `1.0`
- feature: `explicit-version-canonical-branch-worktree-preflight-gate`
- feature_slug: `explicit-version-canonical-branch-worktree-preflight-gate`
- version: `v1.4.10`
- generated_at: `2026-05-25T06:56:05.993511+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "user_story": "docs/beacon/archive/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "test_case": "docs/beacon/archive/v1.4.10/qa/test-cases/explicit-version-canonical-branch-worktree-preflight-gate.md"
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
  "generated_at": "2026-05-25T06:56:05.992958+00:00",
  "feature": "explicit-version-canonical-branch-worktree-preflight-gate",
  "feature_slug": "explicit-version-canonical-branch-worktree-preflight-gate",
  "prd_ref": "docs/beacon/archive/v1.4.10/prd/explicit-version-canonical-branch-worktree-preflight-gate.md",
  "user_story_ref": "docs/beacon/archive/v1.4.10/user-story/explicit-version-canonical-branch-worktree-preflight-gate.md"
}
```

## state_axes
```json
[]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
