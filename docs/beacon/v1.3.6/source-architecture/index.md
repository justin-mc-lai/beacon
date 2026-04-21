# Beacon v1.3.6 Source Architecture

## Current Runtime Release Scope

- Current release line: `v1.3.6`
- Release-validated feature:
  - `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- Draft exploration kept in the docs package but not counted as release closure:
  - `beacon-v1.3.6-visual-management-console-and-material-viewer`

## Runtime Architecture Anchors

- Shared semantic runtime:
  - `beacon/utils/semantic_runtime.py`
- Shared delivery/read-model kernel:
  - `beacon/utils/delivery_kernel.py`
- Requirement command integrations:
  - `beacon/commands/prd.py`
  - `beacon/commands/user_story.py`
  - `beacon/commands/test_case.py`
  - `beacon/utils/prototype_utils.py`
- Delivery/read-model integrations:
  - `beacon/commands/implement.py`
  - `beacon/commands/qa.py`
  - `beacon/commands/status.py`
  - `beacon/utils/help_support.py`
  - `beacon/utils/release_scorecard.py`
  - `beacon/utils/doctor_diagnostics.py`

## Contract References

- Summary:
  - `docs/beacon/v1.3.6/SUMMARY.md`
- Execution index:
  - `docs/beacon/v1.3.6/execution/index.md`
- Runtime blueprint:
  - `docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
- Technical implementation:
  - `docs/beacon/v1.3.6/execution/technical-implementation-beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- Implementation summary:
  - `docs/beacon/v1.3.6/execution/implementation-summary-beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- Runtime release note:
  - `docs/beacon/v1.3.6/release/v1.3.6.md`

## Notes

- Source architecture is derived from Beacon runtime modules plus the versioned docs package.
- Runtime state under `.beacon/` supports execution and evidence, but does not replace requirement truth.
