# State Machine Report

- schema_version: `1.0`
- feature: `implement-mode-frozen-truth-requirement-contract`
- feature_slug: `implement-mode-frozen-truth-requirement-contract`
- version: `v1.4.11`
- generated_at: `2026-05-29T13:17:06.841207+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md",
  "user_story": "docs/beacon/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md",
  "test_case": "docs/beacon/v1.4.11/qa/test-cases/implement-mode-frozen-truth-requirement-contract.md"
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
    "mode_selection",
    "simple",
    "team",
    "ralph",
    "truth_injection",
    "requirement_truth_only",
    "project_truth_present",
    "project_truth_absent",
    "ac_verification",
    "not_reported",
    "pass",
    "partial",
    "blocked",
    "design_alignment",
    "not_applicable",
    "aligned",
    "relation"
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
    "implementation must keep state axes explicit: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation"
  ],
  "qa_coverage_hints": [
    "cover primary and alternate branch-flow paths",
    "cover state transitions, illegal transitions, and recovery paths",
    "cover conflicting conditions using declared decision priority",
    "cover axis combinations across: mode_selection, simple, team, ralph, truth_injection, requirement_truth_only, project_truth_present, project_truth_absent, ac_verification, not_reported, pass, partial, blocked, design_alignment, not_applicable, aligned, relation"
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
      "| Axis | States | Meaning |",
      "| --- | --- | --- |",
      "| `mode_selection` | `simple`, `team`, `ralph` | Implement mode selection remains existing behavior. |",
      "| `truth_injection` | `requirement_truth_only`, `project_truth_present`, `project_truth_absent` | Whether project truth files are injected in addition to frozen requirement truth. |",
      "| `ac_verification` | `not_reported`, `pass`, `partial`, `blocked` | AC-level implementation self-verification status. |",
      "| `design_alignment` | `not_applicable`, `aligned`, `partial`, `blocked` | Implementation relationship to project design truth. |",
      "- `mode_selection`",
      "- `truth_injection`"
    ]
  },
  "generated_at": "2026-05-29T13:17:06.840619+00:00",
  "feature": "implement-mode-frozen-truth-requirement-contract",
  "feature_slug": "implement-mode-frozen-truth-requirement-contract",
  "prd_ref": "docs/beacon/v1.4.11/prd/implement-mode-frozen-truth-requirement-contract.md",
  "user_story_ref": "docs/beacon/v1.4.11/user-story/implement-mode-frozen-truth-requirement-contract.md"
}
```

## state_axes
```json
[
  "mode_selection",
  "simple",
  "team",
  "ralph",
  "truth_injection",
  "requirement_truth_only",
  "project_truth_present",
  "project_truth_absent",
  "ac_verification",
  "not_reported",
  "pass",
  "partial",
  "blocked",
  "design_alignment",
  "not_applicable",
  "aligned",
  "relation"
]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
