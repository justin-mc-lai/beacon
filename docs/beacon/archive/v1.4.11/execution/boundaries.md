# Execution Boundaries (v1.4.11)

## Core Rule

`v1.4.11` is the legacy-burden reduction line after `v1.4.10`.

The current frozen feature is:

```text
authority-vocabulary-and-baseline-inventory-contract
```

This slice is intentionally low risk. It can clarify authority vocabulary and create a baseline inventory, but it must not retire behavior.

## In Scope

- Phase 0 baseline inventory for known legacy / fallback / compatibility surfaces.
- Phase 1 authority vocabulary.
- Current-facing wording must not call `.machine` or machine-readable artifacts requirement truth.
- `docs/beacon/<version>/` remains the human-reviewed requirement truth.
- `.machine`, runtime state, QA matrices, scorecards, and generated ledgers remain projection / evidence / read model surfaces.

## Out of Scope

- Compatibility registry behavior.
- QA legacy mirror policy change.
- PRD legacy mirror policy change.
- Implement legacy loader migration.
- Prototype legacy source behavior change.
- Browser fallback rename or behavior change.
- Memory migration behavior change.
- Intent router behavior change.
- Release verdict change.

## QA Boundary

QA may verify that:

- the authority vocabulary is explicit and testable;
- forbidden machine-as-truth wording is rejected in current-facing surfaces;
- the baseline inventory exists as Markdown and JSON;
- required hotspots are covered by the inventory;
- compatibility behavior has not been retired by this slice.

QA must not reinterpret this slice as permission to delete legacy behavior.

