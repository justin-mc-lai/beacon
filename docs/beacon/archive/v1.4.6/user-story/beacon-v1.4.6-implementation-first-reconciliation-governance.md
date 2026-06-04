# User Story: Beacon v1.4.6 implementation-first reconciliation governance

**Feature**: `beacon-v1.4.6-implementation-first-reconciliation-governance`  
**Version**: `v1.4.6`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer or operator recovering from a case where implementation landed before requirement truth was refreshed,  
**I want** Beacon to treat that situation as a governed recovery path routed through `beacon-change` with explicit provenance and reprojection requirements,  
**So that** the system can recover honesty without pretending post-hoc writeback was truth-first delivery.

## Acceptance Criteria

- AC-001 Beacon defines implementation-first reconciliation as recovery semantics rather than a normal delivery mode.
- AC-002 implementation-first reconciliation routes through `beacon-change` instead of a new public stage.
- AC-003 Beacon freezes a minimal reconciliation artifact contract.
- AC-004 affected truth and proof surfaces must be reprojected or revalidated after reconciliation.
- AC-005 Beacon preserves drift provenance instead of treating post-hoc writeback as if it were pre-implementation truth.
