# Beacon v1.6.7 Overall System Map

## One-line Positioning

Beacon is a CLI kernel that keeps requirement materials, machine artifacts, runtime state, QA evidence, and release governance in one versioned system.

## Core Layering

```text
beacon/main.py
→ beacon/cli_factory.py
→ beacon/commands/*
→ beacon/utils/*
→ beacon/adapters/*
→ docs/beacon/<version> + .machine + .beacon runtime state
```

## Current Source Counts

- command modules: `74`
- utility modules: `173`
- adapter modules: `5`

## Major Code Roots

- `beacon/adapters`
- `beacon/commands`
- `beacon/commands/implement`
- `beacon/utils`

