---
title: Beacon Skill Usage Rules
impact: HIGH
impactDescription: Keeps Beacon aligned with the local standard skill layout while preserving CLI/runtime compatibility.
tags: beacon, skill, workflow, implement, cli
---

# Beacon Skill Usage Rules

## Rule 1: Canonical standard skill path

Beacon now maintains a canonical standard skill package at:

- `skills/beacon/SKILL.md`

This satisfies the `skills/<name>/SKILL.md` convention from `docs/skill-development-standards.md`.

## Rule 2: Compatibility root skill remains

Beacon still keeps the root-level:

- `SKILL.md`

Reason:

- existing diagnostics/tests/readers already consume root `SKILL.md`
- installed skill copies under `~/.agents`, `~/.codex`, `~/.claude` also use `SKILL.md`

So the model is:

- `skills/beacon/` = canonical standard package
- root `SKILL.md` = compatibility + installed-skill mirror entry

## Rule 3: Script-first trigger is supported

The standard wrapper script is:

- `skills/beacon/scripts/run_beacon.sh`

It delegates to:

```bash
python3 -m beacon.main "$@"
```

## Rule 4: Source of truth is still docs/beacon

Skill packaging does not change Beacon's delivery truth:

- `docs/beacon/<version>/` remains source of truth
- `.beacon/` remains runtime state only

## Rule 5: Implement / skill remain CLI surfaces

The skill package wraps these CLI commands instead of replacing them:

- `beacon skill`
- `beacon implement`
- `beacon workflow`
- `beacon review`
