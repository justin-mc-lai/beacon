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

## Loop-goal P0 progress (2026-07-16)

- run_id: `lg-c9924966448c`
- standard_execution_precheck: pass
- workspace admission: pass
- topology_gate: pass (single_repo)
- P0 action: removed `beacon-python` from workspace members; crate archived under `packages/beacon-rs/_archive/beacon-python`
- verification: `cd packages/beacon-rs && cargo test --workspace` → all suites ok (5 core crates)
- remaining: schema 8 vs 9 decision (AC-161), dual-track writer lease (AC-158), full phase delivery P1–P6, QA/release human gate

## Loop-goal P0/P1 progress (2026-07-16 continue)

- run_id: `lg-c9924966448c`
- **AC-161 path (a)**: SCHEMA_VERSION=2 nine-table contract closed
  - ADR: `docs/beacon/v2.0.0/execution/adr-schema-v2-nine-table-contract.md`
  - tables: projects, project_versions, feature_packages, feature_lifecycle, runs, lifecycle_events, gate_results, artifact_refs, checkpoints
  - tests: `tc161_schema_contract_nine_tables_present`, `tc068_project_versions_ensured_on_feature_insert`, `tc075_checkpoints_write_and_read`
- **P1 Spine/projects**: existing AC-017/018/019/021/085 store+CLI tests remain green under V2 schema
- verification: `cd packages/beacon-rs && cargo test --workspace` → pass
- remaining: AC-158 dual-track writer lease, full P2+ orchestrator/gate parity, QA/release
