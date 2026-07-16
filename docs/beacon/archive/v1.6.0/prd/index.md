# PRD Index (v1.6.0)

v1.6.0 uses **feature-package authoritative** truth. Legacy `prd/` is a closure stub for release gate compatibility; canonical requirements live under `features/<slug>/truth.md`.

| Feature | Canonical truth |
|---|---|
| beacon-loop-goal-closed-loop-orchestrator | `docs/beacon/archive/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` |
| beacon-skill-harness-taxonomy-v160 | `docs/beacon/archive/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md` |
| beacon-loop-native-runner-and-automation-retirement | `docs/beacon/archive/v1.6.0/features/beacon-loop-native-runner-and-automation-retirement/truth.md` |
| beacon-pln-review | `docs/beacon/archive/v1.6.0/features/beacon-pln-review/truth.md` |
| beacon-run-harness | `docs/beacon/archive/v1.6.0/features/beacon-run-harness/truth.md` |

Rebuild legacy triptych from package truth: `beacon doctor sync-materials --project-root . --version v1.6.0 --all-features`
