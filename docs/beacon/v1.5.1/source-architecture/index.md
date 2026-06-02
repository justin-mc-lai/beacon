# Beacon v1.5.1 Source Architecture

## Scope

This source architecture index covers:

- `beacon-truth-map-center-and-package-cutover`

v1.5.1 establishes a truth-map resolver center and keeps the v1.5.2 hard cutover out of scope.

## Source Modules Under Review

- `beacon/utils/truth_map.py`
- `beacon/commands/truth_map.py`
- `beacon/utils/feature_package.py`
- `beacon/utils/material_audit.py`
- `beacon/cli_factory.py`
- `skills/beacon/beacon-prd/SKILL.md`
- `skills/beacon/beacon-test-case/SKILL.md`
- `skills/beacon/beacon-implement/SKILL.md`
- `skills/beacon/beacon-qa/SKILL.md`
- `.agents/skills/beacon-prd/SKILL.md`
- `.agents/skills/beacon-test-case/SKILL.md`
- `.agents/skills/beacon-implement/SKILL.md`
- `.agents/skills/beacon-qa/SKILL.md`
- `tests/test_v151_truth_map.py`
- `tests/test_v150_feature_package.py`

## Architecture Position

Target architecture for v1.5.1:

```text
feature package Markdown
-> truth-map resolver center
-> deterministic validation and machine JSON rebuild
-> generated state/evidence with source hashes
-> existing QA/release guardrails
```

The resolver is code and static contract. `truth-map.json` is not an input truth file.

## Feature Architecture

- `docs/beacon/v1.5.1/features/beacon-truth-map-center-and-package-cutover/truth.md`
- `docs/beacon/v1.5.1/features/beacon-truth-map-center-and-package-cutover/tests.md`
- `docs/beacon/v1.5.1/features/beacon-truth-map-center-and-package-cutover/tasks.md`
- `docs/beacon/v1.5.1/features/beacon-truth-map-center-and-package-cutover/evidence.md`

## Gate Boundary

- v1.5.1 does not remove legacy triptych materials.
- v1.5.1 does not require every Markdown truth document to have an equivalent JSON twin.
- Requirement-derived `.machine` JSON must be resolver-generated and source-hash verifiable.
- Runtime/process JSON remains a runtime record and cannot become requirement authority.
- v1.5.2 is responsible for the hard cutover to feature-package Markdown as the normal canonical truth source.
