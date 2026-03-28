---
title: Beacon Skill Usage Rules
impact: HIGH
impactDescription: Keeps Beacon aligned with the local standard skill layout while preserving CLI/runtime compatibility.
tags: beacon, skill, workflow, implement, cli
---

# Beacon Skill Usage Rules

## Rule 1: Packaging path vs content role

Beacon now maintains a canonical standard skill package at:

- `skills/beacon/SKILL.md`

This satisfies the `skills/<name>/SKILL.md` convention from `docs/skill-development-standards.md`.

At the same time, Beacon uses:

- root `SKILL.md` as the **main product document**
- `skills/beacon/SKILL.md` as the **supplementary package document**

So the distinction is:

- **package canonical path** = `skills/beacon/`
- **content primary document** = root `SKILL.md`

## Rule 2: Compatibility root skill remains

Beacon still keeps the root-level:

- `SKILL.md`

Reason:

- existing diagnostics/tests/readers already consume root `SKILL.md`
- installed skill copies under `~/.agents`, `~/.codex`, `~/.claude` also use `SKILL.md`

So the model is:

- `skills/beacon/` = canonical standard package
- root `SKILL.md` = main product entry + compatibility mirror

## Rule 3: Main/supplementary docs must share a fixed structure

To avoid drift, both skill docs must keep the same semantic section slots:

1. current release line
2. product positioning
3. target user / anti-fit
4. quick start
5. workflow model
6. current product surfaces
7. why the skill matters
8. recommended reading order
9. common usage modes
10. command / wrapper surface
11. lifecycle navigation rules
12. docs / troubleshooting / examples / references

The packaged document may be shorter or may merge adjacent sections, but it must not invent a separate product structure.

## Rule 4: Script-first trigger is supported

The standard wrapper script is:

- `skills/beacon/scripts/run_beacon.sh`

It delegates to:

```bash
python3 -m beacon.main "$@"
```

## Rule 5: Source of truth is still docs/beacon

Skill packaging does not change Beacon's delivery truth:

- `docs/beacon/<version>/` remains source of truth
- `.beacon/` remains runtime state only

## Rule 6: Implement / skill remain CLI surfaces

The skill package wraps these CLI commands instead of replacing them:

- `beacon skill`
- `beacon implement`
- `beacon workflow`
- `beacon review`
