---
slug: beacon-hotfix-lane-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO v1.6.8 prod-ops hardening; promotion_ref pln-review"
canonical_refs:
  truth: docs/beacon/archive/v1.6.8/features/beacon-hotfix-lane-v168/truth.md
  tests: docs/beacon/archive/v1.6.8/features/beacon-hotfix-lane-v168/tests.md
  tasks: docs/beacon/archive/v1.6.8/features/beacon-hotfix-lane-v168/tasks.md
  evidence: docs/beacon/archive/v1.6.8/features/beacon-hotfix-lane-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.8/programs/beacon-prod-ops-hardening-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/CLI governance; no product marketing UI"
promotion_ref: docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md
---

# Requirement Truth: Hotfix Lane (v1.6.8 R1)

## 人话

goal --mode hotfix + forward-port + rollback_notes。

- 能做：按合同提供可调用 CLI/门禁/工件，并挂在 GoalRun 主轴上
- 不能做：自证 complete/release；假 runner；第二公共入口替代 beacon-goal
- 怎样算完：AC 测过；主轴 validate；与 v2/Loom 哲学声明一致

## User Intent（一行）

goal --mode hotfix + forward-port + rollback_notes 在 v1.6.8 可交付并同步 Loom。

## User Decisions（locked）

| ID | Value |
|----|-------|
| UD-V168-001 | longrun_default=true for new projects |
| UD-V168-002 | hotfix entry = goal --mode hotfix |
| UD-V168-003 | hotfix requires forward-port plan |
| UD-V168-004 | evidence repair may write .beacon |
| UD-V168-005 | v2/Loom parity contracts same milestone |
| UD-V168-006 | single public facade beacon-goal |
| UD-V168-007 | submachines cannot complete GoalRun |

## Overview

**Role**: goal --mode hotfix + forward-port + rollback_notes

**Program**: `beacon-prod-ops-hardening-v168`  
**Promotion**: `docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-HF-001 | mode | goal --mode hotfix creates GoalRun.mode=hotfix |
| AC-HF-002 | baseline | requires from_version or production tag |
| AC-HF-003 | forward-port | forward_port plan required before release_confirmed |
| AC-HF-004 | rollback | rollback_notes required for hotfix release |
| AC-HF-005 | profile | uses ReleaseProfile.hotfix |
| AC-V168-001 | entry | Hotfix Lane: 合同入口与 reason_code 稳定 |
| AC-V168-002 | fsm | Hotfix Lane: 非法转移 fail-closed |
| AC-V168-003 | cli | Hotfix Lane: CLI/doctor 命令可调用 |
| AC-V168-004 | test | Hotfix Lane: 正负例测通过 |
| AC-V168-005 | axis | Hotfix Lane: 挂 GoalRun 主轴 |
| AC-V168-006 | example | Hotfix Lane: examples 可跟做 |
| AC-V168-007 | no-fake | Hotfix Lane: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-008 | loom-parity | Hotfix Lane: v2/Loom 哲学同源声明 |

## ProseGate tooling states

- contract_draft → frozen → implement → qa → release_pending → human release

禁止：submachine 自写 completed / auto release_confirmed。

## Non-Goals

- 云 CD 引擎本体
- 自动生产回滚执行（仅 rollback_notes）
- Loom CLI 全量双装（v2 Wave 0）
- 默认 BEACON_V2=1

## done_when

- 实现 + 合同测绿
- 主轴挂载
- 人工 release 门可跑
