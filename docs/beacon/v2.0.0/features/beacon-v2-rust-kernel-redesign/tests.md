---
slug: beacon-v2-rust-kernel-redesign
version: v2.0.0
revision: r5-alignment-tc-hardening
parser_contract: beacon-feature-package-v1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
---

# 测试覆盖：Beacon v2 Rust Kernel Redesign（r5）

## 覆盖说明

- 每个 AC（AC-001..AC-104）至少一行 TC。
- **integration tier** 为 agent 类 AC（AC-043–046, AC-099–100）最低验收等级；禁止仅 contract/空壳验收。
- **禁止非行为级验证列**：单独 `integration`、`目录存在`、`fixture`、`可选` 不算可执行 TC；必须写 **Command + Assertion**（或显式 `BLOCKED:<reason>`）。
- Pass/Fail 由 `beacon-eval-qa` 裁决。

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | unit | `test -d packages/beacon-rs/beacon-core` | Rust workspace |
| AC-002 | TC-002 | unit | `cargo build -p beacon-python` | PyO3 可编译 |
| AC-003 | TC-003 | unit | verbose 仅 fallback 显示 compat_route=python | 新能力优先 Rust |
| AC-004 | TC-004 | contract | `beacon truth-map resolve … --version v2.0.0 --json` | truth package authority |
| AC-005 | TC-005 | unit | schema 无 truth_body 列 | DB 无需求正文 |
| AC-006 | TC-006 | contract | `cargo test -p beacon-store storage_authority_non_supremacy` — spine gate 读 DB；仅改 `.beacon/gate-report.json` 不改变 `beacon spine gate --json`；schema 无 truth_body | QA JSON 非权威 |
| AC-007 | TC-007 | contract | `cargo test -p beacon-store three_layer_separation` — L1=MD resolve；L2=`~/.beacon/beacon.db`；L3=`<project>/.beacon/*` blob；写 truth 正文进 DB → `STORAGE_AUTHORITY_VIOLATION` | 三层分离 |
| AC-008 | TC-008 | contract | `cargo test -p beacon-store per_project_db_forbidden` — register 后不创建 `<project>/.beacon/beacon.db`；Spine 仅读 `BEACON_STORE_PATH` 全局库 | 否决 project db |
| AC-009 | TC-009 | contract | `cargo test -p beacon-store loop_runs_non_authority` — v2 运行时不写 `loop-runs.db`；migration fixture 导入 global 后 ledger 只读 | loop-runs 非权威 |
| AC-010 | TC-010 | unit | hash 不匹配标 stale | artifact stale |
| AC-011 | TC-011 | contract | `beacon doctor projection rebuild` 后 spine 字段一致 | projection rebuild |
| AC-012 | TC-012 | unit | 无 UPDATE API | events append-only |
| AC-013 | TC-013 | unit | qa run 后 count+1 | gate_results 写入 |
| AC-014 | TC-014 | unit | run goal 后有 runs 行 | runs 启动写入 |
| AC-015 | TC-015 | unit | 无 blob 仍返回 lifecycle | Spine DB-first |
| AC-016 | TC-016 | unit | 双写检测 fail | v1 JSON 仅迁移 |
| AC-017 | TC-017 | contract | `beacon spine show --json` | spine show |
| AC-018 | TC-018 | contract | `beacon spine list --json` | spine list |
| AC-019 | TC-019 | contract | `beacon spine artifacts <run-id>` | spine artifacts |
| AC-020 | TC-020 | contract | `beacon spine gate …` | spine gate |
| AC-021 | TC-021 | contract | `beacon projects register --path . --json`; `beacon projects list --json \ | projects |
| AC-022 | TC-022 | unit | `for c in core store orchestrator gate cli python; test -f packages/beacon-rs/beacon-$c/Cargo.toml; done`; `cargo metadata --no-deps \ | 六 crate |
| AC-023 | TC-023 | unit | `cargo tree -p beacon-cli` | 依赖无环 |
| AC-024 | TC-024 | unit | `cargo build -p beacon-cli` 无 gRPC feature；truth 记录 D-V2-001 accepted | 无 proto 硬依赖 |
| AC-025 | TC-025 | unit | wc -l 或 ADR | 500 行 |
| AC-026 | TC-026 | unit | unit 非法值失败 | WorkflowStage enum |
| AC-027 | TC-027 | unit | unit Freeze→Think Err | 非法转换 |
| AC-028 | TC-028 | unit | 必带 reason_codes | Blocked codes |
| AC-029 | TC-029 | unit | 无 deferral id 拒绝 | Skipped deferral |
| AC-030 | TC-030 | unit | lifecycle_events 记录 | Crashed/Timeout |
| AC-031 | TC-031 | unit | CHECK 约束 | runs.status 12 态 |
| AC-032 | TC-032 | unit | IntentCapture 等 event_type | plan 链 events |
| AC-033 | TC-033 | unit | SIGINT vs --force | stop 语义 |
| AC-034 | TC-034 | unit | kind=repair | Repairing artifact |
| AC-035 | TC-035 | unit | 无 import 拒绝 | AwaitingQa 门禁 |
| AC-036 | TC-036 | unit | orchestrator 不能直接 Closed | Closed 门禁 |
| AC-037 | TC-037 | unit | unit 字段 | EvidenceChain |
| AC-038 | TC-038 | unit | EVIDENCE_CHAIN_BROKEN | 断链 |
| AC-039 | TC-039 | contract | `cargo test -p beacon-store migration_v1_chain -- --test fixture_v1_evidence_chain` — lifecycle_events 保留；runs.status 可映射 plan 主链 | v1 链迁移 |
| AC-040 | TC-040 | unit | goal/resume/stop/status | run 子命令 |
| AC-041 | TC-041 | unit | blocked exit != 0 | truth-map preflight |
| AC-043 | TC-043 | integration | `cargo test -p beacon-orchestrator codex_backend_multi_iterate -- --test fixture_codex_two_rounds` | Codex 真多轮 |
| AC-044 | TC-044 | integration | `cargo test -p beacon-orchestrator subprocess_backend_iterate -- --test fixture_subprocess_harness` | Subprocess 真一轮 |
| AC-045 | TC-045 | integration | `cargo test -p beacon-orchestrator claude_backend_iterate`（cred 缺失 → `BLOCKED:missing_claude_cred`） | Claude 真一轮 |
| AC-046 | TC-046 | integration | `cargo test -p beacon-orchestrator acp_backend_iterate -- --target acp:fixture` | ACP 真一轮 |
| AC-047 | TC-047 | unit | lifecycle_events notes_injected | checkpoint notes |
| AC-048 | TC-048 | contract | `cargo test -p beacon-orchestrator stop_when_qa_pass -- --fixture tests/fixtures/stop_when_qa_pass.json` — qa pass 触发早停→`Stopped`；未 pass 继续 iterate | stop_when |
| AC-049 | TC-049 | unit | stdout 无 release_ready | 无 QA verdict |
| AC-050 | TC-050 | unit | metadata phase + events | phase controller |
| AC-051 | TC-051 | unit | p95 < 100ms CI 归档 | 冷启动 bench |
| AC-052 | TC-052 | unit | p95 < 50ms | spine bench |
| AC-053 | TC-053 | unit | p95 < 200ms | resolve bench |
| AC-054 | TC-054 | unit | p95 < 50ms | gate bench |
| AC-055 | TC-055 | unit | p95 < 10ms/file | evidence hash bench |
| AC-056 | TC-056 | contract | `cargo test -p beacon-store migration_duration -- --test fixture_typical_project` — wall time <60s；超时 test fail | migration 时长 |
| AC-057 | TC-057 | unit | bench < 100ms | iteration 调度 |
| AC-058 | TC-058 | unit | 超 500MB 日志 | DB 体积 WARN |
| AC-059 | TC-059 | unit | doctor verify-context | python shim |
| AC-060 | TC-060 | unit | Rust 路径 | BEACON_V2=1 |
| AC-061 | TC-061 | unit | 隔离库 | BEACON_STORE_PATH |
| AC-062 | TC-062 | unit | compat_route=python | compat verbose |
| AC-063 | TC-063 | contract | `beacon skill list` 全量 + 每 skill 路由 smoke | **33 skills 全量** |
| AC-064 | TC-064 | unit | 全子命令 | CLI help snapshot |
| AC-065 | TC-065 | unit | spine/projects/run validate | --json schema |
| AC-066 | TC-066 | unit | 集成：5 codes gate 失败往返 + reason-codes.md | reason_codes |
| AC-067 | TC-067 | unit | CRUD | projects 表 |
| AC-068 | TC-068 | unit | is_current 唯一 | project_versions |
| AC-069 | TC-069 | unit | slug 唯一 | feature_packages |
| AC-070 | TC-070 | unit | 更新 | feature_lifecycle |
| AC-071 | TC-071 | unit | enum CHECK | runs 表 |
| AC-072 | TC-072 | unit | append only | lifecycle_events |
| AC-073 | TC-073 | unit | gate_type+verdict | gate_results |
| AC-074 | TC-074 | unit | hash+abs_path | artifact_refs |
| AC-075 | TC-075 | unit | iteration 单调 | checkpoints |
| AC-076 | TC-076 | unit | unit 公开 API | 六 DAO |
| AC-077 | TC-077 | contract | `cargo test -p beacon-store migration_runtime_ledger -- --test fixture_runtime_ledger` — row count match；checksum 一致 | runtime-ledger 迁移 |
| AC-078 | TC-078 | contract | `cargo test -p beacon-store migration_loop_runs -- --test fixture_loop_runs` — runs 导入 global；源 loop-runs.db 标记 read-only archive | loop-runs 迁移 |
| AC-079 | TC-079 | contract | `cargo test -p beacon-store migration_qa_history` — 有 v1 qa fixture 则 import≥1；无 fixture → `BLOCKED:phase-P3-no-qa-history-fixture`（非 skip） | qa 历史迁移 |
| AC-080 | TC-080 | unit | 降级拒绝 | user_version |
| AC-081 | TC-081 | unit | 字段 == SpineSnapshot | SpineDao snapshot |
| AC-082 | TC-082 | unit | --status | list 过滤 |
| AC-083 | TC-083 | unit | 相对路径 Err | 绝对路径 |
| AC-084 | TC-084 | unit | core+store+skeleton tests | P0 出口 |
| AC-085 | TC-085 | unit | spine+projects | P1 出口 |
| AC-086 | TC-086 | unit | orchestrator+**TC-043/044** | P2 出口 |
| AC-087 | TC-087 | unit | gate+migration+**TC-045/046/099/100** | P3 出口 |
| AC-088 | TC-088 | unit | shim+**TC-063 全 skill** | P4 出口 |
| AC-089 | TC-089 | unit | **D-V2-001 accepted**：deferral ledger 有 accepted 记录；**无** P5 proto job；不阻塞 P6 | P5 跳过 |
| AC-090 | TC-090 | unit | 默认 v2+bench | P6 出口 |
| AC-091 | TC-091 | unit | GHA/job 跑 cargo test beacon-rs | CI matrix |
| AC-092 | TC-092 | unit | 迁移前 copy ledger | migration 备份 |
| AC-093 | TC-093 | contract | `cargo test -p beacon-store single_writer_authority` — DB gate 写入后 legacy JSON 双写被拒；reason_code=`DUAL_WRITE_FORBIDDEN` | 单一写者 |
| AC-094 | TC-094 | unit | 文档+测试 mock fail→doctor | skill fail 路由 |
| AC-095 | TC-095 | unit | regression >10% fail | bench 回退阻断 P6 |
| AC-096 | TC-096 | unit | CI phase jobs | phase smoke |
| AC-097 | TC-097 | unit | beacon qa run 全矩阵 | evaluator closure |
| AC-098 | TC-098 | unit | promote 脚本 | plan drift |
| AC-099 | TC-099 | integration | `cargo test -p beacon-orchestrator e2e_worktree_modes -- --test fixture_worktree_modes` | worktree 全模式 |
| AC-100 | TC-100 | integration | `cargo test -p beacon-orchestrator e2e_worktree_harness -- --test fixture_worktree_implement` | ImplementHarness 真一轮 |
| AC-101 | TC-101 | integration | `cargo test -p beacon-gate tig_freeze_block` | TIG freeze block |
| AC-102 | TC-102 | integration | `cargo test -p beacon-orchestrator planner_review_multi_agent` | planner_review artifact |
| AC-103 | TC-103 | contract | `beacon doctor verify-truth-integrity <feature> --version v2.0.0 --mode block` | verify-truth-integrity v2 |
| AC-104 | TC-104 | unit | `cd packages/beacon-rs && cargo test --workspace` | P0 workspace done |

## Alignment Surface（r4 行为级 — 冻结前必须可验）

与 `truth.md` **Alignment Surface** 对齐；下列 TC 不得回退为空壳验证列。

| 面 | TC | Command / Assertion（摘要） |
|----|-----|---------------------------|
| 全局库 + Spine | TC-017–020, TC-061, TC-081–083 | `beacon spine show\|list\|artifacts\|gate --json` + schema 字段断言 |
| projects registry | TC-021, TC-067–068 | register → list → show；`project_key` / `is_current` 唯一 |
| 三层存储 | TC-005–010, TC-007 | unit/integration：L1 MD / L2 全局 DB / L3 blob；跨层写 truth → fail-closed |
| orchestrator 链 | TC-040–041, TC-047–048, TC-033 | goal/resume/stop/status；preflight blocked exit≠0；stop_when fixture |
| agent 真集成 | TC-043–046, TC-099–100 | 见 Agent 集成节；禁 single-shot / subprocess-only 冒充 |
| gate + migration | TC-011–013, TC-056, TC-066, TC-077–079, TC-093 | rebuild 一致；migration 计时；单写者；双写 fail |
| PyO3 + skills | TC-059, TC-063 | doctor verify + 33 skill 路由 smoke（P4） |

## Agent 集成（选项 A — 重点）

| TC ID | AC | 场景 | 命令 / 验证 | Phase |
|-------|-----|------|-------------|-------|
| TC-042 | AC-042 | AgentBackend trait + IterationResult 类型 | unit: schema 字段齐全；非法 payload 拒收 | P2 |
| TC-043 | AC-043 | Codex 真多轮 | integration: 同一 run ≥2 iterate 或 cap；`artifact_refs` 有 iteration 产物；**禁用** `BEACON_TEST_FIXTURE_SINGLE_SHOT` | P2 |
| TC-044 | AC-044 | Subprocess 真一轮 | integration: harness 命令跑通 1 iteration；输出 JSON 符合 schema | P2 |
| TC-045 | AC-045 | Claude 真一轮 | integration: 1 iteration + health_check + abort；CI 可 skip 若无 API key（须显式 `BLOCKED:missing_claude_cred`） | P3 |
| TC-046 | AC-046 | ACP 真一轮 | integration: `acp:<target>` 1 iteration；schema 与 TC-042 一致 | P3 |
| TC-099 | AC-099 | worktree 全模式 | integration: worktree/current-branch/run-branch 各 1 路径；非法组合 fail-closed；harness cwd == worktree | P3 |
| TC-100 | AC-100 | ImplementHarness 真一轮 | integration: worktree 内 `beacon implement` harness 1 iteration；输出符合 AC-042；**非** subprocess 替身或 zero-assertion integration | P3 |

## 矩阵（全量 AC）

| TC ID | AC | 场景 | 命令 / 验证 | Phase |
|-------|-----|------|-------------|-------|
| TC-001 | AC-001 | Rust workspace | `test -d packages/beacon-rs/beacon-core` | P0 |
| TC-002 | AC-002 | PyO3 可编译 | `cargo build -p beacon-python` | P4 |
| TC-003 | AC-003 | 新能力优先 Rust | verbose 仅 fallback 显示 compat_route=python | P4 |
| TC-004 | AC-004 | truth package authority | `beacon truth-map resolve … --version v2.0.0 --json` | P0 |
| TC-005 | AC-005 | DB 无需求正文 | schema 无 truth_body 列 | P0 |
| TC-006 | AC-006 | QA JSON 非权威 | `cargo test -p beacon-store storage_authority_non_supremacy` — spine gate 读 DB；仅改 `.beacon/gate-report.json` 不改变 `beacon spine gate --json`；schema 无 truth_body | P1 |
| TC-007 | AC-007 | 三层分离 | `cargo test -p beacon-store three_layer_separation` — L1=MD resolve；L2=`~/.beacon/beacon.db`；L3=`<project>/.beacon/*` blob；写 truth 正文进 DB → `STORAGE_AUTHORITY_VIOLATION` | P1 |
| TC-008 | AC-008 | 否决 project db | `cargo test -p beacon-store per_project_db_forbidden` — register 后不创建 `<project>/.beacon/beacon.db`；Spine 仅读 `BEACON_STORE_PATH` 全局库 | P1 |
| TC-009 | AC-009 | loop-runs 非权威 | `cargo test -p beacon-store loop_runs_non_authority` — v2 运行时不写 `loop-runs.db`；migration fixture 导入 global 后 ledger 只读 | P2 |
| TC-010 | AC-010 | artifact stale | hash 不匹配标 stale | P2 |
| TC-011 | AC-011 | projection rebuild | `beacon doctor projection rebuild` 后 spine 字段一致 | P3 |
| TC-012 | AC-012 | events append-only | 无 UPDATE API | P0 |
| TC-013 | AC-013 | gate_results 写入 | qa run 后 count+1 | P3 |
| TC-014 | AC-014 | runs 启动写入 | run goal 后有 runs 行 | P2 |
| TC-015 | AC-015 | Spine DB-first | 无 blob 仍返回 lifecycle | P1 |
| TC-016 | AC-016 | v1 JSON 仅迁移 | 双写检测 fail | P3 |
| TC-017 | AC-017 | spine show | `beacon spine show --json` | P1 |
| TC-018 | AC-018 | spine list | `beacon spine list --json` | P1 |
| TC-019 | AC-019 | spine artifacts | `beacon spine artifacts <run-id>` | P2 |
| TC-020 | AC-020 | spine gate | `beacon spine gate …` | P3 |
| TC-021 | AC-021 | projects | `beacon projects register --path . --json`; `beacon projects list --json \| jq -e 'length>=1'`; `beacon projects show --project . --json` — 含 `project_key`, `versions[]`, `is_current` | P1 |
| TC-022 | AC-022 | 六 crate | `for c in core store orchestrator gate cli python; test -f packages/beacon-rs/beacon-$c/Cargo.toml; done`; `cargo metadata --no-deps \| jq -e '.packages\|map(.name)\|index("beacon-proto")\|not'`（D-V2-001） | P0 |
| TC-023 | AC-023 | 依赖无环 | `cargo tree -p beacon-cli` | P0 |
| TC-024 | AC-024 | 无 proto 硬依赖 | `cargo build -p beacon-cli` 无 gRPC feature；truth 记录 D-V2-001 accepted | P0 |
| TC-025 | AC-025 | 500 行 | wc -l 或 ADR | P6 |
| TC-026 | AC-026 | WorkflowStage enum | unit 非法值失败 | P0 |
| TC-027 | AC-027 | 非法转换 | unit Freeze→Think Err | P0 |
| TC-028 | AC-028 | Blocked codes | 必带 reason_codes | P0 |
| TC-029 | AC-029 | Skipped deferral | 无 deferral id 拒绝 | P0 |
| TC-030 | AC-030 | Crashed/Timeout | lifecycle_events 记录 | P2 |
| TC-031 | AC-031 | runs.status 12 态 | CHECK 约束 | P0 |
| TC-032 | AC-032 | plan 链 events | IntentCapture 等 event_type | P2 |
| TC-033 | AC-033 | stop 语义 | SIGINT vs --force | P2 |
| TC-034 | AC-034 | Repairing artifact | kind=repair | P2 |
| TC-035 | AC-035 | AwaitingQa 门禁 | 无 import 拒绝 | P3 |
| TC-036 | AC-036 | Closed 门禁 | orchestrator 不能直接 Closed | P3 |
| TC-037 | AC-037 | EvidenceChain | unit 字段 | P2 |
| TC-038 | AC-038 | 断链 | EVIDENCE_CHAIN_BROKEN | P2 |
| TC-039 | AC-039 | v1 链迁移 | `cargo test -p beacon-store migration_v1_chain -- --test fixture_v1_evidence_chain` — lifecycle_events 保留；runs.status 可映射 plan 主链 | P3 |
| TC-040 | AC-040 | run 子命令 | goal/resume/stop/status | P2 |
| TC-041 | AC-041 | truth-map preflight | blocked exit != 0 | P2 |
| TC-047 | AC-047 | checkpoint notes | lifecycle_events notes_injected | P2 |
| TC-048 | AC-048 | stop_when | `cargo test -p beacon-orchestrator stop_when_qa_pass -- --fixture tests/fixtures/stop_when_qa_pass.json` — qa pass 触发早停→`Stopped`；未 pass 继续 iterate | P2 |
| TC-049 | AC-049 | 无 QA verdict | stdout 无 release_ready | P2 |
| TC-050 | AC-050 | phase controller | metadata phase + events | P2 |
| TC-051 | AC-051 | 冷启动 bench | p95 < 100ms CI 归档 | P6 |
| TC-052 | AC-052 | spine bench | p95 < 50ms | P6 |
| TC-053 | AC-053 | resolve bench | p95 < 200ms | P6 |
| TC-054 | AC-054 | gate bench | p95 < 50ms | P6 |
| TC-055 | AC-055 | evidence hash bench | p95 < 10ms/file | P6 |
| TC-056 | AC-056 | migration 时长 | `cargo test -p beacon-store migration_duration -- --test fixture_typical_project` — wall time <60s；超时 test fail | P3 |
| TC-057 | AC-057 | iteration 调度 | bench < 100ms | P6 |
| TC-058 | AC-058 | DB 体积 WARN | 超 500MB 日志 | P6 |
| TC-059 | AC-059 | python shim | doctor verify-context | P4 |
| TC-060 | AC-060 | BEACON_V2=1 | Rust 路径 | P4 |
| TC-061 | AC-061 | BEACON_STORE_PATH | 隔离库 | P0 |
| TC-062 | AC-062 | compat verbose | compat_route=python | P4 |
| TC-063 | AC-063 | **33 skills 全量** | `beacon skill list` 全量 + 每 skill 路由 smoke | P4 |
| TC-064 | AC-064 | CLI help snapshot | 全子命令 | P1 |
| TC-065 | AC-065 | --json schema | spine/projects/run validate | P1 |
| TC-066 | AC-066 | reason_codes | 集成：5 codes gate 失败往返 + reason-codes.md | P3 |
| TC-067 | AC-067 | projects 表 | CRUD | P0 |
| TC-068 | AC-068 | project_versions | is_current 唯一 | P0 |
| TC-069 | AC-069 | feature_packages | slug 唯一 | P0 |
| TC-070 | AC-070 | feature_lifecycle | 更新 | P0 |
| TC-071 | AC-071 | runs 表 | enum CHECK | P0 |
| TC-072 | AC-072 | lifecycle_events | append only | P0 |
| TC-073 | AC-073 | gate_results | gate_type+verdict | P0 |
| TC-074 | AC-074 | artifact_refs | hash+abs_path | P0 |
| TC-075 | AC-075 | checkpoints | iteration 单调 | P2 |
| TC-076 | AC-076 | 六 DAO | unit 公开 API | P0 |
| TC-077 | AC-077 | runtime-ledger 迁移 | `cargo test -p beacon-store migration_runtime_ledger -- --test fixture_runtime_ledger` — row count match；checksum 一致 | P3 |
| TC-078 | AC-078 | loop-runs 迁移 | `cargo test -p beacon-store migration_loop_runs -- --test fixture_loop_runs` — runs 导入 global；源 loop-runs.db 标记 read-only archive | P3 |
| TC-079 | AC-079 | qa 历史迁移 | `cargo test -p beacon-store migration_qa_history` — 有 v1 qa fixture 则 import≥1；无 fixture → `BLOCKED:phase-P3-no-qa-history-fixture`（非 skip） | P3 |
| TC-080 | AC-080 | user_version | 降级拒绝 | P0 |
| TC-081 | AC-081 | SpineDao snapshot | 字段 == SpineSnapshot | P1 |
| TC-082 | AC-082 | list 过滤 | --status | P1 |
| TC-083 | AC-083 | 绝对路径 | 相对路径 Err | P1 |
| TC-084 | AC-084 | P0 出口 | core+store+skeleton tests | P0 |
| TC-085 | AC-085 | P1 出口 | spine+projects | P1 |
| TC-086 | AC-086 | P2 出口 | orchestrator+**TC-043/044** | P2 |
| TC-087 | AC-087 | P3 出口 | gate+migration+**TC-045/046/099/100** | P3 |
| TC-088 | AC-088 | P4 出口 | shim+**TC-063 全 skill** | P4 |
| TC-089 | AC-089 | P5 跳过 | **D-V2-001 accepted**：deferral ledger 有 accepted 记录；**无** P5 proto job；不阻塞 P6 | — |
| TC-090 | AC-090 | P6 出口 | 默认 v2+bench | P6 |
| TC-091 | AC-091 | CI matrix | GHA/job 跑 cargo test beacon-rs | P4 |
| TC-092 | AC-092 | migration 备份 | 迁移前 copy ledger | P3 |
| TC-093 | AC-093 | 单一写者 | `cargo test -p beacon-store single_writer_authority` — DB gate 写入后 legacy JSON 双写被拒；reason_code=`DUAL_WRITE_FORBIDDEN` | P3 |
| TC-094 | AC-094 | skill fail 路由 | 文档+测试 mock fail→doctor | P4 |
| TC-095 | AC-095 | bench 回退阻断 P6 | regression >10% fail | P6 |
| TC-096 | AC-096 | phase smoke | CI phase jobs | P0–P6 |
| TC-097 | AC-097 | evaluator closure | beacon qa run 全矩阵 | P6 |
| TC-098 | AC-098 | plan drift | promote 脚本 | P1 |

## v1.6 Upstream（AC-101–104，R2 增补）

| TC ID | AC ID | 场景 | Command + Assertion | Phase |
|-------|-------|------|---------------------|-------|
| TC-101 | AC-101 | TIG freeze block | `cargo test -p beacon-gate tig_freeze_block` 或 bad-fixture freeze — 空缺 AC/软 TC/未拍板 deferral → exit≠0 + repair_route | P3 |
| TC-102 | AC-102 | planner_review artifact | `cargo test -p beacon-orchestrator planner_review_multi_agent` — reviewer_lanes/findings/synthesis/execution_mode/fallback_reason + artifact_refs | P2 |
| TC-103 | AC-103 | verify-truth-integrity v2 | `beacon doctor verify-truth-integrity <feature> --version v2.0.0 --mode block` — block 语义同 v1.6 | P3 |
| TC-104 | AC-104 | P0 workspace done | `cd packages/beacon-rs && cargo test --workspace` — 12 passed；六 crate `Cargo.toml` 存在 | P0 |
| TC-105 | AC-105 | CLI 选 agent 跑长任务 | `beacon-v2 run --agent codex --feature <slug> --version v2.0.0` — CLI 进程跑 loop，checkpoint/resume/SIGINT graceful；无 daemon | P3 |
| TC-106 | AC-106 | stop_when maker≠checker | `cargo test -p beacon-orchestrator stop_when_unverified` — agent 自报 stop_signal 但外部检查未过 → `stop_when_unverified` continue；外部检查过 → stop | P3 |
| TC-107 | AC-107 | Developer Feedback checkpoint | `beacon-v2 run --feedback-checkpoint --every 3` — 每 3 iteration 暂停等人注入 notes，resume 后基于 notes 重新 iterate；notes 写入 lifecycle_events | P3 |
| TC-108 | AC-108 | 三层 Loop 可观测 | `beacon-v2 spine show --json` — snapshot 含 `loop_layer` 字段（coding/developer/realworld） | P3 |

## 负向路径

| TC ID | 场景 | 期望 |
|-------|------|------|
| TC-N01 | fixture 单次冒充多轮 | AC-043 测试失败 |
| TC-N02 | 空 contract test 当 AC-045 证据 | 拒绝 |
| TC-N03 | orchestrator 输出 qa_pass | fail |
| TC-N04 | 仅 smoke 无 bench 声称 AC-051–058 | P6 阻断 |
| TC-N05 | subprocess 替身冒充 ImplementHarness（AC-100） | 拒绝 |
| TC-N06 | current-branch + isolated-worktree 非法组合（AC-099） | fail-closed + reason_code |

## E2E

| TC ID | 场景 |
|-------|------|
| TC-E01 | freeze → run goal(codex) → import → qa → release → Closed | `cargo test -p beacon-orchestrator e2e_closed_loop -- --test fixture_delivery_chain`（CI opt-in `BEACON_V2_E2E=1`） |
| TC-E02 | claude+acp 各 1 iteration 同一 feature 不同 run | `cargo test -p beacon-orchestrator e2e_multi_backend -- --backends claude,acp`（cred 缺失 → `BLOCKED:missing_cred`） |
| TC-E03 | projection rebuild 后 spine 一致 | `beacon doctor projection rebuild --project . --json`; `beacon spine show --json` lifecycle/gate 字段与 rebuild 前 snapshot diff 为空（artifact stale 允许） |
| TC-E04 | 33 skills 全量 smoke（P4 gate） | `beacon skill list --json \| jq -e 'length==33'`; 每 skill id 路由 smoke（同 TC-063） |
| TC-E05 | worktree goal → implement harness iteration → spine cwd 一致 | `cargo test -p beacon-orchestrator e2e_worktree_harness -- --test fixture_worktree_implement`（同 TC-099/100） |

**当前**：truth **R2 draft**（r5）；**P0 done**（TC-104）；P1–P6 其余 TC 待实现后由 `beacon-eval-qa` 裁决。
