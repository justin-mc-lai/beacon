# Beacon Orchestration Human Guide

## Purpose

This document explains how Beacon source-repository orchestration is handled for humans.

Beacon orchestration is not a hidden scheduler. It is a governed sequence of explicit lifecycle commands, project-level hooks, and evidence read models.

The canonical lifecycle still stays:

```text
change/refreeze -> prd -> user-story -> test-case -> implement -> qa -> release
```

Project hooks can be attached at finite lifecycle boundaries, but they are not new stages and they do not write requirement truth.

## Human-Facing Surfaces

### Main Lifecycle

- `beacon change-refreeze ...` freezes changed requirement truth.
- `beacon implement ...` implements against frozen PRD, user-story, and test-case truth.
- `beacon qa ...` produces formal QA verdict and acceptance evidence.
- `beacon release ...` decides release readiness from evidence and gate state.

### Project Hooks

Project hooks live under:

```text
docs/beacon/hooks/<hook-id>.md
```

They are project-level contracts. They are not stored under `docs/beacon/<version>/hooks/`.

Runtime evidence is written under:

```text
.beacon/state/hooks/<hook-id>/
```

The latest read model is written under:

```text
docs/beacon/.machine/hooks/<hook-id>.latest.json
```

## Allowed Hook Boundaries

Beacon currently admits only finite hook codes:

- `post_implement_pre_qa`
- `qa_diagnostics`
- `post_qa_pre_release`
- `post_release`

Any unknown hook code must fail closed.

## Safety Rules

- Hooks do not rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict.
- Side-effect hooks require explicit `--confirm`.
- Hook output is evidence, not requirement truth.
- Project hooks must declare produced evidence and a failure route.
- Beacon core does not become an arbitrary shell orchestrator.

## Beacon Source Release Hook

The Beacon source repository has one concrete release hook:

```text
docs/beacon/hooks/beacon-post-release-local-install.md
```

It is attached to:

```text
hook_code: post_release
```

It exists because releasing Beacon source code has a project-specific local follow-up:

- install/materialize local Codex agent skills;
- verify local Codex agent skills;
- install/materialize local Claude agent skills;
- verify local Claude agent skills;
- install or confirm global `beacon` and `beacon-cli` launchers;
- confirm both launchers report the released Beacon CLI version.

This is intentionally project-specific to the Beacon source repository. Downstream projects do not inherit this hook by default.

## Release Flow With Hook

After a feature is release-ready, run the normal release checks first:

```bash
python3 -m beacon.main release check v1.4.10 --project . --json
```

Then inspect the project hook:

```bash
python3 -m beacon.main hooks plan beacon-post-release-local-install \
  --project-root . \
  --version v1.4.10 \
  --feature <feature> \
  --hook-code post_release \
  --json
```

Dry-run evidence can be created without side effects:

```bash
python3 -m beacon.main hooks run beacon-post-release-local-install \
  --project-root . \
  --version v1.4.10 \
  --feature <feature> \
  --hook-code post_release \
  --dry-run \
  --json
```

The side-effect follow-up requires manual confirmation:

```bash
python3 -m beacon.main hooks run beacon-post-release-local-install \
  --project-root . \
  --version v1.4.10 \
  --feature <feature> \
  --hook-code post_release \
  --confirm \
  --json
```

The confirmed hook records the fixed release follow-up commands:

```bash
python3 -m beacon.main doctor setup-agent-surface --project-root . --version <version> --agent codex --force --json
python3 -m beacon.main doctor verify-agent-surface --project-root . --version <version> --agent codex --strict --json
python3 -m beacon.main doctor setup-agent-surface --project-root . --version <version> --agent claude --force --json
python3 -m beacon.main doctor verify-agent-surface --project-root . --version <version> --agent claude --strict --json
python3 -m beacon.main doctor setup --force --json
beacon --version
beacon-cli --version
```

## Current v1.4.10 Evidence

The current confirmed run is:

```text
.beacon/state/hooks/beacon-post-release-local-install/run-20260524T104516Z-6170.json
```

The latest read model is:

```text
docs/beacon/.machine/hooks/beacon-post-release-local-install.latest.json
```

Expected evidence summary:

- hook status: `passed`
- follow-up status: `pass`
- Codex agent surface verify: `PASS`
- Claude agent surface verify: `PASS`
- `beacon --version`: `Beacon CLI v1.4.10`
- `beacon-cli --version`: `Beacon CLI v1.4.10`

## Failure Handling

If the hook fails, stay in release follow-up and repair local installation or agent skill materialization.

Do not reopen requirement truth for local installation failure.

Do not reinterpret hook success as QA or release success; formal QA and release remain owned by `beacon qa` and `beacon release`.
