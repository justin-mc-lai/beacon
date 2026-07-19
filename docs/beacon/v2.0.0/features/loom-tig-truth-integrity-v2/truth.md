---
slug: loom-tig-truth-integrity-v2
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-tig-truth-integrity-v2/truth.md
  tests: docs/beacon/v2.0.0/features/loom-tig-truth-integrity-v2/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-tig-truth-integrity-v2/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-tig-truth-integrity-v2/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-101", "AC-103"]
wave: W3
priority: P1
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom TIG + Truth Integrity v2"
brand: Loom
---

# Requirement Truth: TIG + truth-integrity v2 路由 (W3)

## 人话

冻结/变更不烂：freeze 前 TIG hard block；doctor 路由 Rust。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W3 | P1 | AC-101, AC-103 |

Depends on: loom-run-agent-stop-when-external

## User Intent

冻结/变更不烂：freeze 前 TIG hard block；doctor 路由 Rust。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W3-001 | tig | freeze/refreeze 前 TIG，语义对齐 v1.6 build_truth_integrity_gate |
| UD-LOOM-W3-002 | audit_only | 已 frozen 历史默认 audit_only 不阻断 |
| UD-LOOM-W3-003 | doctor | doctor verify-truth-integrity v2 路由 exit 对齐 v1.6 |
| UD-LOOM-W3-004 | no_pyo3 | 不使用 PyO3 作为 v2 gate runtime fallback |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-101 | tig-hard | 空缺 AC/软 TC/未拍板 deferral/假交付/package 失败 → hard block + repair_route（Must） |
| AC-103 | doctor-route | doctor verify-truth-integrity --mode block exit 与 v1.6 一致（Must） |
| AC-LOOM-W3-001 | frozen-audit | 已 frozen 包 audit_only 不误杀（Must） |
| AC-LOOM-W3-002 | repair-route | block 时给出 repair_route（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W3-001 | 缺 AC 仍 freeze pass |
| I-W3-002 | PyO3 静默 fallback 冒充 v2 gate |

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
