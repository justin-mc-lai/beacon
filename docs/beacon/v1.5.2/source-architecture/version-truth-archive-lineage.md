# Source Architecture: version-truth-archive-lineage

- version: `v1.5.2`
- feature: `version-truth-archive-lineage`

## Runtime Placement

- **Public surface**: extend `beacon.commands.archive` with `catalog` subcommands (`plan`, `apply`, `bootstrap`, `status`) plus `lineage` and `inventory`; reuse existing feature-level `plan/apply/status/explain`.
- **Core modules**: extend `beacon/utils/archive_governance.py`; new `beacon/utils/version_truth_catalog.py` (parse/render/commit); `beacon/utils/versioning.resolve_version_truth_root()` consumed by truth-map, doctor, status, implement preflight.
- **Doctor**: `beacon doctor verify-version-truth-catalog` mirrors governance projection drift pattern from `project-governance-projection-lifecycle`.

## Write Path

1. Operator runs `archive catalog plan` → diff active window vs disk.
2. `catalog apply --confirm` or `catalog bootstrap --confirm` commits **`docs/beacon/governance/version-truth-catalog.md`** (sole authority) with `transaction_id` + `source_hash`.
3. Same transaction relocates version trees, regenerates **`docs/beacon/archive/INDEX.md`**, writes **`.machine/version-truth-catalog.json`**, updates sqlite `source_hash` when shared projection store is enabled.
4. Feature-level archive (four states) remains inside active version trees via existing feature apply path.

## Read Models And Projections

| Surface | Role |
|---------|------|
| `version-truth-catalog.md` | Canonical commit source |
| `.machine/version-truth-catalog.json` | Resolver fast path (generated) |
| sqlite `source_hash` | Drift verify (optional shared store) |
| `archive/INDEX.md` | Human nav (generated, non-canonical) |
| per-version `.machine/archive/*` | Feature-level archive index (existing) |

## Contract Boundaries

- **In scope**: version-level catalog, relocate, lineage/inventory, discovery unification, skill docs, global-boundaries §4.1.
- **Out of scope**: governance branch prune (parent feature); Rolo app code; slug alias MD; deleting archived content.
- **Two planes**: `project-version-governance.md` (git branch) vs `version-truth-catalog.md` (truth tree placement) — never merged.
