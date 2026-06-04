# Beacon v1.4.3 Architecture Blueprint

## Architecture Intent

`v1.4.3` strengthens Beacon's evidence-first positioning by extending evidence discipline from delivery governance into upstream decision surfaces.

The architecture goal is:

> Beacon should not only prove what was built and verified. It should also challenge what is worth defining, clarify how UI/UX decisions are made, and visibly reuse prior learning before implementation begins.

## Layer Placement

The existing `v1.4.0` architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.3` adds a governed decision-surface projection between the Truth Layer and the public human support surfaces:

```text
problem/context signal
-> ceo-review challenge
-> frozen requirement truth
-> design-review challenge
-> prototype freeze / handoff
-> implement / qa / release
-> learning audit / recall
-> next-run support-surface explanation
```

## New Surface Families

### CEO Review Surface

Purpose:

- challenge problem framing
- challenge scope
- support `expand / hold / reduce / reframe`
- route accepted changes back into canonical truth surfaces

Boundary:

- cannot freeze truth directly
- cannot bypass `change`
- cannot redefine completion truth

### Design Review Surface

Purpose:

- challenge UI/UX direction
- review page hierarchy, state clarity, and interaction coherence
- prepare safe entry into conditional `prototype`

Boundary:

- cannot become final product UI delivery
- cannot replace `prototype` handoff truth

### Learn Surface

Purpose:

- expose learning visibility
- support pruning, downgrade, conflict display, and staleness handling
- make skill-specific learning injection auditable

Boundary:

- learning remains advisory
- learning cannot override truth, gate, or release verdict

## Prototype Boundary Clarification

`prototype` remains a conditional formal stage only when real UX/UI handoff is required.

In `v1.4.3`, its scope is tightened to:

- requirement-driven wireframe freeze
- route/state/interaction handoff
- UX contract projection

It is explicitly not:

- CEO-grade challenge
- design final approval
- default UI deliverable authority

## Support-Surface Explainability Contract

`help / status / ask / deep` should be able to explain:

1. why the current route is recommended
2. what evidence is still missing
3. which learning was considered
4. whether that learning is stale or conflicting
5. what next step will produce additional evidence

## Non-Goals

- No new primary lifecycle stage
- No second truth root
- No automatic truth rewrite from review surfaces
- No learning-driven gate override
- No promotion of `v1.4.3` to runtime release line during requirement freeze

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.3`
- feature_count: `1`
- transaction_id: `tx-ff4285b8f7359e26d`
- source_hash: `sha256:91258c08d086338210d266ae6d1affe3a6341d5fcc190859942db80f3ae20985`

### Registered Feature Baselines
- `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation` | revision=`` | branch=`beacon/v1.4.3` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/archive/v1.4.3/.machine/execution/implementation-delivery-baseline-beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
- version: `v1.4.3`

### Source Refs
- prd: `docs/beacon/archive/v1.4.3/prd/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- user_story: `docs/beacon/archive/v1.4.3/user-story/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`
- test_case: `docs/beacon/archive/v1.4.3/qa/test-cases/beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.3-beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation-r0`
- transaction_id: `tx-447ec10ea369da4ad`
- source_hash: `sha256:cd923021eaa02740f821846cd9f6921507c117ce245d47c704c260e04004d04f`
- projection_seq: `1`
- version: `v1.4.3`
- feature: `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.3`
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
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation:END -->
