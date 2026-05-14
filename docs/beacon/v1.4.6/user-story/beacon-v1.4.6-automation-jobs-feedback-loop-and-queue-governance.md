# User Story: Beacon v1.4.6 automation jobs feedback loop and queue governance

**Feature**: `beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance`  
**Version**: `v1.4.6`  
**Revision**: `R1`  
**Status**: `frozen`

## Story

**As a** Beacon operator running project-local scheduled QA and gated implement windows,  
**I want** Beacon automation/jobs to persist a machine-readable QA feedback ledger, update the project queue by explicit rules, generate a project-local automation scaffold on demand, expose executor capability tiers honestly, and emit one shared automation summary schema for wrappers and notifications,  
**So that** one QA run can feed the next QA or gated implement window, new projects do not need to manually copy scheduler assets, notification adapters do not require per-project summary logic, and operators do not confuse scaffold presence with native runtime support.

## Acceptance Criteria

- AC-001 Beacon freezes a project-local QA feedback ledger for automation/jobs.
- AC-002 Beacon exposes `beacon automation summarize-qa` as a public automation surface.
- AC-003 Beacon exposes `beacon automation update-queue` as a public automation surface.
- AC-004 queue update remains explicit and governed: passed QA candidates leave the QA queue, repair-needed candidates may enter the implement queue, and wrappers do not invent opportunistic work.
- AC-005 the nightly QA wrapper refreshes feedback ledger and queue after QA execution.
- AC-006 the gated implement wrapper refreshes queue state after implement execution.
- AC-007 `beacon automation capabilities` reports the feedback loop entrypoints and ledger path.
- AC-008 the supplement remains host-scheduled capability governance and does not create a new Beacon lifecycle stage or absorb scheduler runtime into Beacon core.
- AC-009 Beacon exposes `beacon automation init --project-root .` as a public scaffold bootstrap surface.
- AC-010 scaffold output is project-local and rewrites paths/labels for the target repo.
- AC-011 scaffold generation is conservative by default and refreshes only with explicit force.
- AC-012 Beacon freezes a tiered executor capability matrix instead of claiming uniform native automation across all agents.
- AC-013 scaffold generation supports executor profiles and reflects them in queue/spec outputs.
- AC-014 unsupported executors are not represented as current Beacon-native implement/qa runtimes.
- AC-015 Beacon freezes a shared automation summary schema that multiple QA layers and notification adapters can consume.
- AC-016 Beacon exposes `beacon automation build-summary` as a public automation surface.
- AC-017 scaffolded wrappers and notification helpers consume the same summary schema instead of project-specific summary formats.
- AC-018 Beacon exposes a human-facing `beacon-toolkit-automation` support surface for project-local scheduled automation bootstrap and maintenance.
