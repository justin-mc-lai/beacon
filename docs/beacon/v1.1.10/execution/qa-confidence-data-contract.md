# Beacon v1.1.10 QA Confidence Data Contract

## Goal

Define the machine contracts that connect:

```text
scenario result
→ AC closure
→ feature release confidence
→ audit truth
→ keep/discard training input
```

---

## 1. `scenario-result-v2`

### Path

Suggested embedding:

- `.beacon/qa/features/<feature>/status.json`
- `.beacon/evidence/auto-test/<run_id>/qa9/tc-results.json`

### Required fields

```json
{
  "scenario_id": "SC-001",
  "tc_id": "TC-001-HAPPY",
  "ac_id": "AC-001",
  "feature_slug": "my-feature",
  "scenario_family": "happy",
  "status": "passed",
  "closure_outcome": "accepted",
  "confidence_raw": 0.84,
  "confidence_calibrated": 0.79,
  "confidence_band": "high",
  "requires_human_review": false,
  "evidence_sufficiency": "strong",
  "root_cause_type": "none",
  "browser_required": true,
  "replay_required": true,
  "replay_present": true,
  "browser_evidence_pack_ref": ".beacon/evidence/.../browser-evidence-pack.json",
  "judge_signals": {
    "exhaustiveness_score": 1.0,
    "evidence_score": 0.9,
    "replay_score": 1.0,
    "trace_score": 0.85,
    "flake_penalty": 0.0
  }
}
```

### Field derivation anchors

`scenario-result-v2` should be treated as an additive extension of the existing v1.1.9 execution output.

Recommended source mapping:

| v1.1.10 field | Primary source | Notes |
| --- | --- | --- |
| `status` | existing `tc_results[].status` / `per_item_results[].status` | execution fact, not release truth |
| `scenario_id` | existing story-scenario-map / scenario execution id | keep stable across audit linkage |
| `tc_id` / `ac_id` | existing QA matrix + story trace | requirement anchor |
| `browser_evidence_pack_ref` | existing browser evidence pack ref | evidence anchor |
| `replay_present` | derived from existing replay ref/presence | replay anchor |
| `closure_outcome` | new v1.1.10 judgement output | closure anchor |
| `confidence_raw` | new scoring output from judge signals | judgement anchor |
| `confidence_calibrated` | new calibration layer output | must not exist without raw score provenance |
| `requires_human_review` | derived from abstain threshold + closure state | operator anchor |

Boundary rule:

> v1.1.10 may add judgement semantics, but it must not erase the underlying execution/evidence facts it is judging.

### Enums

#### `status`
- `passed`
- `failed`
- `blocked`
- `pending`
- `review_required`

#### `closure_outcome`
- `accepted`
- `bug_filed`
- `implementation_reopened`
- `requirement_rewrite_required`
- `runner_issue`
- `flake_quarantined`
- `needs_more_evidence`
- `needs_replay`
- `needs_requirement_clarification`

#### `confidence_band`
- `high`
- `medium`
- `low`

#### `evidence_sufficiency`
- `strong`
- `partial`
- `weak`
- `missing`

#### `root_cause_type`
- `none`
- `spec_gap`
- `implementation_gap`
- `runner_gap`
- `environment_gap`
- `flake`
- `evidence_gap`

---

## 2. `ac-closure-report`

### Path

- `.beacon/qa/features/<feature>/ac-closure.json`

### Required fields

```json
{
  "ac_id": "AC-001",
  "feature_slug": "my-feature",
  "required_scenario_families": ["happy", "negative", "recovery"],
  "passed_scenario_families": ["happy", "negative", "recovery"],
  "required_replay_scenarios": ["SC-001", "SC-002"],
  "missing_replay_scenarios": [],
  "scenario_ids": ["SC-001", "SC-002", "SC-003"],
  "closure_status": "accepted",
  "confidence_min": 0.78,
  "confidence_avg": 0.84,
  "open_outcomes": [],
  "blocking_reasons": []
}
```

### `closure_status`
- `accepted`
- `review_required`
- `blocked`
- `failed`

### Derivation rules

`ac-closure-report` must be computed, not hand-authored.

At minimum it should aggregate:

- scenario family coverage
- replay completeness
- evidence sufficiency
- calibrated confidence floor
- open closure outcomes

---

## 3. `feature-qa-scorecard`

### Path

- `.beacon/qa/features/<feature>/scorecard.json`

### Required fields

```json
{
  "feature": "My Feature",
  "feature_slug": "my-feature",
  "run_id": "run-001",
  "ac_total": 8,
  "ac_accepted": 7,
  "scenario_total": 34,
  "scenario_passed": 30,
  "release_confidence_min": 0.74,
  "release_confidence_avg": 0.86,
  "review_required_count": 2,
  "needs_replay_count": 1,
  "false_complete_risk": 0.18,
  "coverage_current": {
    "required_scenarios": 34,
    "executed_scenarios": 21,
    "coverage_rate": 0.6176,
    "missing_scenario_families": ["recovery", "compatibility"],
    "missing_test_case_ids": ["TC-021", "TC-022"]
  },
  "continue_decision": "stop_for_repair",
  "stop_reasons": ["auth_session_invalid", "required_replay_missing"],
  "test_case_backfill_required": true,
  "resume_command": "beacon help --project-root . --version v1.1.10 --feature \"My Feature\"",
  "release_ready": false
}
```

### Interpretation boundary

`feature-qa-scorecard` is an operator summary artifact.

It is allowed to summarize:

- closure counts
- confidence floor / average
- review counts
- false-complete risk

It is not allowed to invent facts absent from:

- scenario results
- AC closure reports
- audit labels

### Additional round-level fields

`feature-qa-scorecard` should also answer the human control question:

> should the current round continue, stop for repair, or hand off to release review?

Recommended additive fields:

| Field | Meaning |
| --- | --- |
| `coverage_current` | current round's executed vs required coverage snapshot |
| `continue_decision` | `continue` / `stop_for_repair` / `ready_for_release` |
| `stop_reasons` | severe blockers that invalidate further testing in the same round |
| `test_case_backfill_required` | whether the next round must expand matrix/test cases before rerun |
| `resume_command` | human-facing command to resume the next QA round |

#### `continue_decision`
- `continue`
- `stop_for_repair`
- `ready_for_release`

---

## 4. `qa-audit-label`

### Path

- `.beacon/state/qa-audits/<run_id>/<scenario_id>.json`

### Required fields

```json
{
  "scenario_id": "SC-001",
  "feature_slug": "my-feature",
  "label": "false_pass",
  "auditor": "human-review",
  "reason": "replay missing but scenario auto-accepted",
  "evidence_refs": [
    ".beacon/evidence/.../browser-evidence-pack.json"
  ]
}
```

### `label`
- `true_pass`
- `false_pass`
- `true_block`
- `false_block`
- `spec_gap`
- `runner_gap`
- `flake`

### Truth rule

`qa-audit-label` outranks automatic judgement for benchmark construction.

If an audit label disagrees with the automatic result, the corpus should record the disagreement rather than mutating history.

---

## 5. `qa-training-candidate`

### Path

- `.beacon/state/evo/qa-candidates/<id>.json`

### Required fields

```json
{
  "candidate_id": "qa-threshold-001",
  "category": "qa_confidence_policy",
  "editable_surface": "confidence_thresholds",
  "benchmark_refs": [
    ".beacon/state/eval-lab/benchmark-corpus.json"
  ],
  "main_kpi": "false_complete_rate",
  "supporting_metrics": [
    "false_block_rate",
    "human_audit_agreement",
    "delta_rerun_precision"
  ]
}
```

---

## 6. `qa-calibration-model`

### Path

- `.beacon/state/qa-calibration/latest.json`

### Required fields

```json
{
  "schema_version": "1.0",
  "model_type": "isotonic",
  "trained_at": "2026-03-28T00:00:00Z",
  "training_sample_count": 120,
  "ece": 0.06,
  "brier_score": 0.11,
  "risk_bands": {
    "auto_accept": 0.85,
    "review_required": 0.60
  }
}
```

### Calibration boundary

This model calibrates risk bands.

It does not replace:

- evidence sufficiency checks
- replay requirements
- open-outcome blocking

---

## 7. Release decision policy

### Auto-accept

Allowed only when:

- `closure_status == accepted`
- `confidence_calibrated >= 0.85` for all high-risk scenarios
- no open outcomes in:
  - `needs_replay`
  - `needs_more_evidence`
  - `review_required`

### Review-required

When:

- `0.60 <= confidence_calibrated < 0.85`
- or mixed evidence sufficiency

### Block

When:

- `confidence_calibrated < 0.60`
- replay missing for required scenario
- browser evidence pack missing
- unresolved `closure_outcome`

---

## 8. Compatibility requirement

v1.1.10 contracts must extend—not break—v1.1.9:

- `story-scenario-map`
- `exhaustiveness-report`
- `browser-evidence-pack`
- `release_scorecard`
- `keep_discard_engine`

The contract rule is:

> **additive evolution first, destructive schema break never by default**.

## 9. Source-of-truth hierarchy

When fields conflict, prefer the following order:

1. requirement trace artifact
2. scenario execution/evidence artifact
3. replay/evidence completeness artifact
4. sampled audit label
5. calibrated confidence summary

Confidence should never override a stronger lower-layer fact.
