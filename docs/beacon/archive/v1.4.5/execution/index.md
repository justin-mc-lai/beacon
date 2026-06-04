# Execution Index (v1.4.5)

## Human Primary Surface

- `boundaries.md`
- Markdown execution notes and release-facing guidance

## Machine Secondary Surface

- `docs/beacon/archive/v1.4.5/.machine/execution/`

## Notes

- `execution/` stays Markdown-first for humans.
- `.beacon/` remains runtime internal state only.

## Host-Scheduled Automation

- Codex Automations is supported as a host-scheduled capability plane, not a Beacon primary lifecycle stage.
- Capability guide: `docs/analysis/codex-automations-and-beacon-capability-guide.md`
- Scheduler assets: `automation/README.md`
- CLI reporting surface: `beacon automation capabilities --project-root .`
- Queue validation surface: `beacon automation validate-queue --project-root .`
