# Change: QA Evo Deep And Skill Eval Kit v1.4.10

**Feature**: `qa-evo-deep-and-skill-eval-kit-v1410`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## 1. Change Reason

Beacon v1.4.9 closed the Markdown-first and support write topology foundations, but QA closure can still be too shallow for stateful products. Existing QA evidence can prove command execution, yet miss state-machine drift, business-flow combinations, permission boundaries, cross-surface closure, repeated scenario failures, and skill/harness regressions.

v1.4.10 must freeze a smaller P0 promise: make deep QA findings routeable and make skill/harness quality regression-testable. This change deliberately does not absorb Ralph Task Loop, project lifecycle hooks, implement mode split, or automatic `beacon learn` skill injection into P0.

## 2. Accepted Change

Freeze the v1.4.10 P0 requirement package for:

1. `qa-evo-deep-state-scenario-round-memory-contract`
2. `better-harness-skill-eval-kit-regression-core`

The accepted behavior is:

- `qa-evo-deep` produces routeable QA findings for state machines, business flows, scenario combinations, permissions, data consistency, cross-surface closure, and repeated QA round memory.
- QA round memory is advisory influence only; it cannot become a pass verdict.
- Skill Eval Kit defines auditable eval cases, tags, splits, regression core, runs, traces, and scorecards for Beacon human-facing skills and harness routes.
- Skill Eval Kit results are harness quality evidence; they cannot rewrite requirement truth.
- Regression core failure can block harness/skill release readiness, but cannot silently change PRD, user-story, test-case, QA verdict, or release verdict.

## 3. Scope

### In Scope

- QA evo-deep human-facing support surface contract.
- QA deep output path and research indexing rule.
- State-machine, business-flow, data-source, permission, cross-surface, and round-memory finding taxonomy.
- Skill Eval Kit case schema, tag taxonomy, split policy, regression core, run output, and scorecard contract.
- Route stability eval cases for existing Beacon support and implement mode routing.
- Requirement clarity boundary that distinguishes QA deep findings and eval evidence from requirement truth.

### Out Of Scope

- Adding a new Beacon lifecycle stage.
- Letting `qa-evo-deep` replace `beacon qa run`.
- Letting `qa-evo-deep` or Skill Eval Kit produce release pass verdicts.
- Project lifecycle hook runtime or automatic hook triggering.
- Ralph Task Loop controller implementation.
- Automatic `beacon learn` context-to-project-skill injection.
- Splitting `beacon-implement` into `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph`.

## 4. Route Decision

- This finding is accepted into v1.4.10 through `beacon-change-refreeze`.
- P0 implementation must first satisfy QA deep output governance and Skill Eval Kit regression core.
- Ralph, hooks, learn injection, and implement mode playbooks remain research inputs and may later enter separate changes.
- Downstream implementation may start only after this refreeze transaction reports complete.

## 5. Freeze Deliverables

- `docs/beacon/archive/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
- `docs/beacon/archive/v1.4.10/source-architecture/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/change/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/prd/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/user-story/qa-evo-deep-and-skill-eval-kit-v1410.md`
- `docs/beacon/archive/v1.4.10/qa/test-cases/qa-evo-deep-and-skill-eval-kit-v1410.md`

## 6. Boundary

This change refreshes requirement truth only. It does not execute implementation, QA, release, hooks, or learning injection.
