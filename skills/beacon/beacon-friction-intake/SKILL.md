---
name: beacon-friction-intake
description: Use when the user wants Beacon to scan project friction or capture a manual friction note, then persist it into the global sqlite governance queue without entering the main 6+3 workflow surface.
---

# Beacon Friction Intake

This skill routes optional friction governance work through Beacon's `friction-intake` support surface.
It is the primary `scan/capture` entry for Beacon friction governance.

## Use for

- scan Beacon source project friction, blockers, and bugs
- capture a manual friction note inside a target project
- classify friction into governance-ready queue items
- persist dual-write evidence into project-local artifacts and global sqlite
- decide whether a friction item should stay queue-only or be explicitly accepted for requirement/change

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon friction-intake run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh friction-intake run ...`

Default expectations:

- `scan` mode is for Beacon source-project friction discovery
- `capture` mode is for manual friction logging in a target project
- both modes write queue items into the global runtime-ledger sqlite
- project-local truth stays in `.beacon/debug/`, `.beacon/memory/`, `.beacon/analysis/`
- requirement/change routing stays explicit and opt-in

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly accepts the item for requirement/change routing.

## Recommended command shapes

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.0 \
  --mode scan \
  --json
```

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.0 \
  --mode capture \
  --note "QA run is blocked because acceptance dual-write did not materialize" \
  --json
```
