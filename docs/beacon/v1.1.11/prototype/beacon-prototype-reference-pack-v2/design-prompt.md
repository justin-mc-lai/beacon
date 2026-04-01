# Design Prompt: beacon-prototype-reference-pack-v2

- version: `v1.1.11`
- design_generation_mode: `spec-driven`
- interactive_prototype_required: `False`
- guidance_anchors: ``
- design_mode_references: ``

## Context
- audience: `product team`
- tone: `disciplined`
- visual_direction: `disciplined / admin-workbench`
- differentiator: `delivery-grade reference UI`

## Prototype Scope
- archetype: `admin-workbench`
- required_pages: `overview, page-inventory, route-closure, delivery-readiness, baseline-protection`
- required_states: `empty, loading, error, auth-required, completed`
- route_closure_required: `True`

## Visual System
- typography: `{"display": "Fraunces", "body": "IBM Plex Sans", "mono": "JetBrains Mono", "scale": [48, 32, 24, 18, 16, 14, 12]}`
- palette: `{"primary": "#2563eb", "secondary": "#0f172a", "accent": "#2563eb"}`
- motion: `minimal-functional`

## LLM Design Prompt

Design a high-fidelity interactive prototype for `beacon-prototype-reference-pack-v2`.
Mode: spec-driven.
Audience: product team.
Tone: disciplined.
Visual direction: disciplined / admin-workbench.
Prototype archetype: admin-workbench.
Required pages: overview, page-inventory, route-closure, delivery-readiness, baseline-protection.
Required states: empty, loading, error, auth-required, completed.
Use the shared design system contract and avoid generic AI aesthetics.
Preserve accessibility, visible focus, reduced motion, semantic navigation, and URL-reflected state where applicable.
