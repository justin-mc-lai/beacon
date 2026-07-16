# Project Skill QA Evolution Blueprint (v1.5.2)

## Intent

v1.5.2 completes the Beacon truth-source cutover:

```text
truth-map resolver -> features/<slug>/{truth,tests,tasks,evidence}.md
```

Feature-package Markdown is the normal authority for requirement, test, task, and evidence truth. Legacy `prd/`, `user-story/`, and `qa/test-cases/` surfaces are rebuild/absorb/archive artifacts only.

## Skill Material Effects

Relevant skills must resolve truth in this order:

1. `beacon truth-map resolve <feature> --project . --version v1.5.2 --json`
2. resolver-selected `features/<slug>/{truth,tests,tasks,evidence}.md`
3. legacy triptych only when explicitly routed through doctor rebuild or change absorb

Generated `.machine` JSON, manifests, QA status, release reports, and runtime records are generated state or evidence. They are not truth authority.

## Required Skill QA Dimensions

QA for this version must verify:

- resolver policy reports `feature_package_authoritative` for v1.5.2+;
- package Markdown validates without required JSON twins;
- normal CLI consumers do not pass only because of `v1.5.1_legacy_exception`;
- material audit treats package surfaces as completeness authority;
- gate, QA, release, and status consume package-derived truth through resolver/parser;
- doctor rebuild targets are legacy outputs only;
- change absorb targets package truth only;
- skills teach package-first read/write guidance for v1.5.2.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen package truth under `docs/beacon/archive/v1.5.2/features/<slug>/`;
- package test matrix covering old-entrypoint drift;
- source architecture map for the cutover;
- version governance surfaces required by resolver preflight;
- executable `tests/test_v152_package_authoritative.py` coverage;
- QA record proving old triptych files cannot win authority.

## Current Status

Requirement truth is frozen. Test-case coverage is expanded. Runtime implementation must now make the v1.5.2 package-authoritative policy true in code.
