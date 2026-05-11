# Beacon Support Surface Runtime Integration Spec

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`
- applies_to:
  - `beacon-ceo-review`
  - `beacon-design-review`
  - `beacon-learn`

## Integration Goal

Integrate the three new support surfaces into Beacon runtime without:

- adding a new primary lifecycle stage
- creating a second truth root
- forking a second help/status read model

## Existing Runtime Anchors

### Human-facing router anchors

- `skills/beacon/using-beacon/SKILL.md`
- `skills/beacon/beacon-help/SKILL.md`
- `skills/beacon/beacon-status/SKILL.md`
- `skills/beacon/beacon-change/SKILL.md`
- `skills/beacon/beacon-prd/SKILL.md`
- `skills/beacon/beacon-user-story/SKILL.md`
- `skills/beacon/beacon-test-case/SKILL.md`
- `skills/beacon/beacon-prototype/SKILL.md`

### Command/runtime anchors

- `beacon/commands/help.py`
- `beacon/commands/status.py`
- `beacon/commands/review.py`
- `beacon/commands/design.py`
- `beacon/commands/recall.py`
- `beacon/commands/remember.py`
- `beacon/commands/change.py` is not present as a file, but `beacon-change` is the routing surface already defined in skills/docs

### Utility anchors

- `beacon/utils/help_support.py`
- `beacon/utils/technical_review_contract.py`
- `beacon/utils/learning_loop.py`
- `beacon/utils/writeback.py`
- `beacon/utils/support_surface_projection.py`
- `beacon/utils/intent_router.py`

## Integration Principles

1. Host-visible entry can expand at the skill layer.
2. Runtime command expansion should prefer existing support command families.
3. State visibility should flow through `help` and `status`.
4. Accepted deltas still route through `change / prd / user-story / test-case / prototype`.
5. Shared transaction receipts should follow one common support-surface contract.

## Recommended Runtime Shape

### Layer 1: Host-visible skill wrappers

Add new skill wrappers:

- `skills/beacon/beacon-ceo-review/SKILL.md`
- `skills/beacon/beacon-design-review/SKILL.md`
- `skills/beacon/beacon-learn/SKILL.md`

These are the human-facing names.

### Layer 2: Runtime command adapters

Prefer internal command adapters under existing command families:

- CEO review adapter under `review`
- design review adapter under `review` or `design`
- governed learning adapter under `recall` plus `help/status` consumption

This keeps implementation close to existing support planes instead of opening a new lifecycle family.

### Layer 3: Shared utility kernel

Add one shared support-surface transaction utility family and three thin surface-specific orchestrators.

## Minimal File Boundary

### Recommended new utils

- `beacon/utils/support_surface_transactions.py`
- `beacon/utils/support_surface_reason_codes.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/learn_surface.py`

### Recommended command touch points

- `beacon/commands/help.py`
- `beacon/commands/status.py`
- `beacon/commands/review.py`
- `beacon/commands/design.py`
- `beacon/commands/recall.py`

### Recommended skill touch points

- `skills/beacon/using-beacon/SKILL.md`
- new skill wrapper directories for the three surfaces

## Read Model Integration

`help` and `status` should read:

- latest support-surface transaction receipt
- latest blocked reason
- latest next route
- latest learning influence summary

They should not compute a second independent verdict.

## Truth Writeback Integration

No surface writes truth directly.

Instead:

- CEO review accepted delta -> `beacon-change` then `beacon-prd`
- design review accepted delta -> `beacon-change`, `beacon-user-story`, `beacon-test-case`, or `beacon-prototype`
- learn governance output -> advisory state, help/status disclosure, or prune governance route

## Status Integration

`beacon status` should add optional payload sections:

- `ceo_review`
- `design_review`
- `learning_governance`

Each section should expose:

- status
- blocked
- reason_code
- state_path
- latest_next_route

## Help Integration

`beacon help` should incorporate:

- support-surface latest route recommendation
- primary blocked reason
- support-surface source label
- recommended next command

## Release / QA Boundary

The three surfaces may influence routing and scope, but they may not directly set:

- QA pass
- release pass
- acceptance truth

For the umbrella feature `beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation`:

- release and strict gate should treat it as an aggregation contract over the accepted subfeatures
- standalone `prototype`, `technical review`, and `implementation plan` requirements belong to concrete subfeatures, not to the umbrella
- legacy draft implementation artifacts for the umbrella are historical projections, not current gate truth

## Delivery Target

The first runtime implementation target is:

- host-visible skill wrappers present
- shared transaction receipts produced
- help/status can read and render latest receipts
- accepted support outputs route to existing truth surfaces
