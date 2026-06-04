# User Story: Memory / Intent Historical Migration Boundary Contract

**Feature**: `memory-intent-historical-migration-boundary-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Story

As a Beacon maintainer reducing legacy runtime weight, I want historical memory migration and legacy intent routing to be explicit compatibility behavior, so that current runtime can keep old data usable without continuously writing old projections or confusing legacy router output with current route evidence.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | memory import | Old memory rows remain importable into current `memory-v1`. |
| AC-002 | migration transaction | First legacy memory migration writes an auditable migration transaction. |
| AC-003 | current projection | `memory-v1` is treated as the current memory projection after migration. |
| AC-004 | no default legacy write | Current memory writes do not update legacy memory projection files by default. |
| AC-005 | explicit compat projection | Legacy memory projection writes require explicit compatibility mode or explicit migration/export command. |
| AC-006 | intent compat classification | Legacy intent router usage is marked as compatibility routing. |
| AC-007 | old intent callable | Old intent APIs remain callable through explicit compatibility admission. |
| AC-008 | no false current route | Current intent routing does not claim legacy router output as current route evidence. |
| AC-009 | memory registry binding | Memory behavior binds to `memory-legacy-projection`. |
| AC-010 | intent registry binding | Intent behavior binds to `intent-legacy-router`. |
| AC-011 | no unrelated behavior | Tests prove no prototype/design, browser, QA/PRD mirror, implement package, command removal, release, or test marker behavior changes. |

## Explicit Non Coverage

- This story does not reopen prototype or design behavior.
- This story does not modify browser deterministic command behavior.
- This story does not modify QA or PRD legacy mirror policy.
- This story does not modify implement package behavior.
- This story does not remove legacy commands or aliases.
- This story does not relayer test markers.
- This story does not create a release verdict by itself.

## Traceability

- Research: `docs/beacon/archive/v1.4.11/research/memory-intent-historical-migration-boundary-contract.md`
- PRD: `docs/beacon/archive/v1.4.11/prd/memory-intent-historical-migration-boundary-contract.md`
- Test cases: `docs/beacon/archive/v1.4.11/qa/test-cases/memory-intent-historical-migration-boundary-contract.md`

