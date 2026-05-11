# Beacon v1.4.3 Project Skill QA Evolution Blueprint

## Status

- version: `v1.4.3`
- status: `implementation-in-progress`
- theme: `evidence-first decision surfaces and governed learning activation`

## Purpose

This blueprint defines how Beacon skill delivery and QA should consume the new `v1.4.3` decision surfaces without expanding the public lifecycle.

The implementation goal is:

1. keep `implement` and `qa` as the only execution and acceptance entrypoints;
2. make `ceo-review`, `design-review`, and `learn` visible as support surfaces;
3. ensure support-surface output becomes auditable evidence and next-step guidance;
4. ensure learning is recalled into later decisions, but remains advisory.

## Skill Delivery Contract

Beacon skills should guide agents to:

1. read `docs/beacon/global-boundaries.md` first;
2. bind to the current version truth package;
3. run CEO-grade requirement challenge before reopening frozen truth;
4. run design-grade challenge before prototype freeze when UI/UX handoff is real;
5. treat prototype as conditional freeze/handoff, not strategy or final design authority;
6. surface learning recall, staleness, conflict, and suppression as explicit operator-visible context;
7. route changes back through `change`, `prd`, `user-story`, and `test-case` instead of mutating truth from support surfaces;
8. use `help` and `status` to explain route, evidence gaps, and learning influence.

## QA Evolution Rules

QA for this line should verify:

- support surfaces write receipts and state summaries;
- route recommendations are executable Beacon commands;
- design-review can precede prototype and also allow no-prototype paths;
- learning recall is visible, auditable, and downgradable;
- requirement package and revision state remain the governing closure contract.

## Anti-Patterns

Agents must not:

- treat support surfaces as a second truth source;
- mark release-ready from learning or review surfaces alone;
- require prototype for features with no real UI/UX handoff;
- collapse design challenge into static prototype semantics;
- hide stale or conflicting learning from later decision surfaces.

## Implementation Touchpoints

- `skills/beacon/beacon-ceo-review/SKILL.md`
- `skills/beacon/beacon-design-review/SKILL.md`
- `skills/beacon/beacon-learn/SKILL.md`
- `skills/beacon/using-beacon/SKILL.md`
- `beacon/commands/review.py`
- `beacon/commands/help.py`
- `beacon/commands/status.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/learn_surface.py`
- `beacon/utils/support_surface_transactions.py`
