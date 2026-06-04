# Beacon v1.4.7 Architecture Blueprint

## Architecture Intent

`v1.4.7` takes the `v1.4.6` anti-drift line and promotes the next layer of operator-facing capability into the runtime release line.

The architecture goal is:

> Keep Beacon's truth/evidence/gate kernel hard, while making the host entry, support-surface family, and bounded automation runtime significantly more usable without turning them into operation scripts or uncontrolled lifecycle sprawl.

## Layer Placement

The architecture remains:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.7` does not add a new layer.
It strengthens coordination between the surface and kernel layers:

```text
host meta-protocol
-> support-surface constitution
-> bounded automation closure-state kernel
-> support-review / truth-refreeze / promotion-proof routing
-> existing truth/evidence/gate governance
```

## Promoted Runtime Focus

### 1. Host Meta-Protocol

Purpose:

- make the top-level `beacon` skill route by decision surface
- keep the public chain compact
- make support-vs-truth-vs-gate boundaries legible to humans

Boundary:

- does not become a full manual
- does not replace frozen requirement truth
- does not expose runtime internals as the default path

### 2. Horizontal Engineering Support Surfaces

Purpose:

- widen practical engineering support beyond brainstorm/deep/review basics
- give operators narrower support routes for context, source anchoring, doubt, security, performance, ADR, and debug recovery

Boundary:

- support surfaces remain non-truth, non-gate, non-stage
- support output that changes frozen truth must route back through `change`

### 3. Bounded Automation Closure-State Kernel

Purpose:

- move automation from a loose QA feedback helper to a bounded runtime kernel
- preserve issue inheritance, queue revision semantics, execution lease safety, and stale-writer rejection
- make bounded round state visible to operators without widening lifecycle authority

Boundary:

- no autonomous deep/refreeze/release execution
- no silent truth mutation
- no bypass of implement/qa/release gates

### 4. Support-Review / Truth-Refreeze / Promotion-Proof Routing

Purpose:

- distinguish support review from plain repair loops
- make truth recompilation barriers explicit
- separate closure supplements from promotion candidates

Boundary:

- automation may surface promotion-grade proof hooks
- automation may not grant release authority by itself

## Release-Line Consequence

`v1.4.7` is the current runtime/docs line because the following are now true:

- version truth is promoted
- host-visible skill routing is aligned to this line
- required execution docs exist for the active line
- targeted QA and real-project validation confirm the promoted line behaves correctly

## Non-Goals

- no new public lifecycle stage
- no conversion of support skills into scripted operation playbooks
- no autonomous closure-loop release agent
- no weakening of truth freeze or evidence-first release gates
