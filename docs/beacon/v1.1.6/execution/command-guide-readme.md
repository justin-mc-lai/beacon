# Beacon v1.1.6 Command Guide

> External-user README-style guide for the Beacon v1.1.6 CLI.

Beacon is an evidence-first product workflow CLI.  
It helps teams move from idea to release with auditable artifacts:

- requirement clarification
- user stories
- PRDs
- test cases
- implementation handoff
- verification
- gates
- release checks

---

## What Beacon is good at

Beacon is best when you need a structured workflow like:

```text
idea → clarify → spec → test → implement → verify → release
```

The v1.1.6 release adds a clearer human/machine delivery split:

- humans primarily read Markdown docs
- machines primarily read `.machine/`
- runtime state stays in `.beacon/`

---

## Installation

```bash
pip install beacon
```

Or in editable mode:

```bash
pip install -e ".[dev]"
```

Check the version:

```bash
beacon --version
```

---

## The 5 commands most users need first

### 1. Plan from natural language

```bash
beacon ask "Create a release-ready requirement package for Beacon v1.1.6" \
  --project-root . \
  --version v1.1.6 \
  --plan-only --json
```

### 2. Start a full workflow

```bash
beacon workflow start "Beacon v1.1.6 layered delivery" \
  --project . \
  --version v1.1.6
```

### 3. Generate the main requirement docs

```bash
beacon think start "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon user-story create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon prd create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon test-case create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
```

### 4. Verify package health

```bash
beacon doctor verify-materials --project-root . --version v1.1.6 --json
beacon doctor verify-delivery --project-root . --version v1.1.6 --json
```

### 5. Check release readiness

```bash
beacon gate check release --project-root . --version v1.1.6 --json
beacon release check v1.1.6 --project .
```

---

## Recommended mental model

Use Beacon in 4 layers:

### Layer 1: Start from intent

- `beacon ask`
- `beacon workflow start`

### Layer 2: Generate formal requirement artifacts

- `beacon think`
- `beacon user-story`
- `beacon prd`
- `beacon prototype`
- `beacon test-case`

### Layer 3: Execute and review

- `beacon skill`
- `beacon implement`
- `beacon review`
- `beacon auto-test`

### Layer 4: Govern and release

- `beacon doctor`
- `beacon status`
- `beacon report`
- `beacon gate`
- `beacon release`

---

## Typical usage scenarios

### Scenario A — “I only know the goal”

```bash
beacon ask "<goal>" --project-root . --version v1.1.6 --plan-only --json
```

### Scenario B — “I want the full package”

```bash
beacon workflow start "<feature>" --project . --version v1.1.6
```

### Scenario C — “I need implementation through OMX”

```bash
beacon skill list --json
beacon implement list-runners --json
beacon implement run "<feature>" --runner omx --project . --version v1.1.6 --json
```

### Scenario D — “I need to migrate old package structure”

```bash
beacon doctor repair-package --project-root . --version v1.1.6 --json
```

### Scenario E — “I need release evidence”

```bash
beacon status --board --project-root . --version v1.1.6
beacon doctor verify-materials --project-root . --version v1.1.6 --json
beacon doctor verify-delivery --project-root . --version v1.1.6 --json
beacon gate check release --project-root . --version v1.1.6 --json
beacon release check v1.1.6 --project .
```

---

## Command groups at a glance

| Group | Main commands | What they do |
| --- | --- | --- |
| Planning | `ask`, `think`, `user-story`, `prd` | Clarify and structure requirements |
| Prototyping | `prototype`, `ui-spec`, `wireframe` | Create UI-facing artifacts |
| Testing | `test-case`, `auto-test`, `test-progress` | Define and track test evidence |
| Implementation | `skill`, `implement`, `review` | Execute implementation via adapters |
| Governance | `doctor`, `status`, `report`, `gate`, `release` | Audit package quality and release readiness |
| Memory | `feedback`, `remember`, `recall`, `resume` | Close the loop between runs and knowledge |

---

## Where to read next

If you want the detailed operator docs:

- `command-reference.md` — full command tree and explanations
- `scenario-quick-reference.md` — task-oriented quick lookup
- `command-reference-bilingual.md` — bilingual command guide

If you want the release materials:

- `../SUMMARY.md`
- `../release/v1.1.6.md`

If you want the machine-readable side:

- `../.machine/execution/`
- `../.machine/qa/`

## Lifecycle-native closure commands

```bash
beacon help --project-root . --version v1.1.6 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.6
beacon implement run "<feature>" --project . --version v1.1.6 --runner native-team --json
beacon doctor advise --project-root . --version v1.1.6 --feature "<feature>" --json
beacon reopen "<feature>" --project . --version v1.1.6 --reason change-request
```
