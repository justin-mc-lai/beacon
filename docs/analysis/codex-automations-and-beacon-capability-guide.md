# Codex Automations and Beacon Capability Guide

## Purpose

This note explains how host-scheduled automation should be used with Beacon without expanding Beacon core into a scheduler.

The boundary is deliberate:

- Codex Automations is one host scheduler and execution trigger.
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

Current examples may be executor-specific:

- `automation/codex/*.md`
- `automation/generic/*.md`

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

Recommended bootstrap entrypoint for real projects:

- `beacon automation init --project-root .`

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

## Queue Contract

The canonical automation intent surface is:

- `automation/beacon-automation-queue.json`

Current queue model is intentionally small:

- `version`
- `project_root`
- `default_workspace_mode`
- `jobs[]`

Each job must declare:

- `job_id`
- `job_kind`
- `target_agent`
- `enabled`
- `feature_selector`
- `preconditions`
- `workspace_mode`
- `risk_level`
- `on_blocked`
- `on_success`
- `notes`

Current allowed values:

- `job_kind`: `status`, `qa`, `implement`
- `target_agent`: `codex`, `claude`, `cursor`, `windsurf`, `trae`
- `workspace_mode`: `worktree`, `local`
- `feature_selector.mode`: `all_active`, `explicit_list`

Boundary rules:

- `status` jobs may use `all_active`
- `qa` and `implement` should use explicit candidate lists
- `implement` jobs must be high risk and must hand off into QA on success
- queue selection belongs to the host plane; execution eligibility belongs to Beacon

Validation and bootstrap entrypoints:

```bash
beacon automation init --project-root .
beacon automation validate-queue --project-root .
beacon automation validate-queue --project-root . --json
```

## Executor Capability Tiers

Beacon should not claim that every agent host has the same native execution plane.

Frozen tier model for `v1.4.6`:

- `codex`
  - tier: `native`
  - Beacon `implement/qa` runtime: supported
- `claude`
  - tier: `native`
  - Beacon `implement/qa` runtime: supported
- `cursor`
  - tier: `supported-via-adapter`
  - official CLI/API exists, but Beacon `implement/qa` host runtime is not yet cursor-native
- `windsurf`
  - tier: `assisted`
  - project-local skills/workflows plus external scheduler only
- `trae`
  - tier: `experimental`
  - scaffold/rules guidance only until stronger public execution surface is proven

## Wrapper Contract

Wrappers under `automation/jobs/` are deliberately thin. They should:

1. read queue intent
2. select only enabled matching jobs
3. call Beacon public CLI only
4. write timestamped run artifacts
5. exit non-zero on malformed queue or unsupported local execution shape

Wrappers should not:

- rewrite queue state during execution
- bypass Beacon gate or truth checks
- publish release readiness by themselves
- treat notification delivery as Beacon truth

Current wrapper expectations:

- `beacon-status-job.sh`
  - read-only status pass
  - single artifact output
- `beacon-qa-job.sh`
  - explicit feature iteration
  - one artifact per feature
- `beacon-gated-implement-job.sh`
  - explicit candidate iteration only
  - never opportunistic selection
  - must preserve gate refusal as refusal

## QA Feedback Loop

For scheduled Beacon QA to become a durable project workflow, one run must leave machine-readable state that the next run can consume.

The minimum loop is:

1. run queued QA
2. write feature QA status and scorecards
3. summarize those results into an automation feedback ledger
4. update the automation queue from that ledger
5. let the next scheduler window consume the updated queue

Current Beacon entrypoints:

```bash
beacon automation summarize-qa --project-root .
beacon automation update-queue --project-root .
```

Current ledger path:

- `.beacon/automation/qa-feedback-ledger.json`

Current queue update semantics:

- remove passed features from QA queue
- add repair-needed features into gated implement queue
- preserve explicit queue governance; never let QA invent opportunistic new work beyond the formal queue update rule

This is enough for:

- nightly QA -> next nightly QA reuse
- nightly QA -> next gated implement handoff
- environment blocker vs product failure separation in later runs

## Why This Matters For Other Agents

The queue and wrapper contract is intentionally host-neutral.

That means the same Beacon automation plane can be used by:

- Codex Automations
- Claude scheduled shell wrappers
- Cursor project tasks
- Windsurf task runners
- Trae local scheduler hooks

The only thing that should vary by agent is:

- trigger runtime
- notification transport
- worktree/session setup

The Beacon truth boundary should not vary by agent.
