# Beacon v1.1.10 QA Confidence Implementation Phasing

## Goal

Ship QA precision improvements without destabilizing the landed v1.1.9 closure line.

---

## Phase 0 — Stabilize the v1.1.9 baseline

### Goal
Freeze the baseline before precision work.

### Deliverables
- verify v1.1.9 doc/implementation alignment
- freeze benchmark seed set for:
  - false pass
  - false block
  - missing replay
  - stale evidence
  - wrong delta rerun selection

### Exit gate
- release note exists for v1.1.9
- v1.1.9 targeted test slice is green
- benchmark corpus contains real QA failure modes

---

## Phase 1 — Add closure outcome + raw confidence

### Goal
Stop treating QA result as status-only.

### Deliverables
- extend scenario result with:
  - `closure_outcome`
  - `confidence_raw`
  - `evidence_sufficiency`
  - `root_cause_type`
- derive AC closure report
- surface feature QA scorecard

### Primary files
- `beacon/commands/qa.py`
- `beacon/commands/auto_test.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/exhaustiveness.py`

### Success metric
- every browser scenario emits `closure_outcome`

---

## Phase 2 — Add calibrated confidence + abstain path

### Goal
Make release decision confidence-aware.

### Deliverables
- add `confidence_calibrated`
- add release thresholds:
  - auto accept
  - review required
  - block
- add abstain/review-required outcomes:
  - `needs_more_evidence`
  - `needs_replay`
  - `review_required`

### Primary files
- `beacon/utils/release_scorecard.py`
- `beacon/commands/release.py`
- `beacon/commands/gate.py`
- `beacon/commands/status.py`
- `beacon/commands/report.py`

### Success metric
- high-risk browser pass cannot auto-close without confidence + replay

---

## Phase 3 — Build QA audit truth set

### Goal
Create the labeled benchmark needed for precision learning.

### Deliverables
- QA audit label schema
- sampled audit workflow
- storage under `.beacon/state/qa-audits/`
- benchmark join between:
  - scenario result
  - release outcome
  - human audit label

### Success metric
- enough labeled cases to compute:
  - `false_complete_rate`
  - `false_block_rate`
  - `human_audit_agreement`

---

## Phase 4 — Connect QA precision to keep/discard evo

### Goal
Make QA policy optimization a first-class evo experiment.

### Deliverables
- new QA precision candidate categories:
  - `qa_confidence_policy`
  - `qa_scenario_expansion_policy`
  - `qa_delta_selection_policy`
  - `qa_evidence_sufficiency_policy`
- fixed-budget experiment runner for QA precision
- keep/review/discard verdicts against real QA benchmark corpus

### Success metric
- lower `false_complete_rate` without unacceptable `false_block_rate` regression

---

## Phase 5 — Release governance upgrade

### Goal
Make calibrated QA precision visible in the main operator surfaces.

### Deliverables
- release scorecard shows:
  - confidence floor
  - review-required count
  - unresolved closure outcomes
- report/status main views show:
  - release confidence summary
  - audit drift signals
  - training readiness

### Success metric
- release owner can answer:
  - what passed
  - how confident we are
  - what still needs human review
  - what should enter the next experiment set

---

## Guardrails

1. no full-repo self-modification
2. no replacing deterministic replay with agent-only truth
3. no hidden threshold changes without keep/discard evidence
4. no release-ready claim when closure outcomes remain unresolved

---

## Recommended milestone order

```text
M1 = closure outcome
M2 = calibrated confidence
M3 = audit truth set
M4 = QA precision evo
M5 = release governance uplift
```

This order matters because:

- confidence without audit truth is bluff
- training without closure outcome is noisy
- governance before calibration creates operator confusion
