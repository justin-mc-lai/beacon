# Project Skill QA Evolution Blueprint (v1.4.9)

## Intent

This blueprint defines how `v1.4.9` must validate Beacon skill evolution after UI/UX execution is externalized and `prototype` becomes a design-result adapter.

The narrow goal is: every human-facing UI/UX or visualization-related Beacon skill invocation must either route to the correct execution owner, update the correct Beacon material, require a writeback, open an obligation, or remain explicitly read-only.

## Required Skill QA Dimensions

QA for this version must verify:

- UI/UX execution intent routes to `ui-ux-dev` instead of Beacon-native design generation.
- Missing `ui-ux-dev` does not trigger silent fallback to internal prototype generation.
- `beacon-prototype` v1.4.9+ behavior is adapter-only for accepted design results.
- `beacon-design-review` remains route / governance support and does not issue canonical truth or release verdicts.
- Accepted design result without adapter truth binding blocks implement.
- Business flow projection exists when required and excludes implementation details.
- State-machine projection exists when required and uses stable closure states.
- PRD / user-story / test-case map exists when required and carries truth bindings.
- Requirement clarity blocks missing projection truth bindings.
- Historical prototype bundles remain readable but do not override v1.4.9 ownership.

## Human-Facing Skill Material Effects

Relevant skill invocations must resolve to one of:

- `route_to_ui_ux_dev`
- `adapter_writeback_completed`
- `adapter_writeback_required`
- `visualization_writeback_completed`
- `visualization_writeback_required`
- `obligation_opened`
- `truth_reopen_required`
- `read_only_route_only`

Any invocation that cannot resolve to one of these effects is not gate-complete.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen PRD / user-story / test-case for `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- requirement clarity gate passing
- executable tests covering AC-001 through AC-012
- route classification tests for `ui-ux-dev` handoff
- adapter-only tests for `prototype`
- fail-closed tests for missing adapter bindings
- fail-closed tests for missing visualization truth bindings
- compatibility tests for historical prototype bundle reads
- release checklist updated from pending to actual observed results

## Current Status

The requirement package is being frozen for implementation planning.

Runtime implementation, executable tests, QA evidence, and release promotion are not complete in this document.

