# Research: Beacon 长程任务稳定性分析（对照 4 个新 loop 项目）

**日期**：2026-08-03
**目的**：结合刚导入 oss-sync 的 4 个 agent loop 项目（`loopx`、`oh-my-pi`、`kun`、`simple-long-horizon-agent`），对 Beacon 长程任务（GoalRun / Ralph 闭环 / DurableSupervisor）的稳定性做系统性对照分析，识别缺口并给出可落地的改进建议。
**镜像**：`/Users/apple/Developer/Personal/oss-sync/`
**前置材料**：`docs/beacon/v2.0.0/research/beacon-v2-goal-durable-longrun.md`、`docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md`、`docs/beacon/research/beacon-competitor-registry.md`

---

## 1. 稳定性定义与维度

长程任务稳定性 = 在跨轮次、跨宿主中断、跨 agent 切换的长周期执行中，系统持续保持 **可恢复、不漂移、不失控、可验证** 的能力。拆成 8 个维度：

| # | 维度 | 含义 | 失效表现 |
|---|---|---|---|
| S1 | 状态持久化 | 执行状态跨进程/跨会话存活 | 重启后不知道做到哪 |
| S2 | 恢复能力 | 中断后可无缝续跑 | 重复劳动 / 上下文丢失 |
| S3 | 防漂移 | 目标与 truth 不随轮次扭曲 | 需求膨胀 / 完成标准漂移 |
| S4 | 预算控制 | 成本、轮次、时间有上限 | 成本失控 / 无限重试 |
| S5 | 防假完成 | 完成必须有可查证据 | 幻觉完成 / 未验证声称成功 |
| S6 | 上下文管理 | 长会话不退化、不爆窗 | 上下文溢出 / 早期信息丢失 |
| S7 | 并发协调 | 多 agent 并行不踩踏、所有权清晰 | 重复工作 / 互相覆盖 |
| S8 | 可观测性 | 每轮可审计、可复盘 | 黑盒 / 无法归因 |

## 2. Beacon 长程任务现状（已有机制盘点）

| 维度 | Beacon 现状 | 机制出处 |
|---|---|---|
| S1 | GoalRun ledger（sqlite `~/.beacon/beacon.db`）、append-only `execution.jsonl` | v2 GoalRun / DurableSupervisor |
| S2 | checkpoint + resume-pack digest；AgentDriver spawn/resume 宿主轮次；`host_interrupted` ≠ `stage_blocked` | v2 AgentDriver |
| S3 | change/refreeze 冻结 truth；truth 层与执行层分离；Ralph canonical stop states | orchestration.md / ralph brainstorm |
| S4 | heartbeat 120s（保活），**无 quota/预算上限机制** | v2 DurableSupervisor |
| S5 | verifier 完成制；`Illegal: auto-complete without verifier`；evidence 读模型 | v2 + orchestration |
| S6 | resume-pack digest 消化式注入；Ralph 每轮全新实例干净上下文 | v2 / ralph brainstorm |
| S7 | 多 worker（ralph implement / qa run / design stage），**无显式所有权租约** | v2 |
| S8 | execution.jsonl + heartbeat + 阶段机（GoalRun: created → … → release_pending） | v2 |

**结论**：Beacon 在 S1/S2/S3/S5/S8 已较强（状态机 + 证据制 + truth 冻结），**S4（预算）与 S7（并发所有权）是明确缺口**，S6 有方案但缺量化验证。

## 3. 新项目稳定性机制对照

### 3.1 loopx —— 状态控制平面（与 Beacon 最同构）

loopx 明确"不是 executor"：Codex/Claude Code/Cursor 执行 bounded turn，loopx 只保存动态 loop 状态。稳定性贡献：

- **quota-aware auto-wake（S4）**：每次唤醒决策带配额感知——`loopx quota should-run`。Beacon 的 DurableSupervisor 只有 heartbeat，没有"该不该跑下一轮"的配额判定。
- **claims / leases / scope（S7）**：多 agent 并行 lane 有 agent 身份、todo ownership、scope lease——不踩踏、可交接。Beacon 的 workers 并行无此机制。
- **evidence writeback + `loopx check`（S5/S8）**：证据回写、公共/私有边界扫描，防越权与防假完成。
- **typed continuation / handoff contract（S2/S3）**：跨宿主交接有显式契约（`codex-app` / `codex-cli` / `claude-code` 分路径激活，拒绝歧义值）。
- **`should_run` gate（S4/S5）**：可挂在宿主 `/loop` 上，低侵入增强现有流程。

### 3.2 oh-my-pi —— 运行时稳定性（编辑与压缩）

- **hashline（S6 变体：编辑稳定性）**：hash-anchored patch 语言，行锚定编辑防大文件 diff 漂移。Beacon implement 阶段的文件编辑可借鉴——比"上下文管理"更细，是**变更应用层的稳定性**。
- **snapcompact（S6）**：位图帧上下文压缩 + SQuAD 评测套件。Beacon 的 resume-pack digest 是文本摘要式消化，snapcompact 提供**量化压缩 + 评测**的升级路径。
- **agentLoop 显式状态/事件流（S1/S8）**：`agentLoop`/`agentLoopContinue` 作为库级 API，loop 状态是头等公民。
- **mnemopi（S1）**：SQLite 记忆引擎，跨会话事实持久化。

### 3.3 kun —— 长流程成本稳定性

- **cache-first agent loop（S4/S6）**：不可变 prompt 前缀 + TTL/LRU 缓存 + inflight 跟踪 + 显式上下文压缩，配套 `docs/kun-cache-optimization.md` 的 token economy 文档。Beacon 可对照评估自身缓存策略。
- **需求先行闭环（S3）**：`.kunsdd/draft/requirement.md → plan → todo → /review` 全程关联，需求变更触发重规划提示——与 Beacon 的 refreeze 同思想，GUI 化落地。
- **成本分层模型组合（S4）**：DeepSeek/MiMo/MiniMax 明确为"长流程跑得起"服务——轻量澄清走快模型、复杂推理走强模型。**成本分层是长程任务预算稳定的产品化前提**。
- **追加式 JSONL 事件日志 + 用量统计（S8）**：与 Beacon execution.jsonl 同构。

### 3.4 simple-long-horizon-agent —— 稳定性评测口径

- **Δ vs Baseline（S-整体）**：同一模型同一任务预算下，agent 相对基线的提升 = 机制贡献，分离"agent 的价值"与"底层模型的能力"。
- **成本/任务发布（S4）**：SWE-bench Pro $7.78、Terminal-Bench $0.57——稳定性改进要可量化成本。
- 意义：**给 Beacon 的稳定性机制（压缩策略、resume 策略、quota 策略）提供量化验收口径**——"机制有效"不应停留在直觉，而应有 Δ 评测。

## 4. 对照矩阵总览

| 维度 | Beacon | loopx | oh-my-pi | kun | SLHA |
|---|---|---|---|---|---|
| S1 状态持久化 | ✅ sqlite ledger | ✅ 状态内核 | ✅ mnemopi | ✅ JSONL | — |
| S2 恢复 | ✅ checkpoint+digest | ✅ handoff | ⚠️ 库级 | ⚠️ 会话级 | — |
| S3 防漂移 | ✅ refreeze+truth | ✅ gates | ⚠️ | ✅ 需求先行 | — |
| S4 预算控制 | ❌ 仅 heartbeat | ✅ quota-aware | ❌ | ✅ cache+分层 | ✅ cost/task 度量 |
| S5 防假完成 | ✅ verifier 制 | ✅ evidence | ⚠️ | ✅ 审批制 | ✅ 评测闭环 |
| S6 上下文 | ✅ digest 注入 | ⚠️ | ✅ snapcompact | ✅ cache-first | — |
| S7 并发协调 | ❌ 无租约 | ✅ claims/leases | ⚠️ swarm ext | ⚠️ | — |
| S8 可观测 | ✅ jsonl+heartbeat | ✅ check | ✅ 事件流 | ✅ 用量统计 | — |

## 5. 缺口与改进建议（按优先级）

### P0-1：quota 预算层（S4）——借鉴 loopx
- **缺口**：DurableSupervisor 只有 heartbeat，没有"配额用尽自动降级/暂停/提请人工"的判定。
- **建议**：在 GoalRun ledger 增加 quota 字段（成本上限、轮次上限、重试上限），AgentDriver 每次 requeue 前执行 `should_run` 判定（对照 loopx `quota should-run`）；配额用尽 → `stage_blocked` 变体或 `awaiting_human`，永不静默继续。
- **落地载体**：v2 AgentDriver 判定逻辑 + GoalRun 状态机扩展（`quota_exhausted` 态）。

### P0-2：稳定性评测口径（整体）——借鉴 SLHA
- **缺口**：压缩、resume、quota 等机制改进无量化验收。
- **建议**：为 Beacon 建立 Δ vs Baseline 评测口径（对代表性目标项目：基线 = 无机制直跑；改进 = 挂机制跑），记录 score 提升与 cost/task；机制进入 freeze 前必须有 Δ 证据。

### P1-1：多 agent 所有权租约（S7）——借鉴 loopx claims/leases
- **缺口**：ralph implement / qa run / design stage 并行时无所有权契约。
- **建议**：Worker 级 claims + scope lease（owner/scope/状态），同一 todo 同一时刻只有一个 worker 持有；交接必须显式（对照 loopx todo claim / lease）。

### P1-2：编辑锚定（S6 扩展）——借鉴 hashline
- **建议**：implement 阶段文件编辑采用行锚定 patch（hash-anchored）而非纯字符串/行号 diff，减少大文件编辑的漂移与误替换；可与 `parallel_plan` 的多文件并行写结合。

### P2：压缩方案升级与量化（S6）——借鉴 snapcompact
- **建议**：对 resume-pack digest 引入压缩质量评测（对照 snapcompact 的 SQuAD 评测套件），比较摘要压缩 vs 结构化压缩在长会话中的信息保持率。

### P2：成本分层路由（S4 产品化）——借鉴 kun
- **建议**：Beacon 长流程可引入模型分层（轻量澄清/重推理/媒体）与成本台账，使 quota 预算在产品侧可感知。

## 6. 落地建议顺序

1. **本轮**：GoalRun 增加 quota 字段 + `should_run` 判定（P0-1）；建立 Δ 评测样例（P0-2）。
2. **下轮**：Worker claims/leases（P1-1）；implement 编辑锚定试点（P1-2）。
3. **后续**：压缩评测（P2）；模型分层路由（P2）。

## 7. 结论

Beacon 的长程任务稳定性底座（truth 冻结 + 状态机 + verifier 证据制 + checkpoint 恢复）在同类项目中已属上游；本次对照暴露的**真实缺口集中在 S4 预算控制与 S7 并发所有权**，且都已有成熟开源参照（loopx quota-aware / claims-leases）可直接借鉴，落地成本低、收益直接。建议以 P0-1/P0-2 为下一步交付，把"稳定性"从机制存在推进到**机制可度量**。

## 附：相关路径速查

- 新镜像：`oss-sync/automation/autoresearch/loopx`、`oss-sync/agents/agent-systems/oh-my-pi`、`oss-sync/agents/agent-systems/kun`、`oss-sync/automation/autoresearch/simple-long-horizon-agent`
- 详见：`oss-sync/index/analysis/agent-loop-landscape-2026-08.md`
