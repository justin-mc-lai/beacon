# 任务：Beacon v2 Rust Kernel Redesign（r15）

## Phase P0 — core + store 骨架（AC-022–031, AC-067–076, AC-084, AC-024）

- [x] TASK-P0-000-R14 materialize `v2-0-0-rust` program surface：manifest、phase graph、lake slices、admission gates、run-state；实现前必须由 TC-145 验证。
- [x] TASK-P0-001-R8 收敛 `packages/beacon-rs/` workspace 为 v2 core 五 crate（core/store/orchestrator/gate/cli），移除或 archive-only 标记 `beacon-python`（**不**因此删除 v1 Python 产品轨）。
- [x] TASK-P0-002 Diagram Truth Layer 类型：WorkflowStage（含 Prototype）、StageStatus（含 Crashed/TimedOut/Interrupted）、Delivery 运行时 enum + plan 链 event_type 常量。
- [x] TASK-P0-003 `IterationResult` 与 `AgentBackend` trait 类型定义（beacon-core）。
- [x] TASK-P0-004 schema v1 九表 + WAL + 六 DAO skeleton。
- [x] TASK-P0-005 migration **skeleton**（user_version、备份钩子）；**非** production 全量迁移。
- [x] TASK-P0-006 unit：TC-026–031, TC-067–076, TC-084。

## Phase P4 / Cross-cutting — Dual-track + Unified skill score（AC-147–156, AC-003/060/062/110）

- [x] TASK-R15-001 双轨隔离契约文档 + CI path filters：`track_v1` vs `track_v2`；混改无 admission → `dual_track_mixed_source`（TC-148）。
- [x] TASK-R15-002 显式 runtime 选择面（`beacon-v2` 或 `--runtime v2`）；更新 AC-060/TC-060b（TC-149）。
- [x] TASK-R15-003 v2 路径 cross-track fallback fail-closed（TC-062b）；确认 v1 路径仍可调用 v1 skills。
- [ ] TASK-R15-004 统一 skill-score schema（结构+实效）；映射现有 `beacon eval` 维度；权威 `runtime_evidence_only`（TC-151–153, TC-156）。
- [ ] TASK-R15-005 score-only human-edit：CLI/skill 禁止自动改 SKILL.md；独立评分与修改建议分离（TC-154–155, TC-N24）。
- [ ] TASK-R15-006 v1 与 v2 各至少一套可比 score fixture（37 面抽样 + 六 public）。

## Phase P1 — Spine + projects（AC-017–021, AC-081–083, AC-064–065, AC-085）

- [x] TASK-P1-001 spine show/list/artifacts/gate + SpineSnapshot JSON schema。
- [x] TASK-P1-002 projects register/list/show。
- [x] TASK-P1-003 reason-codes.md + storage-authority.md；TC-066 预备。
- [ ] TASK-P1-004 plan↔package drift 脚本（TC-098）。

## Phase P2 — orchestrator MVP + codex/subprocess 真集成（AC-040–044, AC-047–050, AC-086）

- [x] TASK-P2-001 run goal/resume/stop/status + truth-map preflight。
- [x] TASK-P2-002 **CodexBackend 真多轮**（AC-043 / TC-043）：≥2 iterate，artifact_refs 写入，禁 fixture 单次。
- [x] TASK-P2-003 **SubprocessBackend 真一轮**（AC-044 / TC-044）。
- [x] TASK-P2-004 checkpoints + stop_when + graceful/force stop。
- [x] TASK-P2-005 phase controller metadata + lifecycle_events。
- [x] TASK-P2-006 integration：TC-040–041, TC-043–044, TC-047–050, TC-086。
- [ ] TASK-P2-007 **planner_review multi-agent runtime**（AC-102 / TC-102）：Rust orchestrator 调用 v1.6 同构 artifact（lanes/synthesis/fallback）；artifact_refs 持久化。
- [x] TASK-P2-008 `intent_snapshot.v1` + prompt snapshot ledger + low-confidence freeze block（AC-111–113）。
- [x] TASK-P2-009 `decision_packet.v1` loop admission（AC-114）。
- [ ] TASK-P2-010 loop guardrails：pattern registry、failure catalog、token budget、readiness audit、protected path denylist（AC-120）。
- [x] TASK-P2-011 `agent_trace.v1` writer + stagnation detector（AC-117–118）。
- [x] TASK-P2-012 progressive disclosure loader：产出 `skill_load_plan.v1`，按 topic 加载 public SKILL + selected references/examples，禁止加载全部历史 skill（AC-126 / TC-126）。
- [x] TASK-P2-013 route examples registry：覆盖 decision_packet、design_primitives、qa-release、branch-blocked 示例，标注 example 非 truth authority（AC-127 / TC-127）。
- [x] TASK-P2-014 `BranchContext.v1` schema + workspace admission 输出：caller cwd / target root / admitted worktree / branch / dirty policy / protected paths（AC-128 / TC-128）。
- [x] TASK-P2-015 harness boundary reason_codes：planner/truth/implement/qa-evidence/release/loop 越界 fixture fail-closed（AC-130 / TC-130）。
- [x] TASK-P2-016 `TraceSpine.v1` + `TraceContext.v1` kernel authority：loop start 创建 append-only trace，绑定 BranchContext / decision_packet / intent_snapshot / truth_hash / design_primitives（AC-131–132 / TC-131–132）。
- [x] TASK-P2-017 trace completeness hard gate：implement、qa-evidence、release 均验证 trace missing / append failure / hash chain invalid / event-to-evidence 断链（AC-133 / TC-133）。
- [x] TASK-P2-018 canonical truth branch hard gate：truth/change/refreeze 只能在 main/master 写入；feature/dev worktree 只能消费 canonical frozen truth（AC-136 / TC-136）。
- [x] TASK-P2-019 empty/drift refreeze guard：reason-only、machine-only refreeze 和 revision narrative drift 均 fail-closed（AC-137 / TC-137）。
- [x] TASK-P2-020 Standard Execution Flow state machine：实现 support_advisory -> canonical_truth_authoring -> canonical_refreeze -> canonical_commit -> feature_worktree_reconcile -> governance_verify -> workspace_admission -> implement_resume 顺序校验（AC-138 / TC-138）。
- [x] TASK-P2-021 canonical baseline commit gate：refreeze complete 后必须提交 canonical branch 并生成 `truth_baseline_commit`，feature branch implement admission 验证该 commit 已合入（AC-139, AC-141 / TC-139, TC-141）。
- [x] TASK-P2-022 stale feature-local refreeze quarantine：feature worktree 合入 main 前检测 `.machine` revision/projection dirty，要求 scoped stash/archive artifact，不得采信本地 bump（AC-140 / TC-140）。
- [x] TASK-P2-023 standard flow admission bundle：汇总 truth-map verify、verify-materials strict、diff check、branch-governance verify、workspace admission 为可引用 bundle，并支持 idempotent resume（AC-142–143 / TC-142–143）。

## Phase P3 — gate + migration + claude/acp/worktree/implement 真集成（AC-045–046, AC-099–100, AC-077–079, AC-011, AC-087, **AC-101, AC-103**）

- [ ] TASK-P3-001 gate 写 `gate_results` + reason_codes 集成测试（TC-066）。
- [x] TASK-P3-002 **ClaudeBackend 真 integration**（AC-045 / TC-045）：iterate + health_check + abort。
- [x] TASK-P3-003 **AcpBackend 真 integration**（AC-046 / TC-046）：`acp:<target>` 一轮。
- [x] TASK-P3-004 **worktree 全模式 parity**（AC-099 / TC-099）：worktree/current-branch/run-branch + 非法组合 fail-closed。
- [x] TASK-P3-005 **ImplementHarnessBackend 真 integration**（AC-100 / TC-100）：worktree 内 implement harness 一轮。
- [ ] TASK-P3-006 全量 migration + **projection rebuild**（AC-011 / TC-011）。
- [ ] TASK-P3-007 单一写者 + migration 备份。
- [ ] TASK-P3-008 integration：TC-045–046, TC-099–100, TC-077–079, TC-087, TC-011。
- [ ] TASK-P3-009 **TIG port**（AC-101 / TC-101）：freeze/refreeze hard block；frozen 历史 audit_only。
- [ ] TASK-P3-010 **verify-truth-integrity v2 路由**（AC-103 / TC-103）。
- [ ] TASK-P3-011 `design_primitives.v1` binding + design_required implement gate（AC-115–116）。
- [ ] TASK-P3-012 remediation sandbox overlay/eval/rollback + human review report（AC-119）。
- [ ] TASK-P3-013 qa-evidence confidence_chain + business FSM coverage + defect repair regression chain（AC-121–122）。
- [x] TASK-P3-014 non-behavior evidence rejection + release human gate invariant（AC-123–124）。
- [x] TASK-P3-015 branch governance hard gate integration：所有 write/agent/evidence/release harness 消费 `BranchContext.v1`，cwd/root/worktree mismatch 阻断（AC-129 / TC-129）。
- [x] TASK-P3-016 stagnation/remediation trace binding：`stagnation-report.v1` 引用 trace event range；`remediation-report.v1` 引用 stagnation report、overlay/eval/rollback evidence 与 human review decision（AC-134–135 / TC-134–135）。

## Phase P4 — 六能力 harness surface + legacy removal（AC-002–003, AC-059–063, AC-088, AC-091, AC-094, AC-109–110, AC-125）

- [x] TASK-P4-001 删除 v2 core 的 PyO3/python runtime fallback；legacy invocation 只给 migration/archive route（TC-002/003/062）。
- [x] TASK-P4-002 `beacon harness list --version v2.0.0 --json` 精确暴露六能力 contract（TC-059/063/109）。
- [ ] TASK-P4-003 CI matrix 覆盖 five-crate Rust workspace + legacy removal regression（TC-091/110）。
- [x] TASK-P4-004 public surface denylist：doctor/router/hooks/metadata/debug/archive 保留 internal module，但不得出现在 v2 host-visible 一等 skill list（AC-125 / TC-125）。
- [x] TASK-P4-005 standard-flow progressive examples：通过 loop/truth/implement/qa-evidence/release examples 暴露标准执行流，不新增第七个 public skill（AC-144 / TC-144）。
- [x] TASK-P4-005 integration：TC-059–063, TC-088, TC-094, TC-109–110, TC-125。

## Phase P5 — proto（v2.0.0 跳过，D-V2-001 accepted defer）

- [x] TASK-P5-001 **不实施**：`beacon-proto`/gRPC 推迟至 post-v2.0.0；TC-089 以 deferral 记录验收。

## Phase P6 — 切换 + benchmark（AC-051–058, AC-090, AC-095–097）

- [ ] TASK-P6-001 criterion bench 套件 + baseline（TC-051–058, TC-095）。
- [ ] TASK-P6-002 默认 Rust v2 路径；v1 JSON 只读迁移，不作为 runtime fallback。
- [ ] TASK-P6-003 E2E TC-E01–E04；evaluator 全矩阵。

## r8 变更摘要（minimal kernel refreeze）

- v2 core closure 移除 v1 Python/PyO3/33 skills 兼容目标，改为 six first-class harness abilities。
- 新增 AC-109–124 对应任务：intent snapshot、prompt ledger、decision packet、design primitives gate、agent trace、stagnation detector、remediation sandbox、loop guardrails、QA evidence chain、release human gate。
- 历史 P0 scaffold 证据保留为 implementation candidate，不再单独满足 R8 minimal-kernel closure。

## r9 变更摘要（skill surface progressive disclosure）

- 新增 AC-125–130 对应任务：六 public skill surface、progressive disclosure loader、route examples registry、BranchContext.v1、branch governance hard gate、harness boundary reason_codes。
- 明确 branch/workspace governance、doctor、router、hooks、metadata、status、archive、debug 保留为 kernel internal module，不作为 v2 host-visible 一等 skill。
- 实现任务必须证明减负发生在使用者入口和加载路径上，而不是删除证据交付、分支治理或 harness 规范。

## TraceSpine 变更摘要（canonical truth branch）

- 新增 AC-131–137 对应任务：TraceSpine authority、TraceContext binding、trace completeness gate、stagnation/remediation trace binding、canonical truth branch、empty/drift refreeze guard。
- 明确 v1.6.6 trace/stagnation/remediation 不能以 advisory signal 形式迁移到 v2；v2 必须把 TraceSpine 作为 loop/implement/qa-evidence/release 的共同 kernel authority。
- 明确需求真相只能在 main/master canonical truth branch 编写、冻结、提交，再由 feature/dev branch 合入消费；feature worktree 不得本地 bump requirement revision。
- 新增 AC-138–144 对应任务：Standard Execution Flow 状态机、canonical baseline commit gate、stale feature-local refreeze quarantine、verification/admission bundle、idempotent resume、progressive examples 暴露。

## r14 变更摘要（program orchestration surface）

- 将 stash 中的 `v2-0-0-rust` P0 intent capture 升级为 main canonical program surface。
- 新增 program manifest、phase graph、admission gates 与 run-state，明确海级 program 拆成 P0/P1/P2/P3/P4/P6 湖级 slices。
- 新增 TC-145/TC-146：program surface 存在性与 revision projection 对齐；阻断 stash-only intent、reason-only refreeze 与 machine-only bump。
- 实现前必须先完成 canonical commit、feature worktree reconcile、governance verify 与 workspace admission；program admission 不等于 QA/release verdict。

## r5 变更摘要（R2 reopen）

- 增补 **AC-101–104**：v1.6 TIG、multi-agent planner review、doctor verify-truth-integrity、P0 完成证据。
- 新增 **v1.6 Upstream Frozen Inputs** 表；tests/tasks 对齐 behavior-level TC。
- 历史 truth 状态：R2 draft；R9 已 refreeze 为 skill-surface progressive-disclosure frozen；R10 补 TraceSpine 与 canonical truth branch hard gate；R11 补 Beacon Standard Execution Flow。

## r3 变更摘要

- **D-V2-001 accepted**：v2.0.0 不做 proto/gRPC；P5 跳过。
- **D-V2-004 rejected**：worktree 全模式纳入 P3（AC-099 / TC-099）。
- **D-V2-005 rejected**：ImplementHarnessBackend 真集成纳入 P3（AC-100 / TC-100）。

## r2 变更摘要

- 删除「contract test 空壳路径」；P2/P3 必须交付 codex/subprocess/claude/acp **真 integration**。
- P0 migration 明确为 skeleton，全量迁移在 P3。

## 边界

truth freeze → implement → evaluator 后才可 closure。


## Phase Cross-cutting — R18 Scenario Completeness（AC-157–173）

- [ ] TASK-R18-001 双轨安装/PATH 与显式 runtime 矩阵（AC-157 / TC-157, TC-N27）。
- [ ] TASK-R18-002 全局 DB 按轨写域 / writer lease 与双写检测（AC-158 / TC-158, TC-N28）。
- [ ] TASK-R18-003 archive plane 显式 version 交付策略 + catalog 一致性（AC-159 / TC-159, TC-N29）。
- [ ] TASK-R18-004 移除或 archive-only `beacon-python`；workspace 五 crate 闭环（AC-160 / TC-160, TC-N30）。
- [ ] TASK-R18-005 schema 九表 vs 实现决策闭环 + ADR/refreeze（AC-161 / TC-161, TC-N31）。
- [ ] TASK-R18-006 truth MD golden parity fixtures（中文/表/frontmatter）（AC-162 / TC-162, TC-N32）。
- [ ] TASK-R18-007 phase_exit_only 权威字段 + 禁止 phase 冒充 release（AC-163 / TC-163, TC-N33）。
- [ ] TASK-R18-008 evaluator 弱 TC 检测 `weak_tc_insufficient`（AC-164 / TC-164, TC-N34）。
- [ ] TASK-R18-009 reason_codes_core.v1 ≥20 全量往返（AC-165 / TC-165）。
- [ ] TASK-R18-010 跨轨证据污染阻断（AC-166 / TC-166, TC-N35）。
- [ ] TASK-R18-011 adversarial_review.v1 release 强制点（AC-167 / TC-167, TC-N36）。
- [ ] TASK-R18-012 dual_track_shared_contract 白名单与 CI path filter（AC-168 / TC-168）。
- [ ] TASK-R18-013 skill-score-corpus.v1 + baseline 对照（AC-169 / TC-169, TC-N37）。
- [ ] TASK-R18-014 建议→人改→复评；禁止 auto apply（AC-170 / TC-170, TC-N38）。
- [ ] TASK-R18-015 GitScopeGraph→BranchContext parity loader（AC-171 / TC-171, TC-N39）。
- [ ] TASK-R18-016 single_repo/monorepo/multi_git topology admission fixtures（AC-172 / TC-172）。
- [ ] TASK-R18-017 loop/implement/standard-flow 强制 topology_gate_ref（AC-173 / TC-173, TC-N40）。


## Deep slice note

2026-07-18: partial completion of dual-track/harness/TraceSpine types/Codex multi-turn/GoalController/skill_load/archive-python. TraceSpine *hard gate wiring* into all implement/qa/release paths still open (P2-017+).


## TraceSpine + BranchContext slice (2026-07-18)

A) harness_trace_gate on implement/qa-evidence/release; HarnessPathController.start_loop/enter_phase; CLI `trace check`.
B) BranchContext.v1 + workspace admit; FlowState order machine; AdmissionBundle implement gate; CLI `workspace admit` / `flow verify`.
Tests: p2_trace_branch_flow.rs (13).


## Closure slice 2026-07-18 (beacon-goal pgr-ee700a59d76b)

- git BranchContext probe (`--git`)
- decision_packet + intent_snapshot gates
- stagnation-report.v1 with trace range
- empty/drift refreeze guards
- harness boundary reason codes
- checkpoints graceful/force
- reason-codes.md + storage-authority.md
- route-examples + harness-examples
- cargo test --workspace green; pytest test_v200_* green
- **Deferred**: Claude/ACP live backends, criterion benches, default v2 runtime switch (W4)


## Loom brand + P3 backends (2026-07-19)

- Worktree modes worktree/current-branch/run-branch + illegal combo (AC-099)
- ClaudeBackend / AcpBackend true process iterate + artifact_refs; missing cred BLOCKED:missing_claude_cred
- Full loom-* public skill prefix mirror (content → skills/beacon/*)
- Binary brand name: **loom** (Beacon evolution CLI; not loom-v2)
