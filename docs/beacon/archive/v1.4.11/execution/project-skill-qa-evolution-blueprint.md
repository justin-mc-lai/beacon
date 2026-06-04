# Project Skill QA Evolution Blueprint (v1.4.11)

## Intent

This blueprint defines how `v1.4.11` verifies the first legacy-burden reduction slice without depending on repeated skill interpretation.

The current feature is:

```text
authority-vocabulary-and-baseline-inventory-contract
```

The expected QA model is deterministic:

- fixed authority role vocabulary;
- static wording checks;
- inventory schema checks;
- regression checks that legacy behavior remains present for later phases.

## Required QA Dimensions

QA for this slice must verify:

- artifact roles include `truth`, `projection`, `evidence`, `runtime_state`, `compat_mirror`, and `historical_fixture`;
- versioned Markdown requirement packages classify as `truth`;
- `.machine` artifacts classify as `projection`;
- forbidden machine-as-truth wording does not return in current-facing code or rendered docs;
- baseline inventory artifacts exist under `docs/beacon/archive/v1.4.11/`;
- inventory rows include source file, symbol, surface category, current behavior, risk, proposed owner, proposed phase, and required evidence;
- known hotspots are covered;
- old compatibility surfaces remain available until a later frozen retirement slice changes them.

## Skill Boundary

`beacon-qa` provides the verification route, but the pass/fail criteria are executable tests and material gates.

This feature does not create a new public skill. It also does not make compatibility registry, legacy mirror retirement, or command cleanup part of the current QA verdict.

## Acceptance Evidence

Promotion-grade evidence for this slice requires:

- frozen change, PRD, user-story, and test-case materials;
- requirement clarity pass;
- implementation evidence for authority helpers and baseline inventory generator;
- targeted regression tests for authority vocabulary, inventory schema, and no-retirement behavior;
- QA status written by `beacon qa run`.

