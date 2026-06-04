# Beacon v1.4.5 Project Skill QA Evolution Blueprint

## Status

- version: `v1.4.5`
- status: `planning_only`
- theme: `guidance family formalization, docs semantics, and governed external capability composition`

This file may describe implementation and QA expectations for artifacts developed inside the `v1.4.5` planning line, but it does not promote `v1.4.5` to the current runtime release line.

## Purpose

This blueprint defines how Beacon skill delivery and QA should consume the `v1.4.5` additions without expanding the public lifecycle.

The implementation goal is:

1. keep `implement` and `qa` as the only execution and acceptance entrypoints;
2. formalize `ceo-review`, `brainstorm`, `design-review`, and `deep` as one guidance family;
3. make docs semantics explicit so truth, guidance, delivery, evidence, and `.machine` do not drift together;
4. admit governed external capability sources without collapsing into ad hoc skill-chain declarations;
5. preserve learning as reusable composition evidence, not a gate override.

## Skill Delivery Contract

Beacon skills should guide agents to:

1. read `docs/beacon/global-boundaries.md` first;
2. bind to the current version truth package;
3. treat guidance surfaces as challenge/explanation layers only;
4. keep docs semantics visible when writing or reading artifacts;
5. select external capability sources from business goal and output shape before chain details;
6. write capability-composition learning outcomes back as reusable evidence;
7. route all truth changes back through `change`, `prd`, `user-story`, and `test-case`;
8. use `help` and `status` to explain route, evidence gaps, and surface boundaries.

## QA Evolution Rules

QA for this line should verify:

- guidance-family members stay non-truth and non-gate;
- shared decision-loop explainability is consistent across support surfaces;
- docs semantics separate truth, guidance, delivery, evidence, and `.machine`;
- progressive materialization avoids eager full-tree creation;
- governed external capability composition preserves boundaries and writes learning outcomes back.

## Anti-Patterns

Agents must not:

- treat guidance-family projections as truth authority;
- force non-software goals through coding-first declarations;
- treat `.machine` artifacts as canonical requirement truth;
- allow external capability selection to bypass frozen Beacon requirement packages;
- mark release-ready from learning or guidance surfaces alone.

## Implementation Touchpoints

- `skills/beacon/beacon-qa/SKILL.md`
- `beacon/utils/guidance_family.py`
- `beacon/utils/docs_structure_contract.py`
- `beacon/utils/project_skills.py`
- `beacon/utils/help_support.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/brainstorm.py`
- `beacon/utils/deep_loop.py`
- `tests/test_v145_guidance_family.py`
- `tests/test_v145_docs_architecture.py`
- `tests/test_v145_external_skills.py`
