---
name: beacon
description: >
  Beacon package router (Scheme A 1+6). Host-visible public cores only:
  beacon-goal, beacon-plan, beacon-truth, beacon-design, beacon-implement,
  beacon-qa, beacon-release. Prefer $beacon-goal for long-run delivery.
metadata:
  author: Beacon CLI
  version: "v1.6.10"
  organization: Beacon
  scheme: "A-1plus6"
  date: July 2026
  abstract: Scheme A public surface — goal transversal + six harness cores. Internal gov packages use SUPPORT.md and are not host-discoverable.
---

# Beacon Skill Package

Canonical package root: `skills/beacon/`.

## Scheme A host-visible surface (only)

| Public id | Skill dir | Role |
|-----------|-----------|------|
| goal | `beacon-goal` | Long-run facade (not counted in the six) |
| plan | `beacon-plan` | Planner |
| truth | `beacon-truth` | Freeze / change / refreeze |
| design | `beacon-design` | UX / design routes |
| implement | `beacon-implement` | Implementation |
| qa | `beacon-qa` | Evidence / QA |
| release | `beacon-release` | Release gate |

Default pipeline:

```text
plan -> truth -> design? -> implement -> qa -> release
```

Daily entry:

```text
$beacon-goal
```

or CLI: `beacon goal run "<goal>" --project . --version <v>`

## Host discovery rules (anti-leak)

- **Host-discoverable** packages carry a top-level `SKILL.md`.
- **Internal support** packages (former `beacon-gov-*`) carry `SUPPORT.md` only — not host-visible.
- Archived pre-1+6 fine-grained skills live under `skills/_archive/` with `SKILL.md.archived` (not discoverable).
- Default install whitelist: goal + six harness cores. `BEACON_INSTALL_ALL=1` / `INSTALL_ALL=1` is advanced opt-in only.
- Project Cursor surface: `.cursor/skills/` via `beacon doctor setup-agent-surface --agent cursor`.
- Never install package root `~/.cursor/skills/beacon` → `skills/beacon` (recursive discovery leak).

## Progressive / internal

Fine-grained capability loads as modes under each public core:

```text
skills/beacon/beacon-<surface>/references/modes/
```

Map: `skills/beacon/references/public-surface-progressive-map.v1.json`

Internal denylist remains non-public: doctor, router, hooks, metadata, debug, archive, status, gov, library, lighthouse.

## Verify

```bash
beacon doctor verify-agent-surface --project-root . --agent cursor --strict
beacon skill package verify --project-root . --version v1.6.10 --package-root skills/beacon --json
```

## Boundaries

- Support surfaces explain/route/diagnose; they do not replace truth, implement, QA, or release.
- No placeholder implementation, docs-only completion, or zero-assertion evidence as delivery.
- Truth authority: `docs/beacon/global-boundaries.md` + `docs/beacon/<version>/`.
