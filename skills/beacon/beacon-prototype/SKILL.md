---
name: beacon-prototype
description: Use when the user wants to generate, review, freeze, or inspect Beacon requirement-driven wireframe + UX PRD closure bundles through the public `prototype` stage.
---

# Beacon Prototype

This skill routes prototype work through Beacon's `prototype` surface.

The public command stays on the `v1.3.9` runtime line while `v1.3.9` keeps prototype output aligned with the host-native requirement material stack instead of reverting to hard-coded template HTML flows.

## Use for

- requirement-driven wireframe freeze package generation
- UX PRD closure bundle generation
- design context / design reasoning / UX contract freezing
- page intent and state visibility contract freezing
- DESIGN.md / preview asset projection before implementation
- prototype review and freeze readiness
- requirement-to-screen-and-UX handoff before implementation

## Operator rule

Prefer:

- `beacon prototype ...`
- or `beacon prototype ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh prototype ...`)

Treat `prototype` as the formal stage between `test-case` and `implement`.
Keep `prototype` inside the requirement stage:

- it remains `requirement-driven wireframe freeze`
- it is not final visual approval
- it is not production UI generation

For `v1.3.10+`, the expected freeze truth must include:

- `design_context`
- `design_reasoning`
- `ux_contract`
- `page_intent_contract`
- `state_visibility_contract`
- `ux-prd.md`
- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

Default design baseline is `apple-inspired-design-md` unless requirement truth records an explicit override reason.

Absorb these internal design expectations without expanding the public lifecycle:

- `impeccable`: require explicit design context instead of generic guessing
- `ui-ux-pro-max-skill`: freeze product surface type, layout pattern, anti-patterns, and decision hierarchy
- `awesome-design-md`: project agent-friendly design assets from canonical truth

Do not revive `wireframe.py`, HTML high-fidelity product pages, or any parallel prototype entrypoint.
