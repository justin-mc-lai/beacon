# User Story: Beacon v1.4.5 governed external skill sources and learning composition

**Feature**: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`  
**Version**: `v1.4.5`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon operator working on content, operations, or cross-industry tasks,  
**I want** Beacon to treat governed external skill sources as first-class capability inputs and learn which compositions work,  
**So that** I can declare business goals and result shapes without hand-specifying every intermediate skill chain.

## Acceptance Criteria

- AC-001 Beacon freezes external skill sources as first-class capability sources.
- AC-002 `core-skills/baoyu-skills` is formalized as the canonical sample source for this line.
- AC-003 users can declare business goals and target outputs without predeclaring the full skill chain.
- AC-004 Beacon defines capability selection and composition semantics.
- AC-005 success, failure, fallback, and human adoption outcomes are written back as learning evidence.
- AC-006 Beacon defines `task-type -> skill-chain -> output-shape` as a reusable learning mapping.
- AC-007 external skill governance preserves existing truth, guidance, and runtime boundaries.
- AC-008 external skill admission preserves strategy philosophy, minimum complete tools, and necessary factual grounding instead of collapsing into rigid step scripts.
