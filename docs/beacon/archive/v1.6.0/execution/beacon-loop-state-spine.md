# Beacon Loop State Spine

Operator-facing progress ledger for `beacon-loop goal` (default delegates to `beacon-run`).

## Purpose

Loop runs produce several on-disk artifacts. This document defines which files are **authoritative** for progress, how **done / in_progress / next_action** are interpreted, and how to query them without manually stitching four state sources.

## Authoritative artifacts

| Artifact | Role | Typical path |
|----------|------|--------------|
| `beacon-phase.json` | **Primary spine** for delegated `beacon-run` runs: current lifecycle phase, completed phases, promotion visibility | `.gnhf/runs/<run-id>/beacon-phase.json` (under repo or worktree cwd) |
| `truth-promotion.json` | Harness checkpoint ledger (`--project-root`, exit codes, demote/repair) | same run dir |
| `run-package.json` | Legacy loop package + goal/feature/version | `.beacon/loop/runs/<id>/run-package.json` |
| `run-state.json` | Legacy loop machine state (iterations, caps) | `.beacon/loop/runs/<id>/run-state.json` |
| SQLite ledger | Cross-run index (optional) | `.beacon/loop/ledger.sqlite` |

**Rule:** Requirement truth remains in `features/<slug>/truth.md`. Spine files are **runtime/generated state**, not requirement authority.

## Progress semantics

| Field | Meaning |
|-------|---------|
| `phase` | Current Beacon lifecycle phase (`truth`, `generate`, `qa`, `release`, `repair`) or legacy machine state |
| `phases_completed` | Phases that passed exit harness and were promoted |
| `phase_promoted` | `false` when last harness failed — operator must inspect `last_harness_exit` in `beacon-phase.json` |
| `next_harness` | Human hint for the next subprocess gate |
| `next_action` | Machine-oriented operator step (`phase:truth`, `resolve_harness_blocker`, etc.) |
| `progress_status` | `done` \| `in_progress` \| `unknown` |

## CLI query

```bash
beacon-loop spine show [--run-id <id>] [--project <root>] [--json]
```

JSON output includes: `phase`, `phases_completed`, `phase_promoted`, `next_harness`, `next_action`, `authoritative_paths[]`, `run_id`.

Equivalent: `beacon-loop status --spine` (same payload).

## Worktree note

When `--worktree` is active, harness `project-root` and agent cwd resolve to the **worktree checkout**. Spine discovery scans both the main repo and `<repo>-gnhf-worktrees/*/.gnhf/runs/`.

## Related ACs

- AC-070: this document + `spine show`
- AC-061 / AC-069: worktree harness root alignment
- AC-071: `--stop-when` requires external verification (`--stop-check-cmd` or phase harness); agent self-report alone is not sufficient
