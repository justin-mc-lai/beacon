# Beacon v2 重写计划

## Context

Beacon v1 (Python + Node.js) 存在 10 个核心架构缺陷：无主流程显式状态机、阶段定义散落 4+ 模块、巨型单文件 (prototype_utils.py 315KB)、纯同步 Python、beacon-loop busy-wait、SQLite 每次 spawn 新进程、缺少 crash/timeout 状态、500+ run 目录无清理、beacon-loop/beacon-run 功能重叠、版本信息三处不一致。

核心洞察：**Prompt 约束只是建议，CLI 层级强制执行才是法律。Agent 会适应并绕过软性限制 — 修复必须是架构层级的。**

**决策**：Rust 核心 + Python 兼容层 | 全新重写 v2 | 双层状态机（类型 + 运行时）| **MD 需求真相 + SQLite 运行态统一存储 + 单一 Operator Spine 查询面**

**存储决策（v2 收敛，延续 v1.6.x 讨论结论）**：

- **需求真相**：仅 Markdown（`features/<slug>/truth.md`、`docs/beacon/<version>/` 等 requirement package）；**不进库当权威**。
- **其余运行态**：统一写入 **本机用户级 SQLite**（`~/.beacon/beacon.db`，WAL；由 v1 `runtime-ledger.sqlite3` 演进合并，**不**按项目各放一份库）；大体积证据仍落在各项目 `.beacon/evidence/` 等目录，库内只存 **artifact 指针（绝对 path + hash + role）**。
- **多项目**：`projects` / `project_versions` / `runs` 等同库管理，`project_key` 关联；方便 portfolio、board、跨项目 spine 查询与后续演进。
- **对外读面**：只暴露 **一个 Operator Spine 查询 API**；实现为 **读全局库优先，必要时按指针回源项目内 blob 文件**。

---

## 1. Crate 结构图

```
beacon-v2/
├── Cargo.toml                        # workspace root
├── crates/
│   ├── beacon-core/                   # 零 IO 依赖：类型、状态机、证据原语
│   │   └── src/{stage, state, evidence, transaction, version, gate, scorecard,
│   │             compatibility, artifact, lock, team, skill, board, harness}.rs
│   │
│   ├── beacon-store/                  # SQLite 存储层 (rusqlite + r2d2 连接池)
│   │   └── src/{pool, migration, project_dao, project_version_dao, feature_dao, run_dao,
│   │             lifecycle_dao, transaction_dao, artifact_dao, evidence_dao, gate_dao,
│   │             scorecard_dao, spine, memory_dao}.rs
│   │
│   ├── beacon-gate/                   # Gate 引擎 + 20+ 子治理模块
│   │   └── src/{engine, reason_codes, scorecard, incremental,
│   │             modules/{evidence_manifest, qa_status, acceptance_kit,
│   │                      version_surface, semantic_contract, requirement_clarity,
│   │                      technical_review, deep_release, test_contract,
│   │                      reconciliation, prompt_boundary, change_documents,
│   │                      browser_release, revision_binding}}.rs
│   │
│   ├── beacon-orchestrator/           # 统一长任务编排器 (替换 beacon-loop + beacon-run)
│   │   └── src/{runtime, goal, phase, agent, delivery, worktree,
│   │             interrupt, resume, ledger,
│   │             backends/{codex, claude, acp, implement_harness}}.rs
│   │
│   ├── beacon-cli/                    # CLI 入口 (clap v4)
│   │   └── src/{main, output,
│   │             commands/{core, support, labs, bridge, governor}}.rs
│   │
│   ├── beacon-python/                 # PyO3 绑定
│   │   └── src/{lib, core_bridge, store_bridge, orchestrator_bridge, compat}.rs
│   │
│   └── beacon-proto/                  # 可选：protobuf 二进制格式 (feature-gated)
│       └── src/{lifecycle, evidence, transaction}.proto
│
├── python/                            # Python 兼容包
│   ├── beacon_v2/{__init__, cli, compat, skill_surfaces}.py
│   └── pyproject.toml
│
└── skills/                            # v1.6.0 33 skill 目录不变
```

**依赖图**：
```
beacon-cli → beacon-orchestrator → beacon-core
    ↘             ↘                    ↑
beacon-python → beacon-store ──────────┘
    ↘             ↑
beacon-gate ──────┘
         ↑
   beacon-proto (optional)
```

---

## 2. 双层状态机

### 2.1 类型层 — Rust enum 编译期穷举匹配

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum WorkflowStage {
    Prd, UserStory, TestCase, Prototype, Implement, Qa, Release,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum StageStatus {
    NotStarted, InProgress, Completed, Failed, Skipped,
    Crashed,      // NEW: 进程异常终止
    TimedOut,     // NEW: 超时
    Interrupted,  // NEW: SIGINT/SIGTERM
    Repairing,    // NEW: 修复中
}
```

### 2.2 转换表 — 每条路径显式声明，无通配符

| From\To      | Prd | UserStory | TestCase | Prototype | Implement | Qa | Release |
|-------------|-----|-----------|----------|-----------|-----------|----|---------|
| **Prd**     | R   | **F**     | X        | X         | X         | X  | X       |
| **UserStory**| X  | R         | **F**    | X         | X         | X  | X       |
| **TestCase** | X  | X         | R        | **F\***   | **F**     | X  | X       |
| **Prototype**| X  | X         | B        | R         | **F**     | X  | X       |
| **Implement**| X  | X         | B        | B\*       | R         | **F**| X     |
| **Qa**      | X   | X         | X        | X         | **B**     | R  | **F**   |
| **Release** | X   | X         | X        | X         | **B**     | **B**| R      |

图例：F=前进, B=回退(repair), R=重试, X=非法, \*=需 prototype_enabled

### 2.3 Delivery FSM — 从 beacon-loop state.ts 迁移并增强

保留 12 个原状态 + 新增 `RepairFromRelease`：
```
IntentCapture → IntentReview → [UserDecisionPending] → TruthGapScan
→ [TruthFill → TruthFreezeGate] → ImplementLoop
→ EvidenceImport → QaPending → [RepairFromQa ↺] → ReleasePending
→ [RepairFromRelease ↺] → TerminalClosed | TerminalAborted
```

### 2.4 运行时层 — Evidence Chain 验证

每次转换必须携带：
- `evidence_refs`: 产出文件路径列表
- `transaction_id`: 事务 ID
- `source_hash`: 源材料 SHA-256
- `sink_checksums`: 写入产物校验和

运行时验证：回溯 evidence chain，确认每个 link 的 hash 一致性。任何断裂 → `TransitionError::EvidenceChainBroken` → 阻断。

### 2.5 存储分层与单一 Spine（v2 规范）

v1 的运行态散落在 `.beacon/**/*.json`、`.gnhf/runs/**`、机器级 `~/.beacon/runtime-ledger/` 等多处；v1.6.1 用 `beacon-loop spine show` 做了**读面聚合**，但**写仍分散**。v2 收敛为三层：

```text
Truth Layer（权威，仅 MD）
  features/<slug>/truth.md
  docs/beacon/<version>/          # requirement package / release 材料
  ↓ 只读引用，禁止 SQLite 反写真相含义

Runtime Layer（权威，本机全局 SQLite）
  ~/.beacon/beacon.db
  项目注册、项目版本、run 痕迹、阶段机、gate 结果、事务/checkpoint、artifact 索引
  ↓ 单一写入路径（beacon-store DAO + project_key）

Blob Layer（大文件，各项目目录）
  <project-root>/.beacon/evidence/、run 日志/junit/截图等
  ↓ 全局库仅存绝对 path + sha256 + mime + size + artifact_role
```

| 数据类 | v2 权威落点 | 说明 |
|--------|-------------|------|
| 需求真相、AC、冻结边界 | **MD only** | gate/QA 消费 resolver，不以 JSON/SQLite 替代 |
| Beacon 项目注册 | 全局库 `projects` | project_key、project_root、kind、portfolio 投影字段 |
| 项目版本线 | 全局库 `project_versions` | docs_version、runtime_version、is_active、truth_catalog_ref |
| Feature 生命周期投影 | 全局库 `feature_lifecycle` + `feature_packages` | 对齐 v1.3.4 Runtime Ledger 表意 |
| Run 痕迹 / 元数据 | 全局库 `runs` | run_id、project_key、feature、version、agent、worktree、status |
| 阶段机 / Delivery FSM | 全局库 `lifecycle_events` + `checkpoints` | 含 crashed/timeout/interrupted |
| Gate / scorecard 结果 | 全局库 `gate_results` | reason_codes、verdict、transaction_id |
| 证据与产物 | 全局库 `artifact_refs` + **项目内文件** | 库记**绝对 path**指针；正文在各项目 `.beacon/` blob 目录 |
| 项目内 `.beacon/` | **仅 blob + 可选导出缓存** | **禁止**再新增项目级 `beacon.db` / 并行 JSON 权威 |

**原则**：

1. **除 MD 需求真相外，运行态以 SQLite 为唯一写权威**；不再新增「第二套 JSON 真相 twin」。
2. **大体积证据不进 BLOB 列**（除非明确 opt-in 的小 payload）；默认 **文件 + artifact_refs**。
3. **JSON 导出仅为兼容投影**（`--json`、`doctor export`），serde 输出可读；**不以 JSON 目录为 resume/gate 的读权威**。
4. **断库可恢复**：`beacon doctor projection rebuild` 扫描本机已注册 `project_root`，从 MD + 各项目 blob + 遗留 v1 `.beacon/` JSON **重建全局库索引**（与 v1.3.4 rebuild 合同一致）。
5. **单库多项目**：v2 **否定**「每项目 `<project>/.beacon/beacon.db`」为权威；v1.6 `loop-runs.db` 迁入全局库后废弃项目级 ledger 文件。

#### Operator Spine 查询 API（对外唯一读入口）

v1 要求 operator 手拼 `beacon-phase.json`、`run-package.json`、ledger、QA status；v2 **禁止**该模式。

```text
beacon spine show [--project <root>] [--run-id <id>] [--json]   # 默认查 ~/.beacon/beacon.db
beacon spine list [--project <root>] [--status active|failed]    # 跨项目 run 痕迹
beacon spine artifacts <run-id> [--role harness_log|junit|screenshot|...]
beacon spine gate <run-id> [--stage qa|release]
beacon projects list|register|show [--json]                      # 多项目注册与版本线
```

实现契约（`beacon-store` + `beacon-cli`）：

- **读路径**：SQLite 优先组装 `SpineSnapshot`（phase、phases_completed、phase_promoted、next_harness、next_action、gate_summary、artifact_index）。
- **回源**：当 `artifact_refs.exists_flag=1` 且调用方需要正文（`--include-body`、`doctor verify`）时，按 path 读文件并校验 sha256。
- **不写分散 state 文件**：orchestrator 只写 SQLite + blob 文件；不再默认写 `.beacon/loop/runs/<id>/run-state.json` 等多份并行权威。
- **与 v1.6 对齐**：字段语义兼容 `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md` 的 `progress_status` / `authoritative_paths[]`（paths 改为 **artifact_refs 解析结果**）。

```rust
pub struct SpineSnapshot {
    pub run_id: String,
    pub project_key: String,
    pub phase: String,
    pub phases_completed: Vec<String>,
    pub phase_promoted: Option<bool>,
    pub next_harness: String,
    pub next_action: String,
    pub progress_status: String, // done | in_progress | unknown
    pub gate_results: Vec<GateResultSummary>,
    pub artifact_refs: Vec<ArtifactRef>,
}
```

---

## 3. 统一长任务编排器 (替换 beacon-loop + beacon-run)

### 3.1 架构决策

| 维度 | v1 (Node.js) | v2 (Rust) |
|------|-------------|-----------|
| 迭代循环 | spawnSync 阻塞 | **tokio async + tokio::process::Command** |
| 退避策略 | busy-wait CPU 空转 | **tokio::time::sleep + CancellationToken** |
| 状态存储 | 500+ JSON 目录 | **SQLite WAL（运行态唯一写权威）+ blob 文件 + artifact_refs** |
| 进度查询 | 手拼多份 JSON | **`beacon spine show` 单一 API** |
| 中断处理 | 写文件信号 | **AbortHandle + ctrlc handler** |
| Agent 调用 | spawnSync("sqlite3", ...) | **rusqlite 连接池** |
| Phase 控制 | BeaconPhaseController (TS class) | **PhaseController (Rust struct)** |

### 3.2 Goal 执行流程

```
goal <utterance>
  → classify_intent()          // 意图分类 + tiebreak
  → planner_review()           // 规划审查
  → apply_lifecycle_route()    // 生命周期路由决策
  → scan_truth_gap()           // 真理缺口扫描
  → run_truth_fill()           // 真理填充 (如需)
  → PhaseController loop:
      before_iteration() → {run_agent | retry | break}
      run_agent_iteration() → async spawn agent
      after_iteration() → {continue | break}
      phase_promote() → truth→generate→qa→release
  → finalize_delivery()
```

### 3.3 Phase Controller 四阶段

```
truth (Agent) → generate (Agent) → qa (Harness) → release (Harness)
```
- Agent phases: Agent 循环内执行
- Harness phases: Agent 循环外，调用 beacon CLI 子命令

### 3.4 Agent Backend Trait

```rust
#[async_trait]
pub trait AgentBackend: Send + Sync {
    async fn iterate(&self, ctx: &AgentContext) -> Result<IterationResult, AgentError>;
    async fn health_check(&self) -> Result<(), AgentError>;
    async fn abort(&self) -> Result<(), AgentError>;
    fn name(&self) -> &str;
}
```

4 个实现：`CodexBackend`, `ClaudeBackend`, `AcpBackend`, `ImplementHarnessBackend`

---

## 4. 性能目标与手段

| 指标 | v1 (Python) | v2 目标 (Rust) | 手段 |
|------|-------------|----------------|------|
| 冷启动 | ~800ms | **<100ms** | 单二进制, clap 延迟加载 |
| 证据验证 | ~50ms/file | **<10ms** | rayon 并行, SHA-256 硬件加速 (sha2 crate) |
| Gate 计算 | ~200ms | **<50ms** | 增量计算 + DashMap 缓存 + 并行子模块 |
| 状态查询 | ~30ms | **<5ms** | SQLite WAL + 连接池 + 预编译语句 |
| 退避等待 | CPU 100% (busy-wait) | **0% CPU** | tokio::time::sleep 异步 |

---

## 5. Python 兼容层

### 5.1 策略

- PyO3 绑定暴露 `WorkflowStateMachine`, `EvidenceManifest`, `GateEngine`, `Store`, `Orchestrator`
- Python `beacon_v2` 包是薄封装，优先调用 Rust 二进制
- v2 **运行态以 SQLite 为准**；按需导出 v1 形状 JSON（`doctor export` / `--json`）仅供迁移与人工查看，**不作为 gate/resume 读权威**
- MD 需求真相路径与 v1.5.2+ package-authoritative 合同不变
- 33 个 skill 目录完全不变，CLI 路由名保持一致

### 5.2 回退

若 Rust 二进制不存在，Python 封装自动回退到 v1 Python CLI。

---

## 6. CLI 命令结构 (保留 v1 分类法)

```
=== Core (7) ===
beacon prd / user-story / test-case / prototype / implement / qa / release

=== Support (25) ===
beacon spine show|artifacts|gate   # Operator 唯一进度/证据/gate 读面（读 SQLite，按需回源 blob）
beacon board / doctor / status / skill / profile / feedback / help
beacon ask / review / report / archive / freeze / reopen
beacon remember / recall / resume / version / init / debug / deep / design / hooks

=== Compat (4) ===
beacon think (→prd) / workflow / gate / verify (→qa)

=== Labs (12) — BEACON_LABS=1 ===
beacon analyze / brainstorm / kano / moscow / persona / lighthouse / ...

=== Bridge (3) ===
beacon run goal/status/stop/resume/review/doctor
beacon team / ralph-bridge

=== Governor (14) — 映射 beacon-gov-* ===
beacon archive / automation / branch / debug / doctor / help / hooks
beacon learn / lighthouse / metadata / router / status / extract / library
```

---

## 7. SQLite Schema（除 MD 真相外，运行态统一入库）

### 7.0 库位置（本机用户级，单库多项目）

**权威库（唯一默认）**：

```text
~/.beacon/beacon.db          # v2 主库（WAL）
~/.beacon/beacon.db-wal      # SQLite WAL 副作用文件
```

- 由 v1 `~/.beacon/runtime-ledger/runtime-ledger.sqlite3` **迁移合并**（表结构扩展，非双库并存）。
- 环境变量：`BEACON_RUNTIME_LEDGER_ROOT` 仍可覆盖根目录（与 v1 一致），库文件名统一为 `beacon.db`。
- **项目目录** `<project-root>/.beacon/` **只放 blob 与可选导出缓存**，**不**再放 `beacon.db`、`loop-runs.db` 或并行 JSON run-state 权威。

**分库例外（仅明确 opt-in，非默认）**：

- `BEACON_STORE_ISOLATED=1` + 测试夹具：内存库或临时库，不进入 v2 产品默认路径。

```sql
-- 本机注册的全部 Beacon 项目
CREATE TABLE projects (
    project_key TEXT PRIMARY KEY,
    project_root TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    project_kind TEXT NOT NULL DEFAULT 'single_repo', -- single_repo | multi_repo_workspace
    current_stage TEXT NOT NULL DEFAULT '',
    blocker TEXT NOT NULL DEFAULT '',
    next_action TEXT NOT NULL DEFAULT '',
    health_status TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

-- 项目版本线（docs / runtime 分离，支持多版本并存与 catalog 对齐）
CREATE TABLE project_versions (
    project_key TEXT NOT NULL REFERENCES projects(project_key),
    docs_version TEXT NOT NULL,
    runtime_version TEXT NOT NULL DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 0,
    truth_catalog_ref TEXT NOT NULL DEFAULT '',
    onboarded_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (project_key, docs_version)
);
CREATE INDEX idx_project_versions_active ON project_versions(project_key, is_active);

-- Feature 包与生命周期投影（承接 v1.3.4 Runtime Ledger）
CREATE TABLE feature_packages (
    project_key TEXT NOT NULL REFERENCES projects(project_key),
    package_key TEXT NOT NULL,
    docs_version TEXT NOT NULL,
    feature TEXT NOT NULL,
    feature_slug TEXT NOT NULL,
    materials_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (project_key, package_key)
);

CREATE TABLE feature_lifecycle (
    project_key TEXT NOT NULL REFERENCES projects(project_key),
    package_key TEXT NOT NULL,
    feature TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    progress_label TEXT NOT NULL DEFAULT '',
    blocked INTEGER NOT NULL DEFAULT 0,
    blocked_reason TEXT NOT NULL DEFAULT '',
    next_action TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (project_key, package_key)
);

CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    project_key TEXT NOT NULL REFERENCES projects(project_key),
    version TEXT NOT NULL,
    feature TEXT NOT NULL,
    goal TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    delivery_state TEXT NOT NULL DEFAULT '',
    machine_state TEXT NOT NULL DEFAULT '',
    iteration INTEGER NOT NULL DEFAULT 0,
    agent_backend TEXT NOT NULL DEFAULT '',
    worktree_path TEXT NOT NULL DEFAULT '',
    prototype_enabled BOOLEAN NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX idx_runs_project_status ON runs(project_key, status);
CREATE INDEX idx_runs_feature ON runs(project_key, feature);

-- 工作流 / Delivery 阶段机事件
CREATE TABLE lifecycle_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    stage TEXT NOT NULL,
    event TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT '',
    reason_code TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'workflow',
    details_json TEXT NOT NULL DEFAULT '{}',
    attempt_seq INTEGER,
    supersedes_event_id TEXT,
    ts TEXT NOT NULL
);
CREATE INDEX idx_lifecycle_run_stage ON lifecycle_events(run_id, stage);

-- Gate / scorecard 结果（QA、release、implement preflight 等）
CREATE TABLE gate_results (
    gate_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    gate_kind TEXT NOT NULL, -- qa | release | implement | truth | prototype | ...
    stage TEXT NOT NULL,
    verdict TEXT NOT NULL, -- pass | fail | blocked | advisory
    reason_codes TEXT NOT NULL DEFAULT '[]',
    scorecard_json TEXT NOT NULL DEFAULT '{}',
    transaction_id TEXT NOT NULL DEFAULT '',
    source_command TEXT NOT NULL DEFAULT '',
    committed_at TEXT NOT NULL
);
CREATE INDEX idx_gate_run_kind ON gate_results(run_id, gate_kind);

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    stage TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    sink_checksums TEXT NOT NULL DEFAULT '{}',
    committed_at TEXT NOT NULL
);

-- 大文件不进库：只存指针（Spine API 回源用）；path 必须为绝对路径
CREATE TABLE artifact_refs (
    artifact_id TEXT PRIMARY KEY,
    project_key TEXT NOT NULL REFERENCES projects(project_key),
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    artifact_role TEXT NOT NULL, -- harness_log | junit | screenshot | stdout | stderr | evidence_bundle | ...
    path TEXT NOT NULL,            -- absolute path under project_root/.beacon/...
    sha256 TEXT NOT NULL,
    size_bytes INTEGER,
    mime_type TEXT NOT NULL DEFAULT '',
    exists_flag INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE (run_id, path)
);
CREATE INDEX idx_artifact_run_role ON artifact_refs(run_id, artifact_role);

-- 全局 evidence manifest（跨 run 去重索引，可选）
CREATE TABLE evidence_manifest (
    path TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    last_verified_at TEXT NOT NULL
);

CREATE TABLE checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    phase TEXT NOT NULL,
    iteration INTEGER NOT NULL,
    delivery_state TEXT NOT NULL,
    phase_promoted INTEGER, -- NULL unknown, 0 false, 1 true
    next_harness TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- v1 迁移：runtime-ledger.sqlite3 + 各项目 loop-runs.db + JSON 目录 → 单库
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

-- 保留策略：runs 超过 retention_days 归档 blob + 压缩 artifact_refs，不删 MD 真相
```

**不进全局 SQLite 的内容**：

- `features/<slug>/truth.md` 及 requirement package MD（项目内）
- 日志/junit/截图等 **blob 正文**（项目内 `.beacon/evidence/` 等；库内仅绝对 path 索引）
- Host skill 文档、`.cursor/skills/` 等 agent 面材料

**明确废弃（v2 不再作为权威）**：

- `<project-root>/.beacon/beacon.db`（若 v2 草案曾出现，**否决**）
- `<project-root>/.beacon/loop/ledger/loop-runs.db`（迁入全局库）
- 并行 JSON run-state / delivery-state 权威双写

### 7.1 Operator Spine 与 store 模块映射

| CLI | store 模块 | 行为 |
|-----|------------|------|
| `beacon projects list` | `project_dao` + `project_version_dao` | 本机多项目注册与版本线 |
| `beacon spine show` | `run_dao` + `checkpoint` + `gate_dao` | 组装 `SpineSnapshot`（默认连 `~/.beacon/beacon.db`） |
| `beacon spine list` | `run_dao` | 跨项目 / 单项目 run 痕迹列表 |
| `beacon spine artifacts` | `evidence_dao` | 列 artifact_refs；`--verify` 校验 sha256 |
| `beacon spine gate` | `gate_dao` | 返回最近 gate_results |
| `beacon doctor projection rebuild` | migration + 全 DAO | 从 MD + 磁盘 blob + 遗留 v1 JSON **重建索引** |

`beacon-store` crate 新增：`project_dao.rs`、`artifact_dao.rs`；`gate_dao` 从 v1 gate 写回改为 **只写 SQLite**。

---

## 8. 实施阶段

| 阶段 | 内容 | 交付物 | 依赖 |
|------|------|--------|------|
| **P0** | `beacon-core` + `beacon-store` | 状态机 enum, 证据链, SQLite schema §7, **SpineSnapshot**, v1 JSON→SQLite migration | 无 |
| **P1** | `beacon-cli` core 7 命令 | prd/user-story/test-case/prototype/implement/qa/release | P0 |
| **P2** | `beacon-gate` | Gate 引擎, 20+ 子治理模块, scorecard, 增量计算 | P0 |
| **P3** | `beacon-orchestrator` | 统一长任务编排, 4 Agent 后端, resume/stop | P0+P2 |
| **P4** | `beacon-python` | PyO3 绑定, Python CLI 封装, v1 JSON 兼容 | P0-P3 |
| **P5** | `beacon-proto` (可选) | protobuf 二进制格式 | P0 |
| **P6** | Switch-over | Rust v2 默认, Python v1 冻结为 `beacon-legacy` | P4 |

### 并行期共存

- P0-P2：Rust v2 引入 `~/.beacon/beacon.db`（合并 v1 runtime-ledger）；各项目 `.beacon/` 仅 blob；**P0 importer** 从 v1 JSON + `loop-runs.db` 灌入全局库，双写窗口尽量短
- P3：`beacon-orchestrator` 可选替换 `beacon-loop`
- P4：Python `beacon-v2` 包发布
- P6：`beacon` 命令指向 Rust 二进制

---

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| PyO3 构建需 Rust 工具链 | CI 预编译 wheel，用户 `pip install beacon-v2` 无需 Rust |
| SQLite 写并发限制 | WAL 模式 + 单用户 CLI 场景足够；多 agent 写入通过队列化 |
| JSON 契约兼容 | 仅 **导出/迁移** 路径保持 v1 形状；运行态读权威已切 SQLite |
| v1 多源 state 残留 | P0 importer 合并 runtime-ledger + loop-runs.db；P6 后禁止项目级 db 与新 JSON run-state 权威 |
| 全局库路径争议 | 默认 `~/.beacon/beacon.db`；`BEACON_RUNTIME_LEDGER_ROOT` 仅改根目录不改「单库」原则 |
| Blob 路径漂移 | `artifact_refs.exists_flag` + doctor verify；hash 不一致 fail-closed |
| Worktree 边缘情况 | 先实现 current-branch 模式，worktree 作为增强 |
| 增量 gate 缓存持久化 | SQLite 持久化缓存元数据，启动时加载 |
| 版本单一真相 | beacon-core::version 从 CARGO_PKG_VERSION 生成，SQLite 维护 version_truth 表 |

---

## 10. 验证方案

### 10.1 P0 验证
- `cargo test` — 状态机转换穷举测试、证据链 hash 测试、SQLite CRUD 测试
- 非法转换编译期报错验证（删除 match arm 确认编译失败）

### 10.2 P1 验证
- `beacon prd --feature test-slug` 产出与 v1 一致的 JSON 结构
- `beacon status --json` 输出与 v1 格式兼容

### 10.3 P2 验证
- `beacon release check --version v1.6.0` 输出与 v1 gate.py 一致的 reason codes
- 增量计算：修改一个文件后，仅相关子模块重算

### 10.3 P3 验证
- `beacon run goal "add login feature" --agent codex` 完整交付流水线
- SIGINT 中断后 `beacon run resume <id>` 恢复
- `beacon run stop <id> --force` 强制终止

### 10.4 P4 验证
- `pip install beacon-v2 && python -c "import beacon_v2; ..."` PyO3 调用正常
- 现有 33 个 skill 通过 Python 封装调用 Rust 核心功能正常

### 10.5 P6 验证
- 现有 `.beacon/` JSON 与 blob **迁移到 SQLite + artifact_refs 无损**；MD 真相路径不变
- `beacon spine show` 为唯一推荐进度查询；不再要求手拼四份 state 文件
- `beacon version` 单一来源，不再有三处不一致
- Gate 结果只读 `gate_results` 表即可复现 release/qa 阻断原因
