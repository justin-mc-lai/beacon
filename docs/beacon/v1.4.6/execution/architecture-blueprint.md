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

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.6`
- feature_count: `1`
- transaction_id: `tx-4614b8d84fcb4fd54`
- source_hash: `sha256:7ad8c7c1f0cebb9b69b518581c038fb2bc9d28c0ea4169cf9426a57d7990495c`

### Registered Feature Baselines
- `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces` | revision=`R1` | branch=`beacon/v1.4.6` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.4.6/.machine/execution/implementation-delivery-baseline-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- version: `v1.4.6`

### Source Refs
- prd: `docs/beacon/v1.4.6/prd/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- user_story: `docs/beacon/v1.4.6/user-story/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`
- test_case: `docs/beacon/v1.4.6/qa/test-cases/beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces.md`

### Delivery Change Surface
- none
### Available Entry Surfaces
- none
### Current Service Facts
- none

### Must Change
- none

### Can Reuse
- none

### No-Expand Guardrails
- none

### Compatibility Rules
- none

### Delivery Constraints
- none

### Implement Handoff
- none
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.6-beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces-R1`
- transaction_id: `tx-7ffa3435b4ea79cc6`
- source_hash: `sha256:e33ff59e0ed6ca40796f0a2feb2c5e9164738fafb584975b8899fc7ae2f5c64f`
- projection_seq: `1`
- version: `v1.4.6`
- feature: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.6`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces:END -->
