# Beacon v1.3.6 Summary

## Status

- `v1.3.6` is the current Beacon runtime and package release line.
- Runtime truth, public docs, packaged skills, and release gating now converge on `v1.3.6`.
- `docs/beacon/v1.3.6/` is the default delivery tree for current Beacon work.

## Line Intent

- Declare Beacon's host-native LLM architecture as the current runtime truth.
- Keep the human-facing workflow on the minimal 7+3 surface.
- Use Beacon CLI as the structured execution kernel for projection, review, freeze, QA, and release.

## Current Package

- Runtime/package version:
  - `1.3.6`
- Default docs line:
  - `docs/beacon/v1.3.6/`
- Current runtime release note:
  - `docs/beacon/v1.3.6/release/v1.3.6.md`
- Host-native runtime blueprint:
  - `docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
- Release-validated feature:
  - `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`
- Release-validated companion feature:
  - `beacon-v1.3.6-visual-management-console-and-material-viewer`

## Runtime Themes

- Host-native requirement compile:
  - `prd / user-story / test-case / prototype` share the same semantic runtime contract.
- Delivery kernel convergence:
  - `implement / qa / release` share one delivery contract and traceability plane.
- Support/read-model convergence:
  - `help / status / doctor` consume the same delivery read model and surface explanation.
- Provider fallback demotion:
  - `BEACON_LLM_API_KEY` remains available for pure CLI fallback, not as the default host-mode requirement.

## Output Boundary

- In scope:
  - requirement truth under `docs/beacon/v1.3.6/`
  - host-native orchestration and semantic/runtime contracts
  - release-ready packaging, HUD, diagnostics, and read-model behavior
- Included companion delivery in the same line:
  - management console and material viewer product line
- Out of scope:
  - replacing requirement truth with runtime state
  - expanding the public command surface beyond the minimal 7+3 model
  - making provider-backed CLI execution the default user path

## Current Reading Order

1. `docs/beacon/global-boundaries.md`
2. `docs/beacon/v1.3.6/SUMMARY.md`
3. `docs/beacon/v1.3.6/execution/index.md`
4. `docs/beacon/v1.3.6/execution/architecture-blueprint.md`
5. `docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
6. `docs/beacon/v1.3.6/prd/`
7. `docs/beacon/v1.3.6/user-story/`
8. `docs/beacon/v1.3.6/qa/test-cases/`
9. `docs/beacon/v1.3.6/release/v1.3.6.md`

## Release References

- Runtime release note:
  - `docs/beacon/v1.3.6/release/v1.3.6.md`
- Promotion completion checklist:
  - `docs/beacon/v1.3.6/release/runtime-promotion-checklist.md`
- Research directory:
  - `docs/beacon/v1.3.6/research/`
