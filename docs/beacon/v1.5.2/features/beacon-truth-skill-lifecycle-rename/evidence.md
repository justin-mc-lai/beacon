# Evidence: Truth Skill Lifecycle Rename

| Surface | Authority | Canonical Artifact | Status | Route |
|---|---|---|---|---|
| beacon-brainstorm | support_advisory | docs/beacon/v1.5.2/research/beacon-truth-skill-lifecycle-rename.md | adopted | change |
| version-summary | requirement_truth | docs/beacon/v1.5.2/SUMMARY.md | indexed | truth |
| feature-package | requirement_truth | docs/beacon/v1.5.2/features/beacon-truth-skill-lifecycle-rename/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.5.2/features/beacon-truth-skill-lifecycle-rename/tests.md | authoritative | truth.coverage |
| existing-skills | support_advisory | skills/beacon/SKILL.md; skills/beacon/beacon-prd/SKILL.md; skills/beacon/beacon-user-story/SKILL.md; skills/beacon/beacon-test-case/SKILL.md | indexed | truth |

## Decision Record

- Accepted: add a preferred `beacon-truth` umbrella skill for v1.5.2+ truth lifecycle language.
- Accepted: keep old `beacon-prd`, `beacon-user-story`, and `beacon-test-case` skills as compatibility aliases.
- Accepted: do not collapse definition, acceptance, and coverage into a single freeform authoring mode.
- Accepted: coverage remains distinct in `features/<slug>/tests.md`.
- Accepted: support surfaces remain advisory and route back to truth or change.

## Closure Status

This evidence file records the accepted support finding and its promotion into package-authoritative requirement truth. It does not claim implementation, QA, or release completion.

`evidence.md` is an index/read model. It must not contain final verdict, gate truth, release readiness, or source-of-truth override fields.
