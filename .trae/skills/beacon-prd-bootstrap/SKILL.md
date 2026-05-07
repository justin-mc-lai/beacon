---
name: beacon-prd-bootstrap
description: Use when the user wants one-click requirement bootstrap (prd + user-story + test-case) with safe defaults (dry-run, strict context verify, no-overwrite).
---

# Beacon PRD Bootstrap

This optional skill reduces requirement startup friction while keeping Beacon safe-by-default.

## Use for

- one-click requirement bootstrap
- creating `prd + user-story + test-case` docs in one run
- low-risk initialization with strict guardrails

## Safety defaults

- strict context verify (`doctor verify-context --strict`)
- dry-run unless explicitly `--apply`
- no-overwrite by default
- lock + state artifact + rollback manifest

## Operator rule

Prefer the installed CLI (hidden command surface):

- `beacon prd-bootstrap run "<feature>" --desc "<需求描述>" --version <version> --dry-run --json`
- `beacon prd-bootstrap run "<feature>" --desc "<需求描述>" --version <version> --apply --allow-overwrite`

Optional repo-local shell wrappers under `skills/beacon/scripts/` remain supported only when that skill pack is vendored into the repo.

Do not treat this as Beacon mainline replacement.
