---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through a standard skill package that delegates to beacon CLI commands and scripts.
metadata:
  author: Beacon CLI
  version: "1.1.5"
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
- you need a standard `skills/<name>/` package instead of only a root-level `SKILL.md`
- you want a script-based entrypoint for Beacon from skill runtimes

## How to Use

1. Read the current version package under [`../../docs/beacon/v1.1.5/`](../../docs/beacon/v1.1.5/SUMMARY.md)
2. Use the wrapper script:

```bash
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh workflow --help
```

3. For implementation adapters:

```bash
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json
bash skills/beacon/scripts/run_beacon.sh doctor repair-package --version v1.1.5 --json
```

## Examples

See:

- [Basic workflow example](./examples/basic-workflow.md)

## References

- [Sections index](./references/_sections.md)
- [Usage rules](./references/usage-rules.md)
- [Skill development standard](../../../docs/skill-development-standards.md)
- [Root compatibility skill](../../SKILL.md)
