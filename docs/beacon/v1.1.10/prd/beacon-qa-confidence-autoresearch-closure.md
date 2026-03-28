# PRD: Beacon QA Confidence / Closure Outcome / Autoresearch Precision Loop（v1.1.10）

## 1. Background

Beacon v1.1.9 already lands a strong closure skeleton:

- feature-aware QA
- `qa evolve`
- story-scenario expansion
- story-exhaustive execution
- browser evidence pack
- release scorecard
- keep/discard + evo harness skeleton

That means the core execution path already exists.

The next problem is no longer “can Beacon execute QA around a feature?”

The real problem is:

> **Can Beacon decide with calibrated confidence whether QA really closed the requirement, produce the right business outcome, and continuously improve QA precision from real evidence?**

---

## 2. Problem statement

Current v1.1.9 gaps:

1. **QA result stops at status**
   - `passed / blocked / failed` is not enough
   - there is no formal closure action such as:
     - accepted
     - bug filed
     - implementation reopened
     - requirement rewrite required
2. **Exhaustiveness is used as a proxy for confidence**
   - useful, but incomplete
   - does not answer: “how trustworthy is this pass decision?”
3. **Low-confidence cases have no first-class abstain contract**
   - Beacon should be able to say:
     - `needs_more_evidence`
     - `review_required`
     - `needs_replay`
4. **Learning plane is not yet centered on QA precision**
   - current keep/discard and evo surfaces are present
   - but they do not yet optimize:
     - scenario expansion quality
     - evidence sufficiency policy
     - false-complete reduction
     - false-block reduction

---

## 3. Goals

### G1. Make QA closure actionable
Every scenario / AC / feature verification result must produce a formal closure outcome instead of only a test status.

### G2. Make QA confidence explicit and calibrated
Beacon must distinguish:

- raw evidence strength
- scoring signals
- calibrated confidence
- release decision threshold

### G3. Introduce abstain and escalation semantics
Beacon must support “do not auto-judge yet” as a first-class outcome.

### G4. Turn QA precision into a learnable surface
Real QA audit labels and real false-complete cases must become benchmark truth for fixed-budget keep/discard experiments.

---

## 4. Non-goals

1. Do not introduce full model training infrastructure in v1.1.10.
2. Do not auto-modify the entire Beacon repository.
3. Do not replace deterministic replay with LLM-only judgement.
4. Do not remove current v1.1.9 exhaustiveness / gate contracts.

---

## 5. Product principles

1. **Status is not confidence**
2. **Confidence is not closure outcome**
3. **Pass without enough evidence must be rejectable**
4. **Low-confidence cases should abstain, not bluff**
5. **Only small QA-policy surfaces are trainable**
6. **All training must be fixed-budget and keep/discard-governed**

---

## 6. Functional requirements

### FR-001 Scenario result must add closure semantics

Each scenario result must include:

- `status`
- `closure_outcome`
- `confidence_raw`
- `confidence_calibrated`
- `requires_human_review`
- `root_cause_type`

### FR-002 AC closure must be derived, not guessed

AC closure must be computed from:

- required scenario families
- replay requirements
- evidence pack completeness
- calibrated confidence threshold
- unresolved closure outcomes

### FR-003 Feature release decision must use calibrated confidence

Release scorecard must evaluate:

- feature closure status
- calibrated confidence summary
- high-risk scenario confidence floor
- abstain/review counts

### FR-004 Beacon must support abstain / review-required path

New review/escalation outcomes:

- `review_required`
- `needs_more_evidence`
- `needs_replay`
- `needs_requirement_clarification`

These must block automatic release closure.

### FR-005 QA audit labels must become formal machine artifacts

Beacon must support a machine-readable QA audit label set for sampled verification results:

- `true_pass`
- `false_pass`
- `true_block`
- `false_block`
- `spec_gap`
- `runner_gap`
- `flake`

### FR-006 QA precision benchmark corpus must be built from real cases

The benchmark corpus must include:

- false complete scenarios
- false block scenarios
- stale evidence cases
- missing replay cases
- wrong delta rerun cases
- story/AC trace mismatch cases

### FR-007 Evo harness must treat QA precision as a first-class optimization target

The allowed optimization surface is limited to:

- scenario expansion heuristics
- impact-selection policy
- evidence sufficiency rules
- confidence calibration parameters
- abstain thresholds
- release scorecard thresholds

### FR-008 v1.1.10 must keep v1.1.9 contracts stable

Existing v1.1.9 contracts must remain compatible:

- story-scenario-map
- story-exhaustive
- browser evidence pack
- release scorecard
- keep/discard engine

---

## 7. Data model scope

v1.1.10 introduces/extends these artifacts:

1. `scenario-result-v2`
2. `ac-closure-report`
3. `feature-qa-scorecard`
4. `qa-audit-label`
5. `qa-training-candidate`
6. `qa-calibration-model`

Canonical contract lives in:

- `execution/qa-confidence-data-contract.md`

---

## 8. Success metrics

### Main KPI
- `false_complete_rate`

### Supporting metrics
- `false_block_rate`
- `review_capture_rate`
- `confidence_calibration_error`
- `high_risk_release_escape_count`
- `delta_rerun_precision`
- `human_audit_agreement`

---

## 9. Rollout strategy

Implementation is phased:

1. capture closure outcomes + raw confidence
2. derive AC / feature closure
3. calibrate confidence + support abstain
4. build QA audit benchmark corpus
5. optimize QA policy via fixed-budget keep/discard

Detailed plan lives in:

- `execution/qa-confidence-implementation-phasing.md`

---

## 10. Final statement

Beacon v1.1.10 is the version where QA becomes:

```text
traceable
+ evidence-backed
+ confidence-calibrated
+ closure-oriented
+ continuously improvable
```

instead of merely:

```text
test-executed
```
