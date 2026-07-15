# 任务：Beacon v2 Rust Kernel Redesign（r8）

## Phase P0 — core + store 骨架（AC-022–031, AC-067–076, AC-084, AC-024）

- [ ] TASK-P0-001-R8 收敛 `packages/beacon-rs/` workspace 为 v2 core 五 crate（core/store/orchestrator/gate/cli），移除或 archive-only 标记 `beacon-python`。
- [x] TASK-P0-002 Diagram Truth Layer 类型：WorkflowStage（含 Prototype）、StageStatus（含 Crashed/TimedOut/Interrupted）、Delivery 运行时 enum + plan 链 event_type 常量。
- [x] TASK-P0-003 `IterationResult` 与 `AgentBackend` trait 类型定义（beacon-core）。
- [x] TASK-P0-004 schema v1 九表 + WAL + 六 DAO skeleton。
- [x] TASK-P0-005 migration **skeleton**（user_version、备份钩子）；**非** production 全量迁移。
- [x] TASK-P0-006 unit：TC-026–031, TC-067–076, TC-084。

## Phase P1 — Spine + projects（AC-017–021, AC-081–083, AC-064–065, AC-085）

- [ ] TASK-P1-001 spine show/list/artifacts/gate + SpineSnapshot JSON schema。
- [ ] TASK-P1-002 projects register/list/show。
- [ ] TASK-P1-003 reason-codes.md + storage-authority.md；TC-066 预备。
- [ ] TASK-P1-004 plan↔package drift 脚本（TC-098）。

## Phase P2 — orchestrator MVP + codex/subprocess 真集成（AC-040–044, AC-047–050, AC-086）

- [ ] TASK-P2-001 run goal/resume/stop/status + truth-map preflight。
- [ ] TASK-P2-002 **CodexBackend 真多轮**（AC-043 / TC-043）：≥2 iterate，artifact_refs 写入，禁 fixture 单次。
- [ ] TASK-P2-003 **SubprocessBackend 真一轮**（AC-044 / TC-044）。
- [ ] TASK-P2-004 checkpoints + stop_when + graceful/force stop。
- [ ] TASK-P2-005 phase controller metadata + lifecycle_events。
- [ ] TASK-P2-006 integration：TC-040–041, TC-043–044, TC-047–050, TC-086。
- [ ] TASK-P2-007 **planner_review multi-agent runtime**（AC-102 / TC-102）：Rust orchestrator 调用 v1.6 同构 artifact（lanes/synthesis/fallback）；artifact_refs 持久化。
- [ ] TASK-P2-008 `intent_snapshot.v1` + prompt snapshot ledger + low-confidence freeze block（AC-111–113）。
- [ ] TASK-P2-009 `decision_packet.v1` loop admission（AC-114）。
- [ ] TASK-P2-010 loop guardrails：pattern registry、failure catalog、token budget、readiness audit、protected path denylist（AC-120）。
- [ ] TASK-P2-011 `agent_trace.v1` writer + stagnation detector（AC-117–118）。

## Phase P3 — gate + migration + claude/acp/worktree/implement 真集成（AC-045–046, AC-099–100, AC-077–079, AC-011, AC-087, **AC-101, AC-103**）

- [ ] TASK-P3-001 gate 写 `gate_results` + reason_codes 集成测试（TC-066）。
- [ ] TASK-P3-002 **ClaudeBackend 真 integration**（AC-045 / TC-045）：iterate + health_check + abort。
- [ ] TASK-P3-003 **AcpBackend 真 integration**（AC-046 / TC-046）：`acp:<target>` 一轮。
- [ ] TASK-P3-004 **worktree 全模式 parity**（AC-099 / TC-099）：worktree/current-branch/run-branch + 非法组合 fail-closed。
- [ ] TASK-P3-005 **ImplementHarnessBackend 真 integration**（AC-100 / TC-100）：worktree 内 implement harness 一轮。
- [ ] TASK-P3-006 全量 migration + **projection rebuild**（AC-011 / TC-011）。
- [ ] TASK-P3-007 单一写者 + migration 备份。
- [ ] TASK-P3-008 integration：TC-045–046, TC-099–100, TC-077–079, TC-087, TC-011。
- [ ] TASK-P3-009 **TIG port**（AC-101 / TC-101）：freeze/refreeze hard block；frozen 历史 audit_only。
- [ ] TASK-P3-010 **verify-truth-integrity v2 路由**（AC-103 / TC-103）。
- [ ] TASK-P3-011 `design_primitives.v1` binding + design_required implement gate（AC-115–116）。
- [ ] TASK-P3-012 remediation sandbox overlay/eval/rollback + human review report（AC-119）。
- [ ] TASK-P3-013 qa-evidence confidence_chain + business FSM coverage + defect repair regression chain（AC-121–122）。
- [ ] TASK-P3-014 non-behavior evidence rejection + release human gate invariant（AC-123–124）。

## Phase P4 — 六能力 harness surface + legacy removal（AC-002–003, AC-059–063, AC-088, AC-091, AC-094, AC-109–110）

- [ ] TASK-P4-001 删除 v2 core 的 PyO3/python runtime fallback；legacy invocation 只给 migration/archive route（TC-002/003/062）。
- [ ] TASK-P4-002 `beacon harness list --version v2.0.0 --json` 精确暴露六能力 contract（TC-059/063/109）。
- [ ] TASK-P4-003 CI matrix 覆盖 five-crate Rust workspace + legacy removal regression（TC-091/110）。
- [ ] TASK-P4-004 integration：TC-059–063, TC-088, TC-094, TC-109–110。

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

## r5 变更摘要（R2 reopen）

- 增补 **AC-101–104**：v1.6 TIG、multi-agent planner review、doctor verify-truth-integrity、P0 完成证据。
- 新增 **v1.6 Upstream Frozen Inputs** 表；tests/tasks 对齐 behavior-level TC。
- 历史 truth 状态：R2 draft；R8 已 refreeze 为 minimal-kernel frozen。

## r3 变更摘要

- **D-V2-001 accepted**：v2.0.0 不做 proto/gRPC；P5 跳过。
- **D-V2-004 rejected**：worktree 全模式纳入 P3（AC-099 / TC-099）。
- **D-V2-005 rejected**：ImplementHarnessBackend 真集成纳入 P3（AC-100 / TC-100）。

## r2 变更摘要

- 删除「contract test 空壳路径」；P2/P3 必须交付 codex/subprocess/claude/acp **真 integration**。
- P0 migration 明确为 skeleton，全量迁移在 P3。

## 边界

truth freeze → implement → evaluator 后才可 closure。
