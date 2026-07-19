---
slug: beacon-release-profile-wiring-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-19: v1.6.8 热修 friction closeout 四湖 program"
canonical_refs:
  truth: docs/beacon/v1.6.8/features/beacon-release-profile-wiring-v168/truth.md
  tests: docs/beacon/v1.6.8/features/beacon-release-profile-wiring-v168/tests.md
  tasks: docs/beacon/v1.6.8/features/beacon-release-profile-wiring-v168/tasks.md
  evidence: docs/beacon/v1.6.8/features/beacon-release-profile-wiring-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/runtime governance; no product marketing UI"
promotion_ref: docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md
---

# Requirement Truth: beacon-release-profile-wiring-v168 (v1.6.8 R1)

## 人话

热修不要再撞全量考古门。select_release_profile 必须接到 beacon release check；hotfix 最小门+rollback_notes+forward-port。

- **能做**：ReleaseProfile.full|hotfix 真正驱动 release check 检查集；hotfix 减负+强制项
- **不能做**：自证 complete/release；假 runner；第二公共入口；用「文档写了」代替代码默认
- **怎样算完**：AC 合同测绿；主轴 validate；examples 可跟做

## User Intent（一行）

release check 按 profile 减负；每个 fail 有单一 repair 命令；hotfix 可走热修门集。

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

**Role**: release profile wiring  
**Program**: `beacon-friction-closeout-v168`  
**Promotion**: `docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md`  
**Implement hint**: `beacon/commands/release.py + prod_ops_v168.select_release_profile`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-RPW-001 | wire | beacon release check 接受 --profile full|hotfix（或从 GoalRun.mode=hotfix 推导）并改变 checks 集合 |
| AC-RPW-002 | hotfix_min | hotfix profile 不要求与 full 等价的全量 scorecard 项；保留安全硬项（rollback_notes、forward_port、基线、关键回归槽） |
| AC-RPW-003 | repair | 每个 blocked check 的 detail/reason 含单一 recommended repair 命令 |
| AC-RPW-004 | selfheal | repair-evidence-manifest + align-run-id 在 hotfix/full 失败路径被推荐且可恢复常见 drift |
| AC-RPW-005 | no_fake | profile 减负不等于 fake green：缺强制项仍 fail-closed |
| AC-V168-FC-001 | shared | beacon-release-profile-wiring-v168: 合同入口与 reason_code 稳定 |
| AC-V168-FC-002 | shared | beacon-release-profile-wiring-v168: 非法转移 fail-closed |
| AC-V168-FC-003 | shared | beacon-release-profile-wiring-v168: CLI/doctor 可调用 |
| AC-V168-FC-004 | shared | beacon-release-profile-wiring-v168: 正负例测通过 |
| AC-V168-FC-005 | shared | beacon-release-profile-wiring-v168: 挂 GoalRun 主轴 |
| AC-V168-FC-006 | shared | beacon-release-profile-wiring-v168: examples 可跟做 |
| AC-V168-FC-007 | shared | beacon-release-profile-wiring-v168: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-FC-008 | shared | beacon-release-profile-wiring-v168: 与 v1.6.8 产运/主轴哲学一致 |

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
