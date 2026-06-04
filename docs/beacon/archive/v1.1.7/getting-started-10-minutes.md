# Beacon v1.1.7 Getting Started in 10 Minutes

> A beginner-friendly quickstart for external users.

Goal: in about 10 minutes, you will understand the main Beacon flow and run the most important commands safely.

---

## What you will do

By the end of this quickstart, you will have:

- confirmed the Beacon version
- generated a plan from natural language
- started a workflow
- generated core requirement artifacts
- checked package health
- run release-readiness commands

---

## Prerequisites

- Python 3.9+
- Beacon installed
- a project directory you can run commands in

Install Beacon if needed:

```bash
pip install beacon
```

Or editable mode:

```bash
pip install -e ".[dev]"
```

---

## Minute 1: Confirm the CLI works

```bash
beacon --version
```

Expected outcome:

- You see a Beacon CLI version string
- You know the binary is available on your PATH

---

## Minute 2: Check the current project status

Run:

```bash
beacon status --board --project-root . --version v1.1.7
```

What this gives you:

- source-of-truth root
- machine root
- coverage snapshot
- next workflow stage, if any

If the project is not initialized yet, that is fine — you can still continue.

---

## Minute 3: Start from natural language

Run:

```bash
beacon ask "Create a release-ready requirement package for Beacon v1.1.7 layered delivery" \
  --project-root . \
  --version v1.1.7 \
  --plan-only --json
```

Why this command first:

- it is the safest entrypoint
- it helps you see Beacon’s recommended path before execution
- it avoids guessing the wrong subcommand

---

## Minute 4: Start a workflow

Run:

```bash
beacon workflow start "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7
```

What this does:

- creates or resumes workflow state
- prepares Beacon to track the feature as a formal delivery path

---

## Minutes 5–6: Generate the core requirement artifacts

Run:

```bash
beacon think start "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon user-story create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon prd create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon test-case create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
```

What you should expect to appear under `docs/beacon/archive/v1.1.7/`:

- `user-story/`
- `prd/`
- `qa/test-cases/`

And, for machine-facing artifacts:

- `.machine/qa/`

---

## Minute 7: Inspect health and package closure

Run:

```bash
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon doctor verify-delivery --project-root . --version v1.1.7 --json
```

How to read the result:

- `verify-materials` checks the formal docs package
- `verify-delivery` checks execution-layer delivery artifacts

If the package is older and not yet layered:

```bash
beacon doctor repair-package --project-root . --version v1.1.7 --json
```

Then re-run the two verification commands.

---

## Minute 8: Check release readiness

Run:

```bash
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

Why both commands matter:

- `gate check release` is the policy/gate view
- `release check` is the release package readiness view

Together they tell you whether the package is truly ready.

---

## Minute 9: Optional — inspect implementation adapters

If you want to continue into execution:

```bash
beacon skill list --json
beacon implement list-runners --json
```

If your project uses OMX:

```bash
beacon implement run "Beacon v1.1.7 layered delivery" \
  --runner omx \
  --project . \
  --version v1.1.7 \
  --json
```

---

## Minute 10: Know where to go next

Read next depending on your need:

- Want the README-style overview:
  - `execution/command-guide-readme.md`
- Want a task-oriented lookup:
  - `execution/scenario-quick-reference.md`
- Want the full command tree:
  - `execution/command-reference.md`
- Want a bilingual guide:
  - `execution/command-reference-bilingual.md`

---

## 10-minute recap

If you only keep one safe sequence, keep this one:

```bash
beacon ask "<goal>" --project-root . --version v1.1.7 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.1.7
beacon think start "<feature>" --project . --version v1.1.7
beacon user-story create "<feature>" --project . --version v1.1.7
beacon prd create "<feature>" --project . --version v1.1.7
beacon test-case create "<feature>" --project . --version v1.1.7
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon doctor verify-delivery --project-root . --version v1.1.7 --json
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

## v1.1.7 Lifecycle Closure Add-on

```bash
beacon help --project-root . --version v1.1.7 --feature "Beacon v1.1.7 lifecycle closure" --json
beacon freeze "Beacon v1.1.7 lifecycle closure" --project-root . --version v1.1.7
beacon implement run "Beacon v1.1.7 lifecycle closure" --project . --version v1.1.7 --runner native-team --json
beacon doctor advise --project-root . --version v1.1.7 --feature "Beacon v1.1.7 lifecycle closure" --json
beacon reopen "Beacon v1.1.7 lifecycle closure" --project . --version v1.1.7 --reason change-request
```
