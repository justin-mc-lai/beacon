---
slug: beacon-v2-rust-kernel-redesign
version: v2.0.0
revision: r19-scenario-completeness-s01-s19
parser_contract: beacon-feature-package-v1
truth_ref: docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
---

# 测试覆盖：Beacon v2 Rust Kernel Redesign（r14）

## 覆盖说明

- 每个 AC（AC-001..AC-173）至少一行 TC。
- **integration tier** 为 agent 类 AC（AC-043–046, AC-099–100）最低验收等级；禁止仅 contract/空壳验收。
- **禁止非行为级验证列**：单独 `integration`、`目录存在`、`fixture`、`可选` 不算可执行 TC；必须写 **Command + Assertion**（或显式 `BLOCKED:<reason>`）。
- Pass/Fail 由 `beacon-eval-qa` 裁决。

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | unit | `test -d packages/beacon-rs/beacon-core` | Rust workspace |
| AC-002 | TC-002 | unit | `cd packages/beacon-rs && cargo metadata --no-deps --format-version 1 \| jq -e '.packages\|map(.name)\|index("beacon-python")\|not'` | v2 core 无 PyO3/python crate |
| AC-003 | TC-003 | unit | legacy Python/Node invocation fixture → exit != 0 + `reason_code=legacy_python_removed` | 无 Python fallback |
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
| AC-022 | TC-022 | unit | `for c in core store orchestrator gate cli; do test -f packages/beacon-rs/beacon-$c/Cargo.toml; done`; `test ! -f packages/beacon-rs/beacon-python/Cargo.toml` | 五个 core crate |
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
| AC-059 | TC-059 | contract | `beacon harness list --version v2.0.0 --json` | 仅六个一等能力 |
| AC-060 | TC-060 | unit | `beacon --version --json` 或等价 runtime payload | 默认 Rust v2 路径 |
| AC-061 | TC-061 | unit | 隔离库 | BEACON_STORE_PATH |
| AC-062 | TC-062 | unit | legacy skill invocation fixture | `legacy_python_removed` / migration route，无 `compat_route=python` |
| AC-063 | TC-063 | contract | `beacon harness list --version v2.0.0 --json \| jq -e 'map(.id)==["loop","truth","design","implement","qa-evidence","release"]'` | 六能力 surface contract |
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
| AC-088 | TC-088 | unit | minimal harness surface + TC-063 + legacy removal | P4 出口 |
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
| 六能力 harness surface | TC-059, TC-063, TC-109–124 | harness list 精确六能力；legacy fallback 被拒；decision/design/evidence gates 可验 |

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
| TC-002 | AC-002 | 无 PyO3/python core crate | `cd packages/beacon-rs && cargo metadata --no-deps --format-version 1 \| jq -e '.packages\|map(.name)\|index("beacon-python")\|not'` | P4 |
| TC-003 | AC-003 | 无 Python fallback | legacy Python/Node invocation fixture → exit != 0 + `reason_code=legacy_python_removed` | P4 |
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
| TC-022 | AC-022 | 五个 core crate | `for c in core store orchestrator gate cli; do test -f packages/beacon-rs/beacon-$c/Cargo.toml; done`; `test ! -f packages/beacon-rs/beacon-python/Cargo.toml`; `cargo metadata --no-deps \| jq -e '.packages\|map(.name)\|index("beacon-proto")\|not'`（D-V2-001） | P0 |
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
| TC-059 | AC-059 | 六能力 surface | `beacon harness list --version v2.0.0 --json` 精确返回 loop/truth/design/implement/qa-evidence/release | P4 |
| TC-060 | AC-060 | explicit dual-track runtime | 显式选择 v2 runtime（二进制或 flag）；禁止文档/CLI 暗示「默认切 v2 即退役 v1」 | P4 |
| TC-061 | AC-061 | BEACON_STORE_PATH | 隔离库 | P0 |
| TC-062 | AC-062 | cross-track fallback forbidden on v2 path | v2 path legacy python backend → `cross_track_fallback_forbidden`；不得出现 `compat_route=python`；v1 path 不受影响 | P4 |
| TC-063 | AC-063 | 六能力 contract | `beacon harness list --version v2.0.0 --json \| jq -e 'map(.id)==["loop","truth","design","implement","qa-evidence","release"]'` | P4 |
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
| TC-088 | AC-088 | P4 出口 | minimal harness surface + TC-063 + TC-062 legacy removal | P4 |
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

## Minimal Kernel Extensions（AC-109–144）

| TC ID | AC ID | 场景 | Command + Assertion | Phase |
|-------|-------|------|---------------------|-------|
| TC-109 | AC-109 | 六个一等能力 | `beacon harness list --version v2.0.0 --json` 精确返回 `loop/truth/design/implement/qa-evidence/release`，无第七能力 | P4 |
| TC-110 | AC-110 | 历史兼容移除 | `cargo metadata` 无 `beacon-python`；legacy skill fixture 返回 migration/archive route，不进入 Python runtime | P4 |
| TC-111 | AC-111 | 强意图识别 | `beacon truth intent-snapshot --prompt fixture --json` 产出 `intent_snapshot.v1` required fields + confidence | P1 |
| TC-112 | AC-112 | prompt snapshot ledger | 连续两轮 prompt 写入 hash；latest accepted 指针更新；旧 rejected snapshot 不可被 loop 消费 | P1 |
| TC-113 | AC-113 | low-confidence freeze block | 低置信/冲突 scope fixture 执行 freeze → exit != 0 + `reason_code=intent_confidence_low` 或 `scope_unconfirmed` | P1 |
| TC-114 | AC-114 | decision packet admission | `beacon loop start --decision-packet missing.json` → blocked；有效 `decision_packet.v1` → 进入 resolving | P2 |
| TC-115 | AC-115 | design primitive gate | UI feature 无 `design_primitives.v1` → implement admission blocked；绑定后 pass | P2 |
| TC-116 | AC-116 | implement admission compound | truth/design/worktree/program/dependency 任一缺失 → typed reason_code；全满足才允许 write | P2 |
| TC-117 | AC-117 | agent trace | governed iteration 后 `agent_trace.v1` 含 decision/output 或 failure/retry/tool_call/gate_verdict；缺 trace fail-closed | P2 |
| TC-118 | AC-118 | stagnation detector | repeat_failure/repeat_labor/plateau 三 fixture 产出稳定 `stagnation-report.v1`；clean fixture 无 finding | P2 |
| TC-119 | AC-119 | remediation sandbox | overlay eval pass 输出 human_review_required；eval fail rollback clean；canonical truth 未改 | P3 |
| TC-120 | AC-120 | loop guardrails | pattern/failure/token/readiness/lease/denylist 任一阻断 fixture → loop preflight blocked + reason_code | P2 |
| TC-121 | AC-121 | confidence + FSM coverage | qa-evidence profile 含 confidence_chain 与 state_machine_coverage；FSM gap 不可记 full pass | P3 |
| TC-122 | AC-122 | defect repair regression | defect->fix->regression 链完整才解 release block；缺回归 → `regression_skipped` | P3 |
| TC-123 | AC-123 | 非行为证据拒绝 | static shell/source-grep/coming_soon/no-op/zero-assertion fixture 均 rejected | P3 |
| TC-124 | AC-124 | release human gate | auto_decide=true 且无 human confirmation → release gate blocked | P3 |
| TC-125 | AC-125 | public skill surface 收敛 | `beacon harness list --version v2.0.0 --json` 只返回六 public skill；doctor/router/hooks/metadata/debug/archive 不出现在 host-visible top-level list | P4 |
| TC-126 | AC-126 | progressive disclosure loader | `beacon harness resolve truth --topic branch --json` 产出 `skill_load_plan.v1`，只包含 public `truth/SKILL.md` + branch reference；不加载全部 historical skill | P2 |
| TC-127 | AC-127 | route examples contract | `beacon harness examples --version v2.0.0 --json` 每个 public skill 至少 1 个 example；包含 decision_packet、design_primitives、qa-release、branch-blocked 四类 route | P2 |
| TC-128 | AC-128 | BranchContext schema | `beacon workspace admit --project-root fixture --version v2.0.0 --feature demo --json` 输出 `BranchContext.v1` required fields，且 `target_project_root != caller_cwd` fixture 仍指向 admitted worktree | P2 |
| TC-129 | AC-129 | branch governance hard gate | 缺 admission / cwd 错配 / protected path write 三 fixture 均 blocked，reason_code 指向具体 BranchContext 字段；不得降级为 warning | P2 |
| TC-130 | AC-130 | harness boundary hard gate | planner 实现、implement 改 frozen truth、qa-evidence 改 implementation、loop 跳 release human gate 四 fixture 均 fail-closed + typed reason_code | P2 |
| TC-131 | AC-131 | TraceSpine authority | `beacon-v2 loop start --fixture trace-spine-authority --json` 产出 append-only `TraceSpine.v1`；`lifecycle_events` / evidence manifest 标记为 projection，不可单独满足 release | P2 |
| TC-132 | AC-132 | TraceContext binding | 缺 BranchContext / decision_packet / intent_snapshot / truth_hash 任一引用时 `loop start` blocked；完整绑定后 trace context 含 required fields | P2 |
| TC-133 | AC-133 | trace completeness gate | implement / qa-evidence / release 三类 fixture 分别覆盖 trace missing、append failure、event hash chain invalid、event-to-evidence 断链，均 fail-closed | P2 |
| TC-134 | AC-134 | stagnation report trace range | repeat_failure / repeat_labor / plateau report 必须含 trace_event_range + reason_code + catalog/pattern refs；无 trace run_id 输入 blocked | P2 |
| TC-135 | AC-135 | remediation report chain | remediation report 必须引用 stagnation report、overlay/eval/rollback evidence 与 human_review_decision；无 human review 时 release blocked | P3 |
| TC-136 | AC-136 | canonical truth branch | 在 feature/dev worktree 执行 `beacon change --refreeze-chain` blocked，`reason_code=truth_canonical_branch_mismatch`；main/master 上允许进入 refreeze | P2 |
| TC-137 | AC-137 | empty/drift refreeze guard | reason-only 或 machine-only refreeze blocked；machine revision 与 human narrative 不一致 blocked，reason_code 分别为 `empty_refreeze_reason_only` / `revision_authority_drift` | P2 |
| TC-138 | AC-138 | standard execution flow order | `beacon-v2 loop verify-flow --fixture canonical-main-to-feature --json` 校验状态顺序 support_advisory -> canonical_truth_authoring -> canonical_refreeze -> canonical_commit -> feature_worktree_reconcile -> governance_verify -> workspace_admission -> implement_resume；跳过 canonical_commit fixture blocked | P2 |
| TC-139 | AC-139 | canonical commit boundary | main 上 refreeze complete 但无 commit 时 feature branch admission blocked，`reason_code=canonical_refreeze_not_committed`；提交后产出 `truth_baseline_commit` | P2 |
| TC-140 | AC-140 | stale feature-local refreeze quarantine | feature worktree 存在本地 `.machine` revision/projection dirty 时，merge main 前必须 scoped stash/archive；直接 commit/merge fixture blocked，`reason_code=stale_feature_local_refreeze` | P2 |
| TC-141 | AC-141 | truth baseline merged | feature branch 未包含 `truth_baseline_commit` 时 `implement check-branch` blocked；merge main 后返回 `up_to_date` / pass | P2 |
| TC-142 | AC-142 | admission evidence bundle | 缺 truth-map verify / verify-materials strict / diff check / branch-governance verify / workspace admission 任一 artifact 时 implement admission blocked，`reason_code=standard_flow_verification_incomplete` | P2 |
| TC-143 | AC-143 | idempotent resume | 标准流重复执行已完成步骤时不 bump requirement revision；refreeze summary revision 保持不变，merge main 返回 `Already up to date` | P2 |
| TC-144 | AC-144 | public examples only | `beacon harness examples --version v2.0.0 --topic standard-flow --json` 只通过 loop/truth/implement/qa-evidence/release examples 暴露；不得新增 top-level `standard-flow` public skill | P4 |
| TC-145 | program admission | v2 Rust program surface | `test -f docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-manifest.md && test -f docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/phase-graph.md && test -f docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/admission-gates.md && jq -e '.fsm_state=="canonical_truth_materialized" and .lake_or_ocean=="海"' docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-run-state.json` | P0 |
| TC-146 | revision projection | human/machine revision alignment | refreeze summary revision, `.machine/execution/*revision.json`, truth frontmatter and evidence decision record must describe the same latest program-orchestration revision; mismatch blocked as `revision_authority_drift` | P2 |
| TC-147 | AC-147 | long-term dual-track policy | truth/deferral 含 UD-dual-B accepted；P6 文档不得要求 retire v1 product track | P4 |
| TC-148 | AC-148 | dual-track merge isolation | fixture PR 同时改 `beacon/` 与 `packages/beacon-rs/` 发布真源且无 `dual_track_shared_contract` admission → blocked `dual_track_mixed_source` | P4 |
| TC-149 | AC-149 | explicit runtime selection | 未显式选轨时不得静默执行另一轨；CLI help/schema 暴露显式选择面 | P4 |
| TC-150 | AC-150 | single writer per track | 双写期同轨第二写者 fail；跨轨只读对照允许 | P3 |
| TC-151 | AC-151 | unified skill-score schema | 同一 score schema 对 v1 skill fixture 与 v2 六 public skill fixture 均可产出可比字段 | P4 |
| TC-152 | AC-152 | structure+effectiveness dual eval | scorecard 同时含 structure 与 effectiveness 段；缺一段 → schema invalid | P4 |
| TC-153 | AC-153 | score not QA/release | scorecard JSON `authority.runtime_evidence_only==true` 且 `formal_verdict_authority==false` | P4 |
| TC-154 | AC-154 | score-only human-edit | optimizer/score CLI 在 dry-run 或默认模式下不得修改 SKILL.md（git dirty 检测为 0） | P4 |
| TC-155 | AC-155 | scorer≠editor separation | 同一步骤既写 skill 又写自增 score 的 fixture 被拒绝 | P4 |
| TC-156 | AC-156 | schema stability | 擅自改权重/维度名而无 change 记录 → contract fail | P4 |
| TC-060b | AC-060 | explicit track select | 无显式 runtime/v2 flag 时不得声称「默认已切 v2 且 v1 退役」 | P4 |
| TC-062b | AC-062 | cross-track fallback forbidden | v2 path 请求 python backend → `cross_track_fallback_forbidden`；v1 path 正常调用 v1 skill 仍 pass | P4 |

| TC-157 | AC-157 | dual-track install/PATH matrix | fixture: install v1+v2 bins；`beacon <v1-only-cmd>` 不走 v2；`beacon-v2 spine show` 或 `beacon --runtime v2 spine show` 不 fallback python；无显式轨时不得静默跨轨 | P0 |
| TC-158 | AC-158 | dual-track writer lease | 同库同字段 v1+v2 并发写 fixture → `dual_track_writer_conflict`；跨轨只读 spine/import 对照 pass | P0 |
| TC-159 | AC-159 | archive plane explicit version | `--version v2.0.0` resolve 到 `docs/beacon/archive/v2.0.0/features/...`；若 catalog archive-readonly 则 implement admit 给 `version_plane_archive_readonly` + unarchive route，不得 silent write | P0 |
| TC-160 | AC-160 | core closure no python member | `cd packages/beacon-rs && cargo metadata --format-version 1 \| jq -e '[.packages[].name] \| index("beacon-python") \| not'` 且 workspace members 仅五 core crate | P0 |
| TC-161 | AC-161 | schema contract closed | `cargo test -p beacon-store schema_contract_matches_truth` — 表/必填列与 AC-067..075 或已 refreeze 的 schema ADR 一致；否则 `schema_contract_drift` | P0 |
| TC-162 | AC-162 | MD parse golden parity | `cargo test -p beacon-cli truth_parse_golden_parity -- --fixture tests/fixtures/truth_parse/*` — Rust 输出 vs golden JSON 规范字段 diff 为空；含中文表/frontmatter | P1 |
| TC-163 | AC-163 | phase exit not release | phase scorecard JSON `authority=="phase_exit_only"` 且无 `release_ready=true`；P0 pass 禁用 v1 CLI fixture → `dual_track_policy_violation` | P0 |
| TC-164 | AC-164 | weak TC rejected | evaluator fixture：仅 `test -d packages/beacon-rs/beacon-core` 作为 AC-001 唯一证据 → `weak_tc_insufficient` block | 全 phase |
| TC-165 | AC-165 | reason_codes core roundtrip | core set（≥20，含 R18 新码）每个 code 有 fail fixture + JSON 往返；删除 core code 无 change → contract fail | P3 |
| TC-166 | AC-166 | cross-track evidence contamination | 仅提交 v1 `.beacon/qa/*.json` 申请 v2 release → `cross_track_evidence_contamination`；v2 gate_results 冒充 v1 release 同阻 | P3 |
| TC-167 | AC-167 | adversarial review required | release fixture 缺 `adversarial_review.v1` 或翻车点 <3 → `adversarial_review_missing` | P3 |
| TC-168 | AC-168 | shared_contract whitelist | PR 同改 `beacon/`+`packages/beacon-rs/` 非白名单路径无 admission → `dual_track_mixed_source`；只改 `global-boundaries.md`+catalog 有 shared admission → pass | P4 |
| TC-169 | AC-169 | skill-score corpus | `beacon skill-score --corpus skill-score-corpus.v1 --skill fixtures/v1/demo --json` 与 v2 `loop` skill 均产出 structure+effectiveness；缺 corpus → `skill_score_corpus_missing` | P4 |
| TC-170 | AC-170 | suggest-human-edit-rescore | score 产出 suggested_diff 后不改文件复评分数不升；自动 apply diff → `skill_auto_edit_forbidden`；人改后独立 grader 会话可复评 | P4 |
| TC-171 | AC-171 | GitScopeGraph→BranchContext | `cargo test -p beacon-cli gitscope_branch_context_parity -- --fixture docs/beacon/v1.6.7/.../fixtures` 或仓库内等价 fixture：topology 字段可加载 | P2 |
| TC-172 | AC-172 | three topology admissions | single_repo/monorepo/multi_git 三 fixture：dirty writable scope → topology_gate blocked；multi_git satellite blocked → aggregate blocked | P2 |
| TC-173 | AC-173 | topology_gate_ref required | loop start / implement admit 无 topology_gate_ref → `topology_gate_missing`；status=blocked → `topology_gate_blocked`；bundle 含 topology_gate 项 | P2 |

## 负向路径

| TC ID | 场景 | 期望 |
|-------|------|------|
| TC-N01 | fixture 单次冒充多轮 | AC-043 测试失败 |
| TC-N02 | 空 contract test 当 AC-045 证据 | 拒绝 |
| TC-N03 | orchestrator 输出 qa_pass | fail |
| TC-N04 | 仅 smoke 无 bench 声称 AC-051–058 | P6 阻断 |
| TC-N05 | subprocess 替身冒充 ImplementHarness（AC-100） | 拒绝 |
| TC-N06 | current-branch + isolated-worktree 非法组合（AC-099） | fail-closed + reason_code |
| TC-N07 | design_required 但无 design_primitives | implement admission fail-closed |
| TC-N08 | decision_packet 引用 rejected prompt snapshot | loop start fail-closed |
| TC-N09 | auto_decide 试图越过 release human gate | release blocked |
| TC-N10 | v2 public surface 暴露 doctor/router/hooks 为一等 skill | surface contract fail |
| TC-N11 | loader 预加载全部历史 skill 正文 | `skill_load_plan.v1` contract fail |
| TC-N12 | harness 从 caller cwd 推断目标 root | BranchContext mismatch blocked |
| TC-N13 | `lifecycle_events` / evidence manifest 无 TraceSpine 仍尝试 release | release blocked |
| TC-N14 | feature worktree 本地 bump requirement revision | `truth_canonical_branch_mismatch` |
| TC-N15 | refreeze 只有 change_reason 或 machine projection 变化 | `empty_refreeze_reason_only` |
| TC-N16 | human evidence 写 R9 但 machine revision 写 R8 | `revision_authority_drift` |
| TC-N17 | refreeze complete 但 canonical branch 未提交就合入 feature | `canonical_refreeze_not_committed` |
| TC-N18 | feature-local stale refreeze dirty 未 quarantine 直接 merge main | `stale_feature_local_refreeze` |
| TC-N19 | feature branch 缺 `truth_baseline_commit` 仍进入 implement | `truth_baseline_not_merged` |
| TC-N20 | admission bundle 缺 branch-governance verify 或 workspace admission | `standard_flow_verification_incomplete` |
| TC-N21 | 重复执行标准流导致新的 requirement revision bump | `standard_flow_order_violation` |
| TC-N22 | program intent 只留在 stash 或 support advisory，main 无 canonical program surface | `program_surface_missing` |
| TC-N23 | refreeze bump 了 machine revision 但 truth/tests/tasks/evidence 未写入对应人类叙事 | `revision_authority_drift` |
| TC-N24 | 评分 CLI 自动改写 SKILL.md | `skill_auto_edit_forbidden` |
| TC-N25 | 用 skill scorecard 声称 release pass | authority boundary fail |
| TC-N26 | P6 成熟度通过后自动禁用 v1 CLI | `dual_track_policy_violation` |
| TC-N27 | 无显式 runtime 却执行 v2-only 行为 | `runtime_track_unspecified` 或等价 fail-closed |
| TC-N28 | v1 与 v2 并发写同一权威 DB 字段 | `dual_track_writer_conflict` |
| TC-N29 | archive-readonly version 上 silent implement 写 truth | `version_plane_archive_readonly` / `version_catalog_plane_mismatch` |
| TC-N30 | workspace 仍含 beacon-python member 声称 P0 complete | `core_closure_python_present` |
| TC-N31 | 实现表集合与 truth schema 不一致无 ADR | `schema_contract_drift` |
| TC-N32 | MD parser 与 golden 字段 diff 非空仍 pass | `truth_parse_parity_mismatch` |
| TC-N33 | phase pass 宣称 release_ready 或禁用 v1 | `dual_track_policy_violation` |
| TC-N34 | 仅目录存在级 TC 作为 AC closure | `weak_tc_insufficient` |
| TC-N35 | v1 QA JSON 单独用于 v2 release | `cross_track_evidence_contamination` |
| TC-N36 | release 无 adversarial_review.v1 | `adversarial_review_missing` |
| TC-N37 | 缺 skill-score-corpus.v1 仍打分 | `skill_score_corpus_missing` |
| TC-N38 | 评分 CLI 自动 apply suggested_diff | `skill_auto_edit_forbidden` |
| TC-N39 | GitScopeGraph 无法投影 BranchContext | `gitscope_branch_context_parity_failed` |
| TC-N40 | loop/implement 缺 topology_gate_ref | `topology_gate_missing` |

## E2E

| TC ID | 场景 |
|-------|------|
| TC-E01 | freeze → run goal(codex) → import → qa → release → Closed | `cargo test -p beacon-orchestrator e2e_closed_loop -- --test fixture_delivery_chain`（CI opt-in `BEACON_V2_E2E=1`） |
| TC-E02 | claude+acp 各 1 iteration 同一 feature 不同 run | `cargo test -p beacon-orchestrator e2e_multi_backend -- --backends claude,acp`（cred 缺失 → `BLOCKED:missing_cred`） |
| TC-E03 | projection rebuild 后 spine 一致 | `beacon doctor projection rebuild --project . --json`; `beacon spine show --json` lifecycle/gate 字段与 rebuild 前 snapshot diff 为空（artifact stale 允许） |
| TC-E04 | 六能力 harness surface（P4 gate） | `beacon harness list --version v2.0.0 --json \| jq -e 'map(.id)==["loop","truth","design","implement","qa-evidence","release"]'` |
| TC-E05 | worktree goal → implement harness iteration → spine cwd 一致 | `cargo test -p beacon-orchestrator e2e_worktree_harness -- --test fixture_worktree_implement`（同 TC-099/100） |

**当前**：R19 frozen（scenario completeness AC-157–173）；implementation/QA 由 evaluator 裁决。
