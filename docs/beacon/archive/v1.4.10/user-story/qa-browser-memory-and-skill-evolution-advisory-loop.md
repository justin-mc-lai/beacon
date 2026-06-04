# User Story: QA Browser Memory And Skill Evolution Advisory Loop

**Feature**: `qa-browser-memory-and-skill-evolution-advisory-loop`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story 1: Browser Site Memory Capture

As a Beacon QA operator, I want real browser QA runs to produce reusable site memory, so that future runs can avoid repeated runner, selector, session, and admission mistakes.

### Acceptance Criteria

- [ ] AC-001 Browser QA site memory is captured from real current-run browser evidence with AC/test IDs, feature, route, host, browser, runner, auth/session mode, evidence refs, and outcome.
- [ ] AC-002 Browser memory admission rejects placeholder-only, listing-only, dry-run, documentation-only, stale, unscoped, or evidence-missing records.

## Story 2: Safe Memory Reuse

As a QA runner planner, I want admitted browser memory to influence future QA execution, so that Beacon can choose better runners, sessions, selectors, and task hints while still requiring fresh evidence.

### Acceptance Criteria

- [ ] AC-003 Admitted browser memory can be automatically retrieved for later QA planning and runner admission.
- [ ] AC-004 Memory influence can guide runner selection, session bridge recommendation, selector/action hints, repeated failure detection, and browser task compilation.
- [ ] AC-005 Memory influence is recorded as advisory/runtime support evidence only and cannot satisfy QA pass, release pass, gate pass, or frozen truth.
- [ ] AC-006 Memory conflict, expiry, host/version/browser/auth mismatch, or protected-surface mismatch must downgrade or block reuse with machine-readable reason codes.

## Story 3: SkillEvolver Proposal Loop

As a Beacon maintainer, I want QA traces to generate audited improvement proposals instead of silent mutations, so that Beacon skills can evolve without breaking truth authority.

### Acceptance Criteria

- [ ] AC-007 SkillEvolver-style trace analysis classifies observations as `Discovery`, `Optimization`, `SkillDefect`, or `ExecutionLapse`.
- [ ] AC-008 Skill evolution output is proposal-only and may include skill patch drafts, checklist updates, runner admission rules, or Skill Eval Kit cases, but must not mutate files automatically.
- [ ] AC-009 Each proposal must bind to trace refs, affected AC/test IDs, evidence refs, failure family, expected route, and risk.

## Story 4: Independent Audit And Route-Back

As a release owner, I want memory and skill-evolution outputs to remain support evidence unless they pass governance, so that QA/release verdicts remain tied to formal current-run evidence.

### Acceptance Criteria

- [ ] AC-010 Independent auditor checks proposals for authority bypass, support evidence promoted to verdict, single-project overfitting, missing evidence binding, silent bypass, and lifecycle-stage sprawl.
- [ ] AC-011 Accepted proposals must route through Beacon change/refreeze before implementation; rejected/deferred proposals remain support evidence only.
- [ ] AC-012 Release and QA scorecards may summarize memory/proposal support evidence, but only formal current-run QA closure can produce release readiness.

## Boundary

Browser memory and skill evolution can change what Beacon recommends or tries next. They cannot change what Beacon declares true.
