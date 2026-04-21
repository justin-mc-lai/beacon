---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through the current v1.3.6 runtime line and its host-native orchestration kernel.
metadata:
  author: Beacon CLI
  version: "1.3.6"
  organization: Beacon
  date: April 2026
  abstract: Standard skill package wrapper for Beacon CLI workflow, lightweight HUD, host-native orchestration runtime, PRD bootstrap, implementation, QA, and release operations.
---

# Beacon Skill

Beacon is an **evidence-first product workflow kernel** for keeping requirements, implementation, QA evidence, and release decisions in one versioned system.

This package is the canonical `skills/beacon/` wrapper for Codex and Claude. It delegates real work to `beacon`, `python3 -m beacon.main`, or `skills/beacon/scripts/run_beacon.sh`.

## Current Release Line

- **Current release line**: `v1.3.6`
- **Current package version**: `1.3.6`
- **Latest accepted docs line**: `docs/beacon/v1.3.6/`
- **Release status**: `release check v1.3.6` passed in-repo
- **Core theme**: core slimming, external skill demotion, and minimal HUD
- **Wireframe predecessor line**: `v1.3.5` froze `prototype` as the formal wireframe-freeze stage
- **Current runtime architecture**: `v1.3.6` uses host-native LLM orchestration and a full-command delivery kernel

`v1.3.6` keeps Beacon lightweight:

```text
human minimal surface
-> host-native implement / qa
-> compatibility plane for external skills and adapters
```

`v1.3.6` defines the current host-native runtime target:

```text
host-native llm
-> semantic envelope
-> beacon delivery kernel
-> release/read-model convergence
```

## Human Surface

Humans should primarily remember the 7+3 surface.

Primary commands:

- `prd`
- `user-story`
- `test-case`
- `prototype`
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
- `beacon-prototype`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

Optional supplemental skills:

- `beacon-prd-bootstrap`: one-click PRD + user-story + test-case bootstrap with safe defaults
- `beacon-toolkit-lighthouse`: fast single-file analysis without entering the main workflow
- `beacon-memory-friction-evolution`: host-visible memory / friction evolution toolkit for optional analysis and writeback planning
- `beacon-real-project-validation`: prove Beacon works against a real target project

## Current v1.3.6 Additions

- **Minimal HUD**: a 1-3 line HUD contract for `help/status`, Ralph, team execution, and Codex fixed HUD injection.
- **Codex fixed HUD hook**: `debug codex-fixed-hud` supports `UserPromptSubmit`, `SessionStart`, `SessionResume`, and `SessionRefresh`, returning HUD text through `hookSpecificOutput.additionalContext`.
- **PRD bootstrap skill**: `beacon-prd-bootstrap` is a human skill, not a new public core command. It defaults to dry-run, strict context verification, no-overwrite, atomic writes, rollback/lock governance.
- **Memory friction toolkit**: memory evolution and target-project friction learning run beside `beacon-toolkit-lighthouse`; use the optional `beacon-memory-friction-evolution` host skill when this analysis plane needs to be explicitly routed.
- **Release gate consistency**: coverage, evidence manifest hashes, implementation-plan progress, and QA matrices are release-gate checked for v1.3.6.

## Current v1.3.6 Runtime Line

- **Host-native requirement compile**: `prd / user-story / test-case / prototype` 默认优先复用宿主原生语义能力。
- **Delivery kernel convergence**: `implement / qa / release` 统一落到共享 delivery contract。
- **Support/read model convergence**: `help / status / doctor` 读取同一 delivery read model 与 surface explanation。
- **Provider fallback demotion**: `BEACON_LLM_API_KEY` 仅保留给纯 CLI / provider fallback。

## Quick Start

Start with the minimal workflow:

```bash
bash skills/beacon/scripts/run_beacon.sh prd create "My Feature" --project . --version v1.3.6
bash skills/beacon/scripts/run_beacon.sh user-story create "My Feature" --project . --version v1.3.6
bash skills/beacon/scripts/run_beacon.sh test-case create "My Feature" --project . --version v1.3.6
bash skills/beacon/scripts/run_beacon.sh implement plan "My Feature" --project . --version v1.3.6 --json
bash skills/beacon/scripts/run_beacon.sh qa run "My Feature" --project . --version v1.3.6 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.6 --project .
```

Ask Beacon what to do next:

```bash
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.6
bash skills/beacon/scripts/run_beacon.sh help --project-root . --version v1.3.6 --feature "My Feature" --json
```

Bootstrap requirement materials safely:

```bash
bash skills/beacon/scripts/run_beacon.sh prd bootstrap "My Feature" --project-root . --version v1.3.6 --dry-run --json
```

Inject Codex fixed HUD context:

```bash
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.3.6"}' \
  | bash skills/beacon/scripts/run_beacon.sh debug codex-fixed-hud --project-root . --version v1.3.6 --json
```

Run final release checks:

```bash
bash skills/beacon/scripts/run_beacon.sh gate check release --project-root . --version v1.3.6 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.6 --project .
```

Optional analysis surface:

```bash
bash skills/beacon/scripts/run_beacon.sh memory-friction-evolution run \
  --project-root . \
  --version v1.3.6 \
  --mode both \
  --json
```

## Workflow Model

Beacon's current human-facing lifecycle target is:

```text
prd
-> user-story
-> test-case
-> prototype
-> implement
-> qa
-> release
```

`prototype` is defined as `requirement-driven wireframe freeze orchestrator`, not HTML high-fidelity output.

For human routing, prefer the minimal 7+3 surface. Do not expose team/subagent/Ralph internals unless the user explicitly asks for them or a Beacon command recommends them.

## Lifecycle Navigation Rules

- Use `beacon help --project-root . --json` when the next step is unclear.
- Run `status` before guessing the current stage.
- QA prompt contract must follow first principles.
- If requirement evidence is incomplete or drifted, return `stop_for_repair`.
- `browser-use` is optional evidence tooling, not the default workflow surface.

## Reading Order

Read current v1.3.6 materials in this order:

1. [`docs/beacon/v1.3.6/SUMMARY.md`](../../docs/beacon/v1.3.6/SUMMARY.md)
2. [`docs/beacon/v1.3.6/execution/index.md`](../../docs/beacon/v1.3.6/execution/index.md)
3. [`docs/beacon/v1.3.6/execution/architecture-blueprint.md`](../../docs/beacon/v1.3.6/execution/architecture-blueprint.md)
4. [`docs/beacon/v1.3.6/execution/project-skill-qa-evolution-blueprint.md`](../../docs/beacon/v1.3.6/execution/project-skill-qa-evolution-blueprint.md)
5. [`docs/beacon/v1.3.6/execution/boundaries.md`](../../docs/beacon/v1.3.6/execution/boundaries.md)
6. [`docs/beacon/v1.3.6/release/v1.3.6.md`](../../docs/beacon/v1.3.6/release/v1.3.6.md)

For host-native runtime architecture detail, then read:

1. [`docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`](../../docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md)
2. [`docs/beacon/v1.3.6/release/v1.3.6.md`](../../docs/beacon/v1.3.6/release/v1.3.6.md)
3. [`docs/beacon/v1.3.6/release/runtime-promotion-checklist.md`](../../docs/beacon/v1.3.6/release/runtime-promotion-checklist.md)

Feature package roots:

- [`docs/beacon/v1.3.6/prd/`](../../docs/beacon/v1.3.6/prd/)
- [`docs/beacon/v1.3.6/user-story/`](../../docs/beacon/v1.3.6/user-story/)
- [`docs/beacon/v1.3.6/qa/test-cases/`](../../docs/beacon/v1.3.6/qa/test-cases/)

## Routing Rules

- If the user asks for requirements, route to `beacon-prd`, `beacon-user-story`, `beacon-test-case`, or `beacon-prd-bootstrap`.
- If the user asks to implement, route to `beacon-implement`.
- If the user asks to verify, inspect coverage, or close evidence, route to `beacon-qa`.
- If the user asks to release, run `beacon-release`.
- If the user is blocked or unsure, run `beacon-help` or `beacon-status` before guessing.
- If context, version, or evidence consistency is broken, route to `beacon-doctor`.

## Compatibility Rule

`v1.3.6` demotes external runners, external skill adapters, and legacy bridge behavior to a compatibility plane. They may still exist for advanced projects, but they must not appear as the default onboarding or main workflow path.

## Troubleshooting

- Materials inconsistent: `beacon doctor verify-context --project-root . --strict --json`
- Runtime upgraded: `beacon doctor sync-materials --project-root . --version v1.3.6 --all-features --json`
- Need current next step: `beacon help --project-root . --version v1.3.6 --feature "<feature>" --json`
- Release confusion: `beacon gate check release --project-root . --version v1.3.6 --json`
- Skill drift: `python3 scripts/check_skill_drift.py --project-root . --json`
- QA prompt contract must follow first principles before doing browser-use or test-case backfill.

## Examples

- [Basic workflow example](./examples/basic-workflow.md)
- [Release readiness example](./examples/release-readiness.md)
- [Implementation compatibility example](./examples/implementation-with-omx.md)
- [Toolkit Lighthouse analysis example](./examples/beacon-toolkit-lighthouse-analysis.md)
