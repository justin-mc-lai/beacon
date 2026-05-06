---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through the current v1.3.9 runtime line and its host-native orchestration kernel.
metadata:
  author: Beacon CLI
  version: "1.3.9"
  organization: Beacon
  date: April 2026
  abstract: Standard skill package wrapper for Beacon CLI workflow, lightweight HUD, host-native orchestration runtime, PRD bootstrap, implementation, QA, and release operations.
---

# Beacon Skill

Beacon is an **evidence-first product workflow kernel** for keeping requirements, implementation, QA evidence, and release decisions in one versioned system.

This package is the canonical `skills/beacon/` wrapper for Codex and Claude. It delegates real work to `beacon`, `python3 -m beacon.main`, or `skills/beacon/scripts/run_beacon.sh`.

## Current Release Line

- **Current release line**: `v1.3.9`
- **Current package version**: `1.3.9`
- **Latest accepted docs line**: `docs/beacon/v1.3.9/`
- **Release status**: `release check v1.3.9` passed in-repo
- **Core theme**: truth lifecycle governance
- **Wireframe predecessor line**: `v1.3.5` froze `prototype` as the formal wireframe-freeze stage
- **Current runtime architecture**: `v1.3.9` promotes the host-native kernel with canonical delivery baseline enforcement, prompt-boundary gating, and archive governance

## Latest Requirement Closure Line

- **Requirement deepening line**: `v1.3.12`
- **Current requirement theme**: `host-llm requirement deepening and human-loop closure`
- **Closed-loop additions**:
  - `requirement_gap_digest`
  - `brainstorm_hint`
  - `supplement_task`
  - `re_freeze_transaction`
  - board jump links to story/test-case supplement entries

`v1.3.9` keeps Beacon lightweight:

```text
human minimal surface
-> host-native implement / qa
-> compatibility plane for external skills and adapters
```

`v1.3.9` defines the current host-native runtime target:

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
- `archive`

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
- `beacon-archive`

Optional supplemental skills:

- `beacon-prd-bootstrap`: one-click PRD + user-story + test-case bootstrap with safe defaults
- `beacon-brainstorm`: read-only first-principles / Socratic / Occam sidecar for requirement convergence and project evolution thinking
- `beacon-archive`: formal archive governance for isolating active truth from historical truth
- `beacon-toolkit-lighthouse`: fast single-file analysis without entering the main workflow
- `beacon-toolkit-metadata`: deterministic metadata toolkit for project/version topology, branch binding, CRUD, and verify
- `beacon-friction-intake`: host-visible friction intake entry for scan/capture plus sqlite queue governance
- `beacon-real-project-validation`: prove Beacon works against a real target project

## Current v1.3.9 Additions

- **Diagram truth admission**: PRD state-machine / branch-flow / decision-priority truth now enters planning and review surfaces.
- **Prompt-boundary closure**: implement prompt-boundary verdict is persisted once and enforced through gate, release scorecard, and release check.
- **Archive governance**: `beacon archive plan/apply/status/explain` is now part of the public support surface with `beacon-archive` routing.
- **Canonical delivery baseline**: implementation-plan, deterministic implementation contract, and git workflow still project from one canonical baseline envelope.
- **Built-in brainstorm sidecar**: `beacon-brainstorm` remains read-only and feeds change/refreeze instead of mutating frozen truth.
- **Minimal HUD and host traceability**: Codex HUD hook and host prompt trace keep current runtime execution auditable.

## Current v1.3.9 Runtime Line

- **Host-native requirement compile**: `prd / user-story / test-case / prototype` 默认优先复用宿主原生语义能力。
- **Requirement bridge family**: `skills/beacon/scripts/run_beacon.sh` 默认导出 `prd / user-story / test-case / prototype` 四条 host bridge 命令，requirement surface 先走 command bridge，再退回兼容注入面。
- **Truth-projected story and QA compile**: `user-story / test-case` 不再只走最小模板占位；bridge 现在会回读目标项目的 requirement truth，生成更贴近冻结材料的 story payload 与 test entries。
- **Delivery kernel convergence**: `implement / qa / release` 统一落到共享 delivery contract。
- **Canonical projection governance**: implementation projections are single-source and gate-verifiable against the canonical delivery baseline.
- **Prompt-boundary enforcement**: release readiness now consumes the same auditable prompt-boundary verdict as gate.
- **Brainstorm sidecar boundary**: brainstorm 读取版本真相、输出独立 markdown，并在需求需要变动时路由回 change/refreeze，而不是直接改写 truth。
- **Support/read model convergence**: `help / status / doctor / archive` 读取同一 delivery read model 与 surface explanation。
- **Provider fallback demotion**: `BEACON_LLM_API_KEY` 仅保留给纯 CLI / provider fallback，不再作为 requirement surface 默认主路径。

## Current v1.3.12 Requirement Closure Line

- `prd / user-story / test-case` now share a unified convergence contract for deepening, supplement, refreeze, and revalidate.
- `brainstorm` stays read-only but can emit gap-aware supplement routing instead of acting as an isolated divergent lane.
- `help / status / board` surface the current gap, supplement target, and re-freeze transaction state.
- `implement / qa / release` still only consume frozen requirement completeness.

## Quick Start

Start with the minimal workflow:

```bash
bash skills/beacon/scripts/run_beacon.sh prd create "My Feature" --project . --version v1.3.9
bash skills/beacon/scripts/run_beacon.sh user-story create "My Feature" --project . --version v1.3.12
bash skills/beacon/scripts/run_beacon.sh test-case create "My Feature" --project . --version v1.3.12
bash skills/beacon/scripts/run_beacon.sh brainstorm run "补齐 PRD 缺口" --project-root . --version auto --mode requirement-convergence --json
bash skills/beacon/scripts/run_beacon.sh implement plan "My Feature" --project . --version v1.3.9 --json
bash skills/beacon/scripts/run_beacon.sh qa run "My Feature" --project . --version v1.3.9 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.9 --project .
```

Ask Beacon what to do next:

```bash
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.9
bash skills/beacon/scripts/run_beacon.sh help --project-root . --version v1.3.9 --feature "My Feature" --json
```

Bootstrap requirement materials safely:

```bash
bash skills/beacon/scripts/run_beacon.sh prd bootstrap "My Feature" --project-root . --version v1.3.9 --dry-run --json
```

Inject Codex fixed HUD context:

```bash
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.3.9"}' \
  | bash skills/beacon/scripts/run_beacon.sh debug codex-fixed-hud --project-root . --version v1.3.9 --json
```

Run final release checks:

```bash
bash skills/beacon/scripts/run_beacon.sh gate check release --project-root . --version v1.3.9 --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.9 --project .
```

Optional analysis surface:

```bash
bash skills/beacon/scripts/run_beacon.sh friction-intake run \
  --project-root . \
  --version v1.3.9 \
  --mode scan \
  --json
```bash
bash skills/beacon/scripts/run_beacon.sh doctor metadata show \
  --project-root . \
  --version v1.3.9 \
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

Read current v1.3.9 materials in this order:

1. [`docs/beacon/v1.3.9/SUMMARY.md`](../../docs/beacon/v1.3.9/SUMMARY.md)
2. [`docs/beacon/v1.3.9/execution/index.md`](../../docs/beacon/v1.3.9/execution/index.md)
3. [`docs/beacon/v1.3.9/execution/architecture-blueprint.md`](../../docs/beacon/v1.3.9/execution/architecture-blueprint.md)
4. [`docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md`](../../docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md)
5. [`docs/beacon/v1.3.9/execution/boundaries.md`](../../docs/beacon/v1.3.9/execution/boundaries.md)
6. [`docs/beacon/v1.3.9/release/v1.3.9.md`](../../docs/beacon/v1.3.9/release/v1.3.9.md)

For host-native runtime architecture detail, then read:

1. [`docs/beacon/v1.3.9/execution/architecture-blueprint.md`](../../docs/beacon/v1.3.9/execution/architecture-blueprint.md)
2. [`docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md`](../../docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md)
3. [`docs/beacon/v1.3.9/release/v1.3.9.md`](../../docs/beacon/v1.3.9/release/v1.3.9.md)

Feature package roots:

- [`docs/beacon/v1.3.9/prd/`](../../docs/beacon/v1.3.9/prd/)
- [`docs/beacon/v1.3.9/user-story/`](../../docs/beacon/v1.3.9/user-story/)
- [`docs/beacon/v1.3.9/qa/test-cases/`](../../docs/beacon/v1.3.9/qa/test-cases/)

## Routing Rules

- If the user asks for requirements, route to `beacon-prd`, `beacon-user-story`, `beacon-test-case`, or `beacon-prd-bootstrap`.
- If the user asks to implement, route to `beacon-implement`.
- If the user asks to verify, inspect coverage, or close evidence, route to `beacon-qa`.
- If the user asks to release, run `beacon-release`.
- If the user is blocked or unsure, run `beacon-help` or `beacon-status` before guessing.
- If context, version, or evidence consistency is broken, route to `beacon-doctor`.
- If the user needs formal historical requirement isolation, route to `beacon-archive`.

## Compatibility Rule

`v1.3.9` demotes external runners, external skill adapters, and legacy bridge behavior to a compatibility plane. They may still exist for advanced projects, but they must not appear as the default onboarding or main workflow path.

## Troubleshooting

- Materials inconsistent: `beacon doctor verify-context --project-root . --strict --json`
- Runtime upgraded: `beacon doctor sync-materials --project-root . --version v1.3.9 --all-features --json`
- Need current next step: `beacon help --project-root . --version v1.3.9 --feature "<feature>" --json`
- Release confusion: `beacon gate check release --project-root . --version v1.3.9 --json`
- Skill drift: `python3 scripts/check_skill_drift.py --project-root . --json`
- QA prompt contract must follow first principles before doing browser-use or test-case backfill.

## Examples

- [Basic workflow example](./examples/basic-workflow.md)
- [Release readiness example](./examples/release-readiness.md)
- [Implementation compatibility example](./examples/implementation-with-omx.md)
- [Toolkit Lighthouse analysis example](./examples/beacon-toolkit-lighthouse-analysis.md)
