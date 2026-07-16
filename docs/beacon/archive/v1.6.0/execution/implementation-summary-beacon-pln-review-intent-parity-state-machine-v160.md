# Implementation Summary: beacon-pln-review-intent-parity-state-machine-v160

## Scope

Implemented the accepted v1.6.0 planner review convergence feature.

## Changed Surfaces

- Added `skills/beacon/beacon-pln-review/` with thin `SKILL.md`, `agents/openai.yaml`, and direct references for reviewer catalog, finding schema, intent/parity artifacts, state-machine review, and skill package standard.
- Updated `beacon/utils/agent_surface.py` so v1.6.0 public planner projection is limited to `beacon-pln-brainstorm`, `beacon-pln-source`, `beacon-pln-review`, and `beacon-pln-friction`.
- Routed demoted planner aliases and compact fine-grained planner names to `beacon-pln-review` instead of materializing them as public planner skills.
- Removed source and generated host-visible `SKILL.md` entries for `beacon-pln-deep`, `beacon-pln-founder`, `beacon-pln-design`, `beacon-pln-security`, `beacon-pln-performance`, `beacon-pln-doubt`, `beacon-pln-context`, `beacon-pln-simplify`, and `beacon-pln-adr`.
- Updated root Beacon skill/router guidance and package metadata to reflect the compact planner public surface.
- Extended `beacon/utils/skill_eval_kit.py` with `beacon-pln-review` route cases and benchmark cases for intent snapshot, full parity, source parity matrix, deferral ledger, state-machine output, state truth/tests landing, finding schema, planner autofix boundary, and reviewer synthesis.
- Updated `tests/test_v160_skill_harness_taxonomy.py` to assert compact planner public surface, internal reviewer catalog, eval-kit routing, benchmark coverage, and generated package projection.

## Verification Run

- `pytest -q tests/test_v160_skill_harness_taxonomy.py` -> 16 passed.
- `beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json` -> pass.
- `beacon skill package materialize --project-root . --version v1.6.0 --force --json` -> pass; generated package now exposes four planner public skills and removes nine demoted planner directories.
- `beacon validate-feature-package beacon-pln-review-intent-parity-state-machine-v160 --project . --version v1.6.0 --json` -> pass.
- `beacon skill package verify-research beacon-pln-review-intent-parity-state-machine-v160 --project-root . --version v1.6.0 --json` -> pass.
- `beacon skill package verify-promotion beacon-pln-review-intent-parity-state-machine-v160 --project-root . --version v1.6.0 --json` -> pass.
- `beacon skill eval-kit benchmark --project . --version v1.6.0 --json` -> pass; evidence root `.beacon/state/skill-eval/benchmarks/skill-benchmark-20260609t084012z`.
- OpenAI skill-creator quick validation for `skills/beacon/beacon-pln-review` -> valid.
- Anthropic skill-creator quick validation for `skills/beacon/beacon-pln-review` -> valid.

## QA Repair Follow-up

- Restored `skills/beacon/beacon-gov-automation/SKILL.md` as the canonical source skill and synchronized `.generated/skills/beacon` plus `.agents/skills` from that source.
- Preserved the automation-retirement guidance: legacy queue/job/launchd automation routes to `beacon-loop goal`, while truth, QA, and release remain formal closure authorities.
- Replaced non-executable `tests.md` pseudo-commands with deterministic CLI/Python assertions that emit structured JSON checks.
- Tightened `beacon-pln-review` reviewer catalog wording so the state-machine reviewer explicitly covers lifecycle, workflow, loop, resume/stop/recovery, permission, and source-parity triggers.
- Rebuilt feature package machine projections after the coverage truth update.

## QA Repair Verification

- `beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json` -> pass.
- `beacon skill package verify --project-root . --version v1.6.0 --json` -> pass.
- `beacon doctor verify-agent-surface --project-root . --version v1.6.0 --agent codex --strict --json` -> pass.
- `beacon truth-map verify beacon-pln-review-intent-parity-state-machine-v160 --project . --version v1.6.0 --json` -> pass.
- `beacon skill eval-kit benchmark --version v1.6.0 --json` -> pass.

## Handoff Boundary

This is implementation evidence only. It does not provide formal QA pass or release readiness. Formal verdict must route to `beacon-eval-qa` and then `beacon-eval-release`.
