# Risk Register

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
    "source": "scoring",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
      ],
      "candidate_parent_refs": [
        {
          "ref_type": "AC",
          "ref_id": "AC-001",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-002",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-003",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-004",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-005",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-006",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-007",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-008",
          "confidence": "medium",
          "inferred": true
        }
      ],
      "route_target": "test-case",
      "truth_impact": "acceptance_delta",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": true
    }
  },
  {
    "finding_id": "DF-002",
    "classification": "state_machine_workflow",
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
    "summary": "state_machine_workflow reviewed by deep loop",
    "source": "state machine",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
      ],
      "candidate_parent_refs": [
        {
          "ref_type": "AC",
          "ref_id": "AC-001",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-002",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-003",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-004",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-005",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-006",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-007",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-008",
          "confidence": "medium",
          "inferred": true
        }
      ],
      "route_target": "test-case",
      "truth_impact": "acceptance_delta",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": true
    }
  },
  {
    "finding_id": "DF-003",
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
    "source": "consistency",
    "lineage": {
      "lineage_mode": "adoption_required",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
      ],
      "candidate_parent_refs": [
        {
          "ref_type": "AC",
          "ref_id": "AC-001",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-002",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-003",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-004",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-005",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-006",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-007",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-008",
          "confidence": "medium",
          "inferred": true
        }
      ],
      "route_target": "test-case",
      "truth_impact": "acceptance_delta",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": true
    }
  },
  {
    "finding_id": "DF-004",
    "classification": "release_blocking_risk",
    "severity": "P3",
    "release_blocking": true,
    "state": "closed",
    "route_decision": {
      "route": "release closure, waiver, or backlog decision",
      "target_surface": "release",
      "next_route": "beacon release"
    },
    "closure_decision": "closed",
    "backlog_decision": "",
    "summary": "release_blocking_risk reviewed by deep loop",
    "source": "release-blocking",
    "lineage": {
      "lineage_mode": "machine_inferred",
      "source_truth_refs": [
        "docs/beacon/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md",
        "docs/beacon/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md"
      ],
      "candidate_parent_refs": [
        {
          "ref_type": "AC",
          "ref_id": "AC-001",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-002",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-003",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-004",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-005",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-006",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-007",
          "confidence": "medium",
          "inferred": true
        },
        {
          "ref_type": "AC",
          "ref_id": "AC-008",
          "confidence": "medium",
          "inferred": true
        }
      ],
      "route_target": "release",
      "truth_impact": "none",
      "promotion_required": false,
      "canonical": false,
      "gate_trust": "canonical_only",
      "blocking": false
    }
  }
]
```

- orphan_finding_count: `0`
