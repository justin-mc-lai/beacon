# Change: QA Browser Memory And Skill Evolution Advisory Loop

**Feature**: `qa-browser-memory-and-skill-evolution-advisory-loop`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

Beacon QA already has real browser evidence packs, runner admission blockers, QA attribution, QA evo-deep round memory, and Skill Eval Kit boundaries. The remaining gap is that browser QA learning is mostly written as isolated evidence, while later QA runs cannot safely reuse it as governed execution advice. SkillEvolver-style traces can also explain how Beacon skills should improve, but there is no frozen product contract that keeps those improvements proposal-only.

This change promotes two connected support capabilities into governed requirement truth:

- browser QA multi-round site memory that may automatically influence future QA planning, runner admission, browser task compilation, selectors, and session strategy;
- SkillEvolver-style self-evolution that may generate audited skill improvement proposals and regression cases, but may not silently mutate skills, frozen truth, QA verdicts, or release verdicts.

## 2. Accepted Change

Freeze `qa-browser-memory-and-skill-evolution-advisory-loop` as a QA support-intelligence feature. It extends Beacon QA with memory and self-evolution advice while preserving truth authority:

- browser memory can be discovered, admitted, retrieved, and applied automatically;
- memory can affect execution planning only, never QA/release pass evidence;
- current-run evidence remains mandatory for QA closure;
- stale, conflicting, protected-surface, or placeholder-only memory must fail closed or downgrade to advisory;
- SkillEvolver-style outputs are candidate proposals only;
- proposals must be bound to traces, affected AC/test IDs, evidence refs, and independent audit;
- accepted proposals must enter the normal `change -> prd -> user-story -> test-case -> implement -> qa -> release` chain before changing Beacon behavior.

## 3. Scope

### In Scope

- Browser site memory capture from current browser evidence packs, runner reports, admission outcomes, action transcripts, session refs, DOM/current URL snapshots, console/network summaries, and QA closure outcomes.
- Browser memory admission, TTL, conflict handling, host/version/browser/auth/session scoping, and evidence binding.
- Automatic memory retrieval for QA planning, runner selection, session bridge recommendation, selector/action hints, and repeated failure detection.
- Explicit recording of memory influence in QA plan/status/scorecard without allowing memory to count as current evidence.
- SkillEvolver-style trace comparison and proposal generation for Beacon QA skill, checklist, runner admission, and eval case improvements.
- Independent auditor checks for authority bypass, single-project overfitting, missing AC/evidence refs, silent bypass, and support evidence promoted to verdict.

### Out Of Scope

- Automatic mutation of `skills/`, Beacon runtime, PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict.
- Treating historical memory as QA pass evidence.
- Treating SkillEvolver proposals as accepted implementation.
- Adding a new Beacon lifecycle stage.
- Hidden browser side effects without explicit QA execution.

## 4. Route Decision

This is a new product semantic, not a small code patch. It must enter v1.4.10 requirement truth before implementation. Downstream work should extend the existing QA, auto-test, QA evo-deep, QA attribution, and Skill Eval Kit surfaces rather than create a new lifecycle stage.

## 5. Freeze Deliverables

- `docs/beacon/v1.4.10/change/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- `docs/beacon/v1.4.10/prd/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- `docs/beacon/v1.4.10/user-story/qa-browser-memory-and-skill-evolution-advisory-loop.md`
- `docs/beacon/v1.4.10/qa/test-cases/qa-browser-memory-and-skill-evolution-advisory-loop.md`

## 6. Boundary

Browser memory and skill evolution are support intelligence. They can improve what QA tries next, but only fresh, executable QA evidence can prove closure.
