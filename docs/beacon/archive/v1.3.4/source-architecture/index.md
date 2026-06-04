# Beacon v1.3.4 Source Architecture Index

This source-architecture index records the code surfaces reshaped by the `v1.3.4` runtime projection and doctor-alignment line.

## Command surfaces

- `beacon/commands/doctor.py` — doctor orchestration entrypoint, split docs/runtime context setup, runtime ledger surfaces
- `beacon/commands/status.py` — lifecycle/status surface with runtime projection summary support
- `beacon/commands/release.py` — release-line change document and release check enforcement

## Core runtime-projection modules

- `beacon/utils/runtime_projection.py` — project truth scan and normalized runtime envelope assembly
- `beacon/utils/runtime_projection_store.py` — sqlite-backed projection persistence and export helpers
- `beacon/utils/control_plane.py` — PocketBase presence, mirror-pack, and control-plane diagnostics

## Context and version alignment

- `beacon/utils/context_files.py` — managed block write/read, including split `BEACON:VERSION` and `BEACON:DOCS_VERSION`
- `beacon/utils/versioning.py` — docs/runtime resolution, partial supplement lines, and feature gating

## Doctor orchestration split

- `beacon/utils/doctor_orchestrator.py` — composed doctor actions instead of flat command-file logic
- `beacon/utils/doctor_registry.py` — doctor responsibility registry and extensibility seam
- `beacon/utils/material_audit.py` — formal package completeness and delivery audit

## Supporting governance modules

- `beacon/utils/release_scorecard.py` — release closure aggregation and version change document status
- `beacon/utils/worktree_quiet.py` — git noise governance for Beacon-managed machine files

## Boundary note

The `v1.3.4` source line adds machine-local project observation and control-plane helpers, but it deliberately stops short of moving formal requirement ownership out of docs and local Beacon evidence.
