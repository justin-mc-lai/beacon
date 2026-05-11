# Beacon CEO Review Runtime Integration

## Human Entry

- host-visible skill: `beacon-ceo-review`
- router registration target: `skills/beacon/using-beacon/SKILL.md`

## Runtime Command Anchor

Preferred internal adapter:

- `beacon review ceo ...`

Fallback implementation path:

- support-surface orchestration utility invoked from host skill wrapper

## Utility Boundary

Recommended runtime utility:

- `beacon/utils/ceo_review_surface.py`

Responsibilities:

- load truth refs
- evaluate challenge scope
- emit support-surface transaction
- prepare writeback route package

## State Integration

- latest receipt: `.beacon/state/beacon-ceo-review-latest.json`
- optional history: `.beacon/transactions/beacon-ceo-review/<transaction-id>.json`

## Read Model Exposure

Expose through:

- `beacon help`
- `beacon status`

Minimum fields:

- latest decision
- blocked reason
- next route
- affected truth refs

## Writeback Route

- PRD-level reframe -> `beacon-change` and `beacon-prd`
- story/test implications -> `beacon-user-story` / `beacon-test-case`

## Minimum Implementation Files

- `skills/beacon/beacon-ceo-review/SKILL.md`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/commands/review.py`
