# Beacon Implementation Tasks Ledger

- feature: `beacon-v2-rust-kernel-redesign`
- version: `v2.0.0`
- plan_id: `plan-beacon-v2-rust-kernel-redesign-r20`
- revision_id: `R20`
- progress: `49/148`
- status: `blocked`
- next_task: `ITASK-002` AC-002 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文
- blocked_tasks: `99`

## Recovery
- progress_json: `docs/beacon/v2.0.0/.machine/execution/implementation-plan-beacon-v2-rust-kernel-redesign.progress.json`
- canonical_plan_json: `docs/beacon/v2.0.0/.machine/execution/implementation-plan-beacon-v2-rust-kernel-redesign.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` AC-001 Agent 写代码→跑 Eval→发现问题→修→再测，自动闭环
  - tests=TEST-001
[-] `ITASK-002` AC-002 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文
  - blocked=verification_failed | tests=TEST-002 | depends_on=ITASK-001 | next
[-] `ITASK-003` AC-003 show [--json]`（机器级多项目）。
  - blocked=verification_failed | tests=TEST-003 | depends_on=ITASK-002
[x] `ITASK-004` AC-004 clean preflight；branch 模式 P2；**worktree 全模式 P3（AC-099）**
  - tests=TEST-004 | depends_on=ITASK-003
[-] `ITASK-005` AC-005 acp:*>` CLI 直接选 agent 跑长任务编码落地；agent 选择映射到对应 AgentBackend；loop 在 CLI...
  - blocked=verification_failed | tests=TEST-005 | depends_on=ITASK-004
[-] `ITASK-006` AC-006 p95 < 100ms 本地
  - blocked=verification_failed | tests=TEST-006 | depends_on=ITASK-005
[-] `ITASK-007` AC-007 p95 < 50ms
  - blocked=verification_failed | tests=TEST-007 | depends_on=ITASK-006
[-] `ITASK-008` AC-008 p95 < 200ms
  - blocked=verification_failed | tests=TEST-008 | depends_on=ITASK-007
[-] `ITASK-009` AC-009 p95 < 50ms
  - blocked=verification_failed | tests=TEST-009 | depends_on=ITASK-008
[-] `ITASK-010` AC-010 p95 < 10ms
  - blocked=verification_failed | tests=TEST-010 | depends_on=ITASK-009
[-] `ITASK-011` AC-011 < 60s 典型 fixture
  - blocked=verification_failed | tests=TEST-011 | depends_on=ITASK-010
[-] `ITASK-012` AC-012 < 100ms 不含 agent
  - blocked=verification_failed | tests=TEST-012 | depends_on=ITASK-011
[-] `ITASK-013` AC-013 软上限 500MB
  - blocked=verification_failed | tests=TEST-013 | depends_on=ITASK-012
[-] `ITASK-014` AC-014 beacon-loop / v1 CLI 并行
  - blocked=verification_failed | tests=TEST-014 | depends_on=ITASK-013
[-] `ITASK-015` AC-015 迁移为可选对照，不强迫退役 v1
  - blocked=verification_failed | tests=TEST-015 | depends_on=ITASK-014
[-] `ITASK-016` AC-016 结构性消除
  - blocked=verification_failed | tests=TEST-016 | depends_on=ITASK-015
[-] `ITASK-017` AC-017 三层+Spine+projection rebuild
  - blocked=verification_failed | tests=TEST-017 | depends_on=ITASK-016
[-] `ITASK-018` AC-018 workspace
  - blocked=verification_failed | tests=TEST-018 | depends_on=ITASK-017
[-] `ITASK-019` AC-019 双 FSM+benchmark
  - blocked=verification_failed | tests=TEST-019 | depends_on=ITASK-018
[-] `ITASK-020` AC-020 六能力 surface + legacy removal + progressive disclosure + BranchContext...
  - blocked=verification_failed | tests=TEST-020 | depends_on=ITASK-019
[-] `ITASK-021` AC-021 九表+DAO
  - blocked=verification_failed | tests=TEST-021 | depends_on=ITASK-020
[-] `ITASK-022` AC-022 P0–P6
  - blocked=verification_failed | tests=TEST-022 | depends_on=ITASK-021
[-] `ITASK-023` AC-023 可执行缓解
  - blocked=verification_failed | tests=TEST-023 | depends_on=ITASK-022
[-] `ITASK-024` AC-024 evaluator 裁决
  - blocked=verification_failed | tests=TEST-024 | depends_on=ITASK-023
[-] `ITASK-025` AC-025 TIG + planner multi-agent + doctor 路由
  - blocked=verification_failed | tests=TEST-025 | depends_on=ITASK-024
[-] `ITASK-026` AC-026 beacon-rs scaffold 已完成
  - blocked=verification_failed | tests=TEST-026 | depends_on=ITASK-025
[-] `ITASK-027` AC-027 用户拒绝延期
  - blocked=verification_failed | tests=TEST-027 | depends_on=ITASK-026
[-] `ITASK-028` AC-028 v1/v2 skill+CLI 语言分叉，需合并互不影响
  - blocked=verification_failed | tests=TEST-028 | depends_on=ITASK-027
[-] `ITASK-029` AC-029 落地稳依赖可测 skill 资产
  - blocked=verification_failed | tests=TEST-029 | depends_on=ITASK-028
[-] `ITASK-030` AC-030 禁止 Darwin 式自动改 SKILL.md
  - blocked=verification_failed | tests=TEST-030 | depends_on=ITASK-029
[-] `ITASK-031` AC-031 planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止...
  - blocked=verification_failed | tests=TEST-031 | depends_on=ITASK-030
[-] `ITASK-032` AC-032 R6 refreeze：六 public skill 渐进式披露 contract；内部保留 branch governance / do...
  - blocked=verification_failed | tests=TEST-032 | depends_on=ITASK-031
[-] `ITASK-033` AC-033 R7 refreeze：TraceSpine.v1 / TraceContext.v1 成为 run authority；loop/imp...
  - blocked=verification_failed | tests=TEST-033 | depends_on=ITASK-032
[x] `ITASK-034` AC-034 R8 refreeze：将 canonical truth author/refreeze/commit -> feature workt...
  - tests=TEST-034 | depends_on=ITASK-033
[-] `ITASK-035` AC-035 ，后者是 L1 MD / L2 SQLite / L3 Blob**）：
  - blocked=verification_failed | tests=TEST-035 | depends_on=ITASK-034
[-] `ITASK-036` AC-036 （stop-when maker≠checker）→ v2 AC-105
  - blocked=verification_failed | tests=TEST-036 | depends_on=ITASK-035
[-] `ITASK-037` AC-037 **）
  - blocked=verification_failed | tests=TEST-037 | depends_on=ITASK-036
[-] `ITASK-038` AC-038 ）
  - blocked=verification_failed | tests=TEST-038 | depends_on=ITASK-037
[-] `ITASK-039` AC-039 ..114）
  - blocked=verification_failed | tests=TEST-039 | depends_on=ITASK-038
[-] `ITASK-040` AC-040 ..116）
  - blocked=verification_failed | tests=TEST-040 | depends_on=ITASK-039
[-] `ITASK-041` AC-041 ..123）
  - blocked=verification_failed | tests=TEST-041 | depends_on=ITASK-040
[x] `ITASK-042` AC-042 **：v2 core closure **不包含** `beacon-python` / PyO3 / v1 Python runtime...
  - tests=TEST-042 | depends_on=ITASK-041
[-] `ITASK-043` AC-043 **：`~/.beacon/beacon.db` 不得存储可编辑的需求正文；只可存 metadata、FSM、gate、artifact 指针。
  - blocked=verification_failed | tests=TEST-043 | depends_on=ITASK-042
[-] `ITASK-044` AC-044 **：`.beacon/qa/*.json`、`.beacon/gate-report.json` 等 v1 投影在 v2 为 **非权威...
  - blocked=verification_failed | tests=TEST-044 | depends_on=ITASK-043
[-] `ITASK-045` AC-045 **：**禁止** `<project>/.beacon/beacon.db` 作为运行态权威（v2 明确否决 per-project DB）。
  - blocked=verification_failed | tests=TEST-045 | depends_on=ITASK-044
[-] `ITASK-046` AC-046 **：**禁止** `<project>/.beacon/loop/ledger/loop-runs.db` 作为 v2 权威；v1.6...
  - blocked=verification_failed | tests=TEST-046 | depends_on=ITASK-045
[-] `ITASK-047` AC-047 **：Blob 文件变更时 `artifact_refs` 必须更新 `content_hash`；hash 不匹配时 Spine 标记...
  - blocked=verification_failed | tests=TEST-047 | depends_on=ITASK-046
[-] `ITASK-048` AC-048 **：`beacon doctor projection rebuild` 须能从已注册 `project_root` 的 MD + bl...
  - blocked=verification_failed | tests=TEST-048 | depends_on=ITASK-047
[-] `ITASK-049` AC-049 存储原则（Plan §2.5）
  - blocked=verification_failed | tests=TEST-049 | depends_on=ITASK-048
[-] `ITASK-050` AC-050 **：每次 gate 评估写入 `gate_results`（pass/fail/blocked + reason_codes JSON）。
  - blocked=verification_failed | tests=TEST-050 | depends_on=ITASK-049
[-] `ITASK-051` AC-051 **：每次 run 启动写入 `runs`；checkpoint 写入 `checkpoints`。
  - blocked=verification_failed | tests=TEST-051 | depends_on=ITASK-050
[-] `ITASK-052` AC-052 **：Spine 查询 **DB-first**；blob 仅当 `artifact_refs` 存在且 hash 有效时拼接。
  - blocked=verification_failed | tests=TEST-052 | depends_on=ITASK-051
[-] `ITASK-053` AC-053 **：v1 JSON 运行态只允许 **export/import 迁移**，不得与 DB 双写竞争权威。
  - blocked=verification_failed | tests=TEST-053 | depends_on=ITASK-052
[-] `ITASK-054` AC-054 Operator Spine API（Plan §2.5）
  - blocked=verification_failed | tests=TEST-054 | depends_on=ITASK-053
[-] `ITASK-055` AC-055 **：必须实现 `beacon spine list [--project PATH] [--status STATUS] [--json]`。
  - blocked=verification_failed | tests=TEST-055 | depends_on=ITASK-054
[-] `ITASK-056` AC-056 **：必须实现 `beacon spine artifacts <run-id> [--json]`。
  - blocked=verification_failed | tests=TEST-056 | depends_on=ITASK-055
[-] `ITASK-057` AC-057 **：必须实现 `beacon spine gate <feature> [--version vX] [--json]`。
  - blocked=verification_failed | tests=TEST-057 | depends_on=ITASK-056
[-] `ITASK-058` AC-058 **：crate 依赖方向：`cli -> {gate, orchestrator, store, core}`；`store -> co...
  - blocked=verification_failed | tests=TEST-058 | depends_on=ITASK-057
[-] `ITASK-059` AC-059 **：v2.0.0 **不交付** `beacon-proto`/gRPC（**D-V2-001 accepted defer**）；CL...
  - blocked=verification_failed | tests=TEST-059 | depends_on=ITASK-058
[-] `ITASK-060` AC-060 **：单文件模块超过 500 行须拆分或 ADR 说明例外（对齐 D-02）。
  - blocked=verification_failed | tests=TEST-060 | depends_on=ITASK-059
[-] `ITASK-061` AC-061 **：阶段转换表显式编码；非法转换返回 typed error + reason_code。
  - blocked=verification_failed | tests=TEST-061 | depends_on=ITASK-060
[-] `ITASK-062` AC-062 **：`Blocked` 必须携带 `reason_codes: Vec<String>` 与可选 `blocking_gate`。
  - blocked=verification_failed | tests=TEST-062 | depends_on=ITASK-061
[-] `ITASK-063` AC-063 **：`Skipped` 仅允许带 `user_accepted_deferral_id` 或 deferral ledger 引用。
  - blocked=verification_failed | tests=TEST-063 | depends_on=ITASK-062
[-] `ITASK-064` AC-064 **：`Crashed` / `TimedOut` / `Interrupted` 须写入 `lifecycle_events` 且可触发...
  - blocked=verification_failed | tests=TEST-064 | depends_on=ITASK-063
[-] `ITASK-065` AC-065 **：Delivery 运行时 12 状态在 `beacon-core` 定义并与 `runs.status` CHECK 一致。
  - blocked=verification_failed | tests=TEST-065 | depends_on=ITASK-064
[-] `ITASK-066` AC-066 **：plan 主链节点转换须写入 `lifecycle_events`（可审计，非仅内存）。
  - blocked=verification_failed | tests=TEST-066 | depends_on=ITASK-065
[-] `ITASK-067` AC-067 **：`Paused` / `Stopping` / `Stopped` 与 v1 beacon-loop graceful+force...
  - blocked=verification_failed | tests=TEST-067 | depends_on=ITASK-066
[-] `ITASK-068` AC-068 **：`Repairing` 须持久化 repair payload 到 `artifact_refs`。
  - blocked=verification_failed | tests=TEST-068 | depends_on=ITASK-067
[-] `ITASK-069` AC-069 **：`AwaitingQa` 仅在 `import-evidence` 成功后可进入。
  - blocked=verification_failed | tests=TEST-069 | depends_on=ITASK-068
[-] `ITASK-070` AC-070 **：`Closed` 仅 release gate pass 或用户显式 archive；orchestrator **不得**自设 C...
  - blocked=verification_failed | tests=TEST-070 | depends_on=ITASK-069
[-] `ITASK-071` AC-071 **：`EvidenceChain` 含 `manifest_hash`、`signature_chain`、`artifact_refs...
  - blocked=verification_failed | tests=TEST-071 | depends_on=ITASK-070
[-] `ITASK-072` AC-072 **：import 断链 fail-closed → `EVIDENCE_CHAIN_BROKEN`。
  - blocked=verification_failed | tests=TEST-072 | depends_on=ITASK-071
[-] `ITASK-073` AC-073 **：v1 `.beacon/evidence-signature-chain.json` 可迁移为 v2 记录。
  - blocked=verification_failed | tests=TEST-073 | depends_on=ITASK-072
[-] `ITASK-074` AC-074 **：启动前 `truth-map resolve`；blocked → exit != 0 + 推荐 `beacon-gen-change`。
  - blocked=verification_failed | tests=TEST-074 | depends_on=ITASK-073
[-] `ITASK-075` AC-075 **（P2）：`SubprocessBackend` 完成 1 次真 integration iteration（可控测试 harness...
  - blocked=verification_failed | tests=TEST-075 | depends_on=ITASK-074
[-] `ITASK-076` AC-076 **（P3）：`AcpBackend`（CLI `acp:<target>`）完成 1 次真 integration iteration；...
  - blocked=verification_failed | tests=TEST-076 | depends_on=ITASK-075
[-] `ITASK-077` AC-077 **：checkpoint resume 后 iteration 递增；notes 注入写入 `lifecycle_events`（可审计）。
  - blocked=verification_failed | tests=TEST-077 | depends_on=ITASK-076
[-] `ITASK-078` AC-078 **：`stop_when` 移植 v1 `stop-when-gate`（含 gate pass 早停）。
  - blocked=verification_failed | tests=TEST-078 | depends_on=ITASK-077
[-] `ITASK-079` AC-079 **：orchestrator **禁止**输出 QA pass / release ready / feature complete v...
  - blocked=verification_failed | tests=TEST-079 | depends_on=ITASK-078
[-] `ITASK-080` AC-080 **：Phase Controller 四阶段写入 `runs.metadata_json`；phase 转换写 `lifecycle_e...
  - blocked=verification_failed | tests=TEST-080 | depends_on=ITASK-079
[-] `ITASK-081` AC-081 **（P3）：Developer Feedback Loop 人注入 checkpoint——`beacon-v2 run --feedb...
  - blocked=verification_failed | tests=TEST-081 | depends_on=ITASK-080
[-] `ITASK-082` AC-082 **（P3）：Loop Engineering 三层 Loop 可观测——spine snapshot 含 `loop_layer` 字段...
  - blocked=verification_failed | tests=TEST-082 | depends_on=ITASK-081
[-] `ITASK-083` AC-083 **：双轨运行时选择必须 **显式**（例如独立 `beacon-v2` 二进制，或 `beacon --runtime v2` / 等价...
  - blocked=verification_failed | tests=TEST-083 | depends_on=ITASK-082
[-] `ITASK-084` AC-084 **：`BEACON_STORE_PATH` 测试隔离；生产默认 `~/.beacon/beacon.db`。
  - blocked=verification_failed | tests=TEST-084 | depends_on=ITASK-083
[-] `ITASK-085` AC-085 **：在 **v2 runtime 路径内**，任何把 v1 Python/legacy skill 当执行后端的请求必须 fail-cl...
  - blocked=verification_failed | tests=TEST-085 | depends_on=ITASK-084
[-] `ITASK-086` AC-086 **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其...
  - blocked=verification_failed | tests=TEST-086 | depends_on=ITASK-085
[-] `ITASK-087` AC-087 **：spine/projects/workflow/truth-map/implement/qa/release/run 子命令可解析且...
  - blocked=verification_failed | tests=TEST-087 | depends_on=ITASK-086
[-] `ITASK-088` AC-088 **：spine/projects/run 支持 `--json` 且 schema 可校验。
  - blocked=verification_failed | tests=TEST-088 | depends_on=ITASK-087
[-] `ITASK-089` AC-089 **：v1 reason_codes 对齐：`gate_results.reason_codes_json` 失败样例须含 documen...
  - blocked=verification_failed | tests=TEST-089 | depends_on=ITASK-088
[-] `ITASK-090` AC-090 **：`project_versions`（id, project_id, version, docs_root, is_current）
  - blocked=verification_failed | tests=TEST-090 | depends_on=ITASK-089
[-] `ITASK-091` AC-091 **：`feature_packages`（id, project_version_id, slug, truth_path, tests...
  - blocked=verification_failed | tests=TEST-091 | depends_on=ITASK-090
[-] `ITASK-092` AC-092 **：`feature_lifecycle`（feature_id, stage, status, reason_codes_json,...
  - blocked=verification_failed | tests=TEST-092 | depends_on=ITASK-091
[-] `ITASK-093` AC-093 **：`lifecycle_events`（id, feature_id, run_id, event_type, payload_jso...
  - blocked=verification_failed | tests=TEST-093 | depends_on=ITASK-092
[-] `ITASK-094` AC-094 **：`gate_results`（id, feature_id, gate_type, verdict, reason_codes_js...
  - blocked=verification_failed | tests=TEST-094 | depends_on=ITASK-093
[-] `ITASK-095` AC-095 **：`artifact_refs`（id, run_id, kind, abs_path, content_hash, size_byt...
  - blocked=verification_failed | tests=TEST-095 | depends_on=ITASK-094
[-] `ITASK-096` AC-096 **：`checkpoints`（id, run_id, iteration, state_json, created_at）
  - blocked=verification_failed | tests=TEST-096 | depends_on=ITASK-095
[-] `ITASK-097` AC-097 **：`beacon-store` 提供 ProjectDao, FeatureDao, RunDao, GateDao, Artifac...
  - blocked=verification_failed | tests=TEST-097 | depends_on=ITASK-096
[-] `ITASK-098` AC-098 **：migration `v1_runtime_ledger`：自 `~/.beacon/runtime-ledger/runtime-...
  - blocked=verification_failed | tests=TEST-098 | depends_on=ITASK-097
[-] `ITASK-099` AC-099 **：migration `v1_loop_ledger`：扫描各项目 `loop-runs.db` 一次性导入。
  - blocked=verification_failed | tests=TEST-099 | depends_on=ITASK-098
[-] `ITASK-100` AC-100 **：migration `v1_qa_projection`：可选历史只读导入。
  - blocked=verification_failed | tests=TEST-100 | depends_on=ITASK-099
[-] `ITASK-101` AC-101 **：schema `user_version` 管理；降级禁止。
  - blocked=verification_failed | tests=TEST-101 | depends_on=ITASK-100
[-] `ITASK-102` AC-102 **：`SpineDao::snapshot` 联查 lifecycle + run + gate + artifacts。
  - blocked=verification_failed | tests=TEST-102 | depends_on=ITASK-101
[-] `ITASK-103` AC-103 **：`list` 支持 lifecycle/run status 过滤。
  - blocked=verification_failed | tests=TEST-103 | depends_on=ITASK-102
[x] `ITASK-104` AC-104 **：`artifact_refs.abs_path` 必须绝对路径。
  - tests=TEST-104 | depends_on=ITASK-103
[x] `ITASK-105` AC-105 **：migration 前自动备份 runtime-ledger 与既有 DB。
  - tests=TEST-105 | depends_on=ITASK-104
[x] `ITASK-106` AC-106 **：双写期 **单一写者**；双向同时写须测试失败。
  - tests=TEST-106 | depends_on=ITASK-105
[x] `ITASK-107` AC-107 **：v2 harness surface / cross-track isolation 回归失败 → `beacon-gov-doct...
  - tests=TEST-107 | depends_on=ITASK-106
[x] `ITASK-108` AC-108 **：v2 benchmark 相对 baseline 回退 >10% 阻断 **v2 P6 成熟度出口**；不授权、不要求关停 v1 轨。
  - tests=TEST-108 | depends_on=ITASK-107
[x] `ITASK-109` AC-109 **：全量 AC closure 由 evaluator 裁决；generator/implementer 不得自证 release re...
  - tests=TEST-109 | depends_on=ITASK-108
[x] `ITASK-110` AC-110 **：frozen package 权威高于 plan；plan 变更须 promote。
  - tests=TEST-110 | depends_on=ITASK-109
[x] `ITASK-111` AC-111 **（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 Rust gate；`--m...
  - tests=TEST-111 | depends_on=ITASK-110
[x] `ITASK-112` AC-112 **：v1 Python / Node / v1 skill 面 **不进入 v2 core closure 的验收依赖**；它们作为 *...
  - tests=TEST-112 | depends_on=ITASK-111
[x] `ITASK-113` AC-113 **：每轮 plan/truth/review/brainstorm 必须保存 prompt snapshot hash，并标记 acce...
  - tests=TEST-113 | depends_on=ITASK-112
[x] `ITASK-114` AC-114 **：intent confidence 低、强意图冲突、scope 未确认或 deferral 未拍板时，truth freeze fa...
  - tests=TEST-114 | depends_on=ITASK-113
[x] `ITASK-115` AC-115 **：loop 启动必须读取 `decision_packet.v1`；缺失、过期或引用未接受 prompt snapshot 时不得进入...
  - tests=TEST-115 | depends_on=ITASK-114
[x] `ITASK-116` AC-116 **：implement admission 必须同时验证 truth_frozen、decision_packet_current、de...
  - tests=TEST-116 | depends_on=ITASK-115
[x] `ITASK-117` AC-117 **：stagnation detector 基于 agent trace 确定性识别 repeat_failure / repeat_l...
  - tests=TEST-117 | depends_on=ITASK-116
[x] `ITASK-118` AC-118 **：remediation sandbox 在 governed worktree 内执行 overlay/eval/rollback；...
  - tests=TEST-118 | depends_on=ITASK-117
[x] `ITASK-119` AC-119 **：loop guardrails 包含 pattern registry、failure catalog、token budget、r...
  - tests=TEST-119 | depends_on=ITASK-118
[x] `ITASK-120` AC-120 **：qa-evidence 必须产出 confidence_chain 与 truth-derived business FSM cov...
  - tests=TEST-120 | depends_on=ITASK-119
[x] `ITASK-121` AC-121 **：QA defect 必须形成 defect -> fix -> regression evidence chain；缺段 `repa...
  - tests=TEST-121 | depends_on=ITASK-120
[x] `ITASK-122` AC-122 **：closure evidence 必须包含可执行行为验证、至少一个有效断言、AC/TC 绑定 artifact 与运行佐证；纯静态...
  - tests=TEST-122 | depends_on=ITASK-121
[x] `ITASK-123` AC-123 **：release human gate 是不变量；`auto_decide=true` 不得触发 release gate 通过。
  - tests=TEST-123 | depends_on=ITASK-122
[x] `ITASK-124` AC-124 **：skill loader 必须采用 progressive disclosure；默认只加载 public `SKILL.md`，按...
  - tests=TEST-124 | depends_on=ITASK-123
[x] `ITASK-125` AC-125 **：六个 public skill 都必须提供 route examples；示例覆盖 `truth review -> decisio...
  - tests=TEST-125 | depends_on=ITASK-124
[x] `ITASK-126` AC-126 **：`BranchContext.v1` 是所有写入/agent/evidence/release harness 的共同输入，字段至少...
  - tests=TEST-126 | depends_on=ITASK-125
[x] `ITASK-127` AC-127 **：branch/workspace governance 是 hard gate；任何 generator/implement/qa-...
  - tests=TEST-127 | depends_on=ITASK-126
[x] `ITASK-128` AC-128 **：Harness boundary 以 reason_code enforce：planner/truth 不实现，implement...
  - tests=TEST-128 | depends_on=ITASK-127
[x] `ITASK-129` AC-129 **：`loop start` 必须创建 `TraceContext.v1` 并绑定 BranchContext、decision_pac...
  - tests=TEST-129 | depends_on=ITASK-128
[x] `ITASK-130` AC-130 **：`implement` / `qa-evidence` / `release` 必须验证 trace completeness；tr...
  - tests=TEST-130 | depends_on=ITASK-129
[x] `ITASK-131` AC-131 **：`stagnation-report.v1` 必须引用 trace event range、reason_code、failure...
  - tests=TEST-131 | depends_on=ITASK-130
[x] `ITASK-132` AC-132 **：`remediation-report.v1` 必须引用 stagnation report、overlay/eval/rollba...
  - tests=TEST-132 | depends_on=ITASK-131
[x] `ITASK-133` AC-133 **：truth/change/refreeze 只能在 `truth_canonical_branch`（默认 main，缺失时 mas...
  - tests=TEST-133 | depends_on=ITASK-132
[x] `ITASK-134` AC-134 **：refreeze transaction 必须拒绝 reason-only / machine-only 变化；revision i...
  - tests=TEST-134 | depends_on=ITASK-133
[x] `ITASK-135` AC-135 **：canonical refreeze 只有在 canonical branch 提交后才成为可消费 baseline；未提交 ref...
  - tests=TEST-135 | depends_on=ITASK-134
[x] `ITASK-136` AC-136 **：feature worktree 中发现 stale feature-local refreeze/projection dirty...
  - tests=TEST-136 | depends_on=ITASK-135
[x] `ITASK-137` AC-137 **：feature/dev branch 进入 implement 前必须包含 canonical `truth_baseline_co...
  - tests=TEST-137 | depends_on=ITASK-136
[x] `ITASK-138` AC-138 **：标准流 admission evidence bundle 必须包含 truth-map verify、verify-materia...
  - tests=TEST-138 | depends_on=ITASK-137
[x] `ITASK-139` AC-139 **：标准流必须可 idempotent resume；已对齐步骤重复执行时返回 `up_to_date` / `pass`，不得因重复执...
  - tests=TEST-139 | depends_on=ITASK-138
[x] `ITASK-140` AC-140 **：标准执行流通过六 public skill 的 progressive examples 暴露，不得新增第七个 public ski...
  - tests=TEST-140 | depends_on=ITASK-139
[x] `ITASK-141` AC-141 **：Beacon 产品策略为长期双轨：`track_v1`（Python CLI + v1 skill 面）与 `track_v2`（R...
  - tests=TEST-141 | depends_on=ITASK-140
[x] `ITASK-142` AC-142 **：双轨隔离契约——代码树、CLI 入口、skill 根、docs version tree、CI job 必须可分轨合并；同一 PR...
  - tests=TEST-142 | depends_on=ITASK-141
[x] `ITASK-143` AC-143 **：运行时选择必须显式（对齐 AC-060）；禁止 v2 路径执行 v1 backend，禁止 v1 路径把请求静默升级为 v2 并改写...
  - tests=TEST-143 | depends_on=ITASK-142
[x] `ITASK-144` AC-144 **：迁移/导入工具可以只读对照另一轨状态，但不得在双写期成为第二写者（延续 AC-093 单写者原则，按轨分别强制）。
  - tests=TEST-144 | depends_on=ITASK-143
[x] `ITASK-145` AC-145 **：统一评分必须包含 **结构质量**（SKILL.md/package/HARD GATE/progressive 合规，对齐 ski...
  - tests=TEST-145 | depends_on=ITASK-144
[x] `ITASK-146` AC-146 **：skill 评分产物权威为 `runtime_evidence_only`；**不得**替代 `qa-evidence` forma...
  - tests=TEST-146 | depends_on=ITASK-145
[x] `ITASK-147` AC-147 **：评分执行者与被评 skill 的「修改建议作者」在流程上必须可分离（独立评分会话或独立 grader）；禁止同一无审计步骤既改 sk...
  - tests=TEST-147 | depends_on=ITASK-146
[x] `ITASK-148` AC-148 **：v1 `beacon eval` 既有 scorecard 维度可映射进统一 schema，但发布门必须以统一 schema 的稳定...
  - tests=TEST-148 | depends_on=ITASK-147

## Blockers
- AC-002 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文
- AC-003 show [--json]`（机器级多项目）。
- AC-005 acp:*>` CLI 直接选 agent 跑长任务编码落地；agent 选择映射到对应 AgentBackend；loop 在 CLI...
- AC-006 p95 < 100ms 本地
- AC-007 p95 < 50ms
- AC-008 p95 < 200ms
- AC-009 p95 < 50ms
- AC-010 p95 < 10ms
- AC-011 < 60s 典型 fixture
- AC-012 < 100ms 不含 agent
- AC-013 软上限 500MB
- AC-014 beacon-loop / v1 CLI 并行
- AC-015 迁移为可选对照，不强迫退役 v1
- AC-016 结构性消除
- AC-017 三层+Spine+projection rebuild
- AC-018 workspace
- AC-019 双 FSM+benchmark
- AC-020 六能力 surface + legacy removal + progressive disclosure + BranchContext...
- AC-021 九表+DAO
- AC-022 P0–P6
- AC-023 可执行缓解
- AC-024 evaluator 裁决
- AC-025 TIG + planner multi-agent + doctor 路由
- AC-026 beacon-rs scaffold 已完成
- AC-027 用户拒绝延期
- AC-028 v1/v2 skill+CLI 语言分叉，需合并互不影响
- AC-029 落地稳依赖可测 skill 资产
- AC-030 禁止 Darwin 式自动改 SKILL.md
- AC-031 planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止...
- AC-032 R6 refreeze：六 public skill 渐进式披露 contract；内部保留 branch governance / do...
- AC-033 R7 refreeze：TraceSpine.v1 / TraceContext.v1 成为 run authority；loop/imp...
- AC-035 ，后者是 L1 MD / L2 SQLite / L3 Blob**）：
- AC-036 （stop-when maker≠checker）→ v2 AC-105
- AC-037 **）
- AC-038 ）
- AC-039 ..114）
- AC-040 ..116）
- AC-041 ..123）
- AC-043 **：`~/.beacon/beacon.db` 不得存储可编辑的需求正文；只可存 metadata、FSM、gate、artifact 指针。
- AC-044 **：`.beacon/qa/*.json`、`.beacon/gate-report.json` 等 v1 投影在 v2 为 **非权威...
- AC-045 **：**禁止** `<project>/.beacon/beacon.db` 作为运行态权威（v2 明确否决 per-project DB）。
- AC-046 **：**禁止** `<project>/.beacon/loop/ledger/loop-runs.db` 作为 v2 权威；v1.6...
- AC-047 **：Blob 文件变更时 `artifact_refs` 必须更新 `content_hash`；hash 不匹配时 Spine 标记...
- AC-048 **：`beacon doctor projection rebuild` 须能从已注册 `project_root` 的 MD + bl...
- AC-049 存储原则（Plan §2.5）
- AC-050 **：每次 gate 评估写入 `gate_results`（pass/fail/blocked + reason_codes JSON）。
- AC-051 **：每次 run 启动写入 `runs`；checkpoint 写入 `checkpoints`。
- AC-052 **：Spine 查询 **DB-first**；blob 仅当 `artifact_refs` 存在且 hash 有效时拼接。
- AC-053 **：v1 JSON 运行态只允许 **export/import 迁移**，不得与 DB 双写竞争权威。
- AC-054 Operator Spine API（Plan §2.5）
- AC-055 **：必须实现 `beacon spine list [--project PATH] [--status STATUS] [--json]`。
- AC-056 **：必须实现 `beacon spine artifacts <run-id> [--json]`。
- AC-057 **：必须实现 `beacon spine gate <feature> [--version vX] [--json]`。
- AC-058 **：crate 依赖方向：`cli -> {gate, orchestrator, store, core}`；`store -> co...
- AC-059 **：v2.0.0 **不交付** `beacon-proto`/gRPC（**D-V2-001 accepted defer**）；CL...
- AC-060 **：单文件模块超过 500 行须拆分或 ADR 说明例外（对齐 D-02）。
- AC-061 **：阶段转换表显式编码；非法转换返回 typed error + reason_code。
- AC-062 **：`Blocked` 必须携带 `reason_codes: Vec<String>` 与可选 `blocking_gate`。
- AC-063 **：`Skipped` 仅允许带 `user_accepted_deferral_id` 或 deferral ledger 引用。
- AC-064 **：`Crashed` / `TimedOut` / `Interrupted` 须写入 `lifecycle_events` 且可触发...
- AC-065 **：Delivery 运行时 12 状态在 `beacon-core` 定义并与 `runs.status` CHECK 一致。
- AC-066 **：plan 主链节点转换须写入 `lifecycle_events`（可审计，非仅内存）。
- AC-067 **：`Paused` / `Stopping` / `Stopped` 与 v1 beacon-loop graceful+force...
- AC-068 **：`Repairing` 须持久化 repair payload 到 `artifact_refs`。
- AC-069 **：`AwaitingQa` 仅在 `import-evidence` 成功后可进入。
- AC-070 **：`Closed` 仅 release gate pass 或用户显式 archive；orchestrator **不得**自设 C...
- AC-071 **：`EvidenceChain` 含 `manifest_hash`、`signature_chain`、`artifact_refs...
- AC-072 **：import 断链 fail-closed → `EVIDENCE_CHAIN_BROKEN`。
- AC-073 **：v1 `.beacon/evidence-signature-chain.json` 可迁移为 v2 记录。
- AC-074 **：启动前 `truth-map resolve`；blocked → exit != 0 + 推荐 `beacon-gen-change`。
- AC-075 **（P2）：`SubprocessBackend` 完成 1 次真 integration iteration（可控测试 harness...
- AC-076 **（P3）：`AcpBackend`（CLI `acp:<target>`）完成 1 次真 integration iteration；...
- AC-077 **：checkpoint resume 后 iteration 递增；notes 注入写入 `lifecycle_events`（可审计）。
- AC-078 **：`stop_when` 移植 v1 `stop-when-gate`（含 gate pass 早停）。
- AC-079 **：orchestrator **禁止**输出 QA pass / release ready / feature complete v...
- AC-080 **：Phase Controller 四阶段写入 `runs.metadata_json`；phase 转换写 `lifecycle_e...
- AC-081 **（P3）：Developer Feedback Loop 人注入 checkpoint——`beacon-v2 run --feedb...
- AC-082 **（P3）：Loop Engineering 三层 Loop 可观测——spine snapshot 含 `loop_layer` 字段...
- AC-083 **：双轨运行时选择必须 **显式**（例如独立 `beacon-v2` 二进制，或 `beacon --runtime v2` / 等价...
- AC-084 **：`BEACON_STORE_PATH` 测试隔离；生产默认 `~/.beacon/beacon.db`。
- AC-085 **：在 **v2 runtime 路径内**，任何把 v1 Python/legacy skill 当执行后端的请求必须 fail-cl...
- AC-086 **：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其...
- AC-087 **：spine/projects/workflow/truth-map/implement/qa/release/run 子命令可解析且...
- AC-088 **：spine/projects/run 支持 `--json` 且 schema 可校验。
- AC-089 **：v1 reason_codes 对齐：`gate_results.reason_codes_json` 失败样例须含 documen...
- AC-090 **：`project_versions`（id, project_id, version, docs_root, is_current）
- AC-091 **：`feature_packages`（id, project_version_id, slug, truth_path, tests...
- AC-092 **：`feature_lifecycle`（feature_id, stage, status, reason_codes_json,...
- AC-093 **：`lifecycle_events`（id, feature_id, run_id, event_type, payload_jso...
- AC-094 **：`gate_results`（id, feature_id, gate_type, verdict, reason_codes_js...
- AC-095 **：`artifact_refs`（id, run_id, kind, abs_path, content_hash, size_byt...
- AC-096 **：`checkpoints`（id, run_id, iteration, state_json, created_at）
- AC-097 **：`beacon-store` 提供 ProjectDao, FeatureDao, RunDao, GateDao, Artifac...
- AC-098 **：migration `v1_runtime_ledger`：自 `~/.beacon/runtime-ledger/runtime-...
- AC-099 **：migration `v1_loop_ledger`：扫描各项目 `loop-runs.db` 一次性导入。
- AC-100 **：migration `v1_qa_projection`：可选历史只读导入。
- AC-101 **：schema `user_version` 管理；降级禁止。
- AC-102 **：`SpineDao::snapshot` 联查 lifecycle + run + gate + artifacts。
- AC-103 **：`list` 支持 lifecycle/run status 过滤。
