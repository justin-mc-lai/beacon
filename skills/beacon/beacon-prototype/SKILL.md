---
name: beacon-prototype
description: Use when the user wants to generate, review, freeze, or inspect Beacon requirement-driven wireframes through the public `prototype` stage.
---

# Beacon Prototype

This skill routes prototype work through Beacon's `prototype` surface.

The public command stays on the `v1.3.8` runtime line while `v1.3.8` keeps prototype output aligned with the host-native requirement material stack instead of reverting to hard-coded template HTML flows.

## Use for

- wireframe freeze package generation
- page list and route-map freezing
- prototype review and freeze readiness
- requirement-to-screen handoff before implementation

## Operator rule

Prefer:

- `beacon prototype ...`
- or `bash skills/beacon/scripts/run_beacon.sh prototype ...`

Treat `prototype` as the formal stage between `test-case` and `implement`.
Do not revive `wireframe.py`, HTML high-fidelity prototype output, or any parallel prototype entrypoint.
