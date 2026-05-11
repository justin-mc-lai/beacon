# Beacon Design Review Runtime Integration

## Human Entry

- host-visible skill: `beacon-design-review`
- router registration target: `skills/beacon/using-beacon/SKILL.md`

## Runtime Command Anchor

Preferred internal adapter:

- `beacon review design ...`

Secondary adapter path when design-specific command ownership is cleaner:

- `beacon design review ...`

## Utility Boundary

Recommended runtime utility:

- `beacon/utils/design_review_surface.py`

Responsibilities:

- load requirement and UI evidence refs
- evaluate hierarchy/state/interaction findings
- decide prototype entry vs revision route
- emit support-surface transaction

## State Integration

- latest receipt: `.beacon/state/beacon-design-review-latest.json`
- optional history: `.beacon/transactions/beacon-design-review/<transaction-id>.json`

## Read Model Exposure

Expose through:

- `beacon help`
- `beacon status`
- optional `prototype` entry preflight

Minimum fields:

- design verdict
- evidence gap summary
- next route
- prototype trigger recommendation

## Writeback Route

- requirement/design mismatch -> `beacon-change` or `beacon-prd`
- acceptance/state mismatch -> `beacon-user-story`
- scenario coverage gap -> `beacon-test-case`
- handoff-ready -> `beacon-prototype`

## Minimum Implementation Files

- `skills/beacon/beacon-design-review/SKILL.md`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/commands/review.py`
- optional `beacon/commands/design.py`
