---
name: beacon-prototype-reconcile
description: Reconciles Beacon prototype/doc artifacts against an existing frontend implementation without changing Beacon core. Use when a project already has UI code, Beacon prototype review is drifting from implementation truth, or takeover work needs docs/prototype/code consistency review.
metadata:
  author: Beacon CLI
  version: "1.1.12"
  organization: Beacon
  date: April 2026
  abstract: OMX-assisted project-level skill for extracting implementation truth, reviewing docs/prototype/code drift, patching prototype artifacts, and handing closure back to Beacon review/gate.
---

# Beacon Prototype Reconcile

Use this skill when Beacon's normal `prototype/review/gate` flow is not enough because the target project already has meaningful frontend code that must be treated as implementation truth.

This skill does **not** change Beacon core. It adds a project-level OMX workflow around Beacon.

## Use This When

- a Beacon prototype cannot reliably trace back to existing UI code
- docs, prototype artifacts, and implementation are drifting
- takeover work needs a code-backed page/route/component inventory
- `implementation-map.json` is mostly synthetic / unbound
- you need OMX-style deep review before handing back to Beacon review/gate

## Do Not Use This For

- generic code review unrelated to Beacon artifacts
- replacing Beacon's requirement/prototype/release lifecycle
- framework-agnostic static analysis across arbitrary repos

## Truth Model

Treat these layers separately, then reconcile them:

1. **Requirement truth**
   - `docs/beacon/<version>/user-story/<feature>.md`
   - `docs/beacon/<version>/prd/<feature>.md`
2. **Prototype truth**
   - `docs/beacon/<version>/prototype/<feature>/...`
3. **Implementation truth**
   - frontend source tree
   - route definitions / navigation helpers
   - query / params / tab consumers
   - shared components
   - theme/token sources
4. **Gate truth**
   - `beacon prototype review`
   - `beacon review design`
   - `beacon gate check`

Never collapse these into one source. Reconcile them explicitly.

## Quick Start

### Standard workflow

1. Identify the Beacon feature/version and target frontend project.
2. Extract implementation truth from the codebase.
3. Produce drift artifacts under `docs/beacon/<version>/execution/`.
4. Patch prototype artifacts only where code truth supports the change.
5. Re-run Beacon review/gate on the patched artifacts.

### Mandatory execution outputs

Write these execution artifacts:

- `implementation-truth-<feature>.json`
- `implementation-truth-<feature>.md`
- `route-closure-audit-<feature>.json`
- `route-closure-audit-<feature>.md`
- `prototype-gap-list-<feature>.json`
- `prototype-gap-list-<feature>.md`
- `prototype-patch-report-<feature>.md`

## Workflow

Detailed phase guidance lives in [references/workflow.md](references/workflow.md).

High-level execution order:

1. **Extract implementation truth**
2. **Review docs/prototype/code drift**
3. **Patch prototype artifacts**
4. **Hand back to Beacon review/gate**

## Allowed Patch Targets

You may update:

- `docs/beacon/<version>/prototype/<feature>/implementation-map.json`
- `docs/beacon/<version>/prototype/<feature>/ui-style-analysis.json`
- `docs/beacon/<version>/prototype/<feature>/ui-style-analysis.md`
- `docs/beacon/<version>/prototype/<feature>/page-specs/*.json`
- `docs/beacon/<version>/prototype/<feature>/pages/*.html`
- `docs/beacon/<version>/prototype/<feature>/states/*.html`
- `docs/beacon/<version>/execution/*.json`
- `docs/beacon/<version>/execution/*.md`

Do **not** silently rewrite requirement intent in user-story/PRD unless the task explicitly asks for requirement changes.

## Drift Codes

Use these reason codes in execution artifacts when applicable:

- `implementation_truth_missing`
- `doc_route_missing_in_code`
- `code_route_missing_in_docs`
- `dead_jump_in_docs`
- `param_contract_drift`
- `tab_landing_drift`
- `prototype_surface_unimplemented`
- `component_dependency_undocumented`
- `design_token_drift`

## Verification

After patching, run:

```bash
beacon prototype review "<feature>" --project "<project_root>" --version <version>
beacon review design "<feature>" --project "<project_root>" --version <version>
```

If the project uses strict Beacon release gating, also run:

```bash
beacon gate check release --project-root "<project_root>" --version <version> --strict
```

## Example

See [examples/slow-uni-bmtop.md](examples/slow-uni-bmtop.md) for the recommended first-pass workflow against `slow_uni_bmtop`.

## Guidelines

- Keep Beacon as the lifecycle container; use OMX as the deep review engine.
- Prefer evidence from code over inference from stale docs.
- Mark uncertain bindings as uncertain; do not invent false certainty.
- Patch the smallest useful set of prototype artifacts first.
- Separate “docs wrong”, “prototype stale”, and “implementation incomplete”.
- Final report must list changed files, remaining drift, and what Beacon still cannot natively enforce.
