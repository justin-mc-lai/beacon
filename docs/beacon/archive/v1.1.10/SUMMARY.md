# Beacon v1.1.10 Summary

**主题**: QA closure outcome、校准置信度与 autoresearch 驱动的 QA 精准度闭环  
**状态**: Implemented / Verified  
**基线版本**: `v1.1.9`  
**日期**: 2026-03-28

---

## Current Closure Assessment

As of the current repository state, `v1.1.10` is:

- `materials-closed`
- `machine-materialized`
- `runtime-closed`

This means:

- requirement materials exist
- `.machine` artifacts exist
- the QA mainline emits precision artifacts
- release/gate consume confidence-aware closure signals
- project-specific verify workflow can participate in `qa run <feature>`
- source-architecture docs are part of formal anti-drift checks
- human-authored QA docs are preserved by default during machine refresh

---

## One-line summary

v1.1.10 is the line that turns Beacon’s landed v1.1.9 closure skeleton into a **precision-oriented QA system**:

```text
story / AC / scenario
→ evidence
→ calibrated confidence
→ closure outcome
→ benchmark truth
→ keep/discard experiment
→ QA policy uplift
```

It does not invent a new QA engine.

It upgrades Beacon from:

```text
test executed
```

to:

```text
test judged
+ abstained when needed
+ audited against truth
+ fed back into the next policy revision
```

---

## Why v1.1.10 exists

v1.1.9 already landed:

- feature-aware QA
- story-exhaustive execution
- scenario families
- browser evidence packs
- release scorecard
- keep/discard + evo harness skeleton

But v1.1.9 still leaves 4 gaps:

1. **pass/fail is not enough**
   - there is no formal `closure_outcome`
2. **exhaustiveness is not confidence**
   - there is no calibrated confidence contract
3. **low-confidence cases still need a first-class abstain path**
   - `review_required` / `needs_more_evidence` is not yet formalized
4. **QA learning is not yet the main training target**
   - the learning plane does not yet optimize QA precision directly

---

## Target result

Beacon v1.1.10 should make the following statement true:

> A QA claim is only releasable when Beacon can explain **what requirement was tested, what evidence exists, how confident the conclusion is, what closure action happened, and how that result feeds the next QA policy iteration**.

---

## Fact Anchors

The planning line is anchored on 5 non-negotiable facts:

1. `status` is an execution fact, not a release truth.
2. `confidence` is a judgement layer, not a substitute for evidence.
3. high-risk browser claims still require deterministic replay and evidence packs.
4. low-confidence outcomes must abstain instead of bluffing.
5. QA precision learning must be fixed-budget and driven by audited truth, not self-scored optimism.

---

## Core deliverables

1. `user-story/beacon-qa-confidence-autoresearch-closure.md`
2. `prd/beacon-qa-confidence-autoresearch-closure.md`
3. `qa/test-cases/beacon-qa-confidence-autoresearch-closure.md`
4. `user-story/beacon-source-architecture-sync.md`
5. `prd/beacon-source-architecture-sync.md`
6. `qa/test-cases/beacon-source-architecture-sync.md`
7. `user-story/beacon-prototype-frontend-route-closure.md`
8. `prd/beacon-prototype-frontend-route-closure.md`
9. `qa/test-cases/beacon-prototype-frontend-route-closure.md`
10. `execution/boundaries.md`
11. `execution/architecture-blueprint.md`
12. `execution/qa-confidence-data-contract.md`
13. `execution/project-skill-qa-evolution-blueprint.md`
14. `execution/prototype-frontend-route-closure-blueprint.md`
15. `execution/qa-confidence-implementation-phasing.md`
16. `source-architecture/`
17. `release/v1.1.10.md`

Machine-backed delivery artifacts must also exist for the same feature:

- `.machine/user-story/beacon-qa-confidence-autoresearch-closure.json`
- `.machine/qa/beacon-qa-confidence-autoresearch-closure.ac-test-matrix.json`
- `.machine/qa/beacon-qa-confidence-autoresearch-closure.story-scenario-map.json`
- `.machine/execution/beacon-qa-confidence-autoresearch-closure.revision.json`
- `.machine/user-story/beacon-source-architecture-sync.json`
- `.machine/qa/beacon-source-architecture-sync.ac-test-matrix.json`
- `.machine/qa/beacon-source-architecture-sync.story-scenario-map.json`
- `.machine/execution/beacon-source-architecture-sync.revision.json`
- `.machine/user-story/beacon-prototype-frontend-route-closure.json`
- `.machine/qa/beacon-prototype-frontend-route-closure.ac-test-matrix.json`
- `.machine/qa/beacon-prototype-frontend-route-closure.story-scenario-map.json`
- `.machine/execution/beacon-prototype-frontend-route-closure.revision.json`
- `.machine/execution/config.json`
- `.machine/execution/source.json`
- `.machine/execution/git-alignment.json`
- `.machine/execution/delivery-manifest.json`
- `.machine/execution/change-impact.json`
- `.machine/execution/terminal.json`

---

## Recommended reading order

1. `./user-story/beacon-qa-confidence-autoresearch-closure.md`
2. `./prd/beacon-qa-confidence-autoresearch-closure.md`
3. `./execution/boundaries.md`
4. `./execution/qa-confidence-data-contract.md`
5. `./execution/project-skill-qa-evolution-blueprint.md`
6. `./qa/test-cases/beacon-qa-confidence-autoresearch-closure.md`
7. `./user-story/beacon-source-architecture-sync.md`
8. `./prd/beacon-source-architecture-sync.md`
9. `./qa/test-cases/beacon-source-architecture-sync.md`
10. `./user-story/beacon-prototype-frontend-route-closure.md`
11. `./prd/beacon-prototype-frontend-route-closure.md`
12. `./qa/test-cases/beacon-prototype-frontend-route-closure.md`
13. `./execution/prototype-frontend-route-closure-blueprint.md`
14. `./execution/architecture-blueprint.md`
15. `./source-architecture/index.md`
16. `./execution/qa-confidence-implementation-phasing.md`
17. `./release/v1.1.10.md`

---

## Completion Standard For This Planning Line

The materials are only considered complete when:

- the user story defines closure, confidence, abstain, audit, and learning boundaries
- the PRD explains first-principles logic and operator decision semantics
- QA test cases cover both divergent scenario spread and fact-anchored truth checks
- source-architecture docs explain current code structure in human-readable form
- machine materials stay compatible with the v1.1.9 workflow surface
- release notes include document/test feedback and remaining implementation risk

The line is considered truly closed because:

- `qa run <feature>` emits closure/confidence-aware machine results
- release/gate are confidence-aware rather than status-only
- project-specific verify workflow can be part of the QA mainline rather than a parallel path
- source-architecture docs are protected by formal materials/gate checks
- machine refresh commands do not overwrite human-authored QA planning docs by default

---

## First-principles QA workflow clarification

The intended `v1.1.10` QA mainline is not:

```text
run tests
→ collect logs
→ keep going until somebody manually stops
```

It is:

```text
user story order
→ scenario expansion
→ current-round execution
→ evidence pack + coverage snapshot
→ continue_decision
→ severe blocker? stop_for_repair
→ repair/implement closure
→ beacon help next-step guidance
→ next QA round with test-case backfill
→ release guidance
```

This means every QA round should answer five human questions in order:

1. what story / AC / scenario was tested
2. what evidence exists right now
3. how much coverage is complete right now
4. should QA continue or stop for repair
5. what is the next command the human should run

If Beacon cannot answer those five questions, it has not closed the QA loop.
