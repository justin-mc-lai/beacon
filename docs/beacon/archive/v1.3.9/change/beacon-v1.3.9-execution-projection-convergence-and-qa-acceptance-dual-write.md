# Beacon Feature Change Document

- feature: `Beacon v1.3.9 execution projection convergence and QA acceptance dual-write`
- feature_slug: `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`
- version: `v1.3.9`
- status: `reopened-requirement-delta`
- previous_revision_id: `R2`
- revision_id: `R3`
- source_revision_id: `R2`
- reason: `add promised-vs-shipped drift gate and standalone non-generic PRD friction scenario`

## Scope
- requirement delta only
- tighten `prototype` non-template boundary
- upgrade QA acceptance from dual-write wording to canonical three-sink transaction wording
- align `status / doctor / gate / release` to the same transaction-blocking contract
- add formal promised-surface vs shipped-surface drift gate scenario
- add standalone PRD non-generic compile friction scenario

## Requirement Delta
- Added explicit requirement that `prototype auto` must not silently degrade to fixed-template output.
- Added explicit requirement that QA acceptance transaction includes runtime projection sink in the same transaction metadata/checksum contract.
- Added explicit requirement that `status / doctor / gate / release` consume and block on the same prototype/acceptance transaction contract.
- Added explicit requirement that Beacon compares promised operator surface against shipped implementation/review evidence and blocks pass/release when drift remains unresolved.
- Added explicit requirement that `beacon prd create` success path is version-aware and requirement-aware; generic placeholder output cannot count as a successful requirement compile.

## Added
- PRD / user-story / test-case delta for AC-012 to AC-013
- explicit `R3` requirement tightening before any further implementation or refreeze

## Removed / Reduced
- reduced ambiguity around whether template fallback can count as valid `prototype` success
- reduced ambiguity around whether QA acceptance dual-write can remain machine/human-only
- reduced ambiguity around whether release/gate may ignore promised-vs-shipped surface drift
- reduced ambiguity around whether PRD generation may still succeed with a generic placeholder shell

## Fixed
- none yet; this change brief only reopens frozen requirement truth and defines the delta to be implemented/refrozen later

## Traceability Refs
- `docs/beacon/archive/v1.3.9/prd/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `docs/beacon/archive/v1.3.9/user-story/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `docs/beacon/archive/v1.3.9/qa/test-cases/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `docs/beacon/archive/v1.3.9/.machine/execution/technical-implementation-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.json`
- `docs/beacon/archive/v1.3.9/execution/technical-implementation-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `docs/beacon/archive/v1.3.9/.machine/execution/implementation-summary-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.json`
- `docs/beacon/archive/v1.3.9/execution/implementation-summary-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
