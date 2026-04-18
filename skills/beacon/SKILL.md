---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through the current v1.3.3 lightweight skill package.
metadata:
  author: Beacon CLI
  version: "1.3.3"
  organization: Beacon
  date: April 2026
  abstract: Standard skill package wrapper for Beacon CLI workflow, lightweight HUD, PRD bootstrap, implementation, QA, and release operations.
---

# Beacon Skill

Beacon is an **evidence-first product workflow kernel** for keeping requirements, implementation, QA evidence, and release decisions in one versioned system.

This package is the canonical `skills/beacon/` wrapper for Codex and Claude. It delegates real work to `beacon`, `python3 -m beacon.main`, or `skills/beacon/scripts/run_beacon.sh`.

## Current Release Line

- **Current release line**: `v1.3.3`
- **Current package version**: `1.3.3`
- **Latest accepted docs line**: `docs/beacon/v1.3.3/`
- **Release status**: `release check v1.3.3` passed in-repo
- **Core theme**: core slimming, external skill demotion, and minimal HUD

`v1.3.3` keeps Beacon lightweight:

```text
human minimal surface
-> host-native implement / qa
-> compatibility plane for external skills and adapters
```

## Human Surface

Humans should primarily remember only the 6+3 surface.

Primary commands:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

Support commands:

- `help`
- `status`
- `doctor`

Compatibility surfaces such as external adapters, legacy bridges, project-specific runners, and deep runtime orchestration must stay opt-in and non-default.

## Host-Visible Skills

The public Codex / Claude surfaces are:

- `using-beacon`
- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

Optional supplemental skills:

- `beacon-prd-bootstrap`: one-click PRD + user-story + test-case bootstrap with safe defaults
- `beacon-toolkit-lighthouse`: fast single-file analysis without entering the main workflow
- `beacon-real-project-validation`: prove Beacon works against a real target project

## Current v1.3.3 Additions

- **Minimal HUD**: a 1-3 line HUD contract for `help/status`, Ralph, team execution, and Codex fixed HUD injection.
- **Codex fixed HUD hook**: `debug codex-fixed-hud` supports `UserPromptSubmit`, `SessionStart`, `SessionResume`, and `SessionRefresh`, returning HUD text through `hookSpecificOutput.additionalContext`.
- **PRD bootstrap skill**: `beacon-prd-bootstrap` is a human skill, not a new public core command. It defaults to dry-run, strict context verification, no-overwrite, atomic writes, rollback/lock governance.
- **Memory friction toolkit**: memory evolution and target-project friction learning run beside `beacon-toolkit-lighthouse`; they do not expand the main human surface.
- **Release gate consistency**: coverage, evidence manifest hashes, implementation-plan progress, and QA matrices are release-gate checked for v1.3.3.

## Quick Start

Start with the minimal workflow:

```bash
bash skills/beacon/scripts/run_beacon.sh prd create "My Feature" --project . --version v1.3.3
bash skills/beacon/scripts/run_beacon.sh user-story create "My Feature" --project . --version v1.3.3
bash skills/beacon/scripts/run_beacon.sh test-case create "My Feature" --project . --version v1.3.3
bash skills/beacon/scripts/run_beacon.sh implement plan "My Feature" --project . --version v1.3.3 --json
bash skills/beacon/scripts/run_beacon.sh qa run "My Feature" --project . --version v1.3.3 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.3 --project .
```

Ask Beacon what to do next:

```bash
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.3
bash skills/beacon/scripts/run_beacon.sh help --project-root . --version v1.3.3 --feature "My Feature" --json
```

Bootstrap requirement materials safely:

```bash
bash skills/beacon/scripts/run_beacon.sh prd bootstrap "My Feature" --project-root . --version v1.3.3 --dry-run --json
```

Inject Codex fixed HUD context:

```bash
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.3.3"}' \
  | bash skills/beacon/scripts/run_beacon.sh debug codex-fixed-hud --project-root . --version v1.3.3 --json
```

Run final release checks:

```bash
bash skills/beacon/scripts/run_beacon.sh gate check release --project-root . --version v1.3.3 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.3 --project .
```

## Workflow Model

Beacon's full internal lifecycle remains:

```text
think
-> user-story
-> prd
-> test-case
-> implement
-> qa
-> gate
-> release
```

For human routing, prefer the minimal 6+3 surface. Do not expose team/subagent/Ralph internals unless the user explicitly asks for them or a Beacon command recommends them.

## Lifecycle Navigation Rules

- Use `beacon help --project-root . --json` when the next step is unclear.
- Run `status` before guessing the current stage.
- QA prompt contract must follow first principles.
- If requirement evidence is incomplete or drifted, return `stop_for_repair`.
- `browser-use` is optional evidence tooling, not the default workflow surface.

## Reading Order

Read current v1.3.3 materials in this order:

1. [`docs/beacon/v1.3.3/SUMMARY.md`](../../docs/beacon/v1.3.3/SUMMARY.md)
2. [`docs/beacon/v1.3.3/execution/index.md`](../../docs/beacon/v1.3.3/execution/index.md)
3. [`docs/beacon/v1.3.3/execution/architecture-blueprint.md`](../../docs/beacon/v1.3.3/execution/architecture-blueprint.md)
4. [`docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md`](../../docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md)
5. [`docs/beacon/v1.3.3/execution/boundaries.md`](../../docs/beacon/v1.3.3/execution/boundaries.md)
6. [`docs/beacon/v1.3.3/release/v1.3.3.md`](../../docs/beacon/v1.3.3/release/v1.3.3.md)

Feature package roots:

- [`docs/beacon/v1.3.3/prd/`](../../docs/beacon/v1.3.3/prd/)
- [`docs/beacon/v1.3.3/user-story/`](../../docs/beacon/v1.3.3/user-story/)
- [`docs/beacon/v1.3.3/qa/test-cases/`](../../docs/beacon/v1.3.3/qa/test-cases/)

## Routing Rules

- If the user asks for requirements, route to `beacon-prd`, `beacon-user-story`, `beacon-test-case`, or `beacon-prd-bootstrap`.
- If the user asks to implement, route to `beacon-implement`.
- If the user asks to verify, inspect coverage, or close evidence, route to `beacon-qa`.
- If the user asks to release, run `beacon-release`.
- If the user is blocked or unsure, run `beacon-help` or `beacon-status` before guessing.
- If context, migration, or evidence consistency is broken, route to `beacon-doctor`.

## Compatibility Rule

`v1.3.3` demotes external runners, external skill adapters, and legacy bridge behavior to a compatibility plane. They may still exist for advanced projects, but they must not appear as the default onboarding or main workflow path.

## Troubleshooting

- Materials inconsistent: `beacon doctor verify-context --project-root . --strict --json`
- Runtime upgraded: `beacon doctor sync-materials --project-root . --version v1.3.3 --all-features --json`
- Need current next step: `beacon help --project-root . --version v1.3.3 --feature "<feature>" --json`
- Release confusion: `beacon gate check release --project-root . --version v1.3.3 --json`
- Skill drift: `python3 scripts/check_skill_drift.py --project-root . --json`
- QA prompt contract must follow first principles before doing browser-use or test-case backfill.

## Examples

- [Basic workflow example](./examples/basic-workflow.md)
- [Release readiness example](./examples/release-readiness.md)
- [Implementation compatibility example](./examples/implementation-with-omx.md)
- [Toolkit Lighthouse analysis example](./examples/beacon-toolkit-lighthouse-analysis.md)
