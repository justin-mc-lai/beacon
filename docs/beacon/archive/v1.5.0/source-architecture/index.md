# Beacon v1.5.0 Source Architecture

## Scope

This source architecture index covers:

- `beacon-v1.5.0-parallel-plan-b-document-capability`

v1.5.0 introduces a parallel feature package read model and keeps the existing requirement and gate architecture authoritative.

## Source Modules Under Review

- `beacon/commands/feature_package.py`
- `beacon/utils/feature_package.py`
- `beacon/utils/artifact_paths.py`
- `beacon/cli_factory.py`
- `skills/beacon/beacon-prd/SKILL.md`
- `skills/beacon/beacon-test-case/SKILL.md`
- `skills/beacon/beacon-implement/SKILL.md`
- `skills/beacon/beacon-qa/SKILL.md`
- `tests/test_v150_feature_package.py`
- `tests/test_entrypoint_parity.py`

## Architecture Position

Target architecture:

```text
canonical requirement triptych
-> explicit feature package materialization
-> deterministic parser/validator
-> validated read model
-> existing implement / QA / release gates
```

The feature package lane is not a replacement for `.machine`, PRD, user story, test cases, QA verdicts, or release readiness.

## Feature Architecture

- `docs/beacon/archive/v1.5.0/source-architecture/beacon-v1.5.0-parallel-plan-b-document-capability.md`

## Gate Boundary

- `truth.md` frontmatter cannot become lifecycle state truth.
- `tasks.md` checkbox rows cannot satisfy implement or QA completion.
- `evidence.md` cannot claim final verdict, gate truth, or release readiness.
- Deep and CEO review outputs remain support advisory surfaces.
- v1.6+ real-project validation is required before any old-system retirement decision.
