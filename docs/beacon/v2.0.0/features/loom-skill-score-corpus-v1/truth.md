---
slug: loom-skill-score-corpus-v1
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-19 option2: freeze W1-W5 kernel closure lakes under program loom-kernel-closure-w1w5-v200"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/loom-skill-score-corpus-v1/truth.md
  tests: docs/beacon/v2.0.0/features/loom-skill-score-corpus-v1/tests.md
  tasks: docs/beacon/v2.0.0/features/loom-skill-score-corpus-v1/tasks.md
  evidence: docs/beacon/v2.0.0/features/loom-skill-score-corpus-v1/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/feature-graph.json
parent_kernel: beacon-v2-rust-kernel-redesign
upstream_acs: ["AC-169"]
wave: W5
priority: P2
ux_required: false
design_deferral: "kernel/CLI; no product marketing UI"
display_name: "Loom Skill-Score Corpus v1"
brand: Loom
---

# Requirement Truth: skill-score corpus 统一 (W5)

## 人话

双轨评分可比：skill-score-corpus.v1 + baseline；缺 corpus fail-closed。

本湖是 Loom（Beacon 进化品牌）内核补齐的一部分；**不**把生产 `beacon` 默认切走。

## Overview

| Wave | Priority | Upstream AC |
|------|----------|-------------|
| W5 | P2 | AC-169 |

Depends on: loom-cross-track-adversarial-release

## User Intent

双轨评分可比：skill-score-corpus.v1 + baseline；缺 corpus fail-closed。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-LOOM-W5-001 | corpus | versioned skill-score-corpus.v1 固定 prompts+负例 |
| UD-LOOM-W5-002 | dual | v1 包与 Loom 六 public 同 schema 字段 |
| UD-LOOM-W5-003 | baseline | with_skill vs no_skill 或等价对照 |
| UD-LOOM-W5-004 | no_auto | score 禁止 auto-apply 改 SKILL.md |
| UD-LOOM-W5-005 | compat | 与现有 loom skill-score 互补；corpus 为权威行为对照 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-169 | corpus | 提供 skill-score-corpus.v1 + baseline；缺 → skill_score_corpus_missing（Must） |
| AC-LOOM-W5-001 | six-public | 六 public loom skill 可被 corpus 跑通（Must） |
| AC-LOOM-W5-002 | v1-sample | 至少一套 v1 skill fixture 同 schema（Must） |
| AC-LOOM-W5-003 | no-auto-edit | CLI 不得自动写 SKILL.md（Must） |

## Illegal

| ID | Illegal |
|----|---------|
| I-W5-001 | 无 corpus 仍宣称正式 skill-score 关单 |
| I-W5-002 | score 自动改 SKILL.md |

## Non-Goals

- 默认 `BEACON_V2=1` / loom 覆盖 beacon
- 本湖单独宣称整个 v2.0.0 release 完成
- feature slug 全量路径 rename

## Alignment Surface

完成定义以上表 AC 为准；implement/QA 须 integration tier 行为证据与可执行 TC。
