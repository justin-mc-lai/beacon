# Beacon Support Surface Transaction Contract

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`
- applies_to:
  - `beacon-ceo-review`
  - `beacon-design-review`
  - `beacon-learn`

## Purpose

Define one shared transaction format for support/review surfaces so Beacon can keep:

- canonical single-source writeback
- human-readable review output
- machine-readable routing output
- explicit blocked reasons
- explicit next-route rendering

without letting any support surface become a second truth root.

## Transaction Model

Every support-surface run must produce one canonical envelope and then project it into:

1. machine sink
2. human sink
3. runtime state sink

Projection is one-way only:

```text
surface run
-> canonical envelope
-> machine sink
-> human sink
-> runtime state sink
```

Human or runtime projections may not overwrite the canonical envelope.

## Canonical Envelope Required Fields

- `schema_version`
- `transaction_id`
- `surface`
- `mode`
- `version`
- `feature`
- `status`
- `decision`
- `reason_codes`
- `truth_refs`
- `evidence_refs`
- `route_decision`
- `next_route`
- `writeback_targets`
- `blocked`
- `blocked_reason`
- `operator_visible_summary`
- `created_at`

## Surface Status Values

- `advisory`
- `accepted_for_writeback`
- `blocked`
- `deferred`

## Decision Value Rules

- `beacon-ceo-review`: `expand | hold | reduce | reframe`
- `beacon-design-review`: `ready_for_prototype | needs_design_revision | prototype_not_required`
- `beacon-learn`: `recall | audit | prune`

The `decision` field must remain surface-specific, but the outer transaction shape must remain shared.

## Machine Sink Contract

The machine projection must include:

- canonical envelope identity
- structured route decision
- normalized reason codes
- writeback targets
- truth binding
- blocked state

Recommended family:

```text
docs/beacon/<version>/.machine/execution/<surface>-transaction.json
```

## Human Sink Contract

The human projection must include:

- visible decision summary
- why this route is recommended
- affected truth surfaces
- blocked reason if present
- next command to run

It must hide low-level transaction metadata by default.

Recommended family:

```text
docs/beacon/<version>/execution/<surface>-transaction.md
```

## Runtime State Sink Contract

Runtime state is allowed to store:

- transaction receipt
- latest route recommendation
- latest blocked reason
- last applied learning influence

Runtime state is not allowed to redefine:

- frozen requirement truth
- release truth
- QA truth

## Writeback Transaction Rule

If a support-surface result is accepted, the envelope must route into a formal writeback transaction instead of directly editing truth.

Allowed path:

```text
support surface
-> canonical envelope
-> accepted_for_writeback
-> beacon-change / prd / user-story / test-case
-> formal truth transaction
```

Forbidden path:

```text
support surface
-> freeform truth overwrite
```

## Blocked Result Rule

When blocked, the envelope must still be committed with:

- `blocked: true`
- `blocked_reason`
- `reason_codes`
- `next_route`

Blocked runs must not disappear from the record.

## Next-Route Rendering Rule

Each committed transaction must render both:

- `next_route.command`
- `next_route.why`

Optional:

- `next_route.priority`
- `next_route.prerequisites`

## Acceptance Binding

This contract is shared execution governance for:

- `beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface`
- `beacon-v1.4.3-design-review-surface-and-prototype-governance`
- `beacon-v1.4.3-governed-learning-recall-and-route-explainability`
