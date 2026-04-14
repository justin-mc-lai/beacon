# Beacon Research Index

**Purpose**: provide a stable entrypoint for Beacon research materials that remain useful across versions, plus a map into version-bound research packs.

---

## 1. How to use this directory

Use `docs/beacon/research/` for research that is expected to stay useful across multiple release lines.

Good fit:

- external reference studies
- method / pattern analysis
- knowledge-plane design notes
- schema / governance concepts
- cross-version product reasoning

Not a good fit:

- single-release delivery notes
- one-off implementation closure artifacts
- version-specific bug or gate investigations that belong under `docs/beacon/<version>/research/`

Rule of thumb:

- if the note is mainly about a specific release line, put it under that version
- if the note describes a reusable pattern Beacon may keep citing later, put it here

---

## 2. Cross-version research

### Active long-lived notes

1. [Karpathy `LLM Wiki` pattern analysis](./beacon-karpathy-llm-wiki-pattern-analysis.md)
   - Why it matters:
     gives Beacon a reusable frame for compiled knowledge layers, `ingest/query/lint`, query-to-doc writeback, and schema-as-maintainer governance.

2. [Beacon multi-project isolation and learning brainstorm](./beacon-multi-project-isolation-and-learning-brainstorm.md)
   - Why it matters:
     proposes a `kernel / project capsule / distill plane` model for strict project isolation, human-thinking/agent-execution split, and reusable but controlled cross-project experience distillation.

3. [Beacon manager strong doc sync brainstorm](./beacon-manager-strong-doc-sync-brainstorm.md)
   - Why it matters:
     defines a separate `beacon-manager` tool/skill for binding multiple project `docs/beacon` trees into one personal GitHub knowledge repo with git-like `bind/pull/sync/status/reconcile/doctor` workflows and strong consistency rules.

4. [Beacon self-iteration and story-QA coverage study from awesome-design-md and autoagent](./beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md)
   - Why it matters:
     proposes a dual structure for Beacon: an asset plane for reusable QA baseline bundles and a bounded eval plane for policy-level self-iteration driven by story/AC coverage and false-complete reduction.

5. [Beacon memory and knowledge-plane study from mempalace](./beacon-memory-asset-eval-plane-study-mempalace.md)
   - Why it matters:
     argues for a raw-plus-structured memory model for Beacon, where important reasoning is preserved verbatim, organized into a navigable knowledge plane, and benchmarked for recall value rather than summarized away too early.

6. [Beacon completeness and maturity matrix](./beacon-completeness-maturity-matrix.md)
   - Why it matters:
     provides a concrete score-based assessment of Beacon's current product surfaces, skill/operator design, architecture responsibilities, and risk concentration, anchored explicitly on the `PRD → story → QA` mainline.

7. [Beacon maturity remediation roadmap](./beacon-maturity-remediation-roadmap.md)
   - Why it matters:
     translates the maturity matrix into an execution order, prioritizing mainline hardening, complexity reduction, asset packaging, and only then bounded self-iteration.

---

## 3. Version-bound research entrypoints

These directories contain research tied to specific release lines and should be read together with that version's `SUMMARY.md` and execution materials.

### v1.2.0

- [`docs/beacon/v1.2.0/research/`](../v1.2.0/research/)
  - Current notable topic:
    product-manager skills design analysis

### v1.1.12

- [`docs/beacon/v1.1.12/research/`](../v1.1.12/research/)
  - Current notable topics:
    practice boundary and learning-plane governance
    design governance and meta-harness closure
    requirement-anchor divergence closure
    external reference study against StatsClaw and awesome-design-md

### v1.1.9

- [`docs/beacon/v1.1.9/research/`](../v1.1.9/research/)
  - Current notable topic:
    Karpathy autoresearch evo translation for Beacon

### v1.1.8

- [`docs/beacon/v1.1.8/research/`](../v1.1.8/research/)
  - Current notable topics:
    gstack gap analysis
    three-track closure audit

### v1.1.6

- [`docs/beacon/v1.1.6/research/`](../v1.1.6/research/)
  - Current notable topics:
    external framework/reference reading pack
    autoresearch, gstack, openspec, bmad-method, memevolve, deer-flow

### Earlier lines

- [`docs/beacon/v1.1.1/research/`](../v1.1.1/research/)
- [`docs/beacon/v1.1.0/research/`](../v1.1.0/research/)
- [`docs/beacon/v1.0.3/research/`](../v1.0.3/research/)
- [`docs/beacon/v1.0.2/research/`](../v1.0.2/research/)
- [`docs/beacon/v1.0.1/research/`](../v1.0.1/research/)

Use these mainly for historical context, not as the first source for current product truth.

---

## 4. Suggested reading order

If you are trying to understand Beacon's long-horizon research direction:

1. Start with [Karpathy `LLM Wiki` pattern analysis](./beacon-karpathy-llm-wiki-pattern-analysis.md)
2. Then read [Beacon multi-project isolation and learning brainstorm](./beacon-multi-project-isolation-and-learning-brainstorm.md)
3. Then read [Beacon manager strong doc sync brainstorm](./beacon-manager-strong-doc-sync-brainstorm.md) for the independent cross-project doc-sync tool direction
4. Then read [Beacon self-iteration and story-QA coverage study from awesome-design-md and autoagent](./beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md)
5. Then read [Beacon memory and knowledge-plane study from mempalace](./beacon-memory-asset-eval-plane-study-mempalace.md)
6. Then read [Beacon completeness and maturity matrix](./beacon-completeness-maturity-matrix.md)
7. Then read [Beacon maturity remediation roadmap](./beacon-maturity-remediation-roadmap.md)
8. Then read [`docs/beacon/v1.1.12/research/`](../v1.1.12/research/) for the most recent governance-heavy release-line studies
9. Then read [`docs/beacon/v1.2.0/research/`](../v1.2.0/research/) for newer product-surface expansion work

If you are trying to solve a concrete versioned task:

1. Start with `docs/beacon/<version>/SUMMARY.md`
2. Read `docs/beacon/<version>/execution/index.md`
3. Only then drill into that version's `research/`

---

## 5. Maintenance rule

When adding a new research note:

1. decide whether it is cross-version or version-bound
2. place it in the correct directory
3. add a one-line entry here if it is cross-version
4. if it materially changes a version line, also update that version's `SUMMARY.md` or execution index as needed
