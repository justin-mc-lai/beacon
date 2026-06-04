# Change: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Change Reason

v1.4.11 has already registered memory and intent compatibility surfaces:

- `memory-legacy-projection`
- `intent-legacy-router`

The next reduction slice is to limit historical migration behavior so current runtime is not dragged by old memory projection writes or ambiguous legacy intent router behavior.

The previous design/prototype rebuild and browser deterministic command rename are already closed. This change must not reopen those surfaces.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Keep old memory rows importable into current `memory-v1`.
2. Record first legacy memory migration as an auditable migration transaction.
3. Treat `memory-v1` as the current memory projection.
4. Stop writing legacy memory projection files during current memory writes by default.
5. Allow legacy memory projection writes only through explicit compatibility mode or explicit migration/export command.
6. Mark legacy intent router usage as compatibility routing.
7. Keep old intent APIs callable through explicit compatibility admission.
8. Ensure current intent routing uses boundary-aware current routing and does not claim legacy router output as current routing.
9. Bind memory behavior to compatibility registry entry `memory-legacy-projection`.
10. Bind intent behavior to compatibility registry entry `intent-legacy-router`.
11. Preserve prototype/design, browser, QA/PRD mirror, implement package, command removal, release, and test marker behavior outside this slice.

## 3. Scope

### In Scope

- `beacon/utils/memory.py` legacy migration and legacy projection write policy.
- Migration transaction evidence for first legacy memory import.
- Explicit compatibility mode for legacy memory projection writes.
- `beacon/utils/intent_router.py` legacy router compatibility classification.
- Current intent route evidence versus legacy compatibility route evidence.
- Compatibility registry binding for memory and intent surfaces.
- Tests proving default current path does not silently write legacy projection.
- Tests proving old memory import and old intent API remain available through compat admission.

### Out Of Scope

- No prototype or design behavior change.
- No browser deterministic command change.
- No QA legacy mirror change.
- No PRD legacy mirror change.
- No implement package change.
- No command alias removal.
- No release verdict change by itself.
- No test marker relayering.

## 4. Source Evidence

- Research: `docs/beacon/archive/v1.4.11/research/memory-intent-historical-migration-boundary-contract.md`
- Legacy retirement plan: `docs/beacon/archive/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Baseline inventory: `docs/beacon/archive/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- Compatibility registry: `beacon/compatibility/registry.py`
- Memory utility: `beacon/utils/memory.py`
- Intent router: `beacon/utils/intent_router.py`

## 5. Route Decision

This change accepts Phase 9 from the v1.4.11 legacy burden reduction plan.

It is intentionally memory/intent-only:

```text
registry -> prototype/design rebuild -> browser fallback rename -> memory/intent historical migration boundary -> later test marker relayering
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/research/memory-intent-historical-migration-boundary-contract.md`
- `docs/beacon/archive/v1.4.11/change/memory-intent-historical-migration-boundary-contract.md`
- `docs/beacon/archive/v1.4.11/prd/memory-intent-historical-migration-boundary-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/memory-intent-historical-migration-boundary-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/memory-intent-historical-migration-boundary-contract.md`

## 7. Boundary

This feature freezes requirement truth for memory and intent historical migration boundaries only.

It does not execute implementation, QA, release, prototype migration, design changes, browser rename, QA/PRD mirror changes, implement package changes, command removal, or test marker relayering.

