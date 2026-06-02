# Project Skill QA Evolution Blueprint (v1.5.0)

## Intent

This blueprint defines how Beacon skills and QA should handle the v1.5.0 feature package capability:

```text
beacon-v1.5.0-parallel-plan-b-document-capability
```

The goal is to let LLM-facing skills produce parser-compatible markdown quickly while preserving Python guardrails, canonical requirement truth, QA verdict authority, and release readiness authority.

## Skill Material Effects

Relevant skill invocations must resolve to one of:

- `feature_package_markdown_drafted`
- `feature_package_materialized`
- `feature_package_validation_passed`
- `feature_package_validation_blocked`
- `canonical_chain_preserved`
- `truth_reopen_required`
- `qa_evidence_indexed`
- `read_only_route_only`

Any invocation that claims QA pass, release readiness, freeze pass, or lifecycle completion from `features/<slug>/` markdown alone is out of bounds.

## Required Skill QA Dimensions

QA for this version must verify:

- `beacon-prd`, `beacon-test-case`, `beacon-implement`, and `beacon-qa` expose compact v1.5.0 quick templates.
- Templates include required frontmatter, checkbox, and evidence authority shapes.
- `truth.md` frontmatter remains parallel/read-model metadata.
- Checkbox rows do not complete implement, QA, or release gates.
- `evidence.md` keeps authority labels and rejects gate-truth fields.
- Support outputs such as deep and CEO review remain advisory when indexed.
- Existing CLI and skill surfaces are preserved.

## Acceptance Evidence

Promotion-grade evidence for this line requires:

- frozen PRD / user-story / test-case for the feature;
- synced version feature manifest for v1.4.12+ material discovery;
- generated feature package under `docs/beacon/v1.5.0/features/<slug>/`;
- deterministic validation report under `.machine/requirement/`;
- executable tests covering parser/validator behavior and entrypoint parity;
- formal QA record showing canonical gate authority is preserved.

## Current Status

Requirement truth is frozen for v1.5.0. Runtime implementation and targeted tests exist for the feature package capability. Release promotion still depends on formal QA and release checks.
