# Project Skill QA Evolution Blueprint v1.6.1

## Intent

v1.6.1 extends the v1.6.0 harness with a **program plan** surface: sea-level utterances become book-shaped program artifacts, per-lake truth freeze, and program freeze gate.

## Skill Material Effects

Program planner skills (`beacon-pln-program*`) are planner harness skills. They write **program artifacts only** under `docs/beacon/<version>/programs/<slug>/`, never `features/*/truth.md`.

## Required QA Dimensions

- `beacon plan start` and `beacon program *` CLI surfaces exist and are catalogued
- Program FSM invalid transitions are covered by `tests/test_program_plan_state_contract.py`
- Agent surface projects program skill triad without unexpected host drift
- TIG block mode passes on frozen feature package after hygiene refreeze

## Current Status

Program harness truth frozen at R2; implementation Phases B–F tracked in feature tasks ledger.
