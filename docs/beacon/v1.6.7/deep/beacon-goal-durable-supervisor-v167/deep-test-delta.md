# Deep Test Delta

- schema_version: `1.0`
- feature: `beacon-goal-durable-supervisor-v167`
- feature_slug: `beacon-goal-durable-supervisor-v167`
- version: `v1.6.7`
- generated_at: `2026-07-18T03:06:30.123553+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md",
  "user_story": "docs/beacon/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md",
  "test_case": "docs/beacon/v1.6.7/qa/test-cases/beacon-goal-durable-supervisor-v167.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- lineage_policy: `trace-on-promotion; L0/L1 are non-canonical support projections, L2 requires truth-surface adoption, L3 belongs to PRD/user-story/test-case`
- artifact_type: `deep_test_delta`
- qa_execution_owner: `qa`
- deep_execution_boundary: `deep derives deltas but does not execute QA`
## deltas
```json
[
  {
    "delta_id": "DTD-001",
    "scenario": "Cover ranking_or_scoring_flow across explicit state/fact-source boundaries",
    "source_family": "ranking_or_scoring_flow",
    "state_axes": [],
    "existing_case_refs": [],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.6.7/prd/beacon-goal-durable-supervisor-v167.md",
        "docs/beacon/v1.6.7/user-story/beacon-goal-durable-supervisor-v167.md",
        "docs/beacon/v1.6.7/qa/test-cases/beacon-goal-durable-supervisor-v167.md"
      ],
      "candidate_parent_refs": [],
      "route_target": "test-case",
      "truth_impact": "acceptance_delta",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": true
    }
  }
]
```
