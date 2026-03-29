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

Earlier lines also already landed two relevant foundations:

- v1.1.7: project-specific skill profile / orchestration / evidence gate
- v1.1.8: technical implementation archive and requirement rewrite input surface

That means the core execution path already exists.

The next problem is no longer “can Beacon execute QA around a feature?”

The real problem is:

> **Can Beacon decide with calibrated confidence whether QA really closed the requirement, produce the right business outcome, and continuously improve QA precision from real evidence?**

---

## 1.6 Current closure blockers

At the current repository state, four blockers prevent v1.1.10 from being truly closed:

1. **runtime judgement is not in the main QA path**
   - the QA mainline still centers on `status / evidence_done / exhaustiveness`
   - new precision fields are documented but not emitted end-to-end
2. **project workflow is parallel, not primary**
   - project-specific verify orchestration exists
   - but `qa run <feature>` does not yet consume it as part of the mainline
3. **source-architecture docs are not yet part of formal materials/gate checks**
   - they exist as requirement materials
   - but formal audit still does not treat them as a required closure surface
4. **machine refresh can still overwrite human-authored QA docs**
   - this weakens the requirement surface itself
5. **QA still lacks a first-class continue/stop decision**
   - the mainline can report evidence and confidence
   - but it still does not formally answer whether testing should continue, stop for repair, or hand off to release

These are not documentation defects only.

They are closure blockers because each one breaks a different truth boundary.

---

## 1.5 First-principles frame

Beacon QA should be modeled as 5 separate layers:

1. **Requirement truth**
   - what user story / AC / scenario is being verified
2. **Evidence truth**
   - what logs, replay, screenshots, browser packs, assertions, and artifacts exist
3. **Judgement layer**
   - how strong the evidence is and how reliable the current claim appears
4. **Closure action**
   - what business/system action should happen next
5. **Learning loop**
   - what benchmark truth and policy update should absorb this case

v1.1.9 already covers layer 1 and much of layer 2.

v1.1.10 exists to make layers 3, 4, and 5 explicit without weakening the earlier layers.

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

### G5. Keep divergent QA coverage anchored to fact logic
Beacon must support broad QA exploration around a requirement, but every broadening step must remain anchored to explicit fact points:

- requirement trace
- evidence sufficiency
- replay truth
- closure outcome
- audit truth

### G6. Let target projects express their own QA execution reality
Beacon must be able to route verification through project-specific skill/profile/orchestration surfaces when the target project requires them.

### G7. Close the QA defect to implement to architecture loop
QA defects and abstain outcomes must be able to drive implementation work and then feed technical architecture archives and next-round requirement updates.

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

## 5.5 Fact anchors

The whole v1.1.10 line should stay anchored to these facts:

### Anchor A — Existing v1.1.9 reality
Beacon already has:

- feature-aware QA
- story-exhaustive execution
- scenario families
- browser evidence pack
- exhaustiveness report
- release scorecard
- keep/discard skeleton

v1.1.10 must extend these artifacts, not bypass them.

### Anchor B — Truth hierarchy

```text
status
!= closure_outcome
!= confidence
!= release decision
```

Each layer is related but not interchangeable.

### Anchor C — High-risk browser release rule
For high-risk browser scenarios:

- exploratory pass is useful
- deterministic replay is still required
- missing replay or missing browser evidence pack blocks auto-close

### Anchor D — Honest abstain
The system is allowed to say:

- `review_required`
- `needs_more_evidence`
- `needs_replay`
- `needs_requirement_clarification`

That is a feature, not an error.

### Anchor E — Audited learning
Policy optimization must be driven by:

- sampled human audit labels
- benchmark truth
- keep/discard scorecards

not by self-reported model confidence alone.

### Anchor F — Project-specific workflow reality
Some projects have a real verification truth path expressed through:

- project profile
- skill registry
- verify orchestration
- required evidence gate

v1.1.10 should use that path rather than flattening every project into the same generic QA route.

### Anchor G — Browser auth persistence
Persistent browser QA requires reusable auth/session records, but those records should be stored as controlled refs and manifests rather than copied as raw secrets into docs.

### Anchor H — Architecture feedback
When QA reveals a real implementation gap, the output should not end at “blocked”.

It should be able to flow into:

- implement tasking
- technical implementation archive
- requirement rewrite input
- architecture blueprint feedback

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

### FR-009 QA coverage must be broad but anchor-bounded

QA must support divergent scenario coverage across:

- happy
- negative
- boundary
- recovery
- compatibility
- stale evidence
- wrong delta rerun
- trace mismatch

But each scenario family must still trace back to at least one anchor:

- requirement anchor
- evidence anchor
- replay anchor
- confidence anchor
- audit anchor

### FR-010 Test feedback must write back into the planning line

Every meaningful QA finding in this line must classify into one of:

- confirms anchor
- exposes boundary gap
- reveals false complete
- reveals false block
- requires operator review
- should enter next experiment set

### FR-011 Project-specific skill workflow must be first-class in QA precision

Beacon must support the ability to bind a feature to a target project profile/skill workflow so that QA precision is evaluated against the real project verification path.

This includes:

- project profile resolution
- feature/profile binding
- verify-stage orchestration
- required evidence gate

### FR-012 Browser auth/session records must be persistable and reusable

Beacon must support persistent QA session manifests for browser-driven QA, including:

- `profile_ref`
- `cookies_ref`
- `storage_state_ref`
- `origin`
- `scopes`
- `expires_at`

These records must support later rerun/replay workflows without weakening secret-handling boundaries.

### FR-013 QA defect routing must integrate with implement and technical archive

When QA produces:

- `implementation_reopened`
- `bug_filed`
- `needs_more_evidence`
- `needs_replay`

Beacon must be able to route the case into:

- implementation work
- technical archive update
- requirement rewrite input
- architecture feedback documentation

### FR-014 Project workflow evolution must remain bounded and learnable

Target project QA workflows may evolve through keep/discard, but only on bounded surfaces such as:

- evidence contract refinement
- required case selection
- profile-level orchestration node policy
- session reuse policy
- delta rerun policy

### FR-015 Runtime QA mainline must emit the documented precision contract

The documented `scenario-result-v2`, `ac-closure-report`, and `feature-qa-scorecard` are not optional reporting artifacts.

They must be emitted by the primary feature-aware QA path.

### FR-016 `qa run <feature>` must consume project workflow truth

The shortest correct path is:

```text
qa run <feature>
→ resolve feature profile
→ run or consume verify-stage orchestration
→ enforce required evidence gate
→ execute feature-aware/story-exhaustive QA
→ derive closure/confidence
```

This is preferred over asking operators to manually run a parallel `verify run` path and then separately run QA.

### FR-017 Source-architecture line must enter formal materials/gate closure

The source-architecture parallel feature is only considered closed when formal audit/gate knows it exists.

Regression tests alone are not enough.

### FR-018 Machine refresh must preserve human-authored QA requirement docs

When refreshing matrix/scenario artifacts, Beacon must preserve human-authored QA planning markdown by default.

The shortest correct behavior is:

- refresh machine outputs
- preserve human docs
- only overwrite human docs on explicit opt-in

### FR-019 QA must execute in story order and emit round-level coverage truth

The QA mainline must proceed in first-principles order:

```text
user story / AC order
→ scenario divergence
→ current-round execution
→ evidence pack
→ coverage_current / coverage_gap
→ continue_decision
```

This means the runtime result must tell the operator:

- what part of the story is already covered
- what part is still uncovered
- whether the next correct step is continue, stop for repair, or release review

### FR-020 Severe blockers must terminate QA instead of creating fake progress

When one of the following makes downstream evidence untrustworthy:

- browser auth/session failure
- required replay missing on high-risk browser paths
- project-specific required evidence gate missing
- contract drift invalidating current traceability
- environment instability that makes repeated results non-comparable

Beacon must mark the round as:

- `continue_decision=stop_for_repair`

and stop claiming that additional QA in the same round improves closure truth.

### FR-021 QA result must produce a human repair/resume handoff

If a round stops for repair, the machine/human output must include:

- blocker summary
- root-cause summary
- repair handoff target
- `resume_command`

The canonical resume path should be compatible with:

```text
beacon help --project-root <root> --version <version> --feature "<feature>"
```

so a human can repair the blocker, confirm closure, and resume the QA mainline without guessing the next command.

### FR-022 Every QA round must backfill missing test cases before claiming improved coverage

Re-running the same passing subset is not enough.

Each new QA round must compare the previous round’s:

- coverage gap
- blocker history
- missing scenario families
- missing replay/evidence obligations

and explicitly decide whether `test_case_backfill_required=true`.

If yes, Beacon must update the test-case/matrix surface before claiming the new round improved coverage.

### FR-023 Browser-driven QA should default to built-in `browser-use` with session continuity

For browser-relevant scenario families, the default QA path should assume Beacon can compile and execute browser tasks through built-in `browser-use`, while still allowing project-specific overrides when needed.

Regardless of the concrete runner, the workflow must preserve:

- session manifest
- profile ref
- cookies ref
- storage-state ref
- scope/origin metadata

so the next round inherits the same user context instead of starting from scratch.

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

Human-readable requirement surfaces must also exist:

- `user-story/beacon-qa-confidence-autoresearch-closure.md`
- `qa/test-cases/beacon-qa-confidence-autoresearch-closure.md`

---

## 7.5 First-principles operator path

The product should make the shortest correct operator path obvious:

```text
run QA around the story
→ inspect evidence and current coverage
→ decide continue / stop_for_repair / ready_for_release
→ if stopped, repair the blocker
→ use beacon help to resume the next QA round
→ backfill missing test cases
→ only then update release guidance
```

Anything longer than that is process waste.

Anything shorter than that is fake closure.
- `execution/boundaries.md`
- `execution/project-skill-qa-evolution-blueprint.md`
- `release/v1.1.10.md`

---

## 7.5 Operator decision semantics

v1.1.10 should let a release owner answer, in order:

1. what requirement slice is being claimed as closed
2. what evidence exists for that claim
3. what calibrated confidence the system assigns
4. whether the system is auto-accepting, abstaining, or blocking
5. what should happen next in human review or policy learning

If Beacon cannot answer all 5, the line has not reached its intended quality bar.

---

## 7.6 Boundary matrix

| Boundary | What v1.1.10 allows | What v1.1.10 does not allow |
| --- | --- | --- |
| Truth | Evidence-backed judgement with replay and audit | LLM-only release truth |
| Confidence | Calibrated thresholds and abstain semantics | Treating exhaustiveness as confidence |
| Closure | Explicit closure outcomes and open-outcome blocking | Status-only closure claims |
| Learning | Fixed-budget keep/discard on small policy surfaces | Full-repo autonomous modification |
| Compatibility | Additive evolution of v1.1.9 contracts | Default destructive schema breaks |
| Project workflow | Profile/skill/orchestration driven QA path | Assuming every project has the same verify path |
| Browser auth | Session manifests and artifact refs | Raw uncontrolled credential sprawl in docs |
| Architecture feedback | QA defect -> implement -> technical archive -> architecture feedback | Defects stranded as isolated QA notes |

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

To truly close the line, two extra workstreams must also be completed:

6. move project-specific verify workflow into the QA mainline
7. move source-architecture and human-doc integrity into formal audit/gate

Detailed plan lives in:

- `execution/qa-confidence-implementation-phasing.md`

Before implementation starts, the planning line should already satisfy:

- user story complete
- PRD complete
- QA test cases complete
- boundaries documented
- release/test feedback file initialized

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

And it must do so while remaining:

```text
fact-anchored
+ reviewable
+ additive to v1.1.9
+ bounded in training scope
```
