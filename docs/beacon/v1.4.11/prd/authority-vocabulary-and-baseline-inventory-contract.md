# PRD: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

This feature freezes the first low-risk slice of v1.4.11 legacy burden reduction.

It requires Beacon to stop describing machine artifacts as requirement truth and to create an auditable inventory of known legacy, fallback, and compatibility surfaces before any behavior-changing retirement work begins.

The feature preserves existing runtime behavior except for authority wording and inventory generation.

## 1. Problem

Beacon's current architecture is moving toward Markdown-first requirement truth, but some policy and generated wording still describe machine artifacts as if they are truth.

At the same time, Beacon contains many legacy, fallback, and compatibility surfaces. Removing them without an inventory would risk breaking QA, release, projection, evidence, git, metadata, version gates, or historical projects.

The first slice must create vocabulary and inventory discipline before cleanup.

## 2. Goals

- AC-001: Beacon defines explicit artifact roles for truth, projection, evidence, runtime state, compatibility mirror, and historical fixture.
- AC-002: Current-facing wording does not describe `.machine` or machine-readable artifacts as requirement truth.
- AC-003: Markdown requirement materials remain the requirement truth for the current version line.
- AC-004: `.machine` remains available as projection, evidence, and read model.
- AC-005: A baseline inventory records known legacy, fallback, and compatibility surfaces before behavior changes.
- AC-006: The inventory includes source file, symbol or function, current behavior, risk, proposed owner, proposed phase, and required evidence.
- AC-007: This feature does not remove or change runtime compatibility behavior.
- AC-008: Tests fail when forbidden machine-as-truth wording or missing inventory coverage is introduced.

## 3. Design Principles

### 3.1 Vocabulary before cleanup

Beacon must fix the authority model before retiring compatibility paths.

### 3.2 Inventory before registry

The baseline inventory is a pre-registry artifact. It proves what exists before Phase 2 turns compatibility into a governed registry.

### 3.3 Projection remains valuable

`.machine` must stay because QA, release, status, evidence, and transaction checks require deterministic projection and read models.

### 3.4 No behavior retirement in this slice

This feature must not remove hidden aliases, legacy mirrors, fallback commands, implement loader behavior, prototype legacy source behavior, memory migration, or intent compatibility behavior.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must expose or document artifact roles: `truth`, `projection`, `evidence`, `runtime_state`, `compat_mirror`, and `historical_fixture`. |
| FR-002 | AC-002 | Beacon must reject or flag current-facing wording that says machine artifacts are requirement truth. |
| FR-003 | AC-003 | Beacon must describe `docs/beacon/<version>/` Markdown requirement package as current requirement truth. |
| FR-004 | AC-004 | Beacon must describe `docs/beacon/<version>/.machine` as projection, evidence, or read model. |
| FR-005 | AC-005 | Beacon must generate a baseline inventory markdown artifact for known legacy, fallback, and compatibility surfaces. |
| FR-006 | AC-005 | Beacon must generate a machine-readable baseline inventory JSON artifact. |
| FR-007 | AC-006 | Each inventory row must include source file, symbol or function, surface category, current behavior, risk, proposed owner, proposed phase, and required evidence. |
| FR-008 | AC-007 | This feature must preserve runtime behavior for compat commands, QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, and intent legacy router. |
| FR-009 | AC-008 | Tests must fail if forbidden wording returns to current-facing policy, status, help, or report output. |
| FR-010 | AC-008 | Tests must fail if required known hotspots are absent from the baseline inventory. |

## 5. Required Inventory Coverage

The baseline inventory must cover at least:

- artifact language policy wording.
- artifact language default policy and renderer.
- command catalog compat and deprecated command aliases.
- CLI factory hidden compatibility registrations.
- implement legacy CLI loader.
- QA canonical status and legacy auto-test mirror.
- PRD legacy mirror and material audit drift classification.
- prototype legacy source status.
- browser fallback command naming and evidence.
- memory legacy migration.
- intent legacy router compatibility facade.

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `authority_role`
- `compat_surface`
- `inventory_status`

### 6.3 Propagation Contract

Authority roles and inventory status must stay explicit through freeze readiness, implementation planning, QA coverage, and later compatibility registry work.

## 7. Success Metrics

- Forbidden machine-as-truth wording is removed or flagged from current-facing surfaces.
- Baseline inventory exists in markdown and JSON.
- Required hotspots are present in inventory coverage.
- Existing runtime compatibility behavior remains available after this slice.
- Later v1.4.11 features can consume the inventory to implement compatibility registry and behavior retirement.

## 8. Non Goals

- No compatibility registry in this slice.
- No legacy mirror policy change in this slice.
- No implement loader migration in this slice.
- No browser fallback rename in this slice.
- No memory or intent route behavior change in this slice.
- No release verdict change in this slice.
