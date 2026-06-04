# Workflow Boundaries (v1.3.0)

- feature: Beacon v1.3.0 simplified Codex-native subagents
- workflow_status: requirements_frozen / implement-first validated
- guardrail: planning line may land bounded implement-team evidence, but must not claim runtime release promotion.

---

## Mainline boundary

`v1.3.0` still serves the same Beacon anchor chain:

```text
PRD
→ user-story
→ QA
→ implementation evidence
→ review / gate / release
```

Subagent capability is subordinate to this chain.

## Workstream boundaries

### Codex-native subagents

- may add bounded delegated execution inside approved stages
- may not turn Beacon into a generic multi-agent runtime
- may not bypass canonical Beacon writeback

### Team surfaces

- may expose `implement-team` and `qa-team` as explicit operator surfaces
- may not blur implement and QA private context
- must exchange only through formal artifacts and handoff summaries

### Version semantics governance

- may centralize version meaning into one canonical contract
- may not let commands reinterpret docs-target and runtime-target ad hoc

### Artifact language policy

- may default human-facing materials to Chinese
- may keep machine-facing contracts in English/stable keys
- may not localize machine keys for presentation-only reasons

## Implement-first boundary

`implement run --runner codex-subagents` is the first adopted delegated surface in `v1.3.0`.

This means:

- implement evidence may be written and reviewed
- later stage expansion remains conditional
- `think` / `user-story` / `prd` / `test-case` / `qa` must not claim full delegated closure by default

## Execution surface boundary

`v1.3.0` keeps the same hard split:

- human execution docs → `docs/beacon/<version>/execution/*.md`
- machine execution docs → `docs/beacon/<version>/.machine/execution/*.json`

Allowed in `execution/`:

- blueprints
- implementation markdown
- review markdown
- summary markdown
- codex-subagent human-readable role reports

Forbidden in `execution/`:

- terminal/config/source/git-alignment/change-impact/delivery-manifest machine payloads
- machine review summaries
- raw runtime state as formal release truth

## Freeze boundary

The `v1.3.0` package is only package-complete when it contains:

- summary / think / user-story / prd / qa docs
- execution blueprints
- source-architecture surface
- release note
- machine user-story baseline
- machine QA matrices required to trace AC / TC / scenario coverage

Frozen materials can feed implement-team execution, but they do not by themselves promote `v1.3.0` to current runtime release.
