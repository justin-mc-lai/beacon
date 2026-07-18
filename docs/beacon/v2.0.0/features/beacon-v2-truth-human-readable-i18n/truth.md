---
slug: beacon-v2-truth-human-readable-i18n
version: v2.0.0
status: frozen
revision_id: R1
language: zh
change_reason: "User GO 2026-07-18: v2 parity of human-readable L0 + humanizer i18n; mount v2 GoalRun axis"
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json
ux_required: false
design_deferral: "Docs/prose gate; no product marketing UI"
upstream_ref: docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/truth.md
---

# Requirement Truth: v2 Truth Human-Readable + i18n + Humanizer (R1)

## 人话

和 v1.6.7 同一件事：需求真相必须有人话层 + humanizer 文风，并支持中英。

v2 **完整继承** UD-HR-001..010 / AC-HR-001..012 语义，挂在 v2 program 主轴上。  
运行时实现优先复用 v1.6.7 模块；Rust 只在 W 波次接线，**不得**另起一套互相矛盾的规则。

## User Intent（一行）

v2 合同与 v167 同语义；主轴可见；无第二套散文标准。

## User Decisions（locked）

| ID | Decision | Value |
|----|----------|-------|
| UD-V2-HR-001 | Full parity | 继承 v167 AC-HR / UD-HR / TruthProseGate |
| UD-V2-HR-002 | Single norms | 共用 `skills/beacon/references/truth-humanizer/*` |
| UD-V2-HR-003 | Axis | 挂 `beacon-v2-product-goal-parallel-v200` GoalRun 主轴 |
| UD-V2-HR-004 | Carrier | Python gate 先；Rust freeze 后接同一 reason_code |
| UD-V2-HR-005 | No dilute | 不得降级为「仅建议、不 fail-closed」 |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-HR-001 | parity | v167 AC-HR-001..012 语义可映射（**Must**） |
| AC-V2-HR-002 | self-l0 | 本 truth 含 `## 人话`（**Must**） |
| AC-V2-HR-003 | norms | 共用 norms 路径存在（**Must**） |
| AC-V2-HR-004 | axis | v2 axis validate 含本湖（**Must**） |
| AC-V2-HR-005 | reason | `truth_human_l0_missing` 跨轨稳定（**Must**） |
| AC-V2-HR-006 | no-second-standard | 禁止 v2 私有矛盾词表（**Must**） |

## Non-Goals

- 在 v2 重写 humanizer 哲学
- 默认 BEACON_V2=1

## done_when

- 镜像包 frozen + 主轴挂载 + parity tests 绿（implement 后）
