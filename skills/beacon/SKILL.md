---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through a standard skill package that delegates to beacon CLI commands and scripts.
metadata:
  author: Beacon CLI
  version: "1.3.0"
  organization: Beacon
  date: April 2026
  abstract: Standard skill package wrapper for Beacon CLI workflow, implement, review, and release operations.
---

# Beacon Skill

## Document Role & Fixed Structure

### Role

- `../../SKILL.md` = **main product document**
- `skills/beacon/SKILL.md` = **supplementary package document**

This packaged document must mirror the main document’s structure instead of drifting into a different product narrative.

### Sync Rules

1. Release-line changes, product positioning changes, workflow-model changes, and onboarding guidance must be updated in both files together.
2. If content conflicts:
   - product explanation follows `../../SKILL.md`
   - package-layout guidance follows `skills/beacon/SKILL.md`
3. This file should stay shorter than the main document, but not structurally different from it.

### Fixed Section Template

Both Beacon skill docs should stably cover these section slots (the packaged doc may compress or merge them, but should not omit them):

1. Current release line
2. Product positioning
3. Who this skill is for
4. Quick start
5. Workflow model
6. Current product surfaces
7. Why this skill matters
8. Recommended reading order
9. Common usage modes
10. Command / wrapper surface
11. Lifecycle navigation rules
12. Docs / troubleshooting / examples / references

## Product Positioning

Beacon is an **evidence-first product workflow kernel**.

This packaged skill is the canonical `skills/beacon/` wrapper for Beacon CLI. It is not just a thin alias layer: it is the standard operator surface for using Beacon as a product workflow system.

Beacon unifies:

- requirement clarification
- user stories
- PRDs
- test cases
- implementation handoff
- technical archive / review
- QA / verification
- gate / release governance

into one versioned, auditable lifecycle.

If you only remember one sentence:

> **Beacon is for teams that want requirements, implementation, evidence, and release decisions to live in one coherent system.**

## Current Release Line

- **Current release line**: `v1.3.0`
- **Current package version**: `1.3.0`
- **Latest accepted docs line**: `v1.3.0`
- **Current landed implementation line**: `v1.3.0` (bounded Codex multi-role team runtime / implement-team tmux HUD / qa-team runtime contract / externalized role config; implemented and verified in-repo)
- **Current supplement line**: `v1.2.1` (Codex `UserPromptSubmit` -> Beacon debug prompt adaptation / guidance / debug evidence ingress)
- **Previous stable line**: `v1.1.12` (design governance / version truth / profile-aware routing / typed learning plane / takeover baseline gate)

`v1.3.0` note:

- the repo now ships implement-team tmux runtime, team HUD, and externalized team-role configs as part of the current release line
- read `../../docs/beacon/v1.3.0/` for the current runtime line
- read `../../docs/beacon/v1.2.1/` for the current Codex hook / debug supplement line

## Overview

It exposes Beacon through a `skills/beacon/` package layout while still delegating real work to:

- `beacon <subcommand>`
- `python3 -m beacon.main <subcommand>`
- `./skills/beacon/scripts/run_beacon.sh`

## Who This Skill Is For

### Good fit
- AI/product teams that want a strict requirement-to-release workflow
- repos that need versioned requirement materials under `docs/beacon/<version>/`
- teams that want stage-aware next-step computation instead of guessing
- projects that care about evidence, gate checks, and machine-backed traceability

### Not the right fit
- “just write some code for me” usage with no requirement or release discipline
- repos that only want a one-off markdown template generator
- using Beacon as a replacement for deployment infrastructure or browser automation infrastructure itself

## Quick Start

### Start a feature lifecycle

```bash
bash skills/beacon/scripts/run_beacon.sh workflow start "My Feature" --project . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh think start "My Feature" --project . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh user-story create "My Feature" --project . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh prd create "My Feature" --project . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh test-case create "My Feature" --project . --version v1.3.0
```

### Ask Beacon what comes next

```bash
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh help --project-root . --feature "My Feature" --version v1.3.0 --json
```

### Adapt Codex `UserPromptSubmit` into Beacon guidance

```bash
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"请帮我梳理登录需求并进入 Beacon 主链"}' \
  | bash skills/beacon/scripts/run_beacon.sh debug codex-user-prompt-submit --project-root . --version v1.2.1 --json
```

### Run implementation and closure

```bash
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
bash skills/beacon/scripts/run_beacon.sh implement plan "My Feature" --project . --version v1.3.0 --json
bash skills/beacon/scripts/run_beacon.sh implement run "My Feature" --project . --version v1.3.0 --runner auto --json
bash skills/beacon/scripts/run_beacon.sh implement run "My Feature" --project . --version v1.3.0 --runner auto --auto-qa --auto-qa-follow-handoff --auto-qa-max-rounds 3 --json
bash skills/beacon/scripts/run_beacon.sh qa run "My Feature" --project . --version v1.3.0 --json
bash skills/beacon/scripts/run_beacon.sh review quality "My Feature" --project . --version v1.3.0 --json
bash skills/beacon/scripts/run_beacon.sh gate check release --project-root . --version v1.3.0 --json
```

## Workflow Model

Beacon’s standard lifecycle is:

```text
think
→ user-story
→ prd
→ [prototype]
→ test-case
→ implementation
→ verify / qa
→ gate
→ release
```

Supporting surfaces:

- `init` for project takeover / onboarding
- `debug` for runtime friction / feedback capture
- `status`, `report`, `resume`, `remember`, `recall` for recovery and observability

## Current Product Surfaces

Current v1.3.0 release-line surfaces:

1. requirement package generation
   - `workflow / think / user-story / prd / test-case`
2. project takeover
   - `init`
3. implementation archive
   - `implement`
   - `implement plan / compile-plan`
   - implementation-plan gate / task progress / writeback closure
   - `technical-implementation-*`
4. feature-aware QA and story-exhaustive verification
   - `qa run <feature>`
   - `qa evolve <feature>`
   - `qa session`
   - `story-exhaustive`
5. debug / recovery / control loop
   - `debug`
   - `resume`
   - exhaustion / checkpoint semantics
   - `debug codex-user-prompt-submit`
6. review / gate / release / learning governance
   - `review`
   - `gate`
   - `release`
   - `release scorecard`
   - keep/discard + evo harness

### QA prompt contract must follow first principles

When this skill routes into `qa`, it must preserve the same first-principles order as the product docs:

```text
user story / AC order
→ scenario divergence
→ current-round execution
→ evidence pack
→ coverage_current / coverage_gap
→ continue_decision
→ severe blocker? stop_for_repair
→ repair handoff
→ beacon help resume
→ next QA round with test-case backfill
→ release guidance
```

Required behaviors:

1. do not skip story/AC order and jump straight to random layers
2. do not claim closure without evidence pack, replay truth, and current coverage snapshot
3. do stop the round when severe blockers make downstream evidence untrustworthy
4. do give humans a repair handoff plus a `beacon help ...` resume path
5. do backfill missing test cases before claiming the next round improved coverage
6. do preserve browser session continuity; default browser path should prefer `browser-use`

## Why This Skill Matters

Without Beacon, teams often scatter delivery truth across:

- chat transcripts
- ad hoc docs
- implementation notes
- QA artifacts
- release checklists

Beacon puts them back together as:

```text
requirements
→ implementation
→ verification evidence
→ gate decision
→ release readiness
```

That is the product contract this skill is exposing.

## When to Use

Use this skill when:

- you need Beacon requirement-material generation
- you need workflow / implement / review / gate / release execution
- you need stage-aware help about current lifecycle status, blockers, or next steps
- you need to freeze the current revision before implementation or reopen a superseded revision
- you need a standard `skills/<name>/` package instead of only a root-level `SKILL.md`
- you want a script-based entrypoint for Beacon from skill runtimes

## Recommended Reading Order

1. [Summary](../../docs/beacon/v1.3.0/SUMMARY.md)
2. [Execution index](../../docs/beacon/v1.3.0/execution/index.md)
3. [Architecture blueprint](../../docs/beacon/v1.3.0/execution/architecture-blueprint.md)
4. [Workflow usage guide](../../docs/beacon/v1.3.0/execution/workflow-usage-guide.md)
5. [Natural-language trigger handbook](../../docs/beacon/v1.3.0/execution/natural-language-trigger-handbook.md)
6. [QA autoresearch usage guide](../../docs/beacon/v1.3.0/execution/qa-autoresearch-usage-guide.md)
7. [Autoresearch module evolution](../../docs/beacon/v1.3.0/execution/autoresearch-module-evolution.md)
8. [Implementation blueprint](../../docs/beacon/v1.3.0/execution/requirement-anchor-implementation-blueprint.md)
9. [Release note](../../docs/beacon/v1.3.0/release/v1.3.0.md)

If you are working on the latest landed closure line, then read:

1. `../../docs/beacon/v1.1.9/SUMMARY.md`
2. `../../docs/beacon/v1.1.9/execution/closure-loop-blueprint.md`
3. `../../docs/beacon/v1.1.9/prd/beacon-closure-control-learning-overlay.md`
4. `../../docs/beacon/v1.1.9/release/v1.1.9.md`

If you are planning the next QA precision line, then read:

1. `../../docs/beacon/v1.3.0/SUMMARY.md`
2. `../../docs/beacon/v1.3.0/prd/beacon-version-truth-profile-boundary-governance.md`
3. `../../docs/beacon/v1.3.0/prd/beacon-prototype-design-governance-loop.md`
4. `../../docs/beacon/v1.3.0/execution/requirement-anchor-implementation-blueprint.md`

## How to Use

1. Read the current version package under [`../../docs/beacon/v1.3.0/`](../../docs/beacon/v1.3.0/SUMMARY.md)
2. Use the command docs hub when you need the right level of operator guidance:

- [Summary](../../docs/beacon/v1.3.0/SUMMARY.md)
- [Execution index](../../docs/beacon/v1.3.0/execution/index.md)
- [Workflow usage guide](../../docs/beacon/v1.3.0/execution/workflow-usage-guide.md)
- [Natural-language trigger handbook](../../docs/beacon/v1.3.0/execution/natural-language-trigger-handbook.md)
- [QA autoresearch usage guide](../../docs/beacon/v1.3.0/execution/qa-autoresearch-usage-guide.md)
- [Autoresearch module evolution](../../docs/beacon/v1.3.0/execution/autoresearch-module-evolution.md)
- [Release note](../../docs/beacon/v1.3.0/release/v1.3.0.md)
- [Architecture blueprint](../../docs/beacon/v1.3.0/execution/architecture-blueprint.md)
- [Closure loop blueprint](../../docs/beacon/v1.1.9/execution/closure-loop-blueprint.md)
3. Use the wrapper script:

```bash
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh workflow --help
bash skills/beacon/scripts/run_beacon.sh help --project-root . --json
bash skills/beacon/scripts/run_beacon.sh freeze "My Feature" --project-root . --version v1.3.0
bash skills/beacon/scripts/run_beacon.sh reopen "My Feature" --project-root . --version v1.3.0 --reason change-request
```

4. For implementation adapters and lifecycle navigation:

```bash
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
bash skills/beacon/scripts/run_beacon.sh implement plan "My Feature" --project-root . --version v1.3.0 --json
bash skills/beacon/scripts/run_beacon.sh help --project-root . --feature "My Feature" --json
bash skills/beacon/scripts/run_beacon.sh doctor upgrade-package --version v1.3.0 --json
```

## Command / Wrapper Surface

Primary command surface:

- `beacon <subcommand>`

Compatible delegated surfaces:

- `python3 -m beacon.main <subcommand>`
- `bash skills/beacon/scripts/run_beacon.sh <subcommand> ...`
- `python3 scripts/check_skill_drift.py --project-root . --json`

## Common Usage Modes

### 1. Requirement package mode
- `workflow`
- `think`
- `user-story`
- `prd`
- `test-case`

### 2. Delivery closure mode
- `implement plan`
- `implement`
- `qa`
- `review`
- `gate`
- `release`

### 3. Project takeover mode
- `init`
- `status`
- `help`
- `doctor`

### 4. Recovery / observability mode
- `resume`
- `report`
- `debug`
- `remember`
- `recall`
- `skill sync-check`

## Lifecycle Navigation Rules

When the user asks "what should I do next", "why am I blocked", or wants to continue a feature without knowing the correct stage:

1. Run `beacon status --board --project-root <root> --version <version>` when you need the raw board.
2. Run `beacon help --project-root <root> --version <version> --feature <feature> --json` for the canonical next-step recommendation.
3. If help indicates the revision is not frozen, run `beacon freeze ...` before implementation.
4. If help indicates implementation-plan drift or absence, run `beacon implement plan ...` before implementation.
5. If help/doctor indicates the current revision is superseded or a change request is pending, run `beacon reopen ...`.
6. If blocked or inconsistent, run `beacon doctor --project-root <root> --json` or `beacon doctor advise ...`.
7. If the project has a profile / project-specific skill path, prefer `beacon verify run ... --profile <profile>` before trying to accept.
8. For QA rounds, prefer:
   - `beacon qa run "<feature>" --project . --version v1.3.0 --json`
   - inspect evidence / coverage / continue decision
   - if blocked, repair first and resume via `beacon help ...`
9. Only then route into `freeze`, `implement`, `review`, `verify`, `orchestrate`, or `release` actions.

Example: `beacon help --project-root . --json`

Never guess the next action when Beacon can compute it.

## Docs & Troubleshooting

Use this section the same way gstack uses its product-level docs footer: as the operator handoff surface for “where do I read more” and “what do I run when things feel wrong”.

## Examples

See:

- [Basic workflow example](./examples/basic-workflow.md)
- [Release readiness example](./examples/release-readiness.md)
- [Implementation with OMX example](./examples/implementation-with-omx.md)

## References

- [Sections index](./references/_sections.md)
- [Usage rules](./references/usage-rules.md)
- [Summary](../../docs/beacon/v1.3.0/SUMMARY.md)
- [Execution index](../../docs/beacon/v1.3.0/execution/index.md)
- [QA PRD](../../docs/beacon/v1.3.0/prd/beacon-version-truth-profile-boundary-governance.md)
- [Skill development standard](../../../docs/skill-development-standards.md)
- [Root compatibility skill](../../SKILL.md)

### Troubleshooting

- Skill wrapper works but CLI fails:
  - run `bash skills/beacon/scripts/run_beacon.sh --version`
- Materials feel inconsistent:
  - run `beacon doctor --project-root . --json`
  - run `beacon doctor verify-materials --project-root . --version v1.3.0 --json`
- Old package line needs current runtime-compatible material upgrades:
  - run `beacon doctor upgrade-package --project-root . --version <old-version> --json`
- Not sure what step comes next:
  - run `beacon help --project-root . --version v1.3.0 --feature "<feature>" --json`
- Gate / release confusion:
  - read `../../docs/beacon/v1.3.0/release/v1.3.0.md`
  - run `beacon gate check release --project-root . --version v1.3.0 --json`
- Not sure whether local Claude/Codex skill copies drifted:
  - run `python3 scripts/check_skill_drift.py --project-root . --json`
  - run `beacon skill sync-check --project-root . --json`
