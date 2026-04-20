# Boundaries: Beacon v1.3.5 Prototype Wireframe Freeze Line

**Version**: `v1.3.5`  
**Status**: `frozen-pending-implementation`  
**Date**: `2026-04-20`

## 1. One-line boundary

`v1.3.5` only solves prototype-stage requirement closure for Beacon.  
It does not deliver the final visual management console product.

```text
requirement truth
  = prd + user-story + test-case
prototype freeze
  = requirement-driven wireframe package
runtime projection
  = canonical -> human/machine/sqlite transactional projection
```

## 2. In scope

- `prototype` as a formal lifecycle stage between `test-case` and `implement`
- wireframe-only prototype semantics
- removal of HTML high-fidelity prototype requirement from Beacon primary line
- route/state/component closure artifacts for freeze
- requirement-driven mapping from page artifacts to AC/TC
- canonical-first multi-sink write rules:
  - canonical envelope
  - human-readable projection
  - machine-readable projection
  - sqlite runtime projection
- anti-drift fields and verification contract:
  - `source_hash`
  - `projection_seq`
  - `transaction_id`
  - `committed_at`
  - `sink_checksums`

## 3. Out of scope

- final visual style system, high-fidelity UI, or design polishing
- complete PocketBase management console implementation
- runtime lane feature delivery for `implement team/single/ralph`
- replacing docs-based requirement truth with sqlite truth
- exposing raw host runtime internals to human-facing board views

## 4. Truth boundary

Authoritative truth remains:

- `docs/beacon/v1.3.5/prd/`
- `docs/beacon/v1.3.5/user-story/`
- `docs/beacon/v1.3.5/qa/test-cases/`
- `docs/beacon/global-boundaries.md`

Projected views only:

- `.machine` wireframe/test matrices
- sqlite runtime projection
- derived status/review snapshots

## 5. Transaction and anti-drift boundary

Any multi-sink write in prototype/runtime projection must follow:

1. `prepare`
2. `validate`
3. `commit`
4. `publish`
5. `verify`

If any sink fails or hash mismatches are detected:

- status must report `drift` or `transaction_failed`
- freeze must fail
- release pass must be blocked

No partial silent success is allowed.

## 6. Human-surface boundary

Human-visible output remains lifecycle-first and minimal:

- current stage
- progress
- blockers
- next action
- requirement-closure state

Machine diagnostics stay in machine artifacts and doctor diagnostics.

## 7. Release-line guardrail

`v1.3.5` is a requirement/prototype closure line.  
It must freeze requirement-facing wireframe contracts before `v1.3.6` visual-console implementation expands product surfaces.
