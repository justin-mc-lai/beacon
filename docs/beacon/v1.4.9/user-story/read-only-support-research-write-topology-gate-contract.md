# User Story: Read-Only Support Research Write Topology Gate Contract

**Feature**: `read-only-support-research-write-topology-gate-contract`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Story

As a Beacon operator refining requirements through read-only support skills, I want every version-bound feature analysis to land in the governed research topology, so that repeated clarification stays traceable and cannot bypass material gates through fallback documents.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | ordinary support topology | `beacon-brainstorm`, `beacon-context-engineering`, `beacon-source-driven`, `beacon-doubt-review`, `beacon-security-review`, `beacon-performance-review`, `beacon-documentation-adr`, `beacon-debug-recovery`, `beacon-ceo-review`, and `beacon-design-review` write version+feature findings into `docs/beacon/<version>/research/<feature>.md`. |
| AC-002 | deep topology | `beacon-deep` writes detailed artifacts into `docs/beacon/<version>/deep/<feature>/` and `.machine/deep/<feature>/`; the research file stores only `Deep Summary` index metadata. |
| AC-003 | learning topology | `beacon-learn` writes learning audit data into `docs/beacon/<version>/learning/<feature>.md` or support transaction; the research file stores only `Learning Influence Summary`. |
| AC-004 | no fallback | `docs/brainstorms/` is not a default target for explicit Beacon version+feature support analysis. |
| AC-005 | repeated clarification | Repeated support clarification in the same version appends rounds or supersedes owned sections in the same research file instead of creating sibling files. |
| AC-006 | version lineage | Cross-version clarification creates a new version research file with lineage fields for previous research, carried-forward findings, and superseded assumptions. |
| AC-007 | fail-closed gate | Gate / requirement clarity blocks invalid support write topology and reports source skill, expected path, actual path, and repair route. |
| AC-008 | pre-write gate | Read-only support output is not persisted until Beacon determines the write target from version, feature, and support surface class; unresolved routing fails closed instead of using legacy fallback. |

## Non Goals

- This story does not make support skills canonical truth writers.
- This story does not make support skills release gates.
- This story does not require rewriting historical brainstorm artifacts.
- This story does not execute implementation, QA, or release.

## Boundary

Support findings remain advisory until adopted by `beacon-change`, PRD, user-story, test-case, execution, QA, release, or an explicit artifact update obligation.
