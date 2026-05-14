# Automation Jobs Runbook (v1.4.6)

## Purpose

This runbook describes the release-facing operator model for Beacon project-local automation/jobs.

It exists to make scheduled QA and gated implement windows maintainable without turning scheduler runtime into Beacon core lifecycle truth.

## Canonical Surfaces

- queue:
  - `automation/beacon-automation-queue.json`
- wrappers:
  - `automation/jobs/beacon-status-job.sh`
  - `automation/jobs/beacon-qa-job.sh`
  - `automation/jobs/beacon-gated-implement-job.sh`
  - `automation/jobs/beacon-notify-feishu-post.py`
- capability guide:
  - `docs/analysis/codex-automations-and-beacon-capability-guide.md`
- feedback ledger:
  - `.beacon/automation/qa-feedback-ledger.json`
- shared summary artifact:
  - `.beacon/automation-runs/<layer>/qa-summary-*.json`

## Core Commands

```bash
beacon automation init --project-root .
beacon automation capabilities --project-root .
beacon automation validate-queue --project-root .
beacon automation summarize-qa --project-root .
beacon automation build-summary --project-root . --job beacon-nightly-qa --layer qa
beacon automation update-queue --project-root .
```

## Bootstrap

For a new or existing project, generate the project-local automation scaffold first:

```bash
beacon automation init --project-root .
beacon automation validate-queue --project-root .
```

Executor-specific bootstrap is also supported:

```bash
beacon automation init --project-root . --executor codex
beacon automation init --project-root . --executor claude
beacon automation init --project-root . --executor cursor
```

This removes the need to manually copy:

- `automation/beacon-automation-queue.json`
- `automation/jobs/`
- `automation/codex/`
- `automation/launchd/`
- `automation/README.md`

Recommended human-facing route for operators:

- `beacon-toolkit-automation`

## Executor Tiers

- `codex`: native Beacon runtime execution + native scheduler option
- `claude`: native Beacon runtime execution + external scheduler
- `cursor`: supported via adapter/scaffold, but not yet a Beacon-native `implement/qa` host runtime
- `windsurf`: assisted only; scaffold/rules plus external scheduler
- `trae`: experimental only; scaffold/rules plus external scheduler

## Operating Model

### Morning status

Use for read-only project triage.

Expected behavior:

- read current project state
- summarize blockers and next route
- do not mutate requirement truth

### Nightly QA

Use for queue-governed scheduled verification.

Expected behavior:

1. execute queued QA candidates
2. persist feature QA status and scorecards
3. write a timestamped QA feedback ledger artifact under `.beacon/automation-runs/qa/`
4. dual-write the same ledger payload into `.beacon/automation/qa-feedback-ledger.json`
5. build a shared automation summary JSON artifact
6. update `automation/beacon-automation-queue.json`
7. optionally emit a Feishu post notification when `AUTOMATION_FEISHU_WEBHOOK` is configured

Expected queue effect:

- passed feature exits QA queue
- repair-needed feature remains visible for follow-up and may enter implement queue

### Gated implement

Use only for explicit queued candidates.

Expected behavior:

- consume queue-governed implement candidates
- preserve gate refusal as refusal
- refresh queue state after execution window

## Launchd Maintenance

Typical maintenance flow:

```bash
launchctl list | rg beacon
launchctl print gui/$(id -u)/com.beacon.nightly-qa.example
launchctl kickstart -k gui/$(id -u)/com.beacon.nightly-qa.example
```

Project-local validation should always precede launchd diagnosis:

```bash
beacon automation init --project-root .
beacon automation validate-queue --project-root .
beacon automation summarize-qa --project-root .
beacon automation update-queue --project-root .
```

Optional notification env:

- `AUTOMATION_FEISHU_WEBHOOK`
- `AUTOMATION_FEISHU_SECRET`

Summary schema notes:

- summary contract is transport-agnostic
- notifier reads `notification.title` and `notification.lines`
- wrappers should not invent per-project summary formats when Beacon summary schema is sufficient

## Real Closure Replay

When a feature looks release-ready from QA but Ralph or release still appears blocked, replay the public Beacon surfaces in this order:

```bash
beacon implement ralph-status "<feature>" --project-root . --json
beacon release check <version> --project-root . --json
beacon deep run "<feature>" --project-root . --version <version> --json
beacon release check <version> --project-root . --json
beacon implement ralph-status "<feature>" --project-root . --json
```

Expected interpretation:

- first `ralph-status` may project a stale release blocker into a more specific current blocker such as `deep_loop_unclosed`
- `deep run` should materialize the missing deep closure artifacts and refresh the release supplement
- second `release check` should be the authoritative release-global verdict
- final `ralph-status` should converge to `stop_state=release_ready` when release truth is fully green

This was the exact closure path for:

- feature: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`
- version: `v1.4.6`
- final release verdict date: `2026-05-14`

## Troubleshooting Rules

### Queue invalid

Symptoms:

- wrapper fails early
- `validate-queue` returns non-zero

Action:

- fix queue contract first
- do not patch wrapper behavior to bypass invalid queue state

### QA passed but queue did not shrink

Action:

1. inspect `.beacon/automation/qa-feedback-ledger.json`
2. compare it with the latest timestamped ledger artifact under `.beacon/automation-runs/qa/`
3. run `beacon automation update-queue --project-root .`
4. confirm the relevant feature has `status=passed`

### QA blocked or stop_for_repair

Action:

- inspect `continue_decision`, `stop_reasons`, `repair_command`
- treat environment blockers as blockers, not product failure
- only admit implement follow-up through explicit queue update

## Boundary Reminder

- Beacon owns truth, QA verdict, and release readiness.
- Host scheduler owns timer lifecycle and notification transport.
- automation/jobs is an operator-facing support plane, not a new lifecycle stage.
