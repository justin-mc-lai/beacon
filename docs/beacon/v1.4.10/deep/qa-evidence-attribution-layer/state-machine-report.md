# State Machine Report

- schema_version: `1.0`
- feature: `qa-evidence-attribution-layer`
- feature_slug: `qa-evidence-attribution-layer`
- version: `v1.4.10`
- generated_at: `2026-05-25T11:46:28.999338+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/qa-evidence-attribution-layer.md",
  "user_story": "docs/beacon/v1.4.10/user-story/qa-evidence-attribution-layer.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/qa-evidence-attribution-layer.md"
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
  "required": true,
  "ready": true,
  "diagram_types": [
    "branch-flow",
    "state-machine",
    "decision-priority"
  ],
  "state_axes": [
    "qa_evidence_state",
    "failure_family_state",
    "route_recommendation_state",
    "authority_boundary",
    "skill_evolution_proposal_state",
    "release_consumption_state"
  ],
  "missing_diagram_types": [],
  "missing_state_axes": false,
  "complexity_signals": [
    "branch-flow",
    "state-machine",
    "decision-priority",
    "state axes"
  ],
  "review_gates": [
    "implementation must cover the declared branch-flow split points",
    "implementation must preserve the declared state-machine transitions",
    "implementation must preserve decision-priority ordering",
    "implementation must keep state axes explicit: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state"
  ],
  "qa_coverage_hints": [
    "cover primary and alternate branch-flow paths",
    "cover state transitions, illegal transitions, and recovery paths",
    "cover conflicting conditions using declared decision priority",
    "cover axis combinations across: qa_evidence_state, failure_family_state, route_recommendation_state, authority_boundary, skill_evolution_proposal_state, release_consumption_state"
  ],
  "evidence_lines": {
    "branch-flow": [
      "- `branch-flow`"
    ],
    "state-machine": [
      "- `state-machine`"
    ],
    "decision-priority": [
      "- `decision-priority`"
    ],
    "state-axes": [
      "- `qa_evidence_state`",
      "- `failure_family_state`",
      "- `route_recommendation_state`",
      "- `authority_boundary`",
      "- `skill_evolution_proposal_state`",
      "- `release_consumption_state`"
    ]
  },
  "generated_at": "2026-05-25T11:46:28.998750+00:00",
  "feature": "qa-evidence-attribution-layer",
  "feature_slug": "qa-evidence-attribution-layer",
  "prd_ref": "docs/beacon/v1.4.10/prd/qa-evidence-attribution-layer.md",
  "user_story_ref": "docs/beacon/v1.4.10/user-story/qa-evidence-attribution-layer.md"
}
```

## state_axes
```json
[
  "qa_evidence_state",
  "failure_family_state",
  "route_recommendation_state",
  "authority_boundary",
  "skill_evolution_proposal_state",
  "release_consumption_state"
]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
