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
  "release_ready": false
}
```

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
