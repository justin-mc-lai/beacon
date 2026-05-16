# Change: beacon-v1.4.7-change-refreeze-one-shot-requirement-closure

**Version**: `v1.4.7`
**Status**: `implemented-and-verified`
**Generated**: `2026-05-16`
**Track**: `human-change-surface + one-shot-requirement-refreeze`

## Why This Change Exists

`beacon-change` is currently the correct human-facing router for frozen truth revision, but its public CLI still exposes the loop as a prepared route:

```text
change
-> reopen
-> revise
-> freeze
```

The operator still has to manually stitch the downstream requirement surfaces:

```text
prd
-> user-story
-> test-case
-> requirement_clarity
-> freeze
```

This change enters a narrower product requirement:

> Add a human-facing one-shot refreeze support surface that can drive a governed `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze` closure package without creating a new primary lifecycle stage.

## Delta

- add an explicit one-shot requirement-refreeze route for post-freeze changes
- keep `beacon-change` as the entry point or add a subordinate support skill under the change family
- make the chain operator-visible and auditable
- preserve fail-closed truth barriers until the full requirement package is refreshed
- avoid treating one-shot convenience as implementation, QA, or release completion

## Candidate Surface Shape

Allowed shapes:

- extend `beacon change` with a governed one-shot mode
- add a human subskill such as `beacon-change-refreeze`

The stable human-facing route is `beacon-change-refreeze`; it must delegate to `beacon change ... --refreeze-chain` rather than create a second refreeze implementation.

The surface must still route through existing truth surfaces:

```text
change
-> prd
-> user-story
-> test-case
-> requirement_clarity
-> freeze
```

It must not introduce a new public lifecycle stage between `test-case` and `implement`.

## Implementation Status

This change has been implemented and verified through the governed `beacon change ... --refreeze-chain` route.

The delivered package defines:

- admission conditions for one-shot refreeze
- generated/updated artifact set
- transaction metadata required across all touched truth surfaces
- failure behavior when any downstream surface cannot be safely refreshed
- operator-visible summary and next route after refreeze

## Out Of Scope

- automatic implementation after refreeze
- automatic QA or release execution
- bypassing `prd / user-story / test-case`
- treating generated drafts as frozen truth without requirement clarity verification

## Traceability

- `skills/beacon/beacon-change/SKILL.md`
- `beacon/commands/change.py`
- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.7/SUMMARY.md`
