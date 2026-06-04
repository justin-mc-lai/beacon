# Beacon v1.4.0 Boundaries

## In Scope

- lightweight kernel refactor without losing Beacon base capabilities
- truth / contract / projection / support surface separation
- minimal machine contract for `implement / qa / gate / release`
- formal `change` transaction kernel
- Codex `goal` as optional execution capability
- Ralph / verification / QA handoff closure alignment
- human-readable task ledger as implementation projection
- explicit global-boundaries human support surface
- skill taxonomy and skill visibility governance

## Out of Scope

- adding a new public lifecycle stage
- replacing frozen markdown truth with database truth
- allowing goals, checkboxes, or boards to define completion truth
- deleting learning, memory, metadata, archive, or host-runtime base kernels
- full domain productization for media/copy/novel in this version
- rewriting Beacon into a non-Python runtime as the primary optimization strategy

## Explicit Constraints

- `docs/beacon/<version>/**/*.md` remains the only canonical frozen truth root
- `implement` remains the only implementation entry
- `qa` remains the only acceptance entry
- `gate` remains the final blocking and completion judge
- projection layers may read compiled contract but may not reverse-write truth
- human boundary surface may explain, calibrate, and route, but may not freely rewrite canonical global truth
- default public skill surface must remain intentionally small and version-frozen
