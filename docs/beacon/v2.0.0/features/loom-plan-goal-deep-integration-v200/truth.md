---
slug: loom-plan-goal-deep-integration-v200
version: v2.0.0
status: frozen
parity_of: docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md
---

# Loom parity: Plan ↔ Goal Deep Integration (P0–P2)

Same AC as v1.6.9. Brand Loom / Rust CLI track for public surface; Python runtime modules remain shared for goal facade until Rust ports land.

Python package must not own PATH name `loom` (only `loom-py` / Rust binary).
