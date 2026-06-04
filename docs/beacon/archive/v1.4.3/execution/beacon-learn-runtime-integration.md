# Beacon Learn Runtime Integration

## Human Entry

- host-visible skill: `beacon-learn`
- router registration target: `skills/beacon/using-beacon/SKILL.md`

## Runtime Command Anchor

Preferred internal adapter:

- `beacon recall governed ...`

Consumption surfaces:

- `beacon help`
- `beacon status`
- `beacon ask`
- `beacon deep`

## Utility Boundary

Recommended runtime utility:

- `beacon/utils/learn_surface.py`

Responsibilities:

- read learning candidates
- classify applied/suppressed/stale/conflicting learning
- emit support-surface transaction
- feed route explanation payloads to help/status/ask/deep

## State Integration

- latest receipt: `.beacon/state/beacon-learn-latest.json`
- optional history: `.beacon/transactions/beacon-learn/<transaction-id>.json`

## Read Model Exposure

Expose through:

- `beacon help`
- `beacon status`
- `beacon ask`
- `beacon deep`

Minimum fields:

- applied learning summary
- stale/conflicting learning summary
- route influence summary
- next route

## Writeback Route

- default path: advisory only
- prune route: archive or governance lane
- conflict route: operator-visible help/status disclosure

## Minimum Implementation Files

- `skills/beacon/beacon-learn/SKILL.md`
- `beacon/utils/learn_surface.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/commands/recall.py`
- touch points in `beacon/commands/help.py`, `beacon/commands/status.py`, `beacon/commands/ask.py`, `beacon/commands/deep.py`
