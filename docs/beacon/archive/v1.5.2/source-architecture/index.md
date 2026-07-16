# Beacon v1.5.2 Source Architecture

## Scope

This source architecture index covers:

- `beacon-truth-map-center-and-package-cutover`

v1.5.2 promotes feature-package Markdown from canonical-ready read model to normal authoritative truth source.

## Source Modules Under Review

- `beacon/utils/truth_map.py`
- `beacon/commands/truth_map.py`
- `beacon/utils/feature_package.py`
- `beacon/utils/material_audit.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/requirement_deepening.py`
- `beacon/utils/acceptance_kit.py`
- `beacon/utils/manifest.py`
- `beacon/utils/release_scorecard.py`
- `beacon/commands/prd.py`
- `beacon/commands/user_story.py`
- `beacon/commands/test_case.py`
- `beacon/commands/workflow.py`
- `beacon/commands/truth.py`
- `beacon/commands/gate.py`
- `beacon/commands/release.py`
- `skills/beacon/**/SKILL.md`
- `.agents/skills/**/SKILL.md`
- `tests/test_v152_package_authoritative.py`

## Architecture Position

Target architecture:

```text
feature package Markdown
-> truth-map resolver center
-> deterministic parser/validator
-> gate / QA / release / status consumers
-> generated state and evidence with non-authority labels
```

The resolver is code and policy. Generated JSON is not an input truth source.

## Feature Architecture

- `docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/truth.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/tests.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/tasks.md`
- `docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/evidence.md`
- `docs/beacon/archive/v1.5.2/source-architecture/beacon-truth-map-center-and-package-cutover.md`

## Gate Boundary

- v1.5.2 does not require deleting legacy triptych files.
- v1.5.2 does require that legacy triptych files cannot act as normal truth authority.
- Missing package surfaces block even when legacy files exist.
- Missing generated JSON does not invalidate package truth.
- Generated JSON that claims truth authority fails closed.
