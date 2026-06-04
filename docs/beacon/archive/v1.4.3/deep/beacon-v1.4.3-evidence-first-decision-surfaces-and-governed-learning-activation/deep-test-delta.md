# Deep Test Delta

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
- artifact_type: `deep_test_delta`
- qa_execution_owner: `qa`
- deep_execution_boundary: `deep derives deltas but does not execute QA`
## deltas
```json
[
  {
    "delta_id": "DTD-001",
    "scenario": "Cover cross_surface_consistency_chain across explicit state/fact-source boundaries",
    "source_family": "cross_surface_consistency_chain",
    "state_axes": [
      "requirement_governance_state",
      "unreviewed -> ceo_challenged -> truth_routed -> freeze_ready",
      "design_governance_state",
      "undifferentiated -> design_reviewed -> prototype_condition_decided -> handoff_ready",
      "learning_governance_state",
      "latent -> recalled -> disclosed -> audited -> pruned_or_retained",
      "support_explainability_state",
      "implicit -> visible -> route_explained -> evidence_first"
    ],
    "existing_case_refs": [
      "TC-US001-001",
      "TC-US002-001",
      "TC-US003-001",
      "TC-US004-001",
      "TC-US005-001",
      "TC-US006-001",
      "TC-US007-001",
      "TC-US008-001"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure"
  },
  {
    "delta_id": "DTD-002",
    "scenario": "Cover ranking_or_scoring_flow across explicit state/fact-source boundaries",
    "source_family": "ranking_or_scoring_flow",
    "state_axes": [
      "requirement_governance_state",
      "unreviewed -> ceo_challenged -> truth_routed -> freeze_ready",
      "design_governance_state",
      "undifferentiated -> design_reviewed -> prototype_condition_decided -> handoff_ready",
      "learning_governance_state",
      "latent -> recalled -> disclosed -> audited -> pruned_or_retained",
      "support_explainability_state",
      "implicit -> visible -> route_explained -> evidence_first"
    ],
    "existing_case_refs": [
      "TC-US001-001",
      "TC-US002-001",
      "TC-US003-001",
      "TC-US004-001",
      "TC-US005-001",
      "TC-US006-001",
      "TC-US007-001",
      "TC-US008-001"
    ],
    "delta_state": "proposed",
    "route_target": "test-case",
    "qa_execution_owner": "qa",
    "execution_status": "not_executed_by_deep",
    "adoption_contract": "adopt through test-case or supplemental QA before claiming QA closure"
  }
]
```
