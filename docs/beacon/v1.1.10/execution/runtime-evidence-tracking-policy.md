# Beacon v1.1.10 Runtime Evidence Tracking Policy

## Purpose

`.beacon/` remains a runtime surface, but Beacon now has a narrower rule for what should be tracked in git.

The goal is:

- keep release-ready evidence reproducible
- avoid polluting commits with timestamped scratch state
- preserve enough tracked artifacts for gate/release/current-line tests to pass in a fresh clone

## Track By Default

These runtime artifacts are allowed to stay tracked when they represent the current release line:

- `.beacon/auto-test-status.json`
- `.beacon/gate-report.json`
- `.beacon/evidence-manifest.json`
- `.beacon/evidence-signature-chain.json`
- `.beacon/coverage-summary.json`
- `.beacon/qa/status.json`
- `.beacon/qa/features/<feature>/ac-closure.json`
- `.beacon/qa/features/<feature>/scorecard.json`
- `.beacon/qa/features/<feature>/exhaustiveness-report.json`
- `.beacon/state/baselines/<version>/latest.json`
- `.beacon/state/baselines/<version>/bl-run-v*.json`
- `.beacon/state/spec-fingerprints/<version>/latest.json`
- `.beacon/state/spec-fingerprints/<version>/run-v*.json`
- `.beacon/state/change-impact/run-v*.json`
- `.beacon/state/implementation-*.json` when they define the active release coverage contract
- `.beacon/evidence/test-results/<current-release-feature>/TC-*.json` when those files are the canonical tracked proof for the release line

## Ignore By Default

These artifacts are scratch/runtime-only and should not be committed:

- `.omx/`
- `.beacon/iteration-governance/`
- `.beacon/state/workflow-hud/`
- `.beacon/runs/run-20*/`
- `.beacon/state/change-impact/run-20*.json`
- `.beacon/state/baselines/*/bl-run-20*.json`
- `.beacon/state/spec-fingerprints/*/run-20*.json`

Those patterns are enforced in the repository `.gitignore`.

## Naming Rule

Beacon now follows a simple distinction:

- `run-v*` means intentional named release evidence and may be tracked
- `run-20*` means timestamped transient runtime output and should stay ignored

## Operator Rule

Before committing:

1. keep current release evidence
2. drop timestamped scratch state
3. verify `gate check release` and `release check`

If a new runtime artifact must be tracked, it should first be justified as:

- release-critical
- reproducibility-critical
- required by current-line tests

Otherwise it stays runtime-only.
