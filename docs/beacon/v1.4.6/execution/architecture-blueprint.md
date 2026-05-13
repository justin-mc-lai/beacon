# Beacon v1.4.6 Architecture Blueprint

## Architecture Intent

`v1.4.6` extends the `v1.4.5` lightweight governance line by tightening host-visible skill behavior before downstream runtime gates need to intervene.

The architecture goal is:

> Beacon should express stronger public-surface contracts, connect challenge outputs back to evidence/state/gate semantics, and preserve philosophy-first skill design without collapsing into rigid operation scripts.

## Layer Placement

The existing architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.6` does not add a new layer.
It tightens contracts inside the surface and projection bands:

```text
public skill contract anatomy
-> anti-rationalization
-> support-surface constitution
-> challenge binding
-> machine-checkable anti-drift checks
-> existing truth/evidence/gate governance
```

## New Contract Focus

### Skill Anatomy v2

Purpose:

- freeze a uniform contract skeleton for key host-visible skills
- expose boundary, workflow, rationalization, verification, evidence, state, and gate semantics
- make misuse harder before execution begins

Boundary:

- cannot become a verbose how-to script template
- cannot replace feature truth or release gate semantics

### Support-Surface Constitution

Purpose:

- unify `brainstorm`, `deep`, `ceo-review`, `design-review`, `help`, `status`, and `doctor`
- preserve their role as challenge/explain/route surfaces
- make overreach auditable

Boundary:

- cannot become truth source
- cannot become gate source
- cannot become a new lifecycle stage

### High-Risk Challenge Binding

Purpose:

- allow adversarial challenge for public promises, release decisions, acceptance closure, and cross-surface consistency
- require challenge output to bind back to route, evidence, state, or gate semantics

Boundary:

- no free-form verdicts without traceable consequence
- no bypass of frozen requirement truth

### Machine-Checkable Anti-Drift Enforcement

Purpose:

- detect missing required sections
- detect support-surface overreach
- detect challenge outputs that are not bound back to Beacon governance surfaces

Boundary:

- checks remain a projection of frozen contract truth
- linting cannot replace human requirement decisions by itself

## Minimal Implementation Slices

### Slice 1: Public Skill Contract Upgrade

Files likely to change:

- `skills/beacon/SKILL.md`
- key skill entry surfaces under `skills/beacon/*/SKILL.md`
- contract-aware validation helpers if present

Outcome:

- key public skills expose one stronger anti-drift anatomy

### Slice 2: Support-Surface Constitution Binding

Files likely to change:

- support-surface skill docs
- route/explainability helpers
- review/challenge projection helpers

Outcome:

- support surfaces share one bounded constitution and clearer handoff semantics

### Slice 3: Anti-Drift Check Projection

Files likely to change:

- docs/skill lint helpers
- projection or doctor checks that validate contract anatomy

Outcome:

- missing or overreaching contracts become machine-detectable

## Non-Goals

- no new public lifecycle stage
- no runtime dependency on external skill packs
- no regression into long procedural step scripts
- no broad rewrite of historical skill lines in one pass
