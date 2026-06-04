# User Story: Beacon v1.4.3 Governed Learning Recall and Route Explainability

**Feature**: `beacon-v1.4.3-governed-learning-recall-and-route-explainability`  
**Version**: `v1.4.3`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon operator,  
**I want** learning to become a visible default decision input instead of a hidden kernel-only capability,  
**So that** support surfaces can explain why Beacon recommends a route, what prior learning is influencing it, and whether that learning is still trustworthy.

## Acceptance Criteria

- AC-001 `beacon-learn` exists as visible learning governance surface.
- AC-002 relevant learning can be injected by default into core decision surfaces.
- AC-003 applied learning is visible with confidence/staleness context.
- AC-004 stale/conflicting learning is downgraded, flagged, or pruned.
- AC-005 `help / status / ask / deep` explain route, evidence gaps, and learning influence.
