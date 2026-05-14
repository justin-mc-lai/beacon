# Beacon Automation Sandbox

This directory holds host-level scheduling assets for Beacon-oriented automation.

Recommended bootstrap path for real projects:

```bash
beacon automation init --project-root .
```

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

- `beacon automation init --project-root .`
  - generate project-local scaffold without manually copying `automation/`
- `automation/jobs/beacon-status-job.sh`
  - safe read-only status pass
- `automation/jobs/beacon-qa-job.sh`
  - queue-aware QA runner
- `automation/jobs/beacon-gated-implement-job.sh`
  - queue-aware gated implement runner

Feedback loop:

- nightly QA should refresh:
  - `.beacon/automation/qa-feedback-ledger.json`
- nightly QA should then update:
  - `automation/beacon-automation-queue.json`
- implement windows may also refresh queue after candidate execution

Codex automation specs live under `automation/codex/`.

macOS launch agents live under `automation/launchd/`.

Reference capability guide:

- `docs/analysis/codex-automations-and-beacon-capability-guide.md`

Support reporting entrypoint:

```bash
beacon automation capabilities --project-root .
beacon automation init --project-root .
beacon automation validate-queue --project-root .
beacon automation summarize-qa --project-root .
beacon automation update-queue --project-root .
```

Contract references:

- queue and wrapper contract:
  - `docs/analysis/codex-automations-and-beacon-capability-guide.md`
