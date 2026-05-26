# Research: v1.4.10 Feature Carry-Forward Intake

**Version**: `v1.4.11`  
**Status**: `research-input`  
**Date**: `2026-05-26`

## Purpose

This document carries forward v1.4.10 research / feature candidates that should not be silently absorbed into the v1.4.10 aggregate release package.

It is not frozen truth for v1.4.11. Any item below must still enter `change/refreeze`, PRD, user-story, test-case, implementation, QA, and release before it becomes v1.4.11 delivery scope.

## Source Boundary

Authoritative source refs:

- `docs/beacon/v1.4.10/SUMMARY.md`
- `docs/beacon/v1.4.10/change/v1.4.10.md`
- `docs/beacon/v1.4.10/release/checklist-v1.4.10.md`
- `docs/beacon/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
- `docs/beacon/v1.4.10/research/embodiskill-skillevolver-qa-attribution-foundation.md`
- `docs/beacon/v1.4.10/change/qa-multi-layer-real-browser-e2e-acceptance.md`
- `docs/beacon/v1.4.10/change/qa-multi-layer-real-browser-e2e-acceptance.refreeze-summary.md`
- `docs/beacon/v1.4.10/.machine/execution/qa-acceptance-qa-multi-layer-real-browser-e2e-acceptance.json`

Do not copy v1.4.10 frozen truth into v1.4.11 as if it were already accepted for the new version. v1.4.11 must make an explicit scope decision.

## Carry-Forward Candidates

### 1. `qa-multi-layer-real-browser-e2e-acceptance`

Current state:

- v1.4.10 refreeze material: present.
- v1.4.10 PRD / user-story / test-case: present.
- v1.4.10 QA acceptance material: present.
- v1.4.10 aggregate package inclusion: absent from `docs/beacon/v1.4.10/change/v1.4.10.md`.

Recommended v1.4.11 treatment:

- Treat as a high-priority carry-forward candidate.
- Reopen through v1.4.11 change/refreeze before implementation or release inclusion.
- Decide whether v1.4.11 adopts the v1.4.10 package as-is, narrows it, or splits it.

Open questions:

- Should real-browser E2E become a v1.4.11 formal QA foundation, or remain a targeted feature?
- Should it depend on `qa-evidence-attribution-layer` and browser memory advisory as already delivered v1.4.10 prerequisites?
- Which runner registry entries are current, compat-only, or future-admitted?

Boundary:

- QA gains closure-veto authority over weak evidence, but it still cannot author PRD / user-story / test-case truth.
- Browser runner evidence cannot become release pass evidence without formal QA closure.

### 2. `ralph-task-loop-checkpoint-recovery-contract`

Current state:

- v1.4.10 research only.
- Explicitly deferred from v1.4.10 P0 because long-task control has a different state model from QA / Skill Eval.

Recommended v1.4.11 treatment:

- Keep as a P1 candidate after the authority / projection cleanup and QA carry-forward decision.
- Freeze a real Task Loop controller contract, not just a longer agent loop.

Minimum research scope:

- Stage model: plan, implement, review, QA, repair, release-readiness.
- Checkpoint schema.
- Resume contract.
- Error taxonomy: tool failure, environment blocker, quality blocker, truth drift, no-delta loop.
- Resource budget: round limit, stage budget, loop detection, human checkpoint.
- Round memory summarization.

Boundary:

- Ralph serves implementation long tasks.
- Ralph does not replace QA or release.
- Ralph machine state is runtime evidence, not requirement truth.

### 3. `learn-context-to-project-skill-lifecycle-injection`

Current state:

- v1.4.10 research only.
- Deferred because automatic project-skill injection can silently pollute truth, route, or gate behavior.

Recommended v1.4.11 treatment:

- Keep as P1/P2 governed learning candidate.
- Require admission before any project skill can influence Beacon lifecycle behavior.

Minimum research scope:

- Candidate skill generation from project context and lifecycle history.
- Source anchors, applicability, non-applicability, expiry condition, and audit trail.
- Admission / rejection reasons.
- Learning influence summaries for change, test-case, implement, and QA.
- Prune / conflict handling for stale or low-confidence learning.

Boundary:

- `beacon-learn` does not define truth.
- Project skill does not automatically become global skill.
- Learning influence may affect judgment or route recommendation, but cannot issue gate verdicts.

### 4. `qa-attribution-regression-kit`

Current state:

- Follow-up candidate from `embodiskill-skillevolver-qa-attribution-foundation`.
- `qa-evidence-attribution-layer` is already included in the v1.4.10 aggregate package; regression fixtures are not a separate completed feature.

Recommended v1.4.11 treatment:

- Treat as a focused QA hardening candidate.
- Add regression fixtures for common attribution mistakes.

Minimum research scope:

- Truth drift vs implementation gap fixtures.
- Coverage gap vs product failure fixtures.
- Runner admission blocker vs product failure fixtures.
- Evidence insufficient vs release blocker fixtures.
- Route stability integration with Skill Eval Kit.

Boundary:

- Regression output is harness / QA quality evidence.
- It can block QA tooling confidence, but it does not rewrite requirement truth.

### 5. `beacon-skill-evolution-proposal-loop`

Current state:

- Follow-up candidate from EmbodiSkill / SkillEvolver research.
- v1.4.10 delivered proposal-only boundaries through QA browser memory / skill evolution advisory, but not a full cross-skill evolution loop.

Recommended v1.4.11 treatment:

- Keep as P2 until attribution regression and learning admission are stable.
- Generate skill patch proposals from traces; do not auto-apply them.

Minimum research scope:

- Trace selection policy.
- Success / failure trace comparison.
- Patch proposal schema.
- Independent auditor checks.
- Route to `beacon-change` before any accepted change mutates Beacon skill behavior.

Boundary:

- No automatic mutation of skills, code, frozen truth, QA verdict, release verdict, or gate behavior.
- Single-project observations must not become global Beacon rules without admission.

## Recommended Ordering

```text
P0/P1 decision: qa-multi-layer-real-browser-e2e-acceptance carry-forward
P1: ralph-task-loop-checkpoint-recovery-contract
P1/P2: learn-context-to-project-skill-lifecycle-injection
P1: qa-attribution-regression-kit
P2: beacon-skill-evolution-proposal-loop
```

This ordering assumes `markdown-first-projection-authority-and-legacy-retirement-contract` remains the first v1.4.11 governance hardening candidate. If v1.4.11 chooses QA hardening as the primary theme instead, `qa-multi-layer-real-browser-e2e-acceptance` and `qa-attribution-regression-kit` should be evaluated first.

## Non-Goals

- Do not reopen the completed v1.4.10 aggregate package by default.
- Do not promote v1.4.10 machine evidence into v1.4.11 requirement truth.
- Do not merge Ralph, learn injection, QA regression, and skill evolution into one oversized P0.
- Do not add a new public lifecycle stage.
- Do not let support, hook, learning, memory, or skill-eval output become gate verdicts.

## Next Route

Recommended first decision:

```bash
beacon change-refreeze "qa-multi-layer-real-browser-e2e-acceptance" --project . --version v1.4.11
```

Alternative if governance cleanup remains first:

```bash
beacon change-refreeze "markdown-first-projection-authority-and-legacy-retirement-contract" --project . --version v1.4.11
```
