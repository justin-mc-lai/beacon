# Workflow Boundaries (v1.2.0)

- run_id: run-20260408T055114Z-1866
- feature: Beacon v1.2.0 - Command Simplification and Project-Skill Workflow Enhancement
- workflow_status: requirements_frozen
- guardrail: workflow/gate consume only main-chain docs; research is input-only.

---

## Mainline boundary

`v1.2.0` has exactly one anchor chain:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

No subordinate workstream may redefine this center.

## Workstream boundaries

### Command simplification
- may simplify entrypoints and routing
- may not blur the mainline or remove traceability

### Project-skill workflow
- may reduce onboarding friction through `skill discover`, starter packs, and profile binding
- may not turn Beacon into a generic project analyzer
- may not pull project-private execution logic into Beacon core

### Prototype anchoring
- may strengthen requirement/prototype traceability
- may not become a second product center competing with `PRD/story/QA`

### QA auto harness
- may evolve bounded QA policy surfaces against a fixed baseline bundle
- may not mutate arbitrary product or project-execution surfaces

## `skill discover` boundary

`beacon skill discover` is defined as a **configuration guidance and binding surface**:

```text
detect project features
→ recommend skill/profile/template
→ preview / dry-run
→ explicit apply
→ doctor / help / profile consume the same result
```

It is not:
- a generic project analysis report generator
- a replacement for project adapters
- a permission to write config without explicit opt-in

## Freeze boundary

The requirement package is only freeze-ready when it contains:
- summary / think / user-story / prd / qa docs
- execution blueprint(s)
- source-architecture surface
- release note
- machine user-story baseline
- machine QA matrices needed to trace ACs and scenarios

Frozen requirement materials become implementation inputs.
They do not bypass the mainline or release governance.

## Execution surface boundary

`v1.2.0` enforces a split execution surface:

- human execution docs → `docs/beacon/<version>/execution/*.md`
- machine execution docs → `docs/beacon/<version>/.machine/execution/*.json`

This is a hard packaging rule, not a taste preference.

### Allowed in `execution/`

- indexes
- blueprints
- operator guides
- review markdown
- implementation markdown
- summary markdown

### Forbidden in `execution/`

- machine summaries
- machine review payloads
- machine init reports
- machine terminal/config/source/git-alignment/change-impact/delivery-manifest payloads

If a command writes execution JSON into the human surface, treat it as package drift and repair it.
