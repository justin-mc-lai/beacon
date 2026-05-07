---
name: beacon-toolkit-metadata
description: Use when the user wants deterministic project/version metadata inspection or CRUD operations through Beacon's metadata toolkit surface, without entering the main delivery workflow.
---

# Beacon Toolkit Metadata

This skill routes metadata work through Beacon's `doctor metadata` support surface.

## Use for

- inspect current resolved metadata view
- list project topology / service binding / version contract state
- create project-level or version-level metadata records
- update existing metadata truth
- delete service bindings or version contracts
- verify runtime state against metadata contract

## Operator rule

Keep metadata operations outside the main workflow by default.

Prefer:

- `beacon doctor metadata show ...`
- `beacon doctor metadata list ...`
- `beacon doctor metadata create ...`
- `beacon doctor metadata update ...`
- `beacon doctor metadata delete ...`
- `beacon doctor metadata verify ...`
- or `beacon doctor metadata ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor metadata ...`)

Default expectations:

- treat `doctor metadata` as the human-facing deterministic metadata toolkit
- keep writes on the canonical metadata transaction path
- let runtime/project validation consume the resolved metadata view
- do not patch only one sink by hand

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the metadata result into the main Beacon workflow.
