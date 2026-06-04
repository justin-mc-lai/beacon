# Source Architecture: UI/UX Externalization, Prototype Adapter, Version Visualization

**Feature**: `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
**Version**: `v1.4.9`
**Status**: `frozen`

## Architecture

This feature changes Beacon's ownership boundary, not the UI rendering stack.

```text
Human UI/UX intent
-> ui-ux-dev router
-> upstream design execution skill
-> accepted UI/UX result
-> Beacon adapter binding
-> Markdown requirement truth
-> minimal machine state / gate diagnostics
```

## Components

### `ui-ux-dev`

Owns:

- `explore`
- `system`
- `review`
- `polish`
- `extract`
- `library`

Does not own:

- Beacon lifecycle
- Beacon gate verdicts
- PRD / user-story / test-case canonical truth

### Beacon prototype adapter

Owns:

- accepted design result intake
- screen intent summary
- state visibility contract
- interaction handoff mapping
- truth binding diagnostics

Does not own:

- UI/UX exploration
- design-system recommendation
- visual polish execution
- high-fidelity prototype generation

### Version visualization projection

Owns:

- business flow projection
- state-machine projection
- three-piece truth map
- truth bindings

Does not own:

- canonical promise
- acceptance criteria
- test truth
- release verdict

## Migration Boundary

Existing `prototype` bundles remain compatibility artifacts.

New v1.4.9 behavior should:

- mark design-generation commands as deprecated or adapter-only
- route UI/UX execution requests to `ui-ux-dev`
- keep gate checks focused on adapter truth bindings, not visual generation artifacts

## Failure Rules

- If a feature has accepted UI/UX output but no adapter binding, implementation must block.
- If business flow or state-machine projection lacks truth bindings, requirement clarity must block.
- If a design review finding changes promise or acceptance, route to `beacon-change`.
- If `ui-ux-dev` is missing on a fresh machine, route to `ui-ux-dev-bootstrap`; do not silently fall back to Beacon-native design generation.
