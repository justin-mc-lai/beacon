# Beacon v1.4.5 Architecture Blueprint

## Architecture Intent

`v1.4.5` repositions Beacon one level above coding-only lifecycle governance while preserving a lightweight runtime and docs surface.

The architecture goal is:

> Beacon should freeze a clearer semantic model for guidance, truth, delivery, evidence, and machine projection, admit governed external capabilities, and stay operationally light by creating structure only when a real surface consumes it.

## Layer Placement

The existing architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.5` does not add a new primary layer.
It tightens contracts between existing layers:

```text
version/package truth
-> guidance family binding
-> docs semantics contract
-> progressive projection/materialization
-> external capability selection
-> learning writeback
-> implement / qa continue as the only execution gates
```

## New Contract Focus

### Guidance Family Binding

Purpose:

- treat `ceo-review`, `brainstorm`, `design-review`, and `deep` as one family
- allow version-level umbrella features to bind to package truth, not only one direct feature slug
- keep route/explainability language consistent

Boundary:

- cannot become a second truth root
- cannot create a new public lifecycle stage
- cannot bypass `change`

### Docs Semantics and Progressive Materialization

Purpose:

- define `truth / guidance / delivery / evidence / .machine` as semantic layers
- avoid default paired human/machine projection when no new semantics are added
- create directories and projections only when the layer is actually used

Boundary:

- no bulk migration requirement for historical versions
- no eager full-tree materialization
- no requirement that every semantic layer must exist on disk in every version

### Governed External Capability Plane

Purpose:

- admit external skill sources as first-class governed capability inputs
- start with one canonical sample source: `core-skills/baoyu-skills`
- let users declare business goals and result shape instead of hand-authoring every chain

Boundary:

- no public marketplace
- no ungoverned runtime dependency download path
- no bypass of truth/guidance/runtime compatibility checks

### Learning Composition Contract

Purpose:

- record `task-type -> skill-chain -> output-shape`
- preserve success, failure, fallback, and adoption outcomes
- reuse validated combinations as advisory priors

Boundary:

- learning remains advisory
- learning cannot replace truth or gate verdicts

## Philosophy-First Skill Admission

`v1.4.5` assumes stronger models should be constrained less by step scripts and more by the right operating frame.

External or internal skills admitted in this line should preferentially preserve:

1. `Agent strategy philosophy`
2. `minimum complete toolset`
3. `necessary factual grounding`

They should avoid turning into long procedural instructions unless a hard boundary genuinely requires it.

## Minimal Implementation Slices

### Slice 1: Support-Surface Truth Binding

Files likely to change:

- `beacon/utils/ceo_review_surface.py`
- adjacent support-surface helpers if they also bind umbrella/version features
- targeted tests for version-package truth binding

Outcome:

- support surfaces can review version-level umbrella lines without false `truth_refs_missing`

### Slice 2: Docs Structure Contract

Files likely to change:

- docs generation or scaffolding helpers
- version summary/change writers
- docs policy helpers if they exist

Outcome:

- Beacon understands semantic layers without eagerly creating the whole tree

### Slice 3: External Capability Registry

Files likely to change:

- `beacon/utils/project_skills.py`
- config/registry loaders
- capability selection helpers

Outcome:

- external governed sources can be registered, inspected, and selected

### Slice 4: Learning Writeback

Files likely to change:

- learning/runtime projection helpers
- skill execution summaries
- state/writeback utilities

Outcome:

- successful and failed compositions become reusable advisory assets

## Non-Goals

- no new primary lifecycle stage
- no heavy docs migration across all historical versions
- no eager creation of `context/`, `guidance/`, `delivery/`, `evidence/`, and `.machine/` in every version
- no expansion into a general-purpose skill marketplace

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`
- version: `v1.4.5`

### Source Refs
- prd: `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`
- user_story: `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`
- test_case: `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.5-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning-R3`
- transaction_id: `tx-65ab8f4d6f0876e36`
- source_hash: `sha256:b696025b56db67837853f4afbe023b25bb66b95a4227c4c68047f17481f64168`
- projection_seq: `1`
- version: `v1.4.5`
- feature: `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.5`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.5`
- feature_count: `2`
- transaction_id: `tx-d81faeff1a06960cc`
- source_hash: `sha256:7136fb953b18dd9ef00bd1ec41c02b4a35c50eead2a5290283abf6ead3435b64`

### Registered Feature Baselines
- `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition` | revision=`R1` | branch=`beacon/v1.4.5` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.5/.machine/execution/implementation-delivery-baseline-beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.json`
- `beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning` | revision=`R3` | branch=`beacon/v1.4.5` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.5/.machine/execution/implementation-delivery-baseline-beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.5-governed-external-skill-sources-and-learning-composition:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`
- version: `v1.4.5`

### Source Refs
- prd: `docs/beacon/archive/v1.4.5/prd/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- user_story: `docs/beacon/archive/v1.4.5/user-story/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`
- test_case: `docs/beacon/archive/v1.4.5/qa/test-cases/beacon-v1.4.5-governed-external-skill-sources-and-learning-composition.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.5-governed-external-skill-sources-and-learning-composition:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.5-governed-external-skill-sources-and-learning-composition:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.5-beacon-v1.4.5-governed-external-skill-sources-and-learning-composition-R1`
- transaction_id: `tx-b644a7643b4cbef21`
- source_hash: `sha256:6c5927c6db911904c6a66fb43c2aa110ccee615d083d5613c8944a17252b0ba6`
- projection_seq: `1`
- version: `v1.4.5`
- feature: `beacon-v1.4.5-governed-external-skill-sources-and-learning-composition`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.5`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.5-governed-external-skill-sources-and-learning-composition:END -->
