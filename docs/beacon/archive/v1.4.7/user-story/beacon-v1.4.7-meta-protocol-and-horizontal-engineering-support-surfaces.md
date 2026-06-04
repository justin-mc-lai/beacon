# User Story: Beacon v1.4.7 meta protocol and horizontal engineering support surfaces

**Feature**: `beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces`  
**Version**: `v1.4.7`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon maintainer, operator, or host-integrated project owner,  
**I want** Beacon to keep its truth/evidence/governance kernel while exposing a clearer meta-protocol, stronger host routing, and a first wave of horizontal engineering support skills,  
**So that** Beacon feels easier to enter and more complete as an engineering operating system without expanding the public main lifecycle or weakening truth/gate boundaries.

## Acceptance Criteria

- AC-001 Beacon converges `skills/beacon/SKILL.md` into a compact meta-protocol that prioritizes decision-surface classification, persistent global rules, route-back rules, and support-surface advisory boundaries over wrapper/manual sprawl.
- AC-002 Beacon converges `skills/beacon/using-beacon/SKILL.md` into the host-native route constitution for truth, execution, verification, gate, and support decisions, with explicit route reasoning and `change` escalation when support output alters accepted scope.
- AC-003 Beacon introduces a first-wave horizontal engineering support skill family that at minimum defines `beacon-context-engineering`, `beacon-source-driven`, and `beacon-doubt-review`, and each remains a support surface rather than a new lifecycle stage.
- AC-004 Beacon freezes the rule that newly added horizontal engineering support skills are non-truth, non-gate, and route back to canonical truth or delivery surfaces when they detect scope, promise, or acceptance drift.
- AC-005 Beacon adds a first-wave lightweight reference package for human-readable operator support, including requirement/research/freeze/QA/release/routing references, and those references are explicitly non-canonical supporting material.
- AC-006 Beacon documents a stable lifecycle mapping that explains how external engineering phase models such as `agent-skills` and specialist sprint models such as `gstack` map onto Beacon's own closure chain without changing Beacon's mainline.
- AC-007 Beacon improves specialist packaging for support surfaces so users can understand what kind of challenge, review, or strengthening a surface provides without Beacon becoming a flat catalog of dozens of public commands.
- AC-008 Beacon improves host/operator readability around multi-host use and browser/session/tooling reality, but treats those as support/readability improvements rather than new lifecycle stages or runtime prerequisites.
- AC-009 Beacon improves human-readable learning and route explainability so operators can tell which route recommendation comes from frozen truth, which parts are learning hints, and which surfaces remain advisory only.
- AC-010 v1.4.7 preserves Beacon's root-preservation rules: compact main chain, support surfaces remain non-stage, truth stays canonical and versioned, QA/release stay fail-closed, and skill defaults remain philosophy + minimum tools + necessary facts instead of rigid scripts.

## First-Slice Narrowing

For implementation-first planning, the first accepted slice should be explicitly narrowed to:

1. `skills/beacon/SKILL.md` meta-protocol convergence
2. `skills/beacon/using-beacon/SKILL.md` route constitution convergence
3. definition and landing path for:
   - `beacon-context-engineering`
   - `beacon-source-driven`
   - `beacon-doubt-review`
4. first lightweight references set sufficient to support the above surfaces

Everything else in the feature remains valid roadmap inside the same requirement package, but should not block first-slice delivery closure.

## Second-Slice Narrowing

The next accepted slice is narrowed to:

1. definition and landing path for:
   - `beacon-security-review`
   - `beacon-performance-review`
   - `beacon-documentation-adr`
   - `beacon-debug-recovery`
2. second-wave lightweight references:
   - `research-closure-checklist.md`
   - `business-flow-checklist.md`
   - `state-machine-checklist.md`
3. route visibility updates in `skills/beacon/SKILL.md` and `skills/beacon/using-beacon/SKILL.md`

This slice must preserve the same support-only constitution established in slice 1 and still must not trigger runtime promotion.
