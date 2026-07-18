---
slug: beacon-version-fleet-ops-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO v1.6.8 prod-ops hardening; promotion_ref pln-review"
canonical_refs:
  truth: docs/beacon/v1.6.8/features/beacon-version-fleet-ops-v168/truth.md
  tests: docs/beacon/v1.6.8/features/beacon-version-fleet-ops-v168/tests.md
  tasks: docs/beacon/v1.6.8/features/beacon-version-fleet-ops-v168/tasks.md
  evidence: docs/beacon/v1.6.8/features/beacon-version-fleet-ops-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.8/programs/beacon-prod-ops-hardening-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/CLI governance; no product marketing UI"
promotion_ref: docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md
---

# Requirement Truth: Version Fleet Ops (v1.6.8 R1)

## 人话

version fleet read model + dual-version productization。

- 能做：按合同提供可调用 CLI/门禁/工件，并挂在 GoalRun 主轴上
- 不能做：自证 complete/release；假 runner；第二公共入口替代 beacon-goal
- 怎样算完：AC 测过；主轴 validate；与 v2/Loom 哲学声明一致

## User Intent（一行）

version fleet read model + dual-version productization 在 v1.6.8 可交付并同步 Loom。

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

**Role**: version fleet read model + dual-version productization

**Program**: `beacon-prod-ops-hardening-v168`  
**Promotion**: `docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-VF-001 | fleet | beacon version fleet shows prod/maint/next/planning |
| AC-VF-002 | dual-init | doctor init-dual-version writes hotfix naming + baselines |
| AC-VF-003 | dual-verify | doctor verify-dual-version fail-closed |
| AC-VF-004 | forbidden | forbidden next_feature->first_production_fix when dual-version on |
| AC-V168-001 | entry | Version Fleet Ops: 合同入口与 reason_code 稳定 |
| AC-V168-002 | fsm | Version Fleet Ops: 非法转移 fail-closed |
| AC-V168-003 | cli | Version Fleet Ops: CLI/doctor 命令可调用 |
| AC-V168-004 | test | Version Fleet Ops: 正负例测通过 |
| AC-V168-005 | axis | Version Fleet Ops: 挂 GoalRun 主轴 |
| AC-V168-006 | example | Version Fleet Ops: examples 可跟做 |
| AC-V168-007 | no-fake | Version Fleet Ops: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-008 | loom-parity | Version Fleet Ops: v2/Loom 哲学同源声明 |

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
