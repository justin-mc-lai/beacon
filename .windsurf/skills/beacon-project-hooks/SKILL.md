---
name: beacon-project-hooks
description: Use when the user wants to inspect, plan, dry-run, manually run, disable, or explain project-level Beacon lifecycle hooks under docs/beacon/hooks.
---

# Beacon Project Hooks

## Overview

This skill routes project-specific lifecycle hook work through Beacon's governed `hooks` toolkit.

Project hooks are project-level extensions opened at finite Beacon lifecycle boundaries. They are not lifecycle stages, not requirement truth, and not QA or release verdicts.

## When to Use

- inspect project hook contracts
- plan a hook before a lifecycle boundary
- dry-run a hook without side effects
- manually confirm a side-effect hook
- disable a hook contract
- inspect latest hook evidence or blocker status

## Boundary

- hook truth lives only in `docs/beacon/hooks/<hook-id>.md`
- do not create canonical hook truth under `docs/beacon/<version>/hooks/`
- do not run arbitrary shell hooks
- do not allow hidden auto-run for side-effect hooks
- do not rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict

## Command

List hooks:

```bash
beacon hooks list --project .
```

Plan a hook:

```bash
beacon hooks plan "<hook-id>" --project . --version <version> --feature "<feature>"
```

Dry-run a hook:

```bash
beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --dry-run
```

Manually confirm a hook:

```bash
beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --confirm
```

Disable a hook:

```bash
beacon hooks disable "<hook-id>" --project .
```

Inspect status:

```bash
beacon hooks status "<hook-id>" --project . --feature "<feature>"
```

## Write Topology

- project hook truth: `docs/beacon/hooks/<hook-id>.md`
- runtime evidence: `.beacon/state/hooks/<hook-id>/<run-id>.json`
- latest read model: `docs/beacon/.machine/hooks/<hook-id>.latest.json`

The runtime evidence and latest read model are evidence only.

## Allowed Hook Codes

- `post_implement_pre_qa`
- `qa_diagnostics`
- `post_qa_pre_release`
- `post_release`

## Common Rationalizations

- “hook 成功了，所以 QA 通过。” -> 不允许；正式 QA 仍归 `beacon qa`。
- “release 后项目总是要安装，所以自动后台跑。” -> 不允许；高副作用 hook 必须手动确认。
- “这个 hook 只在 v1.4.10 用，所以放进 version 目录。” -> 不允许；hook contract 是项目级 truth。

## Verification

- `beacon hooks list` reads `docs/beacon/hooks`
- `beacon hooks plan` fails closed on invalid hook code or missing evidence declaration
- `beacon hooks run --dry-run` writes evidence without side effects
- `beacon hooks run --confirm` is required for side-effect hooks
- `beacon hooks status` never reports requirement, QA, release, gate, or freeze authority

## Cold-start Anchors

- Project hooks are governed project extensions, not lifecycle stages.
- Hook execution evidence is not requirement truth.
- Side-effect hooks require explicit operator confirmation.
