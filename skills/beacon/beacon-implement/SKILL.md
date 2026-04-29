---
name: beacon-implement
description: Use when the user wants to plan or run implementation through Beacon's current v1.3.9 runtime surface. Keep `implement` as the only public implementation entrypoint; treat team runtime and subagent lanes as internal.
---

# Beacon Implement

This skill routes execution work through Beacon's `implement` surface.

The public command stays on the `v1.3.9` runtime line while `v1.3.9` defines the shared delivery kernel and host-native execution contract.

## Use for

- implementation planning
- implementation execution
- implementation progress / handoff checks
- implementation readiness after freeze and technical review

## Operator rule

Prefer:

- `beacon implement ...`
- or `bash skills/beacon/scripts/run_beacon.sh implement ...`

Do not expose `implement-team`, planner/implementer/tester roles, or lane-level runtime details unless the user explicitly asks for internals.
