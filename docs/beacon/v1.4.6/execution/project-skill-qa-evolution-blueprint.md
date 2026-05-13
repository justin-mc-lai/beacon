# Beacon v1.4.6 Project Skill QA Evolution Blueprint

## Status

- version: `v1.4.6`
- status: `release_candidate`
- theme: `anti-drift skill contracts and enforced decision surfaces`

This blueprint describes how Beacon skill delivery and QA should consume the `v1.4.6` contract-tightening line without expanding the public lifecycle or collapsing into playbook-heavy prompts.

## Purpose

`v1.4.6` exists to make Beacon skills more decision-aligned and less drift-prone at the surface where agents actually read and act.

The implementation goal is:

1. keep Skill design philosophy-first rather than script-first;
2. make key host-visible skills expose a stable, minimal, auditable contract anatomy;
3. bind support-surface challenge outputs back to route, evidence, state, or gate consequence;
4. let QA detect contract regression before downstream release ambiguity appears.

## Skill Delivery Contract

Beacon skills in this line should guide agents to:

1. read global boundaries and version truth first;
2. calibrate decision boundary before suggesting execution detail;
3. expose only the minimum complete tool surface needed for the scenario;
4. state necessary facts that are easy for the model to forget but must remain true;
5. avoid verbose operational scripts unless the scenario is inherently procedural or high-risk;
6. make misuse visible through boundary, verification, evidence, and gate sections;
7. route truth changes back through `change`, `prd`, `user-story`, and `test-case` rather than support surfaces.

## QA Evolution Rules

QA for this line should verify:

- required skill anatomy sections exist on governed public/support skill surfaces;
- anti-rationalization guidance is present and aligned with philosophy-first design;
- support surfaces do not present themselves as truth owner or gate owner;
- challenge outputs map back to route, state, evidence, or gate semantics;
- contract linting catches regressions without broadening into non-contract product policy.

## Anti-Patterns

Agents and reviewers must not:

- over-specify strong-model execution with long procedural scripts by default;
- emit challenge verdicts that do not change route, evidence, state, or gate consequence;
- let examples replace boundaries as the primary control surface;
- treat contract lint output as a substitute for product truth freeze or QA acceptance.

## Implementation Touchpoints

- `skills/beacon/SKILL.md`
- key public and support `skills/beacon/*/SKILL.md`
- `beacon/utils/skill_contracts.py`
- `beacon/utils/support_surface_projection.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`
- `tests/test_v146_anti_drift_skill_contracts.py`

## Release Interpretation

Passing this blueprint means:

- Beacon surfaces are harder to misuse
- anti-drift regressions are easier to detect
- stronger models retain more autonomy inside clearer gates

It does not by itself mean:

- runtime/default docs line should be promoted automatically
- every historical skill has already been rewritten
- support surfaces can close delivery without primary lifecycle evidence
