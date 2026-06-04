# User Story: Beacon v1.4.5 docs architecture and machine-truth minimization

**Feature**: `beacon-v1.4.5-docs-architecture-and-machine-truth-minimization`  
**Version**: `v1.4.5`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer or docs operator,  
**I want** Beacon to separate `truth`, `guidance`, `delivery`, `evidence`, and `.machine` more clearly while suppressing redundant paired projections,  
**So that** docs stay navigable and machine truth remains minimal without losing operator closure.

## Acceptance Criteria

- AC-001 `v1.4.5` freezes a clearer docs structure contract.
- AC-002 existing software truth surfaces are explicitly mapped into `truth/`.
- AC-003 guidance surfaces write into `guidance/` rather than mixing with truth by default.
- AC-004 `delivery/` and `evidence/` are separated more clearly.
- AC-005 Beacon does not default to paired human/machine artifacts when no new semantics are added.
- AC-006 `.machine` is explicitly treated as a projection layer with optional human companions.
- AC-007 historical versions may remain as-is while new versions follow the new structure contract.
- AC-008 Beacon creates the new structure progressively as layers are actually used, rather than materializing the whole tree up front.
