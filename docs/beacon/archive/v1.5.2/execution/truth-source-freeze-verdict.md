# Truth Source Freeze Verdict v1.5.2

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- verdict: `requirement_truth_frozen`
- generated_at: `2026-06-02T02:39:36Z`

## Frozen Boundary

v1.5.2 freezes the cutover target: `features/<slug>/{truth,tests,tasks,evidence}.md` is the normal authoritative truth package.

Normal Beacon production and consumption must resolve truth through the truth-map resolver before reading package Markdown.

## Legacy Boundary

Legacy `prd/`, `user-story/`, and `qa/test-cases/` are not normal truth surfaces in v1.5.2. They may remain on disk, but only as:

- `doctor` rebuild output from package truth
- `change` absorb input into package truth

## JSON Boundary

JSON projections are optional diagnostics and evidence. A missing JSON twin must not block Markdown truth validity.

## Current CLI Limitation

The current v1.5.0 validator can validate package shape but cannot yet enforce v1.5.2 authority semantics. v1.5.1 must land the resolver/parser center first.

