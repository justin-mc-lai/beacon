# Beacon Automation Sandbox

This directory holds host-level scheduling assets for Beacon-oriented automation.

Principles:

- Beacon remains the truth-aware execution surface.
- Scheduling stays outside Beacon core commands.
- Queue governance is explicit.
- `implement` jobs must never run without an explicit candidate queue and gate checks.

Current contents:

- `beacon-automation-queue.json`
  - canonical queue for scheduled jobs
- `jobs/`
  - thin wrappers that call Beacon public CLI only
- `codex/`
  - Codex automation prompt specs
- `launchd/`
  - local macOS launch agents

Quick start:

- `automation/jobs/beacon-status-job.sh`
  - safe read-only status pass
- `automation/jobs/beacon-qa-job.sh`
  - queue-aware QA runner
- `automation/jobs/beacon-gated-implement-job.sh`
  - queue-aware gated implement runner

Codex automation specs live under `automation/codex/`.

macOS launch agents live under `automation/launchd/`.

Reference capability guide:

- `docs/analysis/codex-automations-and-beacon-capability-guide.md`

Support reporting entrypoint:

```bash
beacon automation capabilities --project-root .
```
