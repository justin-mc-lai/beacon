# Source Architecture: beacon-truth-map-center-and-package-cutover

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`

## Runtime Placement

The long-lived runtime owner is `beacon.utils.truth_map`.

The public command surface is `beacon truth-map`, with downstream consumption by normal lifecycle commands:

- `prd`
- `user-story`
- `test-case`
- `workflow`
- `truth`
- `gate`
- `qa`
- `release`
- `status`
- `doctor`
- `change`

For v1.5.2, these commands should not independently construct `docs/beacon/<version>/prd`, `user-story`, or `qa/test-cases` paths as authority. They should ask the resolver for the package truth location or for the allowed legacy rebuild/absorb route.

## Write Path

Canonical write target:

```text
docs/beacon/<version>/features/<slug>/truth.md
docs/beacon/<version>/features/<slug>/tests.md
docs/beacon/<version>/features/<slug>/tasks.md
docs/beacon/<version>/features/<slug>/evidence.md
```

The package is Markdown authority. CLI parser/validator owns deterministic interpretation:

- frontmatter
- acceptance criteria table
- test coverage table
- checkbox task ledger
- evidence authority labels

LLM skills may write Markdown body/checklist content when routed by the workflow. State advancement must remain CLI-validated.

Legacy write targets are not normal truth writes in v1.5.2. They are only:

- doctor rebuild outputs from package truth
- change absorb inputs into package truth
- archive/historical material

## Read Models And Projections

Read side starts with:

```text
resolve_truth_map(...)
resolve_feature_truth(...)
resolve_gate_inputs(...)
resolve_version_governance(...)
```

Generated JSON is a read model or process record only. It can be useful for diagnostics and evidence freshness, but it is not required as a twin for Markdown validity.

Allowed generated/read model classes:

- resolver-owned `.machine/requirement/*.json`
- generated governance state
- runtime process records under `.beacon/runs/**`
- QA/release evidence records

All generated state must label itself as non-authoritative.

## Contract Boundaries

In scope:

- version-aware resolver authority policy
- feature package parser/validator
- gate/QA/release package consumption
- material audit package completeness
- skill guidance refresh
- doctor rebuild route
- change absorb route
- legacy drift fail-closed diagnostics

Out of scope:

- deleting all historical PRD/user-story/test-case files
- making JSON a required twin for every Markdown truth document
- using support surfaces such as brainstorm/deep/CEO review as gate truth
- changing runtime process JSON into requirement truth
- broad TypeScript/runtime rewrite

The cutover succeeds only if a normal Beacon workflow can produce and consume truth through the package without falling back to legacy triptych authority.
