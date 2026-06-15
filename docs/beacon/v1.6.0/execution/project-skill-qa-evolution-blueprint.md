# Project Skill QA Evolution Blueprint v1.6.0

## Intent

v1.6.0 changes Beacon's host-visible skill taxonomy from historical stage/support names to harness-first names:

```text
beacon-<harness-code>-<function>
```

Accepted harness codes:

- `pln` -> planner
- `gen` -> generator
- `eval` -> evaluator
- `gov` -> governor

## Skill Material Effects

Relevant skills must resolve truth in this order:

1. `beacon truth-map resolve <feature> --project . --version v1.6.0 --json`
2. resolver-selected `features/<slug>/{truth,tests,tasks,evidence}.md`
3. support research and legacy names only as migration evidence

Generated `.machine` JSON, manifests, QA status, release reports, and runtime records are generated state or evidence. They are not truth authority.

## Required Skill QA Dimensions

QA for this version must verify:

- every v1.6.0 host-visible skill name uses a harness prefix;
- old host-visible skill aliases are absent from the v1.6.0 skill package;
- every skill carries the shared v1.6.0 preamble;
- planner/generator/evaluator/governor hard gates are explicit;
- no-fake-delivery policy is present in generator and evaluator surfaces;
- rough prompt routing emits a harness route without mutating truth or implementation;
- package-authoritative truth remains resolver-selected Markdown.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen package truth under `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/`;
- a rename matrix for old-to-new skill names;
- tests proving no old host-visible skill aliases remain;
- tests proving shared preamble presence;
- tests proving hard-gate boundaries by harness family.

## Current Status

Requirement truth is being frozen for v1.6.0 planning. Runtime implementation and QA must follow after refreeze.
