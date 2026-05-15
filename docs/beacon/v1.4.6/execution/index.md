# Execution Index (v1.4.6)

## Human Primary Surface

- `boundaries.md`
- `human-skill-reference.md`
- Markdown execution notes and release-facing guidance
- `automation-jobs-runbook.md`

## Machine Secondary Surface

- `docs/beacon/v1.4.6/.machine/execution/`

## Notes

- `execution/` stays Markdown-first for humans.
- `.beacon/` remains runtime internal state only.

## Automation Jobs

- Beacon automation/jobs now includes a queue-governed feedback loop for project-local scheduled QA and gated implement.
- Capability guide: `docs/analysis/codex-automations-and-beacon-capability-guide.md`
- Scheduler assets: `automation/README.md`
- Scaffold bootstrap: `beacon automation init --project-root .`
- Executor tiering: `codex|claude` native, `cursor` adapter-capable, `windsurf|trae` scaffold-tier only
- Queue validation: `beacon automation validate-queue --project-root .`
- QA feedback ledger: `beacon automation summarize-qa --project-root .`
- Shared summary schema: `beacon automation build-summary --project-root . --job <job> --layer <layer>`
- Queue update surface: `beacon automation update-queue --project-root .`
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
