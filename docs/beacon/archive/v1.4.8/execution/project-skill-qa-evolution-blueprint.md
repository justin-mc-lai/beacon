# Project Skill QA Evolution Blueprint (v1.4.8)

## Intent

This blueprint defines how `v1.4.8` must validate Beacon skill evolution after the material-gate and human-subskill writeback contract is implemented.

The goal is narrow: every human-facing Beacon skill invocation must either update the right material, require a specific writeback, open an obligation, or stay explicitly read-only with a governed route.

## Required Skill QA Dimensions

QA for this version must verify:

- skill routing explains the matched surface and next material target
- support surfaces remain advisory until adopted through governed truth or obligation surfaces
- toolkit surfaces that mutate branch/service/worktree facts write to canonical execution materials
- default-seeded delivery facts do not unlock implement
- missing execution host materials block implement
- open artifact update obligations block QA/release where declared blocking
- diagnostics name the missing material, weak source, open obligation, and repair route

## Human-Facing Skill Material Effects

Every human-facing skill invocation must resolve to one of:

- `writeback_completed`
- `writeback_required`
- `obligation_opened`
- `truth_reopen_required`
- `execution_host_update_required`
- `evidence_update_required`
- `read_only_route_only`

Any skill invocation that cannot resolve to one of these effects is not gate-complete.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen PRD / user-story / test-case for `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
- executable tests covering AC-001 through AC-012
- material package gate passing
- requirement clarity gate passing
- implement preflight proving fail-closed behavior
- QA evidence proving no silent default or missing-material pass
- release checklist updated from pending to actual observed results

## Current Status

The requirement package is frozen for implementation planning.

Runtime implementation, executable tests, QA evidence, and release promotion are not complete in this document.
