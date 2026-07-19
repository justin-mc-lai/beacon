---
slug: beacon-longrun-contract-align-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-19: v1.6.8 热修 friction closeout 四湖 program"
canonical_refs:
  truth: docs/beacon/v1.6.8/features/beacon-longrun-contract-align-v168/truth.md
  tests: docs/beacon/v1.6.8/features/beacon-longrun-contract-align-v168/tests.md
  tasks: docs/beacon/v1.6.8/features/beacon-longrun-contract-align-v168/tasks.md
  evidence: docs/beacon/v1.6.8/features/beacon-longrun-contract-align-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/runtime governance; no product marketing UI"
promotion_ref: docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md
---

# Requirement Truth: beacon-longrun-contract-align-v168 (v1.6.8 R1)

## 人话

v1.6.8 写了 longrun_default=true 就必须真默认开；opt-out 显式。禁止 BEACON_GOAL_HONOR_LONGRUN_DEFAULT 这种暗门才能生效。

- **能做**：对齐 longrun_default 合同与 product_goal_runtime：默认兑现，无需神秘环境变量
- **不能做**：自证 complete/release；假 runner；第二公共入口；用「文档写了」代替代码默认
- **怎样算完**：AC 合同测绿；主轴 validate；examples 可跟做

## User Intent（一行）

longrun 合同与代码一致；新项目默认长跑可 opt-out；v2/Loom 哲学同源声明。

## User Decisions（locked）

| ID | Value |
|----|-------|
| UD-FC-001 | install_channel_must_not_follow_dirty_feature_branch |
| UD-FC-002 | longrun_default_contract_matches_code_without_env_gate |
| UD-FC-003 | release_profile_drives_release_check_set |
| UD-FC-004 | entity_precedence_gates_implement_admission |
| UD-FC-005 | single_public_entry_beacon_goal |
| UD-FC-006 | four_lakes_one_goalrun_axis |
| UD-V168-001 | longrun_default_true_new_projects_enforced_in_code |
| UD-V168-007 | submachines_cannot_complete_goalrun |

## Overview

**Role**: longrun contract  
**Program**: `beacon-friction-closeout-v168`  
**Promotion**: `docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md`  
**Implement hint**: `beacon/utils/product_goal_runtime.py run_goal_facade + prod_ops_v168.resolve_longrun_enabled`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-LCA-001 | default | 无 --longrun 时：若项目 goal.longrun_default=true（新项目默认 true），则 goal run 生效 longrun=true / longrun_source=project_default |
| AC-LCA-002 | opt_out | CLI --no-longrun 或项目 longrun_default=false 时 longrun 关闭 |
| AC-LCA-003 | no_env_gate | 不得再要求 BEACON_GOAL_HONOR_LONGRUN_DEFAULT=1 才读取项目默认（可保留 env 仅作 force override，不得作为默认门） |
| AC-LCA-004 | bridge_doctor | beacon goal doctor longrun（或 diagnose）报告 bridge/supervise/driver 就绪与 halt_reason |
| AC-LCA-005 | docs | SUMMARY/examples/UD-V168-001 与代码行为一致；v2/Loom parity 声明不反向改写 v1 合同 |
| AC-V168-FC-001 | shared | beacon-longrun-contract-align-v168: 合同入口与 reason_code 稳定 |
| AC-V168-FC-002 | shared | beacon-longrun-contract-align-v168: 非法转移 fail-closed |
| AC-V168-FC-003 | shared | beacon-longrun-contract-align-v168: CLI/doctor 可调用 |
| AC-V168-FC-004 | shared | beacon-longrun-contract-align-v168: 正负例测通过 |
| AC-V168-FC-005 | shared | beacon-longrun-contract-align-v168: 挂 GoalRun 主轴 |
| AC-V168-FC-006 | shared | beacon-longrun-contract-align-v168: examples 可跟做 |
| AC-V168-FC-007 | shared | beacon-longrun-contract-align-v168: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-FC-008 | shared | beacon-longrun-contract-align-v168: 与 v1.6.8 产运/主轴哲学一致 |

## ProseGate tooling states

- contract_draft → frozen → implement → qa → release_pending → human release

禁止：submachine 自写 completed / auto release_confirmed。

## Non-Goals

- 云 CD 引擎本体
- 自动生产回滚执行
- 默认 BEACON_V2=1 替换 Beacon
- 第二公共 skill 入口

## done_when

- 实现 + 合同测绿
- 主轴挂载
- 与同 program 其它湖不互相矛盾
