# User Story Index (v1.6.0)

v1.6.0 uses **feature-package authoritative** truth. Legacy `user-story/` is a closure stub for release gate compatibility; acceptance criteria live in `features/<slug>/truth.md` and `features/<slug>/tests.md`.

| Feature | Stories / AC |
|---|---|
| beacon-loop-goal-closed-loop-orchestrator | `features/beacon-loop-goal-closed-loop-orchestrator/truth.md`, `tests.md` |
| beacon-skill-harness-taxonomy-v160 | `features/beacon-skill-harness-taxonomy-v160/truth.md`, `tests.md` |
| beacon-loop-native-runner-and-automation-retirement | `features/beacon-loop-native-runner-and-automation-retirement/truth.md`, `tests.md` |
| beacon-pln-review | `features/beacon-pln-review/truth.md`, `tests.md` |
| beacon-run-harness | `features/beacon-run-harness/truth.md`, `tests.md` |

Resolver-first: `beacon truth-map resolve <feature> --project . --version v1.6.0 --json`
