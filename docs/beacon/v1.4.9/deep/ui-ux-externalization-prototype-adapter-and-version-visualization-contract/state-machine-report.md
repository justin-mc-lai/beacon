# State Machine Report

- schema_version: `1.0`
- feature: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- feature_slug: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- version: `v1.4.9`
- generated_at: `2026-05-22T06:42:55.481841+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
  "user_story": "docs/beacon/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
  "test_case": "docs/beacon/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md"
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
  "version": "v1.4.9",
  "supported": true,
  "required": true,
  "ready": true,
  "diagram_types": [
    "branch-flow",
    "state-machine",
    "decision-priority"
  ],
  "state_axes": [
    "ui_ux_route",
    "adapter_binding",
    "requirement_visualization",
    "truth_binding"
  ],
  "missing_diagram_types": [],
  "missing_state_axes": false,
  "complexity_signals": [
    "branch-flow",
    "state-machine",
    "decision-priority",
    "state axes",
    "ownership",
    "state machine",
    "decision priority"
  ],
  "review_gates": [
    "implementation must cover the declared branch-flow split points",
    "implementation must preserve the declared state-machine transitions",
    "implementation must preserve decision-priority ordering",
    "implementation must keep state axes explicit: ui_ux_route, adapter_binding, requirement_visualization, truth_binding"
  ],
  "qa_coverage_hints": [
    "cover primary and alternate branch-flow paths",
    "cover state transitions, illegal transitions, and recovery paths",
    "cover conflicting conditions using declared decision priority",
    "cover axis combinations across: ui_ux_route, adapter_binding, requirement_visualization, truth_binding"
  ],
  "evidence_lines": {
    "branch-flow": [
      "- `branch-flow`"
    ],
    "state-machine": [
      "- `docs/beacon/v1.4.8/research/beacon-vnext-business-flow-and-state-machine-document-design.md`",
      "3. Beacon 对整版需求的人类可读 projection 仍不足，缺少 business flow、state-machine 和三件套映射图。",
      "6. 冻结版本级 state-machine projection。",
      "business flow、state-machine 和 three-piece map 只做可读投影，不替代 PRD、user-story、test-case。",
      "- state-machine projection contract",
      "state-machine projection 必须只解释 stable closure states，不解释页面 widget 交互状态。",
      "每个 business flow、state-machine、three-piece map 至少必须声明：",
      "D --> J[Business flow / state-machine / map projection]"
    ],
    "decision-priority": [
      "1. `ui-ux-dev` owns UI/UX execution.",
      "2. Beacon owns requirement truth and gates.",
      "3. Accepted design result must be bound before implementation.",
      "4. Projection without truth bindings is invalid.",
      "5. Historical compatibility must not override v1.4.9 ownership.",
      "- `decision-priority`"
    ],
    "state-axes": [
      "- `ui_ux_route`",
      "- `adapter_binding`",
      "- `requirement_visualization`",
      "- `truth_binding`",
      "- State axes must not be silently compressed into one implicit status field."
    ]
  },
  "generated_at": "2026-05-22T06:42:55.481209+00:00",
  "feature": "ui-ux-externalization-prototype-adapter-and-version-visualization-contract",
  "feature_slug": "ui-ux-externalization-prototype-adapter-and-version-visualization-contract",
  "prd_ref": "docs/beacon/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md",
  "user_story_ref": "docs/beacon/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md"
}
```

## state_axes
```json
[
  "ui_ux_route",
  "adapter_binding",
  "requirement_visualization",
  "truth_binding"
]
```

- state_machine_contract: `state axes stay explicit through implementation, QA, and release evidence`
