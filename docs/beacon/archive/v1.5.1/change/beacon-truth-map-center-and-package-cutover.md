# Change: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`
- reason: `freeze truth-map resolver center and MD-only truth-source direction`

## Accepted Change

v1.5.1 freezes the truth-map resolver center as the required preparation for v1.5.2 package-authoritative cutover.

Accepted source-driven supplement: v1.5.1 also absorbs machine JSON convergence. Requirement-derived `.machine` JSON must be regenerated from resolver-selected Markdown, carry source hashes and role labels, and fail closed when stale. Runtime/process JSON remains allowed as execution record and does not require Markdown twins.

Accepted governance supplement: v1.5.1 also absorbs a version governance resolver layer. The truth-map resolver must resolve both feature truth and version governance truth. Version-level materials such as global boundaries, summary, execution governance, source architecture, release notes, metadata, manifests, material audit, QA, and release generated state must be classified and read through resolver-first routes. They must not be shoved into `features/<slug>/`, and manifest/index JSON must not become authority.

## Frozen Boundary

- Truth map is CLI resolver/schema, not JSON truth.
- Feature-package Markdown is the future canonical truth source.
- Version governance truth remains version-level Markdown/governance state, but it must be resolved through the same truth-map resolver center.
- MD-to-JSON multi-write projection is not a required product capability.
- JSON outputs are optional projection/diagnostic/rebuild evidence only.
- Manifest, material-audit, QA, release, and status outputs are generated governance indexes/state, not truth authority.
- Old PRD/user-story/test-case are not retained as future production truth. They are rebuild/absorb surfaces only.
- Requirement-derived `.machine` JSON is generated state/evidence, not truth authority.
- Runtime/process JSON such as `.beacon/*.json` and `.jsonl` remains execution record, not requirement truth.

## Next Version Commitment

v1.5.2 must promote feature package Markdown to authoritative truth and route normal Beacon production/consumption through truth-map resolver.
