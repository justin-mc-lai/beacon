# Research: Beacon v1.2.0 project-skill workflow deep analysis

**Date**: 2026-04-08  
**Source input**: `.research/beacon-project-skill-workflow-deep-analysis-2026-04-08.md`  
**Purpose**: absorb the deeper project-skill / prototype-anchor findings into the frozen v1.2.0 requirement line.

---

## 1. Imported problem statement

The deep analysis starts from three capability gaps:

1. project-level skill workflow is still too manual
2. prototype outputs are not yet strongly enough anchored to PRD/story truth
3. secondary-development / takeover analysis needs stronger bounded discovery support

The first two are inside the v1.2.0 center.
The third must stay carefully bounded so it does not turn Beacon into a generic analysis platform.

---

## 2. Imported findings for `beacon skill discover`

### 2.1 Existing strengths to reuse

The current repo already has:

- builtin skill registry
- external skill binding via `beacon.config.yaml`
- project profile system
- feature-profile binding
- orchestration nodes with capability / evidence contracts
- contract drift detection
- evidence gate checks

### 2.2 Requirement gaps that belong in v1.2.0

The deep analysis adds three concrete requirement deltas:

1. **template library** for common project types
2. **memory-aware recommendation inputs** for project-skill discovery
3. **explainable preview/apply flow** instead of opaque or auto-writing discovery

These deltas are now part of the v1.2.0 project-skill workstream.

### 2.3 Template guidance imported from research

Candidate starter-pack families include:

- `web-fullstack`
- `mobile-app`
- `api-service`
- `data-pipeline`
- `ml-model`
- domain-specific second-development packs such as ERP / CMS variants

The requirement package does not need all of these implemented yet.
It does need the **template-library direction and contract** to be explicit.

---

## 3. Imported findings for prototype anchoring

The deep analysis adds two important requirement refinements:

1. prototype validation should be both **forward** (`PRD/story → prototype`) and **reverse** (`prototype → PRD/story`)
2. when UI structure exists but PRD/story UI-module information is incomplete, Beacon should surface that gap explicitly and guide template completion

This strengthens the already-frozen subordinate prototype workstream without making prototype the product center.

---

## 4. Imported boundary decision on generic `beacon discover`

The internal research also sketches a broader codebase analysis command:

```text
beacon discover <target>
```

That idea is useful, but for v1.2.0 it should be treated as:

- a future advanced/labs surface
- a bounded second-development research direction
- **not** a core frozen deliverable of the v1.2.0 requirement line

The versioned requirement package therefore imports the insight, but freezes the narrower decision:

> v1.2.0 centers `beacon skill discover`, not a generic core `beacon discover` platform.

---

## 5. Resulting requirement implications

The requirement package should explicitly preserve:

1. preview-first `skill discover`
2. explainable recommendations with evidence and scores
3. bounded discovery state and config merge semantics
4. shared linkage across `help / profile / skill doctor`
5. template-library and memory-aware recommendation direction
6. forward + reverse prototype-anchor validation expectations
7. deferral of generic codebase-wide discover into future advanced scope

---

## 6. Final conclusion

This imported research does not widen the v1.2.0 center.
It sharpens it:

> project-skill onboarding, prototype anchoring, and future second-development discovery should all be expressed as bounded, traceable support surfaces under the `PRD → user-story → QA` mainline.
