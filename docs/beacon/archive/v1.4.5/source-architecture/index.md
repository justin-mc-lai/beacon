# Beacon v1.4.5 Source Architecture Index

## Status

- version: `v1.4.5`
- status: `planning_only`
- theme: `guidance family contracts, docs semantics, and governed external capabilities`

This source-architecture index describes the `v1.4.5` planning line and any associated implementation artifacts without asserting that `v1.4.5` is the current runtime release line.

## Architecture Intent

`v1.4.5` adds a contract layer on top of existing Beacon surfaces.

The intent is to:

- formalize support-surface family behavior;
- clarify artifact semantics without breaking historical versions;
- admit governed external capabilities and composition learning without opening a second runtime.

## Expected Source Touchpoints

### Guidance Family Contract

- `beacon/utils/guidance_family.py`
- `beacon/utils/help_support.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/brainstorm.py`
- `beacon/utils/deep_loop.py`

Responsibilities:

- freeze shared guidance-family membership;
- express non-truth and non-gate boundaries;
- preserve route explainability across support surfaces.

### Docs Structure Contract

- `beacon/utils/docs_structure_contract.py`

Responsibilities:

- define semantic layers for truth, guidance, delivery, evidence, and `.machine`;
- keep historical layout compatibility;
- support progressive materialization instead of eager full-tree creation.

### External Capability Composition

- `beacon/utils/project_skills.py`

Responsibilities:

- model governed external capability sources;
- select capability composition from business goal and output shape;
- record composition learning outcomes back into reusable mappings.

## Non-Touchpoints

`v1.4.5` must not:

- add a public top-level lifecycle command;
- redefine frozen truth ownership;
- let external capability sources override requirement-package or QA gate truth.
