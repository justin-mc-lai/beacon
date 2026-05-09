# Beacon v1.4.2 Source Architecture Index

## Status

- version: `v1.4.2`
- status: `freeze-ready`
- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`

## Architecture Intent

The feature adds test contract governance as a delivery projection between frozen requirement truth and QA/release consumption.

## Expected Source Touchpoints

### New Utility Layer

- `beacon/utils/test_contract_governance.py`

Responsibilities:

- parse AC/TC/test/evidence mappings from frozen test-case materials;
- build Test Contract Index payloads;
- verify lane completeness and stale state;
- emit reason codes and repair commands.

### Doctor Surface

- `beacon/commands/doctor.py`
- `beacon/utils/doctor_orchestrator.py`

Expected additions:

- `build-test-contract-index`
- `verify-test-contract-index`

These remain support commands and do not create a lifecycle stage.

### QA Surface

- `beacon/commands/qa.py`

Expected additions:

- consume lane hints;
- preserve AC order and evidence pack semantics;
- write lane execution status.

### Release Surface

- `beacon/utils/release_scorecard.py`
- `beacon/commands/gate.py`

Expected additions:

- consume test contract governance status;
- block on release-facing lane failures;
- expose contract reason codes.

### Skill and Projection Surfaces

- `SKILL.md`
- `skills/beacon/SKILL.md`
- `skills/beacon/references/usage-rules.md`
- `skills/beacon-iteration-governance/`
- `beacon/utils/context_files.py`

Expected additions:

- contract-lane test guidance;
- generated surface sync expectations;
- agent resume behavior through `beacon help`.

## Non-Touchpoints

The implementation must not change runtime version surfaces manually. Version strings remain governed by `beacon/version-truth.json` and `beacon doctor sync-version-surfaces`.
