# State Machine Report

- schema_version: `1.0`
- feature: `qa-evo-deep-and-skill-eval-kit-v1410`
- feature_slug: `qa-evo-deep-and-skill-eval-kit-v1410`
- version: `v1.4.10`
- generated_at: `2026-05-23T09:00:22.151664+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
  "user_story": "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
  "test_case": "docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
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
    "qa_deep_output_status",
    "qa_round_memory_role",
    "skill_eval_case_state",
    "regression_core_status",
    "authority_boundary"
  ],
  "missing_diagram_types": [],
  "missing_state_axes": false,
  "complexity_signals": [
    "branch-flow",
    "state-machine",
    "decision-priority",
    "state axes",
    "state machine"
  ],
  "review_gates": [
    "implementation must cover the declared branch-flow split points",
    "implementation must preserve the declared state-machine transitions",
    "implementation must preserve decision-priority ordering",
    "implementation must keep state axes explicit: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary"
  ],
  "qa_coverage_hints": [
    "cover primary and alternate branch-flow paths",
    "cover state transitions, illegal transitions, and recovery paths",
    "cover conflicting conditions using declared decision priority",
    "cover axis combinations across: qa_deep_output_status, qa_round_memory_role, skill_eval_case_state, regression_core_status, authority_boundary"
  ],
  "evidence_lines": {
    "branch-flow": [
      "- `branch-flow`"
    ],
    "state-machine": [
      "- AC-003: Cover state-machine, business-flow, scenario-combination, permission, data-consistency, and cross-surface closure findings.",
      "| FR-003 | AC-003 | QA evo-deep must support finding families for state machine, business flow, scenario combination, permission boundary, data-source consistency, cross-surface closure, and repeated failure. |",
      "- `state-machine`",
      "| AC-003 | deep coverage taxonomy | QA evo-deep supports state-machine, business-flow, scenario-combination, permission-boundary, data-source-consistency, cross-surface-closure, and repeated-failure finding families. |"
    ],
    "decision-priority": [
      "- `decision-priority`"
    ],
    "state-axes": [
      "- `qa_deep_output_status`",
      "- `qa_round_memory_role`",
      "- `skill_eval_case_state`",
      "- `regression_core_status`",
      "- `authority_boundary`"
    ]
  },
  "generated_at": "2026-05-23T09:00:22.150958+00:00",
  "feature": "qa-evo-deep-and-skill-eval-kit-v1410",
  "feature_slug": "qa-evo-deep-and-skill-eval-kit-v1410",
  "prd_ref": "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
  "user_story_ref": "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md"
}
```

## state_axes
```json
[
  "qa_deep_output_status",
  "qa_round_memory_role",
  "skill_eval_case_state",
  "regression_core_status",
  "authority_boundary"
]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
