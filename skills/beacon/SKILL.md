---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through a standard skill package that delegates to beacon CLI commands and scripts.
metadata:
  author: Beacon CLI
  version: "1.1.8"
  organization: Beacon
  date: March 2026
  abstract: Standard skill package wrapper for Beacon CLI workflow, implement, review, and release operations.
---

# Beacon Skill

## Overview

This is the canonical standard-skill wrapper for Beacon.

It exposes Beacon through a `skills/beacon/` package layout while still delegating real work to:

- `beacon <subcommand>`
- `python3 -m beacon.main <subcommand>`
- `./skills/beacon/scripts/run_beacon.sh`

## When to Use

Use this skill when:

- you need Beacon requirement-material generation
- you need workflow / implement / review / gate / release execution
- you need stage-aware help about current lifecycle status, blockers, or next steps
- you need to freeze the current revision before implementation or reopen a superseded revision
- you need a standard `skills/<name>/` package instead of only a root-level `SKILL.md`
- you want a script-based entrypoint for Beacon from skill runtimes

## How to Use

1. Read the current version package under [`../../docs/beacon/v1.1.8/`](../../docs/beacon/v1.1.8/SUMMARY.md)
2. Use the command docs hub when you need the right level of operator guidance:

- [Summary](../../docs/beacon/v1.1.8/SUMMARY.md)
- [Execution index](../../docs/beacon/v1.1.8/execution/index.md)
- [Release note](../../docs/beacon/v1.1.8/release/v1.1.8.md)
- [Architecture blueprint](../../docs/beacon/v1.1.8/execution/architecture-blueprint.md)
- [Project lifecycle onboarding](../../docs/beacon/v1.1.8/execution/project-lifecycle-onboarding.md)
3. Use the wrapper script:

```bash
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh workflow --help
bash skills/beacon/scripts/run_beacon.sh help --project-root . --json
bash skills/beacon/scripts/run_beacon.sh freeze "My Feature" --project-root . --version v1.1.8
bash skills/beacon/scripts/run_beacon.sh reopen "My Feature" --project-root . --version v1.1.8 --reason change-request
```

4. For implementation adapters and lifecycle navigation:

```bash
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
bash skills/beacon/scripts/run_beacon.sh help --project-root . --feature "My Feature" --json
bash skills/beacon/scripts/run_beacon.sh doctor repair-package --version v1.1.8 --json
```


## Lifecycle Navigation Rules

When the user asks "what should I do next", "why am I blocked", or wants to continue a feature without knowing the correct stage:

1. Run `beacon status --board --project-root <root> --version <version>` when you need the raw board.
2. Run `beacon help --project-root <root> --version <version> --feature <feature> --json` for the canonical next-step recommendation.
3. If help indicates the revision is not frozen, run `beacon freeze ...` before implementation.
4. If help/doctor indicates the current revision is superseded or a change request is pending, run `beacon reopen ...`.
5. If blocked or inconsistent, run `beacon doctor --project-root <root> --json` or `beacon doctor advise ...`.
6. If the project has a profile / project-specific skill path, prefer `beacon verify run ... --profile <profile>` before trying to accept.
7. Only then route into `freeze`, `implement`, `review`, `verify`, `orchestrate`, or `release` actions.

Example: `beacon help --project-root . --json`

Never guess the next action when Beacon can compute it.

## Examples

See:

- [Basic workflow example](./examples/basic-workflow.md)
- [Release readiness example](./examples/release-readiness.md)
- [Implementation with OMX example](./examples/implementation-with-omx.md)

## References

- [Sections index](./references/_sections.md)
- [Usage rules](./references/usage-rules.md)
- [Summary](../../docs/beacon/v1.1.8/SUMMARY.md)
- [Execution index](../../docs/beacon/v1.1.8/execution/index.md)
- [Skill development standard](../../../docs/skill-development-standards.md)
- [Root compatibility skill](../../SKILL.md)
