# Beacon v1.4.4 Architecture Blueprint

## Architecture Intent

`v1.4.4` makes Beacon's design quality more usable by default while preserving the lightweight human surface established in earlier lines.

The architecture goal is:

> Beacon should offer a restrained, reusable design baseline that improves UI/UX taste and interaction quality by default, but without turning design into a parallel command system or a large skill marketplace.

## Layer Placement

The existing architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.4` adds a small design-baseline contract inside the existing surface/projection boundary:

```text
frozen requirement truth
-> design-review rubric
-> template preset selection
-> prototype design-asset projection
-> implement consumes same design truth
-> qa verifies anti-drift and anti-AI baseline
```

## New Contract Focus

### Design Review Rubric Enrichment

Purpose:

- evaluate hierarchy, state clarity, interaction coherence
- evaluate baseline anti-AI UI/UX violations
- decide whether a feature can stay on default template baseline or needs explicit override reason

Boundary:

- cannot become a final visual approval surface
- cannot create a new truth root
- cannot expand into a full design skill family

### Template Preset Contract

Purpose:

- provide a fixed, small set of reusable design templates
- normalize design references into Beacon-owned preset truth
- keep template count intentionally small and operationally useful

Boundary:

- cannot become an open-ended style marketplace
- cannot require the upstream reference repo during runtime
- cannot bypass requirement truth or design-review sequencing

### Prototype Design Asset Projection

Purpose:

- project chosen preset and design rules into `DESIGN.md` and preview assets
- give implement/qa one stable design asset surface to consume

Boundary:

- prototype remains conditional and formal
- design assets are projections, not an independent editable truth root

## Template Catalog

`v1.4.4` freezes exactly 3 default templates:

1. `restrained-product`
   - baseline source: `apple`
   - intended surfaces: general product UI, settings, account, lightweight SaaS
2. `operator-console`
   - baseline source: `vercel`
   - intended surfaces: workbench, admin, project console, operational dashboards
3. `editorial-calm`
   - baseline source: `apple + vercel hybrid`
   - intended surfaces: docs-heavy pages, decision summaries, mixed content/product surfaces

## Non-Goals

- no new public primary command
- no `/audit /polish /distill /bolder ...` style Beacon command family
- no arbitrary style cloning
- no direct runtime dependency on `VoltAgent/awesome-design-md`
