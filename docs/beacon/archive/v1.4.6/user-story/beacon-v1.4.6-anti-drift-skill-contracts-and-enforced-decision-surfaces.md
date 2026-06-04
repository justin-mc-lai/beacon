# User Story: Beacon v1.4.6 anti-drift skill contracts and enforced decision surfaces

**Feature**: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`  
**Version**: `v1.4.6`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer, operator, or workflow governance owner,  
**I want** Beacon's public skills and support surfaces to carry stronger anti-drift contracts connected to evidence, state, and gate semantics,  
**So that** host-visible behavior becomes harder to misuse before machine governance must intervene.

## Acceptance Criteria

- AC-001 Beacon freezes a `Skill Anatomy v2` baseline for key host-visible skills with explicit sections for usage boundary, workflow or decision loop, rationalization risk, verification, evidence, state, and gate semantics.
- AC-002 `using-beacon`, `beacon-prd`, `beacon-change`, `beacon-brainstorm`, `beacon-implement`, `beacon-qa`, and `beacon-release` all include explicit anti-rationalization guidance instead of relying on implied operator discipline.
- AC-003 Beacon defines one unified support-surface constitution for `brainstorm`, `deep`, `ceo-review`, `design-review`, `help`, `status`, and `doctor`, and that constitution preserves `not truth source`, `not gate source`, and `not new lifecycle stage`.
- AC-004 high-risk challenge output is formalized so review-style surfaces can challenge decisions, but the result must map back to route, evidence, state, or gate impact instead of ending as free-form commentary.
- AC-005 Beacon formalizes a public surface family model that distinguishes truth surfaces, execution surfaces, support surfaces, and gate surfaces with clear escalation and handoff boundaries.
- AC-006 machine-checkable anti-drift enforcement is defined for the new contract baseline so missing sections, overreaching support surfaces, or unbound challenge outputs can be detected automatically.
- AC-007 the v1.4.6 contract preserves Beacon's philosophy-first skill design and does not regress into step-by-step operation scripts for strong models.
- AC-008 Beacon absorbs external workflow-skill methods as internal contract design, anti-rationalization, and orchestration patterns without creating a runtime dependency on external skill packs.
- AC-009 `brainstorm` and `change` remain distinct: `brainstorm` can sharpen options and framing, but only `change` can promote requirement truth intended for downstream implementation and QA.
- AC-010 the new anti-drift contract is documented as a host-visible behavior upgrade for Beacon rather than a new lifecycle stage or a replacement for existing truth, evidence, and gate governance.
