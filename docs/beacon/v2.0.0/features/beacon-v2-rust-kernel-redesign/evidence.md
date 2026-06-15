# 证据：Beacon v2 Rust Kernel Redesign

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| source-plan | support_advisory | docs/plans/beacon-v2-redesign.md | indexed | truth.define |
| planner-research | support_advisory | docs/beacon/v2.0.0/research/beacon-v2-rust-kernel-redesign.md | promoted | truth.define |
| feature-package-truth | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md | **R2 draft** (r5) | truth.define |
| v16-pln-review-runtime | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | **frozen** upstream | P2 |
| v16-truth-integrity-gates | support_advisory | docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md | **frozen** upstream | P3 |
| planner-review-r2 | support_advisory | conversation: beacon-pln-review option-A | accepted-for-truth | truth.define |
| package-tests | test_truth | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md | evidence-indexed | evaluate |
| v1-runtime-ledger | support_advisory | ~/.beacon/runtime-ledger/runtime-ledger.sqlite3 | migration-source | P3 |
| v1-loop-ledger | support_advisory | <project>/.beacon/loop/ledger/loop-runs.db | migration-source | P3 |
| v1-spine-doc | support_advisory | docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md | semantic-ref | truth.define |
| v134-blueprint | support_advisory | docs/beacon/archive/v1.3.4/execution/architecture-blueprint.md | semantic-ref | truth.define |
| implementation-beacon-rs | support_advisory | packages/beacon-rs/ | **P0 scaffolded** | generate |

## 决策记录

- 已采纳：r2 planner review **选项 A（真集成）** — AC-043–046 替代 r1 AC-040 空壳路径。
- 已采纳：Diagram Truth Layer；AC 重编号至 AC-098（r2）；r3 新增 AC-099/100。
- 已采纳：33 skills **全量**回归（AC-063），非抽样。
- 已移除：claude/cursor「contract test 空壳路径」验收。
- **r3 用户 deferral 拍板**：
  - **D-V2-001 accepted** — v2.0.0 不做 `beacon-proto`/gRPC；P5 跳过。
  - **D-V2-004 rejected defer** — worktree 全模式 **in-scope**（AC-099 / TC-099，P3）。
  - **D-V2-005 rejected defer** — ImplementHarnessBackend 真集成 **in-scope**（AC-100 / TC-100，P3）。
- **r3.1 intent snapshot**：User Intent 一行 + Alignment Surface / Phased Backlog 写入 truth。
- **r4 alignment TC hardening**：tests.md 软 TC 收紧；`beacon-gen-truth` Truth Freeze Intent Loop。
- **Round 6–7（2026-06-13）**：research clarity + **frozen R1** `r4-frozen`。
- **R2 reopen（2026-06-13）**：补 AC-101–104（TIG、multi-agent planner review、verify-truth-integrity 路由、P0 done）；upstream v1.6 frozen features 表；去除 tests 页「frozen 阻塞」陈旧表述。

## Implementation Candidate Evidence

| Phase | 预期证据路径 | 状态 |
|-------|--------------|------|
| P0 | packages/beacon-rs/beacon-core, beacon-store + unit tests | **done (2026-06-13)** |
| P1 | beacon-cli spine/projects + TC-016–020 | not_started |
| P2 | beacon-orchestrator + run logs in artifact_refs | not_started |
| P3 | migration reports under ~/.beacon/migrations/ | not_started |
| P4 | wheel + skill smoke log | not_started |
| P6 | benchmark JSON + qa closure JSON | not_started |

### P0 verification (2026-06-13)

```bash
cd packages/beacon-rs && cargo test --workspace
# 12 tests passed (beacon-core transition/agent + TC-026; beacon-store TC-031/067-076/084/075)
```

Deliverables:
- Workspace: `packages/beacon-rs/Cargo.toml` — six crates (core, store, orchestrator, gate, cli, python)
- `beacon-core`: WorkflowStage, StageStatus, RunStatus (12), LifecycleEventType, transition guards, IterationResult, AgentBackend
- `beacon-store`: schema v1 (9 tables), WAL, Project/Feature/Run/Gate/Artifact/Spine DAOs, migration skeleton + backup hook
- Stubs: orchestrator, gate, cli, python (AC-022 workspace membership)

## QA / Release Verdict

**无** — truth **R2 draft**；P0 实现证据见上表。formal closure 仅由 `beacon-eval-qa` / `beacon-eval-release` 产出。
