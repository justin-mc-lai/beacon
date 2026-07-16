# ADR: Schema V2 nine-table contract (AC-161 path a)

- date: 2026-07-16
- status: accepted
- feature: beacon-v2-rust-kernel-redesign
- decision: **path (a)** implement full nine-table truth contract rather than refreeze-down

## Context

P0 scaffold used 8 operational tables + spine_snapshots/schema_meta, missing
`project_versions` and `checkpoints`, and named artifact storage `artifacts`
instead of `artifact_refs` (AC-074). AC-161 forbids silent drift.

## Decision

- Bump `SCHEMA_VERSION` to **2**.
- Materialize required tables: projects, project_versions, feature_packages,
  feature_lifecycle, runs, lifecycle_events, gate_results, artifact_refs,
  checkpoints.
- Keep `spine_snapshots` + `schema_meta` as projection/meta (not counted).
- Fresh install uses SCHEMA_V2; v1 DBs migrate via SCHEMA_V1_TO_V2 + column
  ensures + conditional backfill from legacy `artifacts` when present.
- `FeatureDao::insert` ensures `project_versions` row (AC-068).
- Contract assertion: `assert_schema_contract` / TC-161.

## Consequences

- Existing v1 DBs migrate without destructive rewrite of feature/run rows.
- Artifact writes go to `artifact_refs.abs_path`.
- P1 projects show prefers `project_versions` list, with feature_packages fallback.
