# Beacon v1.3.7 Source Architecture

## Release Scope

- Delivery line: `v1.3.7`
- Runtime line used by public command routing: `v1.3.6`
- Release-scoped features:
  - `beacon-v1.3.7-implement-frozen-truth-verification-and-canonical-delivery-baseline-envelope`
  - `beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking`

## Architecture Anchors

- Canonical delivery projection:
  - `beacon/utils/delivery_baseline.py`
  - `beacon/utils/implementation_plan.py`
  - `beacon/utils/technical_review_contract.py`
- Brainstorm sidecar:
  - `beacon/commands/brainstorm.py`
  - `beacon/utils/brainstorm.py`
  - `skills/beacon/beacon-brainstorm/SKILL.md`
- QA / release closure:
  - `beacon/commands/qa.py`
  - `beacon/commands/review.py`
  - `beacon/commands/release.py`
  - `beacon/utils/help_support.py`
  - `beacon/utils/writeback.py`

## Contract References

- Summary:
  - `docs/beacon/v1.3.7/SUMMARY.md`
- Execution index:
  - `docs/beacon/v1.3.7/execution/index.md`
- Architecture blueprint:
  - `docs/beacon/v1.3.7/execution/architecture-blueprint.md`
- Release document:
  - `docs/beacon/v1.3.7/release/v1.3.7.md`

## Notes

- Runtime state under `.beacon/` supports execution evidence and feature-aware QA isolation, but does not replace version truth.
- Projection docs are valid only as one-way outputs from the canonical delivery baseline envelope.
