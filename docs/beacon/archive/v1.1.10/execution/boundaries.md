# Beacon v1.1.10 Boundaries

## Goal

Define what v1.1.10 is allowed to conclude, optimize, and release.

This file exists to keep the planning line broad enough for real QA coverage, while still anchored to deterministic truth and explicit evidence.

---

## 1. Truth boundary

### Source of truth order

```text
requirement material
→ executable scenario
→ evidence artifact
→ replay truth
→ human audit truth
```

Rules:

1. `status` is an execution fact.
2. `closure_outcome` is an action/result fact.
3. `confidence` is a judgement layer built on top of evidence.
4. release truth must not skip replay/evidence truth for high-risk browser scenarios.

---

## 2. Confidence boundary

Confidence is allowed to answer:

- how strong the evidence looks
- how much the system should trust a pass/block claim
- whether the case should auto-close, abstain, or block

Confidence is not allowed to:

- replace missing evidence
- replace deterministic replay
- override unresolved closure outcomes
- claim audit truth without audit labels

---

## 3. Closure boundary

Allowed closure outcomes:

- `accepted`
- `bug_filed`
- `implementation_reopened`
- `requirement_rewrite_required`
- `runner_issue`
- `flake_quarantined`
- `needs_more_evidence`
- `needs_replay`
- `needs_requirement_clarification`

Boundary rule:

> If the system cannot choose a closure outcome honestly, it must abstain rather than silently pass.

---

## 4. QA coverage boundary

v1.1.10 should support broad QA coverage, but every broadening step must stay anchored to a fact point.

### Required anchor classes

1. requirement anchor
   - user story / AC / scenario trace
2. evidence anchor
   - logs, screenshots, replay refs, browser evidence pack refs
3. closure anchor
   - explicit closure outcome
4. confidence anchor
   - raw/calibrated signals and threshold semantics
5. audit anchor
   - sampled human label or benchmark truth reference

### Required divergent families

- happy
- negative
- boundary
- recovery
- compatibility

### Additional divergence allowed when grounded

- stale evidence
- wrong delta rerun
- trace mismatch
- mixed evidence sufficiency
- flake / runner instability

---

## 5. Release boundary

Auto-release is allowed only when all are true:

- closure accepted
- no unresolved abstain/review outcomes
- high-risk browser scenarios satisfy replay and evidence requirements
- calibrated confidence is above the auto-accept threshold

Release is blocked when any of the following remains open:

- `needs_replay`
- `needs_more_evidence`
- `review_required`
- unresolved closure outcome
- missing browser evidence pack
- missing required scenario families

---

## 6. Learning boundary

The learning plane may optimize only small policy surfaces:

- scenario expansion heuristics
- impact-selection policy
- delta rerun policy
- evidence sufficiency rules
- confidence calibration parameters
- abstain thresholds
- release scorecard thresholds

The learning plane may not:

- self-modify the full Beacon repository
- redefine truth using model-only scores
- change hidden thresholds without keep/discard evidence

---

## 7. Compatibility boundary

v1.1.10 must remain additive to v1.1.9:

- `story-scenario-map`
- `exhaustiveness-report`
- `browser-evidence-pack`
- `release_scorecard`
- `keep_discard_engine`

Compatible evolution means:

- new fields may be added
- derived reports may be added
- stricter release policies may be layered in

It does not mean:

- deleting required v1.1.9 fields by default
- changing artifact paths without migration
- treating v1.1.9 evidence semantics as obsolete

---

## 8. Operator boundary

Operators should be able to answer four questions without reading raw logs:

1. what passed
2. how confident we are
3. what still needs human review
4. what should feed the next QA experiment set

If a surface cannot answer these four questions, it is incomplete for v1.1.10.

---

## 9. Project workflow boundary

v1.1.10 may use project-specific verification paths when the target project defines them through:

- profile binding
- skill registry
- verify orchestration
- required evidence gate

Boundary rule:

> Beacon should adapt to the target project’s real verification path, but it should still express the result in Beacon’s common truth model.

Allowed:

- `beacon skill bind`
- `beacon verify run`
- profile-level required cases
- skill-backed orchestration nodes

Not allowed:

- bypassing evidence gates just because an external skill said “done”
- treating project-specific scripts as self-validating truth

---

## 10. Browser auth/session boundary

Browser QA may persist and reuse auth/session records via canonical manifests.

Allowed persisted fields:

- `origin`
- `runner_type`
- `profile_ref`
- `cookies_ref`
- `storage_state_ref`
- `expires_at`
- `sensitivity`
- `scopes`

Boundary rule:

> Persist refs, manifests, and scope metadata. Do not spread uncontrolled raw secrets through requirement docs, release notes, or ad hoc logs.

---

## 11. Implement and architecture feedback boundary

When QA reveals a defect or unresolved outcome, the loop may continue through:

```text
qa finding
→ implement
→ technical archive
→ requirement rewrite input
→ architecture feedback
```

Allowed outputs:

- implementation summary
- technical implementation archive
- requirement rewrite input
- architecture blueprint update or linked feedback note

Not allowed:

- stopping the loop at a defect list with no implementation/archive follow-up
- claiming closure before archive and architecture feedback paths are visible
