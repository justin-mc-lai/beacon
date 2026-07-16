---
slug: beacon-oss-borrow-hardening-v165-research
version: v1.6.5
research_kind: support_advisory
promotion_ref: ""
user_decision: pending
generated_at: 2026-07-02
sources:
  - kunchenguid/treehouse (Go worktree pool CLI)
  - cobusgreyling/loop-engineering (loop methodology + tooling)
---

# v1.6.5 调研：treehouse × loop-engineering 对 beacon 的借鉴蒸馏

> 本文是 planner `support_advisory` artifact，非 requirement truth。需用户确认 + `promotion_ref` 才能升级为 truth。

## 一、解决什么问题（第一性原理）

### 根本问题
beacon v1.6.4 已完成 QA 能力增强（chrome e2e / confidence chain / state machine / defect repair / methodology），但**交付基础设施自身有两个结构性短板**：

1. **worktree 一次性开销**：每次 implement/qa 新建 worktree，用完即删。v1.6.4 的 5 个 feature worktree 重复建/删，丢失依赖缓存与 runtime ledger，开销显著。下次同版本 feature 又从零建。
2. **loop 就绪度不可见**：beacon 有 10+ 分散 gate（version-surfaces / truth-integrity / requirement-clarity / qa / release / verify-closure），但**无单一指标**让用户/CI 快速判断"我的项目 loop 就绪了吗"。gate 分散导致认知负担高，新人不知道先补哪个。

3. **loop 治理缺体系**：beacon 有 ralph/ultrawork loop，但无机器可读 pattern registry、无 token 预算、无 safety denylist、无 failure-mode catalog。loop 失控时无护栏。

### 这两个开源库各自解决什么

**treehouse 解决的问题**：agent 用 git worktree 隔离时，每次新建/销毁的开销 + 并发抢夺 + 进程崩溃后 worktree 悬挂。treehouse 把 worktree 变成**池化资源**（pre-warmed、复用、lease 保护、in-use 检测）。

**loop-engineering 解决的问题**：agent loop（自动循环执行）缺乏工程化方法论——不知道 loop 就绪度、无 pattern 复用、无 token 预算、无 safety 护栏、无失败模式积累。loop-engineering 提供**五大原语 + readiness score + pattern registry + budget + safety + failure catalog**。

## 二、treehouse 蒸馏（借鉴点 1：worktree pool/lease）

### 核心机制
| 机制 | treehouse 实现 | 解决的问题 |
|---|---|---|
| **worktree pool** | worktree 归池，release 归还非删除，下次 acquire 复用 | 重复建/删开销，依赖缓存丢失 |
| **durable lease** | `Leased`/`LeaseHolder`/`LeasedAt` 进程无关持久租约 | 进程崩溃后 worktree 被误 prune |
| **in-use 检测** | 进程扫描 + 短期 owner reservation | 并发 agent 抢同一 worktree |
| **safe-by-default destroy** | 风险分类（in-use/leased/unlanded/disposable），每类独立 opt-in，无全局 --force | 误删活跃 worktree |
| **两阶段 reservation** | flock + pre_destroy hook，hook 期间不被 re-acquire | hook 窗口期竞态 |
| **state 恢复** | corrupt state 文件恢复时所有 entry 标 leased（保守） | 状态文件损坏导致误判 |
| **lifecycle hooks** | post_create / pre_destroy 用户配置命令 | 复用时重置环境 |

### beacon 现状对照
beacon `workspace_admission.py` 现状：
- `worktree_mode=dedicated-worktree`（v1.6.2+）：每次 implement 新建
- admission 状态机：`required → dirty_only check → artifact`（无 pool/lease/release 语义）
- 无 in-use 检测（仅 dirty_only + cwd_mismatch）
- worktree 用完即删（v1.6.4 的 5 worktree 已删 1，其余待清）

### 借鉴后 beacon 的变化
- §4.2 worktree 模式从"一次性 dedicated"升级为"pool + lease"
- `beacon workspace admit` 增 lease 语义（feature → worktree 持久租约）
- `beacon workspace release`（新命令）归还池非删除
- in-use 检测避免并发 implement 抢同一 lane
- 复用保留 `.beacon/` runtime ledger + 依赖缓存

### 需完善的上下文
- beacon admission 状态机需扩展：`available → in-use → released-to-pool → available`（多状态 + 归还）
- governance contract `worktree_mode` 需新增 `pooled` 值（与 `dedicated` 共存，向后兼容）
- v1.6.4 既有 `dedicated` 模式不破坏（F2 truth-on-main 向后兼容原则）

## 三、loop-engineering 蒸馏（借鉴点 2-6）

### 借鉴 2：Loop Readiness score

**机制**：`loop-audit` CLI 打 0-100 分，聚合 15 信号（state file / triage skill / verifier / LOOP.md / safety / workflows / MCP / worktree / pattern registry / budget / run log / loop activity）。L0-L3 分级（draft → report-only → assisted → unattended）。`<40` exit 2（CI gate）。

**解决的问题**：gate 分散无单一指标，认知负担高。

**beacon 借鉴**：`beacon doctor loop-audit` 聚合现有 gate（version-surfaces + truth-integrity + requirement-clarity + qa + release）为单一 0-100 分 + L0-L3 分级 + `--suggest`。`<阈值` block。

**需完善的上下文**：beacon 已有 `beacon status --board`（人类可读）+ 各 gate JSON，聚合层是新增，不破坏现有。

### 借鉴 3：pattern registry

**机制**：`patterns/registry.yaml` 机器可读（id / cadence / risk / skills / state / phases / human_gates / token_cost / daily_cap）。被 loop-audit / loop-cost / 文档站消费。

**解决的问题**：loop 模式在 skill 文本里，无法被工具消费/复用。

**beacon 借鉴**：把 ralph/ultrawork/team/autopilot 提取为 `docs/beacon/<version>/loop-patterns/registry.yaml`，字段对齐 beacon 语义（harness_skills = planner/generator/evaluator/governor）。

**需完善的上下文**：beacon loop 模式分散在 `.claude/skills/` 与 `skills/beacon/`，需先盘清现有 loop 模式清单。

### 借鉴 4：safety path denylist

**机制**：显式 path denylist（`.env*` / `secrets/` / `credentials/` / `*_key*` / `migrations/` / `auth/` / `payments/`）。implementer skill 入口校验，触碰 → escalate human。

**解决的问题**：fail-closed gate 通用，无显式"永不自动改"清单。

**beacon 借鉴**：`global-boundaries` 增 §「protected path denylist」（cross-version），implement/qa/change 入口校验。

**需完善的上下文**：beacon 已有 `NON_ACCEPTANCE_EVIDENCE_KINDS` fail-closed 模式，denylist 是同构扩展。落 global-boundaries（cross-version canonical）。

### 借鉴 5：token cost 治理

**机制**：`loop-budget.md` 三档 token 成本（noop/report/action）+ max runs/day + max tokens/day + max sub-agent spawns。超预算 → pause + run-log + issue。kill switch（`loop-pause-all` label）。`loop-cost` CLI 估算。

**解决的问题**：loop 无 token 预算，长 loop 烧 token 无上限。

**beacon 借鉴**：loop-pattern registry 增 `token_cost` 字段；`beacon status` 增 token 追踪 + daily_cap soft gate + kill switch。

**需完善的上下文**：beacon loop（ralph/ultrawork）当前无 token 追踪，需新增 ledger。

### 借鉴 6：failure-mode catalog

**机制**：`failure-modes.md` S1/S2/S3 分级（Annoying / Harmful / Critical），每模式含症状/原因/缓解。如 infinite fix loop（S2：hard cap 3 attempts → escalate）。

**解决的问题**：reason_code 是运行时分类，非系统性失败模式积累。

**beacon 借鉴**：`docs/beacon/<version>/execution/loop-failure-modes.md`，把 beacon 已知失败模式（truth drift / git-alignment blocked / evidence-manifest stale / infinite fix loop）系统化为 S1/S2/S3 catalog。被 defect-repair-loop（v1.6.4 Phase 4）消费。

**需完善的上下文**：beacon 已有 reason_code 分类，catalog 是上层系统化。

## 四、借鉴点优先级与依赖

| 借鉴 | 优先级 | 依赖 | 复杂度 |
|---|---|---|---|
| 1 worktree pool/lease | P1 | 无（基础设施） | 高（admission 重写） |
| 2 loop-audit score | P1 | 无（聚合层） | 中 |
| 3 pattern registry | P2 | 无 | 中 |
| 4 denylist | P2 | 无 | 中（cross-version） |
| 5 token cost | P2 | 借鉴3（registry 字段） | 中 |
| 6 failure-mode catalog | P3 | 借鉴3 + v1.6.4 Phase 4 | 低（文档+分类） |

依赖链：1 独立 / 2 独立 / 3→5 / 3→6 / 4 独立。可并行：1+2+3+4 同时启动。

## 五、与 beacon v1.6.4 已落地能力的协同

| v1.6.4 能力 | v1.6.5 借鉴后增强 |
|---|---|
| Phase 2 confidence chain | loop-audit score 消费 confidence_chain 作 readiness 信号 |
| Phase 3 business state machine | failure-mode catalog 消费 FSM 不可达态作失败模式 |
| Phase 4 defect repair loop | pattern registry token_cost + failure-mode catalog 增强缺陷分类 |
| Phase 5 methodology (对抗式审查) | denylist 加入 §5 safety 契约，对抗式审查翻车点含 denylist 触碰 |
| §4.2 worktree 隔离 | worktree pool/lease 升级（基础设施复用） |

## 六、scope 判断（湖/海）

**海级**——6 借鉴点跨 4 域（worktree 基础设施 / loop-audit 聚合 / loop 治理体系 / failure catalog），单 feature 100+ AC 投影。需拆 phase。

用户要求"一次性补齐"= v1.6.5 同版本多 phase（如 v1.6.4 模式），不跨版本延后。

## 七、需用户拍板的开放问题

| ID | 问题 | 选项 |
|---|---|---|
| UD-1 | "一次性" 语义 | v1.6.5 同版本 6 phase 全交付（推荐）/ 跨版本分期 |
| UD-2 | phase 拆分 | 1(worktree pool) / 2(loop-audit) / 3(pattern registry) / 4(denylist) / 5(token cost) / 6(failure-mode) |
| UD-3 | "交付到 loop 任务" 语义 | (a) 能力被 beacon loop 消费 / (b) 交付过程用 ralph loop 执行 |
| UD-4 | 借鉴4 denylist 落点 | global-boundaries（cross-version，推荐）/ v1.6.5 feature |
| UD-5 | 借鉴6 failure-mode 本版本 | 本版本（用户要"一次性"）/ 延后（待 v1.6.4 实战积累） |

## 八、recommended_route（planner，非指令）

1. 用户拍板 UD-1..5
2. → governor 开 v1.6.5 版本契约
3. → `beacon-pln-program` 拆 6 phase + feature-graph + P4 ack
4. → 逐 phase `beacon-gen-truth` freeze
5. → implement（可选 ralph loop 执行，UD-3b）

## 九、不借鉴的部分（beacon 已有更好方案）

- **maker/checker split**：beacon 4-harness（planner/generator/evaluator/governor）比 loop-engineering implementer/verifier 二分更细
- **human gate**：beacon 用户主权 + release gate 更系统
- **Skills as intent memory**：beacon truth.md（frozen + integrity gate）比 SKILL.md 更强
- **AGENTS.md/CLAUDE.md conventions**：beacon `setup-context` 已有 managed block 机制

## 十、源仓库 artifact

- treehouse: `oss-sync/agents/agent-skills/treehouse/`
- loop-engineering: `oss-sync/agents/agent-skills/loop-engineering/`
- 对比分析: `oss-sync/index/analysis/beacon-borrow-analysis.md`
- 本调研: `docs/beacon/archive/v1.6.5/research/beacon-oss-borrow-hardening-v165-research.md`
