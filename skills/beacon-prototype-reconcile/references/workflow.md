# Beacon Prototype Reconcile Workflow

## Phase 1: Extract implementation truth

Collect evidence from the target frontend project:

- actual pages
- actual route entrypoints
- navigation edges
- query / params / tab consumers
- shared component dependencies
- theme/token sources

Recommended sources for UniApp/Vue projects:

- `src/pages/**`
- `src/subPages/**`
- `pages.config.ts`
- route helpers / navigation wrappers
- `src/components/**`
- `src/App.vue`
- theme/token files

Write:

- `implementation-truth-<feature>.json`
- `implementation-truth-<feature>.md`

## Phase 2: Review drift

Compare:

1. docs required pages vs actual pages
2. docs route closure intent vs actual navigation edges
3. docs param expectations vs actual parameter consumption
4. prototype page specs vs actual page/component structure
5. prototype implementation map vs actual route targets
6. prototype style analysis vs actual token/theme usage

Write:

- `route-closure-audit-<feature>.json`
- `route-closure-audit-<feature>.md`
- `prototype-gap-list-<feature>.json`
- `prototype-gap-list-<feature>.md`

## Phase 3: Patch prototype artifacts

Patch only where code truth supports the change.

Priority order:

1. `implementation-map.json`
2. `ui-style-analysis.json/.md`
3. `page-specs/*.json`
4. `pages/*.html`
5. `states/*.html`

Write:

- `prototype-patch-report-<feature>.md`

## Phase 4: Hand back to Beacon

Run:

```bash
beacon prototype review "<feature>" --project "<project_root>" --version <version>
beacon review design "<feature>" --project "<project_root>" --version <version>
```

Optional strict closure:

```bash
beacon gate check release --project-root "<project_root>" --version <version> --strict
```

## Reporting Requirements

The final report must separate:

- requirement drift
- prototype drift
- implementation gaps
- Beacon-native failures
- remaining uncertain bindings
