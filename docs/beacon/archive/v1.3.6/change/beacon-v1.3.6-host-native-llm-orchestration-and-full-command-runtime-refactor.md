# Beacon Feature Change Document

- feature: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- feature_slug: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- version: `v1.3.6`
- status: `completed`

## Scope
- Promoted Beacon's host-native LLM orchestration, shared semantic runtime, delivery kernel, and current release-line documentation into the `v1.3.6` runtime truth.

## Added
- Added shared host-native semantic runtime support in `beacon/utils/semantic_runtime.py`.
- Added shared delivery/read-model kernel support in `beacon/utils/delivery_kernel.py`.
- Added current-line execution guidance in `docs/beacon/archive/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`.
- Added runtime-promotion release records under `docs/beacon/archive/v1.3.6/release/`.

## Removed / Reduced
- Reduced dependence on provider-first execution as the default host path.
- Reduced public documentation ambiguity about `v1.3.6` being only a migration target.

## Fixed
- Updated version truth in `beacon/__init__.py`, `pyproject.toml`, and `beacon/version-truth.json`.
- Updated root docs and packaged skills to describe `v1.3.6` as the current runtime release line.
- Updated host pack examples and governance skill examples to use `v1.3.6`.
- Updated runtime alignment and host-skill-pack regression coverage for the promoted release line.

## Traceability Refs
- `beacon/utils/semantic_runtime.py`
- `beacon/utils/delivery_kernel.py`
- `beacon/commands/prd.py`
- `beacon/commands/user_story.py`
- `beacon/commands/test_case.py`
- `beacon/utils/prototype_utils.py`
- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/status.py`
- `beacon/utils/release_scorecard.py`
- `beacon/version-truth.json`
- `README.md`
- `SKILL.md`
- `docs/beacon/archive/v1.3.6/SUMMARY.md`
- `docs/beacon/archive/v1.3.6/release/v1.3.6.md`
- `docs/beacon/archive/v1.3.6/release/runtime-promotion-checklist.md`
- `tests/test_v136_delivery_kernel_read_model.py`
- `tests/test_v136_host_native_requirement_contracts.py`
