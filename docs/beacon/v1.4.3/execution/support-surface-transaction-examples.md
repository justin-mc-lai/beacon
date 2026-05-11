# Beacon Support Surface Transaction Examples

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`

## Example 1: `beacon-ceo-review`

```json
{
  "schema_version": "1.0",
  "transaction_id": "tx-beacon-ceo-review-v1.4.3-001",
  "surface": "beacon-ceo-review",
  "mode": "full",
  "version": "v1.4.3",
  "feature": "beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface",
  "status": "accepted_for_writeback",
  "decision": "reframe",
  "reason_codes": [],
  "truth_refs": [
    "docs/beacon/v1.4.3/prd/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md",
    "docs/beacon/v1.4.3/user-story/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md",
    "docs/beacon/v1.4.3/qa/test-cases/beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface.md"
  ],
  "evidence_refs": [
    "docs/analysis/beacon-v1.4.0-human-surface-and-subskill-benchmark-vs-gstack.md"
  ],
  "route_decision": {
    "route": "change/refreeze",
    "target_surface": "beacon-change"
  },
  "next_route": {
    "command": "beacon change \"v1.4.3\"",
    "why": "Requirement framing must be revised before implementation planning remains valid.",
    "target_surface": "beacon-change",
    "priority": "high",
    "prerequisites": [
      "accepted ceo-review decision"
    ]
  },
  "writeback_targets": [
    "beacon-change",
    "beacon-prd"
  ],
  "blocked": false,
  "blocked_reason": "",
  "operator_visible_summary": "Current package is coherent but aimed at the wrong framing layer. Reframe before freezing implementation details.",
  "created_at": "2026-05-11T00:00:00Z"
}
```

## Example 2: `beacon-design-review`

```json
{
  "schema_version": "1.0",
  "transaction_id": "tx-beacon-design-review-v1.4.3-001",
  "surface": "beacon-design-review",
  "mode": "interaction",
  "version": "v1.4.3",
  "feature": "beacon-v1.4.3-design-review-surface-and-prototype-governance",
  "status": "accepted_for_writeback",
  "decision": "ready_for_prototype",
  "reason_codes": [],
  "truth_refs": [
    "docs/beacon/v1.4.3/prd/beacon-v1.4.3-design-review-surface-and-prototype-governance.md"
  ],
  "evidence_refs": [
    "docs/beacon/v1.4.3/execution/beacon-design-review-command-contract.md"
  ],
  "route_decision": {
    "route": "prototype-entry",
    "target_surface": "beacon-prototype"
  },
  "next_route": {
    "command": "beacon prototype \"beacon-v1.4.3-design-review-surface-and-prototype-governance\"",
    "why": "A real UI handoff exists and design-review cleared the feature for formal prototype freeze.",
    "target_surface": "beacon-prototype",
    "priority": "medium",
    "prerequisites": [
      "design_verdict=ready_for_prototype"
    ]
  },
  "writeback_targets": [
    "beacon-prototype"
  ],
  "blocked": false,
  "blocked_reason": "",
  "operator_visible_summary": "Hierarchy and state model are coherent enough to enter formal prototype freeze.",
  "created_at": "2026-05-11T00:00:00Z"
}
```

## Example 3: `beacon-learn`

```json
{
  "schema_version": "1.0",
  "transaction_id": "tx-beacon-learn-v1.4.3-001",
  "surface": "beacon-learn",
  "mode": "audit",
  "version": "v1.4.3",
  "feature": "beacon-v1.4.3-governed-learning-recall-and-route-explainability",
  "status": "advisory",
  "decision": "audit",
  "reason_codes": [
    "learning_conflict_requires_operator_resolution"
  ],
  "truth_refs": [
    "docs/beacon/v1.4.3/prd/beacon-v1.4.3-governed-learning-recall-and-route-explainability.md"
  ],
  "evidence_refs": [
    "docs/beacon/v1.4.3/execution/beacon-learn-command-contract.md"
  ],
  "route_decision": {
    "route": "operator-guidance",
    "target_surface": "beacon-help"
  },
  "next_route": {
    "command": "beacon help",
    "why": "Learning conflicts with current route assumptions and needs operator-visible guidance.",
    "target_surface": "beacon-help",
    "priority": "medium",
    "prerequisites": [
      "conflicting learning detected"
    ]
  },
  "writeback_targets": [
    "learning audit log",
    "route explanation output"
  ],
  "blocked": false,
  "blocked_reason": "",
  "operator_visible_summary": "Two prior learnings conflict; route guidance should disclose both before the next requirement decision.",
  "created_at": "2026-05-11T00:00:00Z"
}
```

## Example 4: Blocked Result

```json
{
  "schema_version": "1.0",
  "transaction_id": "tx-beacon-design-review-v1.4.3-002",
  "surface": "beacon-design-review",
  "mode": "full",
  "version": "v1.4.3",
  "feature": "beacon-v1.4.3-design-review-surface-and-prototype-governance",
  "status": "blocked",
  "decision": "needs_design_revision",
  "reason_codes": [
    "ux_evidence_missing",
    "state_model_missing"
  ],
  "truth_refs": [],
  "evidence_refs": [],
  "route_decision": {
    "route": "support-recovery",
    "target_surface": "beacon-help"
  },
  "next_route": {
    "command": "beacon help",
    "why": "No valid design evidence package exists, so Beacon must route to explicit recovery guidance.",
    "target_surface": "beacon-help",
    "priority": "high",
    "prerequisites": []
  },
  "writeback_targets": [],
  "blocked": true,
  "blocked_reason": "ux_evidence_missing",
  "operator_visible_summary": "Design review cannot proceed because the UI evidence package is missing.",
  "created_at": "2026-05-11T00:00:00Z"
}
```
