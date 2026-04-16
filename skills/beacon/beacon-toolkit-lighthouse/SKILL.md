---
name: beacon-toolkit-lighthouse
description: Use when the user wants a fast, single-file analysis of a target project, open-source repo, third-party package, infra chain, or feature slice using Mermaid plus concise explanation, without entering Beacon's main workflow.
---

# Beacon Toolkit Lighthouse

This skill routes analysis work through Beacon's optional `Toolkit Lighthouse` surface.

## Use for

- fast repo ramp-up
- open-source library analysis
- third-party package decomposition
- infrastructure chain mapping
- feature slice breakdown
- single-file system maps similar to `system-architecture-map`

## Operator rule

Keep Toolkit Lighthouse outside the main workflow by default.

Prefer:

- produce one Markdown artifact
- default output to `.beacon/analysis/<slug>.md`
- for Beacon source iterations, also produce a versioned deliverable:
  - `docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md`
- use Mermaid + concise Chinese explanation
- distinguish `Confirmed Facts` from `Inferred Structure`
- include key source refs and key files

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`

unless the user explicitly asks to continue into the main Beacon workflow.

## Recommended output shape

```markdown
# <Target> Lighthouse Map

## 1. Summary
## 2. Scope
## 3. Mermaid Maps
## 4. Key Entry Points
## 5. Key Modules / Subsystems
## 6. Dependencies / Infra Chain
## 7. Confirmed Facts
## 8. Inferred Structure
## 9. Open Questions / Risks
## 10. Recommended Next Steps
```
