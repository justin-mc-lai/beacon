# Beacon v2 重写计划

## Context

Beacon v1 (Python + Node.js) 存在 10 个核心架构缺陷：无主流程显式状态机、阶段定义散落 4+ 模块、巨型单文件 (prototype_utils.py 315KB)、纯同步 Python、beacon-loop busy-wait、SQLite 每次 spawn 新进程、缺少 crash/timeout 状态、500+ run 目录无清理、beacon-loop/beacon-run 功能重叠、版本信息三处不一致。

核心洞察：**Prompt 约束只是建议，CLI 层级强制执行才是法律。Agent 会适应并绕过软性限制 — 修复必须是架构层级的。**

**决策**：Rust 核心 + Python 兼容层 | 全新重写 v2 | 双层状态机（类型 + 运行时）

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
│   │   └── src/{pool, migration, run_dao, lifecycle_dao, transaction_dao,
│   │             evidence_dao, gate_dao, scorecard_dao, memory_dao, skill_dao}.rs
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

---

## 3. 统一长任务编排器 (替换 beacon-loop + beacon-run)

### 3.1 架构决策

| 维度 | v1 (Node.js) | v2 (Rust) |
|------|-------------|-----------|
| 迭代循环 | spawnSync 阻塞 | **tokio async + tokio::process::Command** |
| 退避策略 | busy-wait CPU 空转 | **tokio::time::sleep + CancellationToken** |
| 状态存储 | 500+ JSON 目录 | **SQLite WAL + checkpoint 表** |
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
- `.beacon/` 目录 JSON 契约保持 v1 格式兼容 (serde_json 输出与 Python json.dumps 一致)
- 33 个 skill 目录完全不变，CLI 路由名保持一致

### 5.2 回退

若 Rust 二进制不存在，Python 封装自动回退到 v1 Python CLI。

---

## 6. CLI 命令结构 (保留 v1 分类法)

```
=== Core (7) ===
beacon prd / user-story / test-case / prototype / implement / qa / release

=== Support (25) ===
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

## 7. SQLite Schema (替换 500+ JSON 目录)

```sql
CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    feature TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    prototype_enabled BOOLEAN NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE TABLE lifecycle_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    stage TEXT NOT NULL,
    event TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'workflow',
    evidence_refs TEXT NOT NULL DEFAULT '[]',
    attempt_seq INTEGER,
    supersedes_event_id TEXT,
    ts TEXT NOT NULL
);
CREATE INDEX idx_lifecycle_run_stage ON lifecycle_events(run_id, stage);

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    stage TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    sink_checksums TEXT NOT NULL DEFAULT '{}',
    committed_at TEXT NOT NULL
);

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
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 自动清理：替代 500+ 目录无清理问题
-- runs 超过 retention_days 的可自动归档
```

---

## 8. 实施阶段

| 阶段 | 内容 | 交付物 | 依赖 |
|------|------|--------|------|
| **P0** | `beacon-core` + `beacon-store` | 状态机 enum, 证据链, SQLite CRUD, migration | 无 |
| **P1** | `beacon-cli` core 7 命令 | prd/user-story/test-case/prototype/implement/qa/release | P0 |
| **P2** | `beacon-gate` | Gate 引擎, 20+ 子治理模块, scorecard, 增量计算 | P0 |
| **P3** | `beacon-orchestrator` | 统一长任务编排, 4 Agent 后端, resume/stop | P0+P2 |
| **P4** | `beacon-python` | PyO3 绑定, Python CLI 封装, v1 JSON 兼容 | P0-P3 |
| **P5** | `beacon-proto` (可选) | protobuf 二进制格式 | P0 |
| **P6** | Switch-over | Rust v2 默认, Python v1 冻结为 `beacon-legacy` | P4 |

### 并行期共存

- P0-P2：Rust v2 与 Python v1 共享 `.beacon/` 目录，互不干扰
- P3：`beacon-orchestrator` 可选替换 `beacon-loop`
- P4：Python `beacon-v2` 包发布
- P6：`beacon` 命令指向 Rust 二进制

---

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| PyO3 构建需 Rust 工具链 | CI 预编译 wheel，用户 `pip install beacon-v2` 无需 Rust |
| SQLite 写并发限制 | WAL 模式 + 单用户 CLI 场景足够；多 agent 写入通过队列化 |
| JSON 契约兼容 | serde_json 自定义 formatter 确保输出与 v1 Python 一致 |
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
- 现有 `.beacon/` 目录数据迁移到 SQLite 无损
- `beacon version` 单一来源，不再有三处不一致
