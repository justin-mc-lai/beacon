# 证据：Beacon v2 Rust Kernel Redesign

## 证据索引

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| source-plan | support_advisory | docs/plans/beacon-v2-redesign.md | indexed | truth.define |
| planner-research | support_advisory | docs/beacon/archive/v2.0.0/research/beacon-v2-rust-kernel-redesign.md | promoted | truth.define |
| feature-package-truth | requirement_truth | docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md | **frozen R18** scenario completeness | truth.change |
| v16-pln-review-runtime | support_advisory | docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md | **frozen** upstream | P2 |
| v16-truth-integrity-gates | support_advisory | docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md | **frozen** upstream | P3 |
| planner-review-r2 | support_advisory | conversation: beacon-pln-review option-A | accepted-for-truth | truth.define |
| planner-review-r8 | support_advisory | conversation: v2 minimal Rust harness kernel, six first-class abilities, no v1 Python compat | accepted-for-truth | truth.define |
| planner-review-r9 | support_advisory | conversation: v2 skill surface progressive disclosure, branch governance retained, harness contracts retained | accepted-for-truth | truth.define |
| planner-review-r10 | support_advisory | conversation: v1.6.6 trace/stagnation/remediation closure gap; TraceSpine authority; canonical truth branch requirement | accepted-for-truth | truth.define |
| planner-review-r11 | support_advisory | conversation: standardize canonical main refreeze -> feature merge -> governance verify -> workspace admission -> implement resume as Beacon Standard Execution Flow | accepted-for-truth | truth.define |
| planner-review-r14 | support_advisory | conversation: materialize v2 Rust program orchestration, promote stash intent to canonical program surface, repair revision projection drift | accepted-for-truth | truth.define |
| package-tests | test_truth | docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md | task-intent-indexed | generate |
| package-evidence | support_advisory | docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md | evidence-indexed | evaluate |
| program-manifest | requirement_truth | docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-manifest.md | canonical-program-surface | truth.define |
| program-phase-graph | requirement_truth | docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/phase-graph.md | canonical-program-surface | truth.define |
| program-admission-gates | requirement_truth | docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/admission-gates.md | canonical-program-surface | truth.define |
| program-run-state | requirement_truth | docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-run-state.json | canonical-program-state | truth.define |
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
- **R10 change/refreeze intent（2026-07-15）**：用户确认 v1.6.6 的 trace/stagnation/remediation 不能停留在 advisory/report_only；v2 必须把 `TraceSpine.v1` 作为 run authority，并把 loop/implement/qa-evidence/release gate 绑定 trace completeness。
- **R10 branch governance decision（2026-07-15）**：用户确认需求真相唯一来源应为 canonical truth branch（main，缺失时 master）；feature/dev branch 只能合入并消费 main/master 已冻结 truth，不能本地 bump requirement revision。
- **R11 standard execution flow（2026-07-15）**：用户确认把已跑通的 main canonical refreeze、canonical commit、feature worktree stale refreeze quarantine、merge main、truth/materials/branch verification、workspace admission、implement resume 固化为 Beacon 标准执行流程。
- **R14 program orchestration surface（2026-07-15）**：用户确认继续 v2 Rust program 编排；将 stash 中 `v2-0-0-rust` P0 intent capture 升级为 main canonical program surface，补 phase graph、lake slices、admission gates、run-state，并要求修复 R12/R13 machine/human projection 漂移后再进入 implement。
- **R15 dual-track + unified skill score（2026-07-16）**：用户确认 **选项 B 长期双轨**；**统一 skill 评分进入 v2.0.0 合同且可用于 v1**；**只评分、人改**。废止「P6 切默认即退休 v1」叙事；保留 v2 路径内禁止 cross-track fallback。Planner runtime：`pln-review-20260716t024005z`。
- **R18 scenario completeness（2026-07-16）**：用户确认按 `beacon-gen-change` 将 comprehensive-thinking 产出的 S-01..S-19 **高优子集**写入 AC-157–173 / TC-157–173 / TC-N27–N40；覆盖双轨写域、archive 面、scaffold/schema、弱 TC 禁独过、GitScopeGraph 拓扑、skill-score 操作化。已 refreeze 为 frozen R18。

## Implementation Candidate Evidence

| Phase | 预期证据路径 | 状态 |
|-------|--------------|------|
| P0 | packages/beacon-rs/beacon-core, beacon-store + unit tests | 历史候选已完成（2026-06-13）；R8 five-crate/no-python 重新验证仍需执行 |
| P0 admission | docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/* + TC-145 | program surface materialized; implementation admission still pending |
| P1 | beacon-cli spine/projects + TC-016–020 | not_started |
| P2 | beacon-orchestrator + TraceSpine/TraceContext + canonical truth branch gate + standard execution flow admission bundle | not_started |
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

**无** — truth 已由当前 refreeze transaction 冻结；TraceSpine/canonical truth branch/standard execution flow implementation/QA/release closure 尚未裁决。formal closure 仅由 `beacon-eval-qa` / `beacon-eval-release` 产出。

## Implement + contract QA (2026-07-18)

- Product Goal run: `pgr-51a763f2a691`
- Suite: `python3 -m pytest tests/test_v200_*.py` → **90 passed**
- Scorecard: `.beacon/qa/features/v2-0-0-full-delivery/scorecard.json`
- Release: **human gate** (not auto-confirmed)
- Open: full Rust kernel P1/P2/carrier (track_v2); W4 default BEACON_V2 still forbidden

## Deep implement slice (2026-07-18)

Rust kernel deep work landed (not full P3/P6 closure):

- `beacon-core`: TraceSpine.v1 + TraceContext hash chain; HarnessSurface six abilities; dual_track isolation
- `beacon-orchestrator`: CodexBackend multi-turn (≥2 + artifact_refs); GoalController create/status/resume/stop; skill_load_plan.v1
- `beacon-gate`: reason_codes parse; dual-track gate; release human invariant; trace completeness gate
- `beacon-cli` (`beacon-v2`): harness list, goal run/status/stop, dual-track check, skill-load
- `beacon-python`: **ARCHIVE_ONLY** marker (no PyO3 runtime fallback)
- Docs: `docs/beacon/v2.0.0/execution/dual-track-isolation.md`
- Tests: `cargo test --workspace` green (incl. p2_codex_goal, trace_and_track, archive_only)

Still open: full P2-007..023 (TraceSpine hard gates in implement path, BranchContext, standard execution flow machine), P3 Claude/ACP/worktree, P4 CI matrix / legacy removal, P6 default switch.

## TraceSpine hard gates + BranchContext/admission (2026-07-18)

- `beacon-core/branch_context.rs`, enhanced `trace_spine.rs` (bindings + authority_gate)
- `beacon-gate/harness_trace_gate.rs` — implement/qa-evidence/release fail-closed
- `beacon-orchestrator/workspace_admission.rs`, `standard_flow.rs`, `harness_path.rs`
- CLI: `beacon-v2 workspace admit | flow stages|verify | trace check`
- `cargo test --workspace` green incl. `p2_trace_branch_flow` (13 tests)

## Goal closure pgr-ee700a59d76b (2026-07-18)

- Python: `pytest tests/test_v200_*.py` → **95 passed**
- Rust: `cargo test --workspace` → green (incl. p2_trace_branch_flow 13 + p2_closure_slice 8)
- Scorecard: `.beacon/qa/features/v2-0-0-full-delivery/scorecard.json`
- Goal status: **completed** (verifier attached); **release_human_gate=true**
- New: git BranchContext (`--git`), decision_packet/intent, stagnation, refreeze guards, harness boundary, checkpoints, reason-codes/storage-authority docs, route-examples

## Kernel closure program mount (2026-07-19)

- Program: `docs/beacon/v2.0.0/programs/loom-kernel-closure-w1w5-v200/`
- Lakes W1–W5 frozen as separate packages (AC-099/100/105/106/101/103/166/167/171-173/169)
- Implement order: W1→W2→W3→(W4a∥W4b)→W5
- Change: `docs/beacon/v2.0.0/change/loom-kernel-closure-w1w5-v200.md`

- **W1 implement (2026-07-19T11:41:18Z)**: `loom-git-worktree-implement-harness` code landed — real git worktree + ImplementHarnessBackend; cargo test w1_worktree_implement_harness 5 passed (AC-099/100/042). W2–W5 still frozen pending implement.
- **W1–W5 kernel closure implement (2026-07-19T11:55:39Z)**: lakes loom-*-w1w5 code+integration tests landed (worktree/harness, external stop_when, TIG, adversarial release, gitscope, skill-score corpus). Not P6 default switch.
