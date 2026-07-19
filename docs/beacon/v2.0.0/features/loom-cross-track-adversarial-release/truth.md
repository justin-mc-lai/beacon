---
slug: loom-cross-track-adversarial-release
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/truth.md
  tests: docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-cross-track-adversarial-release/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-166", "AC-167"]
wave: W4a
priority: P1
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom Cross-Track + Adversarial Release"
brand: Loom
---

# Requirement Truth: 跨轨证据污染 + adversarial release (W4a)

## 人话

敢做人审 release：v1 证据不能关 v2；adversarial_review.v1 强制。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W4a | P1 | AC-166, AC-167 |

Depends on: loom-tig-truth-integrity-v2

## User Intent

敢做人审 release：v1 证据不能关 v2；adversarial_review.v1 强制。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W4A-001 | no_contam | v1 qa/scorecard 不得单独满足 v2 release |
| UD-LOOM-W4A-002 | symmetric | v2 gate_results 不得冒充 v1 release |
| UD-LOOM-W4A-003 | adversarial | release 前 adversarial_review.v1 ≥3 翻车点+证据 |
| UD-LOOM-W4A-004 | human | 不得用 skill-score/phase exit 替代 adversarial 或人审 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-166 | cross-track | 混用跨轨证据 → cross_track_evidence_contamination（Must） |
| AC-167 | adversarial | 缺 adversarial_review.v1 → adversarial_review_missing fail-closed（Must） |
| AC-LOOM-W4A-001 | schema | adversarial_review.v1 字段：≥3 failure points + evidence refs（Must） |
| AC-LOOM-W4A-002 | legal-illegal | legal dual-track clean + illegal contamination（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W4A-001 | 仅 v1 scorecard 宣称 v2 release_ready |
| I-W4A-002 | skill-score 替代 adversarial |

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
