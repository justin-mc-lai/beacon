# 证据：Beacon v2 Rust Kernel Redesign

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| source-plan | support_advisory | docs/plans/beacon-v2-redesign.md | indexed | truth.define |
| planner-research | support_advisory | docs/beacon/v2.0.0/research/beacon-v2-rust-kernel-redesign.md | promoted | truth.define |
| feature-package-truth | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md | **R9 frozen** | truth.define |
| v16-pln-review-runtime | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | **frozen** upstream | P2 |
| v16-truth-integrity-gates | support_advisory | docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md | **frozen** upstream | P3 |
| planner-review-r2 | support_advisory | conversation: beacon-pln-review option-A | accepted-for-truth | truth.define |
| planner-review-r8 | support_advisory | conversation: v2 minimal Rust harness kernel, six first-class abilities, no v1 Python compat | accepted-for-truth | truth.define |
| planner-review-r9 | support_advisory | conversation: v2 skill surface progressive disclosure, branch governance retained, harness contracts retained | accepted-for-truth | truth.define |
| package-tests | test_truth | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md | evidence-indexed | evaluate |
| v1-runtime-ledger | support_advisory | ~/.beacon/runtime-ledger/runtime-ledger.sqlite3 | migration-source | P3 |
| v1-loop-ledger | support_advisory | <project>/.beacon/loop/ledger/loop-runs.db | migration-source | P3 |
| v1-spine-doc | support_advisory | docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md | semantic-ref | truth.define |
| v134-blueprint | support_advisory | docs/beacon/archive/v1.3.4/execution/architecture-blueprint.md | semantic-ref | truth.define |
| implementation-beacon-rs | support_advisory | packages/beacon-rs/ | historical P0 scaffold; R8 revalidation required | generate |

## 决策记录

- 已采纳：r2 planner review **选项 A（真集成）** — AC-043–046 替代 r1 AC-040 空壳路径。
- 已采纳：Diagram Truth Layer；AC 重编号至 AC-098（r2）；r3 新增 AC-099/100。
- 已废弃为 v2 core closure：PyO3 / v1 Python / 33 skills 全量回归；R8 改为六能力 harness surface（loop/truth/design/implement/qa-evidence/release）。
- 已移除：claude/cursor「contract test 空壳路径」验收。
- **r3 用户 deferral 拍板**：
  - **D-V2-001 accepted** — v2.0.0 不做 `beacon-proto`/gRPC；P5 跳过。
  - **D-V2-004 rejected defer** — worktree 全模式 **in-scope**（AC-099 / TC-099，P3）。
  - **D-V2-005 rejected defer** — ImplementHarnessBackend 真集成 **in-scope**（AC-100 / TC-100，P3）。
- **r3.1 intent snapshot**：User Intent 一行 + Alignment Surface / Phased Backlog 写入 truth。
- **r4 alignment TC hardening**：tests.md 软 TC 收紧；`beacon-gen-truth` Truth Freeze Intent Loop。
- **Round 6–7（2026-06-13）**：research clarity + **frozen R1** `r4-frozen`。
- **R2 reopen（2026-06-13）**：补 AC-101–104（TIG、multi-agent planner review、verify-truth-integrity 路由、P0 done）；upstream v1.6 frozen features 表；去除 tests 页「frozen 阻塞」陈旧表述。
- **R8 refreeze（2026-07-15）**：用户确认 v2 极简 Rust harness kernel；保留 6 个一等能力；完全抛弃 v1 Python 历史兼容；补意图强识别、prompt snapshot、decision_packet、design_primitives gate、agent 排查、v1.6.4–1.6.6 loop/QA/evidence 能力语义迁移。
- **R9 refreeze（2026-07-15）**：用户确认目标是简化 public skill 和加载路径，而不是删除治理能力；补 progressive disclosure package contract、route examples、`BranchContext.v1`、branch governance hard gate、Harness Boundary reason_codes（AC-125–130）。

## Implementation Candidate Evidence

| Phase | 预期证据路径 | 状态 |
|-------|--------------|------|
| P0 | packages/beacon-rs/beacon-core, beacon-store + unit tests | 历史候选已完成（2026-06-13）；R8 five-crate/no-python 重新验证仍需执行 |
| P1 | beacon-cli spine/projects + TC-016–020 | not_started |
| P2 | beacon-orchestrator + run logs in artifact_refs | not_started |
| P3 | migration reports under ~/.beacon/migrations/ | not_started |
| P4 | six-ability harness surface + progressive disclosure + legacy removal regression | not_started |
| P6 | benchmark JSON + qa closure JSON | not_started |

### P0 verification (2026-06-13)

```bash
cd packages/beacon-rs && cargo test --workspace
# 12 tests passed (beacon-core transition/agent + TC-026; beacon-store TC-031/067-076/084/075)
```

Deliverables (historical candidate, superseded by R8 minimal-kernel closure where noted):
- Workspace: `packages/beacon-rs/Cargo.toml` — originally six crates (core, store, orchestrator, gate, cli, python); R8 requires five core crates and removal/archive-only treatment for python.
- `beacon-core`: WorkflowStage, StageStatus, RunStatus (12), LifecycleEventType, transition guards, IterationResult, AgentBackend
- `beacon-store`: schema v1 (9 tables), WAL, Project/Feature/Run/Gate/Artifact/Spine DAOs, migration skeleton + backup hook
- Stubs: orchestrator, gate, cli, python (historical scaffold; python no longer counts toward AC-022 closure)

## QA / Release Verdict

**无** — truth **R9 frozen**；R9 implementation/QA/release closure 尚未裁决。formal closure 仅由 `beacon-eval-qa` / `beacon-eval-release` 产出。
