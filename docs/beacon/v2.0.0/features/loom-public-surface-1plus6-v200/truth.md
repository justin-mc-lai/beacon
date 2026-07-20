---
slug: loom-public-surface-1plus6-v200
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "Parity freeze with v1.6.9 Scheme A 1+6 public surface; brand Loom/Rust only"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/truth.md
  tests: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/evidence.md
ux_required: false
shared_synonym_table: skills/beacon/references/public-surface-1plus6.md
parity_of: docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/truth.md
rust_public_abilities_ref: packages/beacon-rs/beacon-core/src/harness.rs
---

# Requirement Truth: Loom Public Surface 1+6 (v2.0.0 R1)

## 人话

与 v1.6.9 **同一张** 1+6 同义表。Loom 只换品牌与 **Rust CLI**；不另发明第七公共 harness。

## User Decisions

同 v1.6.9 UD-PS-001..006。

## Canonical table

`skills/beacon/references/public-surface-1plus6.md`

Rust authority for the six: `PUBLIC_ABILITIES` in `harness.rs` must stay length 6 and map:

| Public id | Rust id |
|-----------|---------|
| plan | loop |
| truth | truth |
| design | design |
| implement | implement |
| qa | qa-evidence |
| release | release |

Goal: `loom-goal` + Rust `loom`/`beacon-v2` — transversal long-run only.

## Acceptance

Same AC-PS-001..008 as v1.6.9 package (shared tests).
