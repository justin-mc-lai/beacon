---
slug: workspace-clean-exit-gate-v1610
version: v1.6.10
status: frozen
revision_id: R1
language: zh
domain_required: true
ux_required: false
package_maturity: filled
parser_contract: beacon-feature-package-v2
git_canonical_branch: main
participating_services: [beacon]
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.10/features/workspace-clean-exit-gate-v1610/truth.md
  user_story: docs/beacon/v1.6.10/features/workspace-clean-exit-gate-v1610/truth.md
  test_case: docs/beacon/v1.6.10/features/workspace-clean-exit-gate-v1610/tests.md
truth_source_model: feature_package_authoritative
promotion_ref: docs/beacon/v1.6.10/research/implement-worktree-admission-prewrite-review-20260723.md
change_reason: "R1: add lifecycle exit clean-workspace gate; split formal/runtime evidence; isolate post-release projections"
humanizer_applied: true
---

# Requirement Truth: Workspace Clean Exit Gate (v1.6.10 R1)

## 人话

Beacon 现在能挡住 main 上直接提交业务代码，但还不能保证一条需求真相交付链跑完后工作区干净。release、truth review、QA、post-release hook 会写 `.machine`、`.beacon`、agent surface、trace、evidence manifest；这些副作用如果不分类、不提交、不忽略，就会把下一个项目带进脏工作区。

本湖只做一件事：把“交付完成后工作区干净”变成强不变量。所有写入都必须先归类：真相与正式证据要提交；本地 runtime 要 ignored 或生成脱敏 digest；host projection 要隔离到临时 worktree 或形成 deterministic surface-sync commit；未知脏改动一律阻断。

- 能做：新增 clean-workspace exit gate、dirty manifest 分类、formal/runtime evidence 分离、trace 脱敏/提升规则、post-release temp worktree 规则。
- 不能做：用 `quiet-worktree` 冒充 release proof、把 raw trace/本地 hook evidence 当正式证据、让 post-release hook 污染主工作区、自动 release。
- 怎样算完：`beacon doctor verify-clean-workspace --strict --json` 可重放；feature/release 出口对 unclassified dirty fail-closed；post-release 后原 project root 无新增 tracked dirty。

## User Intent

确保 Beacon 管理项目走完 plan→truth→freeze→implement→qa→release/post-release 后，工作区可证明干净，且任何剩余文件都已被正式提交、显式忽略、或作为本地 runtime 分类。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
scope_mode: lifecycle_governance_hardening
outcome: workspace_clean_after_beacon_truth_delivery
non_negotiables:
  - lifecycle_exit_must_verify_full_git_status
  - main_business_commit_guard_is_not_enough
  - formal_evidence_and_runtime_evidence_must_be_split
  - task_checkbox_requires_promoted_evidence
  - raw_agent_trace_is_local_confidential_runtime_by_default
  - post_release_local_install_must_not_dirty_original_root
  - quiet_worktree_is_convenience_not_release_proof
out_of_scope:
  - automatic_release_confirmation
  - deleting historical evidence without explicit cleanup command
  - replacing requirement truth gates
```

## Alignment Surface

R1 只收口工作区干净不变量、artifact 分类、出口 gate、post-release 投影隔离、trace/evidence promotion 与 CLI/doctor 接入。它不实现业务功能、不改变 release human gate、不改变 truth review 的 A/B/C/D 定义。

## Phased Backlog

| Phase | Scope | Decision |
|-------|-------|----------|
| R1 | clean-workspace verifier、dirty manifest、evidence split、trace redline/promotion、post-release temp worktree、release/pre-push接入 | accepted |
| Later | 历史 evidence 全量隐私审计、跨机器租约、远端 PR 自动化、按项目定制 projection 策略 UI | accepted defer |

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-WC-001 | plan review synthesis | must | AC-WC-001 | covered |
| INT-WC-002 | architecture reviewer | must | AC-WC-002 | covered |
| INT-WC-003 | QA reviewer | must | AC-WC-003, AC-WC-004 | covered |
| INT-WC-004 | security reviewer | must | AC-WC-005, AC-WC-006 | covered |
| INT-WC-005 | code governance reviewer | must | AC-WC-007, AC-WC-008 | covered |
| INT-WC-006 | current Beacon incident | must | AC-WC-009 | covered |
| INT-WC-007 | user lifecycle requirement | must | AC-WC-010, AC-WC-011 | covered |
| INT-WC-008 | release human gate boundary | must | AC-WC-012 | covered |
| INT-WC-HIST-001 | future audit | should | Non-goal: historical evidence audit separate lake | deferred |

## First principles（域）

| ID | Constraint |
|----|------------|
| FP-WC-001 | 完成定义来自 requirement truth 与可重放证据，不来自 agent 自述或 hook 成功。 |
| FP-WC-002 | `git status` 是工作区干净事实源；skip-worktree/quiet 只能降噪，不能作为 release proof。 |
| FP-WC-003 | 每个 dirty path 必须有 artifact_role；未知角色不能进入下一阶段。 |
| FP-WC-004 | formal evidence 必须 branch-carried、tracked、hash-valid；runtime evidence 不能支撑 release verdict。 |
| FP-WC-005 | raw trace 默认本地敏感；只有脱敏 digest 可 promotion 为正式证据。 |
| FP-WC-006 | post-release local install 是副作用面，必须隔离或独立提交，不能污染原 release root。 |

## 用户旅程

### Journey A：feature truth 冻结

1. 用户确认 planner findings 进入 truth。
2. truth 包写入 `workspace-clean-exit-gate-v1610`。
3. Truth Review Gate 通过后 freeze。
4. freeze 结束运行 clean-workspace 分类；仅允许本 feature truth/package 与必要 gate report 成为 scoped dirty。
5. 任何无归类 dirty 阻断进入 implement。

### Journey B：实现与 QA

1. implement 前执行 `workspace admit`，只在 admitted worktree 写代码。
2. 实现产生 AC evidence；每个 `[x] evidence=` 必须 tracked/promoted。
3. QA 运行后验证 formal manifest、task evidence、trace digest 与 workspace clean。
4. 孤儿 evidence 或 unchecked task 对应现存 evidence 均阻断。

### Journey C：release/post-release

1. release 前 full `git status --porcelain` 经 dirty manifest 分类后必须 clean。
2. post-release local install 在临时 worktree 或独立 surface-sync 事务运行。
3. 原 project root 只接受 ignored runtime state 或已提交 projection；否则 hook blocked。
4. hook 成功不替代 QA/release verdict。

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-WC-001 | 提供 `verify_clean_workspace`（或等价）统一出口 gate，读取完整 `git status --porcelain=v1 -uall`，按 artifact_role 分类并对 unclassified dirty fail-closed |
| AC-WC-002 | dirty manifest 至少区分 `canonical_truth`、`formal_evidence`、`machine_projection`、`host_projection`、`runtime_private`、`forbidden`，并给出每类允许动作 |
| AC-WC-003 | formal evidence manifest 仅可包含 tracked、branch-carried、hash-valid 的正式证据；local hook/runtime evidence 必须进入 runtime manifest 或 ignored state，不能支撑 QA/release verdict |
| AC-WC-004 | tasks.md 中 `[x] + evidence=PATH` 必须要求 evidence 文件存在、可解析、tracked/promoted、并被 evidence.md 或 formal manifest 索引；`[ ] + existing evidence` 必须作为 orphan evidence 阻断或要求清理 |
| AC-WC-005 | agent_trace 写入前必须执行 redline/allowlist gate，禁止 `full_chat`、非空 `chat_body`、raw messages、prompt/completion、token/cookie/env/private key 等字段写入或 promotion |
| AC-WC-006 | raw `.beacon/traces/**` 默认分类为 `runtime_private`；正式证据只能使用脱敏 digest，digest 含 event_count、harness、feature_slug、reason_codes、sha256、`redaction_status=pass` |
| AC-WC-007 | `beacon-post-release-local-install` 默认在临时 git worktree 或等价隔离区执行 project-local agent/context projection；原 project_root 运行前后快照不得新增 tracked dirty |
| AC-WC-008 | `quiet-worktree`/skip-worktree 只能作为开发者降噪；`verify-clean-workspace --strict` 必须揭示 skip-worktree hidden dirty，且不允许 skip-worktree hidden dirty 进入 `clean_verified` 或被当作 clean proof |
| AC-WC-009 | host projection 必须二选一：local-only ignore/skip 策略，或 deterministic `surface-sync` commit；禁止 release 后留下未提交 `.agents/.codex/.cursor/.trae/.windsurf` 投影改动 |
| AC-WC-010 | truth/freeze/qa/release/post-release 出口都必须调用 clean-workspace gate 或记录同 schema verification bundle；失败 reason_code 明确指向 commit、promote、ignore、clean 或 rerun route |
| AC-WC-011 | pre-push/main-push profile 必须阻断 generator dirty 与 unclassified dirty，不再只检查 staged business paths；business code main guard 仍保留为 defense-in-depth |
| AC-WC-012 | release human gate 保持最高边界；clean-workspace pass 不等于 release pass，post-release hook pass 也不等于 QA/release verdict |

## Domain Model

| Entity | Key | Requires |
|--------|-----|----------|
| WorkspaceSnapshot | project_root + git_head + timestamp | git repository |
| DirtyEntry | path + xy status | WorkspaceSnapshot |
| ArtifactRole | role id | dirty manifest rule |
| FormalEvidenceManifest | version + feature | tracked evidence refs |
| RuntimeEvidenceManifest | run_id | local runtime refs |
| TraceDigest | feature_slug + run_id | redacted trace source |
| HostProjectionTxn | agent + version + source_hash | surface setup/verify |
| CleanWorkspaceGate | profile + snapshot | classification results |

## Domain FSM CleanWorkspaceExit

| State | From | Guard |
|-------|------|-------|
| clean_baseline | — | git_status_empty_or_classified_baseline |
| lifecycle_writing | clean_baseline | harness_started |
| artifacts_classifying | lifecycle_writing | harness_finished |
| promotion_required | artifacts_classifying | formal_dirty_detected |
| runtime_quarantined | artifacts_classifying | runtime_private_detected |
| blocked_dirty | artifacts_classifying, promotion_required, runtime_quarantined | unclassified_or_forbidden_or_unpromoted |
| clean_verified | artifacts_classifying, promotion_required, runtime_quarantined | all_dirty_resolved |
| next_stage_allowed | clean_verified | gate_profile_pass |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|----|--------|
| clean_baseline | StageStart | baseline_snapshot_ok | lifecycle_writing | record_pre_snapshot |
| lifecycle_writing | StageExit | command_completed | artifacts_classifying | collect_git_status |
| artifacts_classifying | ClassifyDirty | role_known | promotion_required | emit_required_actions |
| artifacts_classifying | ClassifyRuntime | runtime_private | runtime_quarantined | ignore_or_digest |
| artifacts_classifying | UnknownDirty | role_missing | blocked_dirty | reason=workspace_dirty_unclassified |
| promotion_required | PromoteEvidence | tracked_hash_valid | clean_verified | update_formal_manifest |
| runtime_quarantined | RuntimeAllowed | ignored_or_digest_promoted | clean_verified | record_runtime_manifest |
| clean_verified | ContinueLifecycle | profile_pass | next_stage_allowed | attach_clean_gate_ref |
| blocked_dirty | RepairApplied | status_rechecked | artifacts_classifying | rerun_gate |

## Illegal transitions

- lifecycle_writing → next_stage_allowed without `verify_clean_workspace`
- unclassified dirty → release_ready
- raw trace → formal evidence without digest/redaction pass
- local hook evidence → QA/release verdict authority
- `[x] evidence=PATH` while PATH untracked or missing
- `[ ] evidence=PATH` while PATH exists and is unclassified
- post-release local install → original root dirty tracked files
- skip-worktree-hidden dirty → clean proof
- clean-workspace pass → automatic release pass

## Deferral Ledger

| Deferral ID | Capability | Reason | User Decision | Impact |
|-------------|------------|--------|---------------|--------|
| D-WC-001 | historical evidence full privacy audit | separate large audit lake | accepted defer | no impact on new lifecycle gate |
| D-WC-002 | cross-machine distributed workspace lease | operational concern beyond local clean exit | accepted defer | local proof remains required |
| D-WC-003 | UI for per-project projection policy | CLI policy is enough for R1 | accepted defer | no impact on enforcement |

## Non-goals

- 不自动确认 release。
- 不删除历史证据。
- 不把 `.beacon/traces` 原文作为默认正式证据。
- 不用 skip-worktree 替代治理检查。
- 不允许旧 package 形状绕过 v1.6.10 gate。
- 不改变 implement 必须 workspace admit 的规则。

## Downstream Routes

- implement: `beacon/utils/workspace_clean.py`、doctor CLI、post-release hook 隔离、agent_trace redline、evidence manifest 分类、pre-push profile
- qa: workspace clean profile 回归、task evidence promotion、trace redaction、post-release root clean
- release: human gate + clean-workspace advisory hardening

## Freeze readiness R1

- [x] Intent Matrix must 无 missing。
- [x] 用户旅程、first principles、Domain Model、FSM 五元组与 illegal 已写满。
- [x] 每 AC 可映射到 tests.md 的 Command+Assertion。
- [x] domain 湖含 exec-layer TC。
- [x] Deferral Ledger 全部为 accepted defer。
- [x] package_maturity: filled。
- [x] Truth Review Gate pass，R1 已 freeze。
