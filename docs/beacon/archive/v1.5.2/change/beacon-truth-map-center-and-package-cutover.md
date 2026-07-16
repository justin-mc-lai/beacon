# Change: Feature Package Authoritative Cutover

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`
- reason: `promote feature package Markdown to normal canonical truth`

## Accepted Change

Beacon v1.5.2 switches normal production and consumption truth to feature-package Markdown through truth-map resolver.

## Removed Normal Authority

- `prd/`
- `user-story/`
- `qa/test-cases/`
- JSON twin projections as truth requirements

## Remaining Legacy Uses

- `doctor`: rebuild legacy surfaces from package truth.
- `change`: absorb legacy surfaces into package truth.

