# Risk Register

- schema_version: `1.0`
- feature: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
- feature_slug: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
- version: `v1.4.3`
- generated_at: `2026-05-11T11:50:37.027360+00:00`
## source_refs
```json
{
  "prd": "docs/beacon/archive/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md",
  "user_story": "docs/beacon/archive/v1.4.3/user-story/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md",
  "test_case": "docs/beacon/archive/v1.4.3/qa/test-cases/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md"
}
```

- canonical_truth_policy: `read_only_frozen_truth`
- artifact_type: `risk_register`
## findings
```json
[
  {
    "finding_id": "DF-001",
    "classification": "ranking_or_scoring_flow",
    "severity": "P3",
    "release_blocking": false,
    "state": "closed",
    "route_decision": {
      "route": "test-case delta",
      "target_surface": "test-case",
      "next_route": "beacon test-case"
    },
    "closure_decision": "closed",
    "backlog_decision": "",
    "summary": "ranking_or_scoring_flow reviewed by deep loop",
    "source": "score"
  },
  {
    "finding_id": "DF-002",
    "classification": "cross_surface_consistency_chain",
    "severity": "P3",
    "release_blocking": false,
    "state": "closed",
    "route_decision": {
      "route": "test-case delta",
      "target_surface": "test-case",
      "next_route": "beacon test-case"
    },
    "closure_decision": "closed",
    "backlog_decision": "",
    "summary": "cross_surface_consistency_chain reviewed by deep loop",
    "source": "一致性"
  }
]
```

- orphan_finding_count: `0`
