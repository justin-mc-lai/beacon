---
slug: beacon-fsm-implement-order-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-19: v1.6.8 热修 friction closeout 四湖 program"
canonical_refs:
  truth: docs/beacon/archive/v1.6.8/features/beacon-fsm-implement-order-v168/truth.md
  tests: docs/beacon/archive/v1.6.8/features/beacon-fsm-implement-order-v168/tests.md
  tasks: docs/beacon/archive/v1.6.8/features/beacon-fsm-implement-order-v168/tasks.md
  evidence: docs/beacon/archive/v1.6.8/features/beacon-fsm-implement-order-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/archive/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/runtime governance; no product marketing UI"
promotion_ref: docs/beacon/archive/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md
---

# Requirement Truth: beacon-fsm-implement-order-v168 (v1.6.8 R1)

## 人话

先商品后订单。entity precedence 与合法 walk 必须挡住「先做下游」的 implement admission。

- **能做**：domain FSM / entity precedence 强制 implement 任务序，禁止空中楼阁切片
- **不能做**：自证 complete/release；假 runner；第二公共入口；用「文档写了」代替代码默认
- **怎样算完**：AC 合同测绿；主轴 validate；examples 可跟做

## User Intent（一行）

domain-bearing 功能的 implement 只能按状态机/实体前置顺序推进；QA 负例可证明。

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

**Role**: fsm implement order  
**Program**: `beacon-friction-closeout-v168`  
**Promotion**: `docs/beacon/archive/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md`  
**Implement hint**: `implement admission + domain_fsm helpers + task ordering`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-FIO-001 | admission | domain_required=true 时 implement admission 读取 entity precedence / FSM；前置未 verified 则 blocked + reason_code |
| AC-FIO-002 | tasks_order | tasks 生成/校验：下游实体任务不得排在前置实体完成前（或标记 blocked_until） |
| AC-FIO-003 | qa_negative | golden/negative：无前置实体不能完成下游动作（合同测或 fixture） |
| AC-FIO-004 | axis | 挂 GoalRun：stage_active implement 守卫引用 FSM order；非法 complete 仍禁 |
| AC-FIO-005 | escape | 显式 non-domain 湖（domain_required=false）不强制实体序 |
| AC-V168-FC-001 | shared | beacon-fsm-implement-order-v168: 合同入口与 reason_code 稳定 |
| AC-V168-FC-002 | shared | beacon-fsm-implement-order-v168: 非法转移 fail-closed |
| AC-V168-FC-003 | shared | beacon-fsm-implement-order-v168: CLI/doctor 可调用 |
| AC-V168-FC-004 | shared | beacon-fsm-implement-order-v168: 正负例测通过 |
| AC-V168-FC-005 | shared | beacon-fsm-implement-order-v168: 挂 GoalRun 主轴 |
| AC-V168-FC-006 | shared | beacon-fsm-implement-order-v168: examples 可跟做 |
| AC-V168-FC-007 | shared | beacon-fsm-implement-order-v168: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-FC-008 | shared | beacon-fsm-implement-order-v168: 与 v1.6.8 产运/主轴哲学一致 |

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
