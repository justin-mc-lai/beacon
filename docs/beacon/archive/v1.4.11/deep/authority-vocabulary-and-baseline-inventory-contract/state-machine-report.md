# State Machine Report

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
  "required": true,
  "ready": true,
  "diagram_types": [
    "branch-flow",
    "state-machine",
    "decision-priority"
  ],
  "state_axes": [
    "authority_role",
    "compat_surface",
    "inventory_status"
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
    "implementation must keep state axes explicit: authority_role, compat_surface, inventory_status"
  ],
  "qa_coverage_hints": [
    "cover primary and alternate branch-flow paths",
    "cover state transitions, illegal transitions, and recovery paths",
    "cover conflicting conditions using declared decision priority",
    "cover axis combinations across: authority_role, compat_surface, inventory_status"
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
      "- `authority_role`",
      "- `compat_surface`",
      "- `inventory_status`"
    ]
  },
  "generated_at": "2026-05-26T11:18:32.526051+00:00",
  "feature": "authority-vocabulary-and-baseline-inventory-contract",
  "feature_slug": "authority-vocabulary-and-baseline-inventory-contract",
  "prd_ref": "docs/beacon/archive/v1.4.11/prd/authority-vocabulary-and-baseline-inventory-contract.md",
  "user_story_ref": "docs/beacon/archive/v1.4.11/user-story/authority-vocabulary-and-baseline-inventory-contract.md"
}
```

## state_axes
```json
[
  "authority_role",
  "compat_surface",
  "inventory_status"
]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
