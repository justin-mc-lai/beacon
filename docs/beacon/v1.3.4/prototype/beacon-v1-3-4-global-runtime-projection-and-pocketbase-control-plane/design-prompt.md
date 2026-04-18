# Design Prompt: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

- version: `v1.3.4`
- design_generation_mode: `description-as-design`
- interactive_prototype_required: `True`
- guidance_anchors: `frontend-design, web-design-guidelines`
- design_mode_references: `Beacon v1.3.4 main PRD lifecycle-first board model; Beacon v1.3.4 one-person-company ops board model; PocketBase as control plane; not formal delivery truth; Beacon admin-workbench prototype discipline; human minimal surface with runtime drilldown only`

## Context
- audience: `one-person-company CEO and project owner`
- tone: `disciplined`
- visual_direction: `disciplined / admin-workbench`
- differentiator: `lifecycle-first`

## Prototype Scope
- archetype: `admin-workbench`
- required_pages: `portfolio-overview, project-detail, runtime-center, recovery-diagnostics`
- required_states: `healthy-summary, requirement-incomplete, implement-running, qa-running, release-ready, team-active, ralph-active, blocked, db-offline, partial-rebuild`
- route_closure_required: `True`

## Visual System
- typography: `{"display": "Fraunces", "body": "IBM Plex Sans", "mono": "JetBrains Mono", "scale": [48, 32, 24, 18, 16, 14, 12]}`
- palette: `{"primary": "#1F6FEB", "secondary": "#0F172A", "accent": "#1F6FEB"}`
- motion: `minimal-functional`

## LLM Design Prompt

Design a high-fidelity interactive prototype for `beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane`.
Mode: description-as-design.
Audience: one-person-company CEO and project owner.
Tone: disciplined.
Visual direction: disciplined / admin-workbench.
Prototype archetype: admin-workbench.
Required pages: portfolio-overview, project-detail, runtime-center, recovery-diagnostics.
Required states: healthy-summary, requirement-incomplete, implement-running, qa-running, release-ready, team-active, ralph-active, blocked, db-offline, partial-rebuild.
Use the shared design system contract and avoid generic AI aesthetics.
Preserve accessibility, visible focus, reduced motion, semantic navigation, and URL-reflected state where applicable.
Reference mode inspirations: Beacon v1.3.4 main PRD lifecycle-first board model; Beacon v1.3.4 one-person-company ops board model; PocketBase as control plane; not formal delivery truth; Beacon admin-workbench prototype discipline; human minimal surface with runtime drilldown only.
Guidance anchors: frontend-design, web-design-guidelines.

