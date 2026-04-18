# UI Style Analysis: beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

- version: `v1.3.4`
- analysis_mode: `design-governed-prototype`

## Unified Directory
- directory_page: `index.html`
- landing_kind: `reference-pack-directory`
- required_pages: `portfolio-overview, project-detail, runtime-center, recovery-diagnostics`
- required_states: `healthy-summary, requirement-incomplete, implement-running, qa-running, release-ready, team-active, ralph-active, blocked, db-offline, partial-rebuild`

## Visual System
- tone: `disciplined`
- visual_direction: `disciplined / admin-workbench`
- differentiator: `lifecycle-first`
- typography: `{"display": "Fraunces", "body": "IBM Plex Sans", "mono": "JetBrains Mono", "scale": [48, 32, 24, 18, 16, 14, 12]}`
- palette: `{"primary": "#1F6FEB", "secondary": "#0F172A", "accent": "#1F6FEB"}`
- motion: `minimal-functional`

## Component Patterns
- navigation: `overview, projects, runtime, diagnostics`
- primary_cta: `查看项目详情`
- secondary_cta: `打开运行态`
- states: `healthy-summary, requirement-incomplete, implement-running, qa-running, release-ready, team-active, ralph-active, blocked, db-offline, partial-rebuild`

## Secondary Build Contract
- source_refs: `docs/beacon/v1.3.4/user-story/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md`
- required_artifacts: `prototype-plan.json, design-brief.json, design-system-contract.json, design-prompt.json, ui-style-analysis.json, tokens.css, navigation-map.json, interaction-map.json, index.html`

## Extension Rules
- analyze existing shared tokens and interaction patterns before extending pages
- preserve the unified prototype directory as the navigation source of truth
- extend via design-brief and design-system contract, not ad-hoc page-local styling
- route design/security findings back through review before freeze
