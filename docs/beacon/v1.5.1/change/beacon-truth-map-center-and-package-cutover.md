# Change: Beacon Truth Map Center and Package Cutover

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`
- reason: `freeze truth-map resolver center and MD-only truth-source direction`

## Accepted Change

v1.5.1 freezes the truth-map resolver center as the required preparation for v1.5.2 package-authoritative cutover.

## Frozen Boundary

- Truth map is CLI resolver/schema, not JSON truth.
- Feature-package Markdown is the future canonical truth source.
- MD-to-JSON multi-write projection is not a required product capability.
- JSON outputs are optional projection/diagnostic/rebuild evidence only.
- Old PRD/user-story/test-case are not retained as future production truth. They are rebuild/absorb surfaces only.

## Next Version Commitment

v1.5.2 must promote feature package Markdown to authoritative truth and route normal Beacon production/consumption through truth-map resolver.

