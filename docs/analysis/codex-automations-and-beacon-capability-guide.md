# Codex Automations and Beacon Capability Guide

## Purpose

This note explains how Codex Automations should be used with Beacon without expanding Beacon core into a scheduler.

The boundary is deliberate:

- Codex Automations is the host scheduler and execution trigger.
- Beacon is the truth-aware workflow kernel and gate surface.
- Host scheduling should stay outside Beacon core commands.

## What Codex Automations Is Good At

Codex Automations is a good fit when you need:

- scheduled read-only status passes
- scheduled QA windows
- scheduled gated implement windows for explicitly queued candidates
- host-level launch control, worktree isolation, and notification fan-out

In practice, the useful pattern is:

1. Codex Automations wakes up on a schedule.
2. A thin host wrapper selects a queued job.
3. The wrapper calls Beacon public CLI only.
4. Beacon decides whether the job is safe, blocked, or allowed.
5. The wrapper publishes artifacts and notifications.

## What Beacon Should Own

Beacon should continue to own:

- requirement truth
- revision and freeze boundaries
- gate decisions
- implementation eligibility
- QA evidence interpretation
- release readiness

Beacon should not own:

- cron / timer runtime
- `launchd` lifecycle
- webhook transport plumbing as a core lifecycle primitive
- opportunistic job picking outside explicit queue governance

## Recommended Integration Pattern

Keep the integration layered:

### 1. Queue

Use a queue file as the canonical automation intent surface.

Example:

- `automation/beacon-automation-queue.json`

That queue should declare:

- `job_id`
- `job_kind`
- `target_agent`
- `enabled`
- `notes`

### 2. Prompt Spec

Use a dedicated Codex automation prompt spec per job family.

Current examples:

- `automation/codex/morning-status.md`
- `automation/codex/nightly-qa.md`
- `automation/codex/gated-implement.md`

These prompt specs should stay host-facing, not become Beacon requirement truth.

### 3. Thin Wrapper

Use a host wrapper that:

- reads the queue
- validates the requested candidate or mode
- calls Beacon public CLI
- writes run artifacts
- emits notifications

Current examples:

- `automation/jobs/beacon-status-job.sh`
- `automation/jobs/beacon-qa-job.sh`
- `automation/jobs/beacon-gated-implement-job.sh`

### 4. Host Scheduler

Use a host scheduler outside Beacon core.

Current local example:

- `automation/launchd/`

This is where schedule frequency, install/uninstall, and host env configuration should live.

## Job Types Beacon Can Support Well

### Morning Status

Safe, read-only.

Recommended Beacon behavior:

- summarize current active feature or queue state
- point to next gate or next operator action
- do not mutate requirement truth

### Nightly QA

Evidence-first, non-release.

Recommended Beacon behavior:

- run queued QA only
- return layered verdicts
- distinguish blocked environment from product failure
- produce repair handoff hints without forcing implementation

### Gated Implement

Most sensitive.

Recommended Beacon behavior:

- run only for explicitly queued candidates
- require freeze/gate readiness
- refuse opportunistic implementation
- never reopen requirement truth automatically

## Capability Matrix

| Capability | Codex Automations | Beacon |
|---|---|---|
| Schedule / timer | Owns | Does not own |
| Workspace / worktree session | Owns | Consumes indirectly |
| Candidate queue trigger | Owns queue execution | Interprets queue intent |
| Requirement truth | Does not own | Owns |
| Gate / freeze / release decisions | Does not own | Owns |
| QA evidence interpretation | Assists with host execution | Owns verdict logic |
| Notification transport | Owns | Optional artifact source only |

## Why This Boundary Matters

If Beacon absorbs scheduler behavior directly, three things drift quickly:

1. truth and host runtime become coupled
2. notification failures start looking like product failures
3. non-Beacon host concerns leak into the public workflow surface

The current external-scheduler model avoids that.

## Current Beacon Assets

Beacon already contains the right level of support material:

- host scheduling sandbox: `automation/`
- Codex automation prompt specs: `automation/codex/`
- host wrappers: `automation/jobs/`
- example launch agents: `automation/launchd/`

That means the next useful step is not a new public lifecycle stage.

The next useful step is:

- better queue governance
- better artifact summaries
- safer candidate selection
- clearer host-runtime documentation

## Recommended Source-of-Truth Rule

For Codex Automations support:

- Beacon core should expose guidance and thin reporting surfaces.
- Beacon docs should explain supported patterns and boundaries.
- Scheduler-specific operational details should live under `automation/`.

This keeps Beacon compatible with:

- Codex Automations
- Claude scheduled wrappers
- Cursor / Windsurf / Trae project-local host loops

without making Beacon itself depend on one scheduler product.
