# User Story: Compatibility Registry and Command Catalog Contract

**Feature**: `compatibility-registry-and-command-catalog-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Story

As a Beacon maintainer reducing legacy burden, I want every known compatibility, fallback, deprecated, legacy, and historical surface to be registered and every command catalog entry to have an explicit layer, so that later cleanup can be audited without breaking current users, old scripts, QA, release, projection, evidence, memory, intent, or project hooks.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | registry schema | Beacon defines a compatibility registry schema with required fields for each compat, fallback, legacy, deprecated, or historical surface. |
| AC-002 | inventory coverage | The registry covers all required compatibility-governance surfaces from the v1.4.11 baseline inventory. |
| AC-003 | lifecycle metadata | Each registry entry records owner, surface category, reason, current replacement, default behavior, allowed version range, retirement route, and required evidence. |
| AC-004 | command layering | Command catalog entries are classified into current, support, advanced, labs, compat, deprecated, or internal layers. |
| AC-005 | behavior preserved | Existing compat and deprecated command behavior remains available during this slice. |
| AC-006 | route discipline | Default help, status, or next-route output does not promote compat or deprecated commands as normal current mainline routes. |
| AC-007 | validation fail-closed | Unregistered compatibility, fallback, deprecated, or legacy surfaces fail registry or catalog validation. |
| AC-008 | no hidden retirement | Tests prove QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent routing behavior are not changed by this slice. |

## Non Goals

- This story does not remove old commands.
- This story does not change QA legacy mirror behavior.
- This story does not change PRD legacy mirror behavior.
- This story does not migrate implement loader behavior.
- This story does not split prototype legacy inspector behavior.
- This story does not rename browser fallback runtime behavior.
- This story does not change memory or intent runtime behavior.
- This story does not create a new human lifecycle stage.
- This story does not produce QA or release verdicts.

## Boundary

This story is a registration and validation prerequisite.

It makes compatibility paths explicit before later v1.4.11 features change defaults, require explicit admission, or retire behavior.
