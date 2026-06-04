# Beacon Support Surface State Sink Paths

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`

## Canonical Envelope Paths

- `docs/beacon/archive/v1.4.3/.machine/execution/beacon-ceo-review-transaction.json`
- `docs/beacon/archive/v1.4.3/.machine/execution/beacon-design-review-transaction.json`
- `docs/beacon/archive/v1.4.3/.machine/execution/beacon-learn-transaction.json`

## Human Render Paths

- `docs/beacon/archive/v1.4.3/execution/beacon-ceo-review-transaction.md`
- `docs/beacon/archive/v1.4.3/execution/beacon-design-review-transaction.md`
- `docs/beacon/archive/v1.4.3/execution/beacon-learn-transaction.md`

## Runtime State Paths

- `.beacon/state/beacon-ceo-review-latest.json`
- `.beacon/state/beacon-design-review-latest.json`
- `.beacon/state/beacon-learn-latest.json`

## Optional History Paths

- `.beacon/transactions/beacon-ceo-review/<transaction-id>.json`
- `.beacon/transactions/beacon-design-review/<transaction-id>.json`
- `.beacon/transactions/beacon-learn/<transaction-id>.json`

## Path Rules

- machine sink stores the canonical envelope projection
- human sink stores operator-facing summary output
- runtime state stores only latest receipt and route recommendation
- transaction history, if enabled, stores append-only receipts

## Boundary Rule

No sink path above may be treated as a new truth root. Truth changes still route back into canonical requirement transactions.
