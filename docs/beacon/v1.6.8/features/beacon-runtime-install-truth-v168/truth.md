---
slug: beacon-runtime-install-truth-v168
version: v1.6.8
status: frozen
revision_id: R1
language: zh
domain_required: false
change_reason: "User GO 2026-07-19: v1.6.8 热修 friction closeout 四湖 program"
canonical_refs:
  truth: docs/beacon/v1.6.8/features/beacon-runtime-install-truth-v168/truth.md
  tests: docs/beacon/v1.6.8/features/beacon-runtime-install-truth-v168/tests.md
  tasks: docs/beacon/v1.6.8/features/beacon-runtime-install-truth-v168/tasks.md
  evidence: docs/beacon/v1.6.8/features/beacon-runtime-install-truth-v168/evidence.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
program_ref: docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json
ux_required: false
design_deferral: "Ops/runtime governance; no product marketing UI"
promotion_ref: docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md
---

# Requirement Truth: beacon-runtime-install-truth-v168 (v1.6.8 R1)

## 人话

全局 beacon 版本必须可信：不跟着脏 feature 分支漂；一键 diagnose 说清 CLI 路径、version-truth、git HEAD、docs 线。

- **能做**：生产安装通道与 CLI/version-truth/git HEAD 三联诊断，禁止 feature 分支污染全局
- **不能做**：自证 complete/release；假 runner；第二公共入口；用「文档写了」代替代码默认
- **怎样算完**：AC 合同测绿；主轴 validate；examples 可跟做

## User Intent（一行）

安装面与版本真相可诊断、可固定，全局 CLI 不被任意工作分支回退。

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

**Role**: install truth  
**Program**: `beacon-friction-closeout-v168`  
**Promotion**: `docs/beacon/v1.6.8/research/beacon-friction-closeout-v168-gen-change.md`  
**Implement hint**: `beacon/utils/runtime_install_truth.py + doctor diagnose-runtime`

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-RIT-001 | diagnose | beacon doctor diagnose-runtime（或等价）输出 CLI path / package_version / toolkit_version / version-truth current line / git HEAD+branch / docs line |
| AC-RIT-002 | pin | 生产安装支持非 editable 固定通道（tag/wheel 或 doctor setup --release-line）；文档明确禁止「任意 feature 分支 editable 当生产」 |
| AC-RIT-003 | drift | 当 CLI 版本 ≠ version-truth.current_runtime_release_line 时 fail-closed 并给单一 repair 命令 |
| AC-RIT-004 | fleet | beacon version fleet（或 diagnose）展示 prod/maint/next 与本机实际安装源 |
| AC-RIT-005 | example | skills/beacon/examples 提供 30s 安装诊断路径 |
| AC-V168-FC-001 | shared | beacon-runtime-install-truth-v168: 合同入口与 reason_code 稳定 |
| AC-V168-FC-002 | shared | beacon-runtime-install-truth-v168: 非法转移 fail-closed |
| AC-V168-FC-003 | shared | beacon-runtime-install-truth-v168: CLI/doctor 可调用 |
| AC-V168-FC-004 | shared | beacon-runtime-install-truth-v168: 正负例测通过 |
| AC-V168-FC-005 | shared | beacon-runtime-install-truth-v168: 挂 GoalRun 主轴 |
| AC-V168-FC-006 | shared | beacon-runtime-install-truth-v168: examples 可跟做 |
| AC-V168-FC-007 | shared | beacon-runtime-install-truth-v168: 禁止 placeholder/fake-runner 闭环 |
| AC-V168-FC-008 | shared | beacon-runtime-install-truth-v168: 与 v1.6.8 产运/主轴哲学一致 |

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
