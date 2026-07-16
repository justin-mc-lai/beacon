# Truth Source Freeze Verdict v1.5.1

- version: `v1.5.1`
- feature: `beacon-truth-map-center-and-package-cutover`
- verdict: `requirement_truth_frozen`
- generated_at: `2026-06-02T02:39:36Z`

## Frozen Boundary

v1.5.1 freezes the truth-map resolver center requirement. The truth map is deterministic CLI resolver/static contract, not JSON truth.

Feature package Markdown is canonical-ready for v1.5.2. JSON outputs may exist only as projection, diagnostic, evidence, cache, or rebuild metadata.

## Explicit Non-Authority

- `truth-map.json` is not authority.
- `.machine/*.json` is not the Markdown truth twin.
- Legacy `prd/`, `user-story/`, and `qa/test-cases/` are future rebuild/absorb surfaces, not future normal authority.
- `features/<slug>/evidence.md` remains an index/read model and does not carry gate truth.

## Current CLI Limitation

The existing v1.5.0 feature package validator passes package shape, but still reports `gate_authority=canonical_surfaces_preserved`. That is a parser/resolver limitation and is part of the v1.5.1 implementation target.

`beacon change --refreeze-chain` is not used as the final closure mechanism for this new truth-source model because it still hardcodes the old `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze` chain.

