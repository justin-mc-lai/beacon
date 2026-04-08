# Research: Beacon maturity remediation roadmap

**Date**: 2026-04-08  
**Intent**: turn the current maturity assessment into a concrete remediation and strengthening roadmap, anchored on Beacon's mainline:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

This roadmap is not a generic backlog.
It is a sequencing recommendation for what Beacon should strengthen next if the goal is to become a more complete product-governance system without drifting into a generic agent platform.

---

## 1. Executive summary

Beacon does **not** need “more features” first.

Beacon needs:

1. stronger packaging of the features it already has
2. lower complexity in the orchestration/gate core
3. more explicit `PRD/story/QA`-anchored benchmark and asset layers

That means the roadmap should follow three priorities:

### Priority A — protect the root chain

Strengthen:

- PRD-to-story fidelity
- story-to-QA coverage
- evidence-to-gate closure

### Priority B — reduce structural maintenance risk

Refactor:

- oversized command modules
- writeback/state coupling
- operator ambiguity between product core and advanced surfaces

### Priority C — productize advanced surfaces only after A/B

Then, and only then, expand:

- self-iteration
- memory / knowledge plane
- reusable asset packs

---

## 2. First-principles rule

Every roadmap item should answer one question:

> Does this make the `PRD → story → QA → evidence → closure` chain more reliable, more explainable, or more reusable?

If not, it is not a roadmap priority.

This rule excludes a lot of tempting but lower-value work:

- generic agent-runtime expansion
- unbounded memory features
- extra command proliferation
- visual polish detached from delivery truth

---

## 3. Current diagnosis recap

From the maturity matrix, Beacon currently looks like this:

### Strongest areas

- requirement kernel
- evidence kernel
- QA / review / gate logic
- versioned docs package

### Most fragile areas

- command concentration in `workflow.py` and `gate.py`
- packaging lag between internal capability and external usability
- incomplete productization of self-iteration / knowledge layers

### Most important strategic risk

Beacon's advanced layers can outgrow its mainline clarity if they are not repeatedly re-anchored to:

```text
PRD
→ story
→ QA
```

---

## 4. Roadmap structure

The roadmap is split into four phases.

## Phase 1 — Mainline hardening

Goal:

- make the core chain harder to drift
- make coverage and traceability more explicit

### 1.1 Formalize the `PRD → story → QA` anchor contract

Deliverables:

- a formal anchor contract doc
- explicit required mappings:
  - PRD requirement → story
  - story AC → test cases
  - scenario families → evidence expectations

Why first:

- this is the root of every other system

### 1.2 Package story-QA baseline bundles

Deliverables:

- standard baseline bundle schema
- one human-readable bundle view
- one machine-readable bundle view

Suggested bundle contents:

- `prd/<feature>.md`
- `user-story/<feature>.md`
- `.machine/user-story/<feature>.json`
- `qa/test-cases/<feature>.md`
- `.machine/qa/*.ac-test-matrix.json`
- `.machine/qa/*.story-scenario-map.json`
- `.machine/qa/*.qa9-matrix.json`
- coverage/evidence scorecard

Why first:

- this is the easiest way to turn internal capability into reusable product truth

### 1.3 Strengthen coverage scoring

Deliverables:

- explicit PRD-to-story traceability score
- story coverage score
- AC coverage score
- scenario-family coverage score
- evidence closure score
- false-complete score

Why first:

- coverage should stop being only “tests exist” and become “delivery truth exists”

---

## Phase 2 — Core complexity reduction

Goal:

- reduce maintenance risk in the orchestration core

### 2.1 Split `workflow.py` into stage modules

Current problem:

- workflow logic is too concentrated
- planning, continuation, terminal-state logic, and handoff paths are too co-located

Target:

- stage-specific modules or subservices for:
  - planning
  - progression
  - stage execution dispatch
  - closure bookkeeping

Expected result:

- lower local complexity
- easier test targeting
- safer changes

### 2.2 Split `gate.py` into gate domains

Current problem:

- release, stage-local, evidence, coverage, lifecycle, and implementation-plan checks are densely mixed

Target gate domains:

- requirements gate
- QA/coverage gate
- implementation-plan gate
- release evidence gate
- memory closure gate

Expected result:

- better explainability
- easier future benchmark mapping

### 2.3 Clarify writeback ownership

Current problem:

- many surfaces depend on writeback consistency
- user-facing closure can diverge from memory lifecycle state

Target:

- define writeback ownership per stage
- define which artifacts are authoritative for:
  - status
  - help
  - review
  - gate

Expected result:

- less “docs complete but lifecycle says not_started” drift

---

## Phase 3 — Asset-plane productization

Goal:

- convert advanced capability into reusable packages instead of hidden internal power

### 3.1 Introduce bundle-first examples

Deliverables:

- example requirement package bundles
- example implementation-plan bundles
- example review/gate bundles

This should follow the lesson from `awesome-design-md`:

- one artifact type
- fixed package structure
- easy to copy, inspect, and compare

### 3.2 Add project-adapter starter packs

Deliverables:

- profile starter pack
- verify starter pack
- delivery evidence starter pack
- adapter boundary checklist

Why:

- project execution adapters are structurally present, but still not low-friction enough

### 3.3 Add scorecard bundles

Deliverables:

- QA scorecard bundle
- release scorecard bundle
- review summary bundle

Why:

- these make “evidence-first” legible to users, not just to maintainers

---

## Phase 4 — Bounded self-iteration and knowledge plane

Goal:

- only after the mainline and packaging are stable, add controlled self-improvement surfaces

### 4.1 Add a bounded eval plane

Allowed subject surfaces:

- `qa_policy`
- `scenario_policy`
- `coverage_policy`
- `review_policy`
- `rewrite_policy`

Explicitly not allowed:

- arbitrary repo-wide mutation
- project-specific execution commands
- unbounded runtime orchestration changes

### 4.2 Add a structured knowledge plane

Suggested layers:

- raw reasoning artifacts
- compiled knowledge pages
- machine-readable indices

But the navigation order must remain:

```text
PRD first
→ story
→ QA / evidence
→ supporting research / memory
```

### 4.3 Benchmark the advanced layers

Metrics should be tied to mainline outcomes:

- PRD-to-story fidelity
- story/AC coverage gains
- evidence closure gains
- false-complete reduction

This is the main lesson from `autoagent` and `mempalace`:

- advanced systems only become product-grade once their gains are benchmarked honestly

---

## 5. Prioritization table

| Priority | Item | Why |
|---------|------|-----|
| P0 | Anchor contract for `PRD → story → QA` | Root product truth |
| P0 | Story-QA baseline bundle | Converts core capability into reusable asset |
| P0 | Coverage score expansion | Makes QA closure measurable in the right dimensions |
| P1 | `workflow.py` split | Reduces maintenance risk in mainline orchestration |
| P1 | `gate.py` split | Improves explainability and future evolution safety |
| P1 | Writeback ownership contract | Reduces lifecycle/state drift |
| P2 | Example bundles | Improves product usability and proof surface |
| P2 | Project-adapter starter packs | Makes project-aware execution more adoptable |
| P3 | Bounded eval plane | Advanced capability, but only after mainline stabilization |
| P3 | Structured knowledge plane | Valuable, but must remain subordinate to root chain |

---

## 6. What should not happen next

The following are specifically the wrong next moves:

### 6.1 Do not expand command count casually

Beacon already has enough command surface.
The next win is better consolidation, better bundles, and better explainability.

### 6.2 Do not treat memory as a new center

Memory is not the center.
`PRD → story → QA` remains the center.

### 6.3 Do not make self-iteration repo-wide

Beacon should not adopt a free-form “self-improving everything” model.
Only bounded policy surfaces should ever be evolvable.

### 6.4 Do not let prototype/design overshadow the core

Design governance is useful, but it is still a support layer.
Beacon's product center is delivery truth, not prototype aesthetics.

---

## 7. Suggested concrete next documents

If continuing immediately, the strongest next artifacts to create are:

1. `Beacon PRD-story-QA anchor contract`
2. `Beacon story-QA baseline bundle contract`
3. `Beacon coverage scorecard contract`
4. `Beacon workflow-core decomposition plan`
5. `Beacon gate-domain decomposition plan`

That sequence preserves the right order:

```text
mainline contract
→ asset package
→ measurement contract
→ complexity reduction
→ advanced evolution
```

---

## 8. Final recommendation

The next stage for Beacon should not be described as “adding more capabilities.”

It should be described as:

> hardening, packaging, and benchmarking the `PRD → story → QA → evidence → closure` chain, then cautiously allowing bounded evolution around it.

That is the shortest path from:

- a strong workflow kernel

to:

- a mature product governance system.

