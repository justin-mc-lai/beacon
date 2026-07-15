---
slug: beacon-v2-rust-kernel-redesign
version: v2.0.0
status: frozen
language: zh
revision: r9-skill-surface-disclosure-frozen
canonical_refs:
  truth: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
  tests: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md
  tasks: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md
  evidence: docs/beacon/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
source_plan: docs/plans/beacon-v2-redesign.md
planner_review: beacon-pln-review option-A true-integration
---

# 需求真相：Beacon v2 Rust Kernel Redesign

## 概述

`beacon-v2-rust-kernel-redesign` 定义 Beacon **v2.0.0** 产品线级重写：

```text
beacon-core      -> Rust 类型层：双 FSM、证据链、Gate 结果类型
beacon-store     -> Rust 持久层：~/.beacon/beacon.db 全局 SQLite + blob 指针
beacon-orchestrator -> Rust 编排层：统一 goal/run/team 长任务（吸收 beacon-loop + beacon-run）
beacon-gate      -> Rust 门禁层：truth_freeze / qa / release / implement
beacon-cli       -> Rust 主 CLI：loop / truth / design / implement / qa-evidence / release
beacon-harness   -> Rust 极简 harness contract：六个一等能力，不保留 v1 Python 兼容面
```

**User Intent（冻结锚点，一行）**：v2.0.0 交付 **Rust 极简 harness kernel + 六个一等能力（loop / truth / design / implement / qa-evidence / release）+ 全局 `beacon.db` + Operator Spine + 跨 harness loop 闭环**；v1 Python / Node / 33 skills 历史兼容 **不进入 v2 core closure**，仅作为只读迁移语义源或 archive reference。

**需求真相** 仍只存在于 Markdown feature package（`docs/beacon/v2.0.0/` + `features/<slug>/truth.md`）。  
**运行态权威** 迁入机器级全局 SQLite `~/.beacon/beacon.db`；大文件留在项目 `<project>/.beacon/` blob 层，DB 只存绝对路径 + hash 指针。

### Truth 规范基准（R6 增补）

v2.0.0 以 **v1.5.2 package-authoritative cutover** 为 truth 规范全新基准：

- **文档结构**：v2 **不生成** `prd/<slug>.md`、`user-story/<slug>.md`、`qa/test-cases/<slug>.md` 等顶层 legacy 文档。需求真相唯一存在于 `features/<slug>/{truth,tests,tasks,evidence}.md`（v1.5.2 cutover 后已是事实，v2 显式声明继承）。
- **frontmatter canonical_refs**：使用 package-authoritative 字段名 `truth/tests/tasks/evidence`，不用 legacy `prd/user_story/test_case`。
- **Rust FSM stage 枚举**：`beacon-core::WorkflowStage`（Think/UserStory/Prd/TestCase/Prototype/Freeze/Implement/Qa/Release/Archive）是**类型层状态机变体名**，保留作 v1.6 兼容（转换表显式标注），**不**等同于文档结构。文档结构无 prd/user-story 顶层文件，与 Rust enum 变体名是两个层面。
- **状态机真相**：`state_machine_required: true`；Rust 内核的 FSM（WorkflowStage / StageStatus / RunStatus / LifecycleEventType）是运行态权威的机器级投影，Markdown truth 是需求权威，二者通过 `beacon.db` 桥接（DB 存运行态，不存需求真相）。

v2 不复用 v1 的 33 host-visible skill 面。human-facing 能力面收敛为：

```text
loop | truth | design | implement | qa-evidence | release
```

其中 `loop` 是跨 harness 编排入口，不是替代其他能力的超级阶段；`truth` 吸收 plan/pre-freeze intent 工作；`design` 仅在存在 UI/视觉/交互交付时成为 implement 前置 gate；`qa-evidence` 承接 evaluator 语义但不允许修改 truth 或 implementation。

### Loop Engineering 三层 Loop（R7 增补）

v2.0.0 按 [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) 三层 Loop 理论完善 harness loop 能力。beacon 生命周期天然映射三层 Loop（**注意：「Loop 三层」≠「存储三层」§AC-007，后者是 L1 MD / L2 SQLite / L3 Blob**）：

| Loop Engineering 层 | beacon 生命周期映射 | 含义 | v2.0.0 实现 |
|---|---|---|---|
| **Coding Loop**（内） | `generate -> evaluate` | Agent 写代码→跑 Eval→发现问题→修→再测，自动闭环 | orchestrator iterate loop + stop_when + AgentBackend（AC-040..050） |
| **Developer Feedback Loop**（中） | `truth -> generate`（change/refreeze） | 人看实现→修正 Spec→重新实现；人注入 AI 不知道的上下文 | change/refreeze 流程 + Developer Feedback checkpoint（AC-106） |
| **Real-world Feedback Loop**（外） | `plan -> truth`（research/brainstorm） | 真实世界反馈→改产品方向→更新 Spec | **延后**（DEF-loop-006，需真实反馈源集成） |

**Eval 复用**：Loop Engineering 的「Eval」= beacon 的 `qa gate` + `tests.md` TC（Command+Assertion），**不另建 Eval 机制**。

**Host 运行模式**：loop 采用 **CLI 进程 + checkpoint/resume/信号**（对齐 v1.6 `beacon-run`），**无 daemon**。host 稳定靠 checkpoint/resume/信号处理（SIGINT graceful stop），不靠常驻服务。`beacon-v2 run --agent <X>` 启动 CLI 进程跑 loop，跑完退出或被信号中断后可 resume。

**Loop 语义源**（v1.6 已实现，v2 Rust 重现）：
- `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md` R10（worktree+freeze 不断链 / state spine / stop-when 可执行检查）
- `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md`（spine 字段语义）
- v1.6 AC-071（stop-when maker≠checker）→ v2 AC-105

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | v2 使用 Rust 重写极简 Beacon harness；抛弃 v1 Python 历史兼容；保留六个一等能力；plan 阶段强识别意图、保存提示词快照、反复对齐，产出 loop 可一键跑闭环的决策包；实现前必须有视觉/设计原语绑定 |
| `lake_or_ocean` | **海**（见 research）— 单包 truth **不**等于全量实现 closure；按 phase 煮干 |
| 强度词 | 极简 harness、彻底抛弃历史包袱、强感知识别、一键决策跑闭环、视觉设计实现前前置 |
| 非协商边界 | 需求不进 DB 当权威；orchestrator 不裁决 QA/release；无空壳验收；v1 Python/PyO3/33 skills 不作为 v2 core 验收；design_required 时未绑定设计原语不得 implement |

### Alignment Surface（v2.0.0 冻结时必须煮干）

与 v1.6 closed-loop **行为对齐**的最小面（freeze 前 intent parity 对照源：`beacon-loop-goal-closed-loop-orchestrator` + `beacon-loop-state-spine.md`）：

- 全局 SQLite + Spine read（show/list/artifacts/gate）+ projects registry
- orchestrator：goal/resume/stop/status、truth-map preflight、checkpoint、stop_when
- **planner_review 多代理 runtime**（对齐 v1.6 `beacon-pln-review-runtime-multi-agent-v160`：reviewer lanes + synthesis + fallback，**AC-102**）
- **Truth Integrity Gate**（对齐 v1.6 `beacon-truth-integrity-gates-v160`：freeze/refreeze hard block，**AC-101**）
- agent 真集成：codex 多轮、subprocess、claude、acp、implement harness（AC-043–046, AC-100）
- git/worktree 全模式（AC-099）
- gate 写库 + reason_codes；v1→v2 migration + projection rebuild
- 六个一等能力 kernel surface：loop / truth / design / implement / qa-evidence / release（AC-109）
- truth pre-freeze：强意图识别、prompt snapshot ledger、brainstorm/review synthesis、decision_packet.v1（AC-111..114）
- design before implement：design_primitives.v1 绑定、视觉/交互状态矩阵、实现准入阻断（AC-115..116）
- v1.6.4–v1.6.6 新能力以 Rust 语义重现：agent trace、stagnation detector、remediation sandbox、loop governance、QA confidence/repair chain（AC-117..123）

### Phased Backlog（plan 对照，按 P 煮干，非单包空壳 closure）

- P6 benchmark 门禁（AC-051–058）、默认 BEACON_V2=1
- post-v2.0.0：`beacon-proto`/gRPC（**D-V2-001 accepted defer**）

### v1.6 Upstream Frozen Inputs（R2 增补，非空壳引用）

| v1.6 frozen feature | v2 迁移义务 | Phase |
|---------------------|-------------|-------|
| `beacon-pln-review-runtime-multi-agent-v160` | `planner_review()` 产出同构 runtime artifact（lanes/findings/synthesis/fallback） | P2 |
| `beacon-truth-integrity-gates-v160` | freeze/refreeze `mode=block`；历史 frozen 包 `audit_only` | P3 |
| `beacon-loop-goal-closed-loop-orchestrator` | delivery FSM + spine + import/qa 链行为 parity | P2–P3 |

#### v1.6.3 免疫系统修复（R6 增补，语义重现义务）

v2 Rust 内核必须**语义重现**以下 v1.6.3 免疫修复（Rust 实现对齐行为，非仅引用），否则 v2 会重新带回 v1.6.3 之前已修好的漂移：

| v1.6.3 frozen feature | v2 迁移义务（语义重现） | Phase |
|----------------------|----------------------|-------|
| `beacon-gate-truth-model-alignment-v163` | Rust `beacon-gate` 按 semver 分流：`<v1.5.2` 顶层目录契约；`≥v1.5.2` package-authoritative feature 包闭环校验 | P3 |
| `beacon-freeze-integrity-drift-repair-v163` | Rust freeze 校验器：parser_contract 单一源（v1/v2 都合法）、forbidden field 词边界、pytest hard marker、错误自描述 | P3 |
| `beacon-version-resolve-fail-closed-v163` | Rust 版本解析：消除硬编码 fallback，用 `resolve_target_version`，runtime↔docs drift 守卫 | P1 |
| `beacon-workflow-memory-completion-gate-v163` | Rust `workflow_memory`：区分 no-run（warn）vs run-without-transaction（fail-closed） | P2 |
| `beacon-ecosystem-discovery-sync-drift-v163` | Rust manifest sync 扫 features/、sync-materials 重算 hash、freeze 重物化 .machine | P2 |
| `beacon-truth-format-package-auth-skip-v163` | Rust truth_format 校验对 ≥v1.5.2 跳过 legacy、feature paths 返回 features/、status 从 frontmatter | P3 |
| `beacon-spec-fingerprint-package-auth-paths-v163` | Rust `_find_layer_files` 扫 features/<slug>/{truth,tests}.md，spec drift 检测对 truth 有效 | P3 |
| `beacon-post-release-hook-agent-coverage-v163` | Rust post-release hook 覆盖全 5 agent（SUPPORTED_HOST_AGENTS），drift 阻断 | P4 |
| `beacon-runtime-release-alignment-v163` | Rust release gate 阻断 runtime≠docs，hook 路由 sync-version-surfaces | P3 |

语义源（只读，不复制进 DB）：

- `docs/beacon/v1.6.0/features/beacon-pln-review-runtime-multi-agent-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-truth-integrity-gates-v160/truth.md`
- `docs/beacon/v1.6.0/execution/beacon-loop-state-spine.md`
- `docs/beacon/v1.6.0/features/beacon-loop-goal-closed-loop-orchestrator/truth.md`（R10 Loop Engineering 对齐 + AC-071 stop-when maker≠checker → v2 AC-105/106）
- `docs/beacon/v1.6.3/features/beacon-{gate-truth-model-alignment,freeze-integrity-drift-repair,version-resolve-fail-closed,workflow-memory-completion-gate,ecosystem-discovery-sync-drift,truth-format-package-auth-skip,spec-fingerprint-package-auth-paths,post-release-hook-agent-coverage,runtime-release-alignment}-v163/truth.md`

#### v1.6.4–v1.6.6 闭环能力迁移（R8 增补，保留语义、不保留 Python 形态）

| upstream feature | v2 Rust kernel 义务 | Phase |
|------------------|---------------------|-------|
| `beacon-program-next-action-admission-v164` | implement admission 读取 program/lake next_action 与 dependency closure；blocked 时 diagnostic-only，不写 delivery evidence | P2–P3 |
| `beacon-qa-coverage-confidence-chain-v164` | qa-evidence 产出 confidence_chain；单层 pass 不得冒充端到端 pass | P3 |
| `beacon-qa-business-state-machine-v164` | 从 truth State Model 提取业务 FSM，生成边界/非法转换覆盖，触达不可达态 fail-closed | P3 |
| `beacon-qa-defect-repair-loop-v164` | defect -> repair_route -> regression QA -> closure evidence chain；缺段 release block | P3 |
| `beacon-loop-pattern-registry-v165` | loop pattern registry 成为 Rust loop guardrail read model | P2 |
| `beacon-loop-failure-mode-catalog-v165` | failure catalog 与 reason_code / stagnation finding 交叉引用 | P2 |
| `beacon-loop-token-budget-v165` | automated loop 前检查 daily cap、kill switch、token ledger | P2 |
| `beacon-loop-readiness-audit-v165` | `loop readiness` 作为 advisory/strict preflight，不伪装 release verdict | P2 |
| `beacon-workspace-pool-lease-v165` | worktree lane lease / release / corrupt-state fail-closed | P3 |
| `beacon-protected-path-denylist-v165` | automatic write surfaces 统一保护路径阻断 | P2 |
| `beacon-loop-goal-v166` | loop 一键编排 truth -> design? -> implement -> qa-evidence -> release；release 永远人工确认 | P3 |
| `beacon-agent-structured-trace-v166` | governed agent iteration 写 `agent_trace.v1` | P2 |
| `beacon-loop-stagnation-detector-v166` | 基于 trace 确定性识别 repeat_failure / repeat_labor / plateau | P2 |
| `beacon-harness-remediation-sandbox-v166` | 在 governed worktree sandbox 中 overlay/eval/rollback；成功也必须 human review | P3 |

## Scope Mode

`scope_mode` = **`full_parity`**（对照 `docs/plans/beacon-v2-redesign.md` 全量场景）。

任何从 full parity 到 MVP 的降级必须进入 `Deferral Ledger` 并获用户显式接受。默认 **in-scope** 项不得静默裁剪。

**禁止** 以空壳 AC、stub-only、纯文档闭环、contract-test-without-integration 作为唯一验收路径（r2 收紧，响应 planner review）。

## v2 Minimal Harness Kernel Contract（R8）

v2 public kernel surface 只保留六个一等能力：

| 能力 | 职责 | 关键阻断 |
|------|------|----------|
| `loop` | 跨 harness 编排 truth -> design? -> implement -> qa-evidence -> release；支持 auto-decide、checkpoint/resume、worktree lane 并行推进 | 不替代 truth/implement/QA/release；release 必须人工确认 |
| `truth` | plan/pre-freeze intent 捕获、prompt snapshot、brainstorm/review synthesis、truth gap scan、freeze/refreeze | low-confidence intent、未拍板 deferral、状态机缺失时不得 freeze |
| `design` | UI/视觉/交互交付的 design primitive contract；产出 tokens/components/layout/state/a11y/visual evidence baseline | `design_required=true` 且未绑定 `design_primitives.v1` 时不得 implement |
| `implement` | 只消费 frozen truth + bound design + admitted worktree + decision_packet；运行 agent/backend loop | 不改 frozen truth，不自证 QA/release pass，不接受 static-only evidence |
| `qa-evidence` | 行为证据导入、confidence chain、business FSM coverage、defect repair regression、trace/stagnation/remediation 报告 | 缺行为证据链、回归链或断链时 release block |
| `release` | 最终 go/no-go gate，检查 truth/design/qa/evidence/human confirmation | 不允许 auto-decide 越过 human release gate |

`plan` 不作为第七个一等能力。用户在 plan 时给 Beacon 的灵感、思路、目标、约束、参考和业务判断，必须进入 `truth.pre_freeze_intent`，形成可审计的 `intent_snapshot.v1` 与 loop 可消费的 `decision_packet.v1`。

### Decision Packet Contract

`decision_packet.v1` 是 loop admission 的输入，最少包含：

```text
run_goal, feature_slug, version, raw_prompt_hash,
intent_snapshot_ref, accepted_scope, non_negotiables,
truth_refs, design_required, design_primitives_ref?,
worktree_policy, auto_decide_policy, human_gates,
qa_evidence_expectation, release_confirmation_required=true
```

缺失 `decision_packet.v1` 或其引用的 latest accepted prompt snapshot 时，`loop start` 必须 fail-closed。

### Skill Surface Progressive Disclosure Contract（R9）

v2 的减负目标是**减少使用者要理解和选择的入口**，不是删除治理能力。六个 public skill 是稳定人类入口；branch governance、doctor、router、hooks、metadata、status、archive、debug、generator/evaluator 细分能力都降级为 kernel internal module，通过渐进式披露按需加载。

| 层 | 暴露对象 | 规则 |
|----|----------|------|
| Public skill | `loop` / `truth` / `design` / `implement` / `qa-evidence` / `release` | 用户只需要显式选择这六个入口之一，或由 router 基于意图选择 |
| Progressive references | `references/<topic>.md` / `examples/<route>.md` / `schemas/*.json` | 仅在触发对应 topic 时加载；每次加载写 `skill_load_plan.v1` |
| Internal module | branch/workspace governance、doctor、hooks、metadata、router、status、archive、debug、TIG、evidence manifest | 保留为 kernel service；不可作为第七个 lifecycle stage 或公共 skill 面 |

每个 public skill package 必须包含：

```text
SKILL.md                 # 入口 contract、触发条件、边界、progressive reference index
references/<topic>.md    # 按需加载的细分规则
examples/<route>.md      # 可复制的 route 示例与 expected artifact refs
schemas/*.json           # machine contract，至少覆盖 input/output/error reason_codes
```

`SKILL.md` 只能承载入口级 contract 和 reference index，不得内联历史 33 skills 的全部正文。loader 默认只加载 public `SKILL.md`；只有当 intent/topic 命中时才加载对应 reference/example。禁止一次性加载所有历史 skill 或把 internal modules 重新暴露成 host-visible skill 列表。

### BranchContext + Harness Boundary Contract（R9）

分支治理是 v2 kernel hard gate，不随 skill surface 精简而移除。所有会写项目文件、运行 agent、导入 evidence、给 release 建议的 harness 都必须消费同一个 `BranchContext.v1`：

```text
caller_cwd, target_project_root, admitted_worktree_path,
base_branch, feature_branch, truth_canonical_branch,
worktree_mode, merge_base_head, git_head,
dirty_policy, protected_paths, admission_artifact_ref
```

`BranchContext.v1` 由 workspace admission 产生，是 truth/design/implement/qa-evidence/release 的共同前置输入。任何 harness 不得用 `Path.cwd()` 或 host shell 当前分支推断目标项目；`target_project_root` 与 `admitted_worktree_path` 冲突时 fail-closed，reason_code 必须指向具体字段。

Harness boundary 同样保留为 kernel contract：

- `truth` 可以冻结/refreeze requirement truth，但不能声称 implementation/QA/release 完成。
- `implement` 只能消费 frozen truth、bound design、decision packet 和 BranchContext；不能修改 frozen truth，也不能自证 QA/release pass。
- `qa-evidence` 只能裁决 evidence 与 TC/AC 绑定；不能修 truth 或实现。
- `release` 只能在 QA evidence、human confirmation、hook evidence contract 均满足时给 release go/no-go。
- `loop` 只能编排这些 harness；不能绕过 release human gate 或 branch admission。

## Diagram Truth Layer

`state_machine_required`: **true**

### 权威选择（canonical）

| 轴 | Canonical 来源 | 落地 |
|----|----------------|------|
| **WorkflowStage**（产品生命周期） | plan §2.1 + v1.6 package 扩展 | `beacon-core` enum；含 `Prototype`；扩展阶段 `Think`/`Freeze`/`Archive` 为 v1.6 兼容，转换表显式标注 |
| **Delivery FSM**（goal/run 编排） | plan §2.3 为主链；v1.6 `delivery-state` 子图为 implement 路径 | DB `runs.status` 存 **运行时压缩枚举**（见下）；`lifecycle_events` 存 plan 链事件 |
| **Gate 轴** | freeze / qa / release / implement | `gate_results.gate_type` + FSM `Blocked` reason_codes |

### WorkflowStage（类型层）

```text
Think, UserStory, Prd, TestCase, Prototype, Freeze, Implement, Qa, Release, Archive
```

### StageStatus（类型层）

```text
NotStarted, InProgress, Blocked, Completed, Failed, Skipped,
Crashed, TimedOut, Interrupted, Repairing
```

### Delivery FSM — Plan 主链（逻辑层，写入 lifecycle_events）

```text
IntentCapture → PromptSnapshot → IntentReview → BrainstormReviewSynthesis
→ [UserDecisionPending] → TruthGapScan → [TruthFill → TruthFreezeGate]
→ [DesignRequired? → DesignPrimitiveBind] → ImplementAdmission → ImplementLoop
→ EvidenceImport → QaPending → [RepairFromQa ↺] → ReleasePending
→ [RepairFromRelease ↺] → TerminalClosed | TerminalAborted
```

### Delivery FSM — 运行时压缩（runs.status，与 v1 beacon-loop 操作语义对齐）

```text
Created, Resolving, Running, Paused, Stopping, Stopped,
Succeeded, Failed, Repairing, Importing, AwaitingQa, Closed
```

**映射义务**：每个 `runs.status` 必须可追溯到 plan 主链节点或 v1.6 implement_loop 子状态；非法转换 fail-closed（typed error + reason_code）。

### Phase Controller（v2 六能力面）

```text
loop (Governor) → truth (Kernel) → design? (Kernel) → implement (Agent) → qa-evidence (Harness) → release (Harness)
```

写入 `runs.metadata_json.phase`；与 WorkflowStage **不同轴**，不得混写为同一 enum。

## 背景与动机（Plan §1）

v1 架构级缺陷必须在 v2 被 **结构性消除**，不得仅靠文档或 wrapper：

| 缺陷 ID | 描述 | v2 承诺 |
|---------|------|---------|
| D-01 | 状态机无编译期约束 | `beacon-core` 枚举 + 转换表 + `thiserror` |
| D-02 | 巨型单文件（如 `prototype_utils.py` 5k+ 行） | crate 边界 + 模块 ≤500 行软上限 |
| D-03 | 双栈分裂（Python beacon + TS beacon-loop） | 统一 `beacon-orchestrator`（Rust） |
| D-04 | 运行态散落 JSON/SQLite 多源 | 全局 `beacon.db` + Spine 单查询面 |
| D-05 | Gate 与状态脱节 | `gate_results` 表 + reason_codes 与 FSM 绑定 |
| D-06 | 无统一 Operator Spine | `beacon spine show/list/artifacts/gate` |
| D-07 | 长任务 resume/stop 语义分裂 | orchestrator 统一 checkpoint + signal |
| D-08 | 证据链可伪造/可跳过 | `EvidenceChain` 校验 + 签名链延续 |
| D-09 | 多项目无机器级索引 | `projects` / `project_versions` 表 |
| D-10 | QA/Release JSON 与真相双写漂移 | MD truth 唯一；JSON 仅投影/缓存 |

## 架构决策（Plan §2）

### AC-001 Rust 核心 + 极简 harness

- **AC-001**：v2 默认执行面为 Rust workspace（`packages/beacon-rs/` 或等价根）。
- **AC-002**：v2 core closure **不包含** `beacon-python` / PyO3 / v1 Python runtime fallback；若仓库仍存在历史 scaffold，必须在 P4 前移除或标记为 archive-only，不能作为验收依赖。
- **AC-003**：v1 Python / Node / 33 skills 只可作为 migration/archive reference；v2 新能力不得 fallback 到 Python 路由。

### AC-004 需求真相边界

- **AC-004**：`features/<slug>/truth.md` 与 `docs/beacon/<version>/` 为 **唯一** requirement authority。
- **AC-005**：`~/.beacon/beacon.db` 不得存储可编辑的需求正文；只可存 metadata、FSM、gate、artifact 指针。
- **AC-006**：`.beacon/qa/*.json`、`.beacon/gate-report.json` 等 v1 投影在 v2 为 **非权威**；Spine 读 DB 优先，文件仅 fallback/export。

### AC-007 存储三层（Plan §2.5）

| 层 | 权威 | 路径 |
|----|------|------|
| L1 需求真相 | MD only | `docs/beacon/<version>/features/<slug>/` |
| L2 运行态 | 全局 SQLite | `~/.beacon/beacon.db`（WAL） |
| L3 Blob | 磁盘 | `<project>/.beacon/{evidence,logs,junit,screenshots,...}` |

- **AC-007**：实现必须遵守上表三层分离。
- **AC-008**：**禁止** `<project>/.beacon/beacon.db` 作为运行态权威（v2 明确否决 per-project DB）。
- **AC-009**：**禁止** `<project>/.beacon/loop/ledger/loop-runs.db` 作为 v2 权威；v1.6 ledger 须在 migration 中导入全局库后只读归档。
- **AC-010**：Blob 文件变更时 `artifact_refs` 必须更新 `content_hash`；hash 不匹配时 Spine 标记 `stale`。
- **AC-011**：`beacon doctor projection rebuild` 须能从已注册 `project_root` 的 MD + blob + 遗留 v1 JSON **重建**全局库索引（plan §2.5 原则 4）；rebuild 后 `spine show` 与 rebuild 前 snapshot 在 lifecycle/gate 字段上一致（artifact 指针允许 stale 标记）。

### AC-012 存储原则（Plan §2.5）

- **AC-012**：Append-only `lifecycle_events`；状态覆盖写 `feature_lifecycle` 当前快照。
- **AC-013**：每次 gate 评估写入 `gate_results`（pass/fail/blocked + reason_codes JSON）。
- **AC-014**：每次 run 启动写入 `runs`；checkpoint 写入 `checkpoints`。
- **AC-015**：Spine 查询 **DB-first**；blob 仅当 `artifact_refs` 存在且 hash 有效时拼接。
- **AC-016**：v1 JSON 运行态只允许 **export/import 迁移**，不得与 DB 双写竞争权威。

### AC-017 Operator Spine API（Plan §2.5）

`SpineSnapshot` 须兼容 plan §2.5 与 v1.6 spine 语义：

```rust
SpineSnapshot {
  run_id, project_key, project_root, version, feature_slug,
  lifecycle_stage, lifecycle_status,
  phase, phases_completed, phase_promoted,
  next_harness, next_action, progress_status,
  active_run_id, run_status, iteration,
  gate_results: Vec<GateResultSummary>,
  artifact_refs: Vec<ArtifactRef>,
  blocking_reason_codes, updated_at
}
```

- **AC-017**：必须实现 `beacon spine show [--project PATH] [--feature SLUG] [--json]`。
- **AC-018**：必须实现 `beacon spine list [--project PATH] [--status STATUS] [--json]`。
- **AC-019**：必须实现 `beacon spine artifacts <run-id> [--json]`。
- **AC-020**：必须实现 `beacon spine gate <feature> [--version vX] [--json]`。
- **AC-021**：必须实现 `beacon projects list|register|show [--json]`（机器级多项目）。

## Crate 结构（Plan §3）

```
packages/beacon-rs/
  beacon-core/
  beacon-store/
  beacon-orchestrator/
  beacon-gate/
  beacon-cli/
  beacon-proto/          # v2.0.0 不做（D-V2-001 accepted defer）
```

- **AC-022**：workspace core closure 必须收敛为五个 Rust crate（core/store/orchestrator/gate/cli）；`beacon-python` 不属于 v2.0.0 core closure。
- **AC-023**：crate 依赖方向：`cli -> {gate, orchestrator, store, core}`；`store -> core`；`orchestrator -> {store, core}`；禁止循环依赖。
- **AC-024**：v2.0.0 **不交付** `beacon-proto`/gRPC（**D-V2-001 accepted defer**）；CLI 与 orchestrator 不得硬依赖 gRPC；未来版本可单独 reopen。
- **AC-025**：单文件模块超过 500 行须拆分或 ADR 说明例外（对齐 D-02）。

## 类型层状态机（Diagram Truth Layer）

- **AC-026**：`WorkflowStage` 与 `StageStatus` 在 `beacon-core` 以 Rust `enum` 定义，禁止字符串裸奔。
- **AC-027**：阶段转换表显式编码；非法转换返回 typed error + reason_code。
- **AC-028**：`Blocked` 必须携带 `reason_codes: Vec<String>` 与可选 `blocking_gate`。
- **AC-029**：`Skipped` 仅允许带 `user_accepted_deferral_id` 或 deferral ledger 引用。
- **AC-030**：`Crashed` / `TimedOut` / `Interrupted` 须写入 `lifecycle_events` 且可触发 recovery 路径。

## Delivery FSM（运行时 + plan 映射）

- **AC-031**：Delivery 运行时 12 状态在 `beacon-core` 定义并与 `runs.status` CHECK 一致。
- **AC-032**：plan 主链节点转换须写入 `lifecycle_events`（可审计，非仅内存）。
- **AC-033**：`Paused` / `Stopping` / `Stopped` 与 v1 beacon-loop graceful+force stop 对齐。
- **AC-034**：`Repairing` 须持久化 repair payload 到 `artifact_refs`。
- **AC-035**：`AwaitingQa` 仅在 `import-evidence` 成功后可进入。
- **AC-036**：`Closed` 仅 release gate pass 或用户显式 archive；orchestrator **不得**自设 Closed。

## 证据链（Plan §4.3）

- **AC-037**：`EvidenceChain` 含 `manifest_hash`、`signature_chain`、`artifact_refs` 有序列表。
- **AC-038**：import 断链 fail-closed → `EVIDENCE_CHAIN_BROKEN`。
- **AC-039**：v1 `.beacon/evidence-signature-chain.json` 可迁移为 v2 记录。

## Orchestrator（Plan §5）

| 维度 | v2 要求 |
|------|---------|
| 入口 | `beacon run goal` / `resume` / `stop` / `status` |
| 真相预检 | `truth-map resolve` fail-closed |
| Agent backends | Codex, Claude, Acp, Subprocess, ImplementHarness（plan §3.4） |
| Checkpoint | `checkpoints` + blob `checkpoint.json` |
| Caps | max_iterations, max_tokens, stop_when |
| Git | clean preflight；branch 模式 P2；**worktree 全模式 P3（AC-099）** |

- **AC-040**：`beacon-orchestrator` 经 `beacon-cli` 暴露 goal/resume/stop/status。
- **AC-041**：启动前 `truth-map resolve`；blocked → exit != 0 + 推荐 `beacon-gen-change`。

### Agent Backend Contract（真集成 — 选项 A）

对齐 v1.6 `beacon-loop-native-runner` AC-028/029 与 plan §3.4。**禁止** fixture 单次硬编码冒充多轮；**禁止** zero-assertion contract test 作为 closure 证据。

`IterationResult`（所有 backend 必须输出）：

```text
success, summary, key_changes_made, key_learnings,
optional stop_signal, token_usage, agent_name
```

- **AC-042**：`AgentBackend` trait 定义 `iterate`, `health_check`, `abort`, `name`；`IterationResult` 在 `beacon-core` 强类型定义。
- **AC-043**（P2）：`CodexBackend` **真多轮** integration：同一 run-id 下 ≥2 次成功 `iterate` 或触达 `--max-iterations`/`--stop-when`；iteration 产物写入 `artifact_refs`；**非** env fixture 单次返回。
- **AC-044**（P2）：`SubprocessBackend` 完成 1 次真 integration iteration（可控测试 harness 命令），输出符合 AC-042 schema。
- **AC-045**（P3）：`ClaudeBackend` 完成 1 次真 integration iteration；`health_check` 与 `abort` 有 integration 测试证据；输出 schema 与 AC-042 一致。
- **AC-046**（P3）：`AcpBackend`（CLI `acp:<target>`）完成 1 次真 integration iteration；输出 schema 与 AC-042 一致。**Cursor 宿主不单独列为 backend**，走 ACP 或 subprocess。
- **AC-099**（P3）：Git **worktree 全模式 parity**（**D-V2-004 rejected defer**）：支持 `worktree`、`current-branch`、`beacon-run/<run-id>`（或 plan 等价 run-branch）branch 模式；非法组合 fail-closed（如 `current-branch` + `--isolated-worktree`）；harness/agent `project-root` 与 worktree cwd 对齐（对齐 v1.6 AC-026）。
- **AC-100**（P3）：`ImplementHarnessBackend` 完成 1 次真 integration iteration（**D-V2-005 rejected defer**）：经 `beacon implement` harness 在 worktree 内跑通一轮；输出 schema 与 AC-042 一致；禁止 subprocess-only 冒充 harness 或 zero-assertion integration test。

- **AC-047**：checkpoint resume 后 iteration 递增；notes 注入写入 `lifecycle_events`（可审计）。
- **AC-048**：`stop_when` 移植 v1 `stop-when-gate`（含 gate pass 早停）。
- **AC-049**：orchestrator **禁止**输出 QA pass / release ready / feature complete verdict。
- **AC-050**：Phase Controller 四阶段写入 `runs.metadata_json`；phase 转换写 `lifecycle_events`。

### Loop Engineering 对齐 AC（R7 增补）

- **AC-105**（P3）：`beacon-v2 run --agent <codex|claude|acp:*>` CLI 直接选 agent 跑长任务编码落地；agent 选择映射到对应 AgentBackend；loop 在 CLI 进程内跑，checkpoint/resume/信号（SIGINT graceful stop）保证 host 稳定，**无 daemon**。
- **AC-106**（P3）：`stop_when` 对齐 v1.6 AC-071 **maker≠checker**——loop **禁止**仅因 agent 自报 `stop_signal` 而终止；每轮 agent 后必须执行外部可验证检查（harness gate exit 0 / `--stop-check-cmd` exit 0 / terminal evaluator）；agent 自报 alone → `reason_code=stop_when_unverified`，continue 下一 iteration。
- **AC-107**（P3）：Developer Feedback Loop 人注入 checkpoint——`beacon-v2 run --feedback-checkpoint` 在每 N iteration 后暂停 loop，等待人注入上下文修正（写入 `lifecycle_events` notes_injected），resume 后基于修正重新 iterate；人注入是 harness 接口，不绕过 truth（truth 变更仍走 change/refreeze）。
- **AC-108**（P3）：Loop Engineering 三层 Loop 可观测——spine snapshot 含 `loop_layer` 字段（coding/developer/realworld），标注当前 run 在哪层 Loop；Coding Loop 内的 iteration + Developer Feedback 的 checkpoint + Real-world 的 research 都可追溯。

## 性能目标（Plan §4 + §2.5）

| AC | 指标 | 目标 | 验收 |
|----|------|------|------|
| AC-051 | CLI 冷启动 | p95 < 100ms 本地 | `cargo bench cold_start` CI 归档 |
| AC-052 | `beacon spine show` | p95 < 50ms | `cargo bench spine_show` |
| AC-053 | `beacon truth-map resolve` | p95 < 200ms | bench + fixture project |
| AC-054 | Gate 计算 | p95 < 50ms | `beacon-gate` bench |
| AC-055 | 单文件证据 hash 验证 | p95 < 10ms | rayon 并行 bench |
| AC-056 | DB migration v1→v2 | < 60s 典型 fixture | integration timer |
| AC-057 | orchestrator iteration 调度 | < 100ms 不含 agent | bench 不含 agent 调用 |
| AC-058 | `beacon.db` 体积 | 软上限 500MB | 超阈值 WARN 日志 + metric |

**AC-051..AC-058** 均须 **criterion/bench 或 CI benchmark job** 归档；**不得** 仅 smoke test 或文档声明替代。

## 极简 Harness Surface（取代 Plan §6 Python 兼容）

- **AC-059**：v2 host-visible harness surface 只暴露 `loop`、`truth`、`design`、`implement`、`qa-evidence`、`release` 六个一等能力。
- **AC-060**：v2 默认走 Rust 路径；`BEACON_V2=1` 不再是 opt-in 兼容开关。
- **AC-061**：`BEACON_STORE_PATH` 测试隔离；生产默认 `~/.beacon/beacon.db`。
- **AC-062**：任何 v1 Python/legacy skill invocation 在 v2 core 中必须返回 migration/archive route 或 `reason_code=legacy_python_removed`，不得静默 fallback。
- **AC-063**：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其 contract metadata；不得要求 33 skills smoke 作为 v2 closure。

## CLI 面

- **AC-064**：spine/projects/workflow/truth-map/implement/qa/release/run 子命令可解析且 `--help` snapshot 稳定。
- **AC-065**：spine/projects/run 支持 `--json` 且 schema 可校验。
- **AC-066**：v1 reason_codes 对齐：`gate_results.reason_codes_json` 失败样例须含 documented code；`docs/beacon/v2.0.0/execution/reason-codes.md` 与 **集成测试** 中至少 5 个 code 往返一致。

## SQLite Schema（Plan §7）

全局库：`~/.beacon/beacon.db`，WAL。

### 九表字段合同

- **AC-067**：`projects`（id, root_path UNIQUE, name, registered_at）
- **AC-068**：`project_versions`（id, project_id, version, docs_root, is_current）
- **AC-069**：`feature_packages`（id, project_version_id, slug, truth_path, tests_path, status）
- **AC-070**：`feature_lifecycle`（feature_id, stage, status, reason_codes_json, updated_at）
- **AC-071**：`runs`（id, feature_id, run_kind, status, iteration, started_at, ended_at, metadata_json）
- **AC-072**：`lifecycle_events`（id, feature_id, run_id, event_type, payload_json, created_at）
- **AC-073**：`gate_results`（id, feature_id, gate_type, verdict, reason_codes_json, evaluated_at）
- **AC-074**：`artifact_refs`（id, run_id, kind, abs_path, content_hash, size_bytes, created_at）
- **AC-075**：`checkpoints`（id, run_id, iteration, state_json, created_at）

### DAO / Migration / Spine

- **AC-076**：`beacon-store` 提供 ProjectDao, FeatureDao, RunDao, GateDao, ArtifactDao, SpineDao。
- **AC-077**：migration `v1_runtime_ledger`：自 `~/.beacon/runtime-ledger/runtime-ledger.sqlite3` 导入。
- **AC-078**：migration `v1_loop_ledger`：扫描各项目 `loop-runs.db` 一次性导入。
- **AC-079**：migration `v1_qa_projection`：可选历史只读导入。
- **AC-080**：schema `user_version` 管理；降级禁止。
- **AC-081**：`SpineDao::snapshot` 联查 lifecycle + run + gate + artifacts。
- **AC-082**：`list` 支持 lifecycle/run status 过滤。
- **AC-083**：`artifact_refs.abs_path` 必须绝对路径。

## 并行共存（Plan §8）

| Phase | 交付物 | v1 共存 |
|-------|--------|---------|
| P0 | core + store + schema + migration **skeleton**（非 production migration） | v1 全功能 |
| P1 | Spine read + projects | v1 JSON 仍可写 |
| P2 | orchestrator MVP + **AC-043/044** codex/subprocess 真集成 | beacon-loop 并行 |
| P3 | gate 写库 + **AC-045/046** claude/acp 真集成 + migration 完成 | legacy projection/import 只读对照 |
| P4 | 六能力 harness surface + legacy removal | v1 Python/33 skills 仅 archive reference |
| P5 | ~~proto~~ **v2.0.0 跳过**（D-V2-001） | v1 无 gRPC 亦可 |
| P6 | 默认 v2 + benchmark 门禁 | 切换 |

- **AC-084**..**AC-090**：P0–P6 阶段出口（见 tests.md TC-084–090）；**P5 在 v2.0.0 以 D-V2-001 accepted defer 跳过**，不阻塞 P6 switch-over。

## 风险与缓解（Plan §9）

- **AC-091**：CI **必须**执行 `cargo build/test` for `beacon-rs` matrix（macOS + Linux 至少）；非仅 README 声明。
- **AC-092**：migration 前自动备份 runtime-ledger 与既有 DB。
- **AC-093**：双写期 **单一写者**；双向同时写须测试失败。
- **AC-094**：harness surface / legacy removal 回归失败 → `beacon-gov-doctor`，禁止静默 legacy fallback。
- **AC-095**：benchmark 相对 baseline 回退 >10% 阻断 P6 switch-over。

## 验收总则（Plan §10）

- **AC-096**：每 phase 跑 tests.md 对应 TC 子集 + phase integration job。
- **AC-097**：全量 AC closure 由 evaluator 裁决；generator/implementer 不得自证 release ready。
- **AC-098**：frozen package 权威高于 plan；plan 变更须 promote。

### v1.6 治理与 Planner Runtime 移植（R2 增补）

- **AC-101**（P3）：`beacon-gate` 在 freeze/refreeze 前执行 **Truth Integrity Gate**，语义对齐 v1.6 `build_truth_integrity_gate`：空缺 AC、软 TC、未拍板 deferral、假交付、package validation 失败 → hard block + `repair_route`；已 frozen 历史包默认 `audit_only` 不阻断。
- **AC-102**（P2）：`beacon-orchestrator` 的 `planner_review()` 必须产出 v1.6 multi-agent runtime 同构字段（`reviewer_lanes`、`findings`、`synthesis`、`execution_mode`、`fallback_reason`、`runtime_evidence_only=true`）；artifact 写入 `artifact_refs`；无 subagent 时 **禁止** 声称 parallel execution。
- **AC-103**（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 Rust gate；`--mode block` exit code 与 v1.6 一致，不使用 PyO3 compat。
- **AC-104**（历史 P0 证据）：2026-06-13 的 `packages/beacon-rs/` scaffold 与 12 个 P0 unit tests 是 implementation candidate evidence；R8 minimal-kernel closure 需重新验证 AC-002/022/059/063 后才可算 P0/P4 完成。

### R8/R9 Minimal Kernel AC（AC-109–130）

- **AC-109**：v2 public kernel surface 明确定义并只允许六个一等能力：loop / truth / design / implement / qa-evidence / release。
- **AC-110**：v1 Python / Node / 33 skills compatibility 从 v2 core closure 移除；只保留为 migration/archive reference。
- **AC-111**：truth pre-freeze 必须生成 `intent_snapshot.v1`，含 raw_prompt、normalized_intent、strength_signals、non_negotiables、open_questions、scope_mode、confidence。
- **AC-112**：每轮 plan/truth/review/brainstorm 必须保存 prompt snapshot hash，并标记 accepted/latest；loop 只能消费 latest accepted snapshot。
- **AC-113**：intent confidence 低、强意图冲突、scope 未确认或 deferral 未拍板时，truth freeze fail-closed。
- **AC-114**：loop 启动必须读取 `decision_packet.v1`；缺失、过期或引用未接受 prompt snapshot 时不得进入 implement。
- **AC-115**：UI/视觉/交互 feature 必须先产出并绑定 `design_primitives.v1`；内容覆盖 tokens、components、layout、state matrix、responsive、a11y、visual evidence baseline。
- **AC-116**：implement admission 必须同时验证 truth_frozen、decision_packet_current、design_bound（当 required）、worktree_admitted、program_next_action_aligned、dependencies_closed。
- **AC-117**：所有 governed agent iteration 写 `agent_trace.v1`，事件类型覆盖 decision / failure / retry / output / tool_call / gate_verdict。
- **AC-118**：stagnation detector 基于 agent trace 确定性识别 repeat_failure / repeat_labor / plateau，输出 `stagnation-report.v1`。
- **AC-119**：remediation sandbox 在 governed worktree 内执行 overlay/eval/rollback；不得写 canonical truth，eval pass 后仍需 human review。
- **AC-120**：loop guardrails 包含 pattern registry、failure catalog、token budget、readiness audit、workspace lease、protected path denylist。
- **AC-121**：qa-evidence 必须产出 confidence_chain 与 truth-derived business FSM coverage；状态机 gap 削弱或阻断对应 evidence claim。
- **AC-122**：QA defect 必须形成 defect -> fix -> regression evidence chain；缺段 `repair_chain_broken` 或 `regression_skipped` 时 release block。
- **AC-123**：closure evidence 必须包含可执行行为验证、至少一个有效断言、AC/TC 绑定 artifact 与运行佐证；纯静态 shell、源文本匹配或无行为恢复控件不得满足 closure。
- **AC-124**：release human gate 是不变量；`auto_decide=true` 不得触发 release gate 通过。
- **AC-125**：v2 public skill surface 只暴露六个入口；governor/doctor/router/hooks/metadata/debug/archive 只能作为 internal module 或 reference topic 出现，不得重新成为 host-visible 一等 skill。
- **AC-126**：skill loader 必须采用 progressive disclosure；默认只加载 public `SKILL.md`，按 intent/topic 选择性加载 `references/` 与 `examples/`，并产出 `skill_load_plan.v1`。
- **AC-127**：六个 public skill 都必须提供 route examples；示例覆盖 `truth review -> decision_packet -> loop`、`design_primitives -> implement`、`qa-evidence -> release`、`branch blocked -> repair_route`，且示例不是 requirement authority。
- **AC-128**：`BranchContext.v1` 是所有写入/agent/evidence/release harness 的共同输入，字段至少覆盖 caller cwd、target project root、admitted worktree、base/feature/canonical branch、dirty policy、protected paths 与 admission artifact。
- **AC-129**：branch/workspace governance 是 hard gate；任何 generator/implement/qa-evidence/release 写路径缺失 admission 或 BranchContext mismatch 时必须 fail-closed，不能降级为 warning。
- **AC-130**：Harness boundary 以 reason_code enforce：planner/truth 不实现，implement 不改 frozen truth/不自评 QA，qa-evidence 不改 truth/implementation，release 不绕过 human gate，loop 不替代任一裁决面。

## Parity Matrix（Plan 场景复刻索引）

| Plan 章节 | AC 范围 | 场景 |
|-----------|---------|------|
| §1 缺陷 | AC-001–010, D-01..10 | 结构性消除 |
| §2 存储+Spine+rebuild | AC-004–021 | 三层+Spine+projection rebuild |
| §3 Crate | AC-022–025 | workspace |
| §4 FSM+性能 | AC-026–036, AC-051–058 | 双 FSM+benchmark |
| §5 Orchestrator+Agent | AC-040–050, **AC-042–046/099/100 真集成** | 无空壳 AC；worktree+implement 不 defer |
| §6 极简 Harness+CLI | AC-059–066, AC-109–130 | 六能力 surface + legacy removal + progressive disclosure + BranchContext |
| §7 Schema | AC-067–083 | 九表+DAO |
| §8 阶段 | AC-084–090 | P0–P6 |
| §9 风险 | AC-091–095 | 可执行缓解 |
| §10 验收 | AC-096–098 | evaluator 裁决 |
| §v1.6 治理 | AC-101–103 | TIG + planner multi-agent + doctor 路由 |
| §P0 证据 | AC-104 | beacon-rs scaffold 已完成 |

## Deferral Ledger

| deferral_id | capability | reason | user_decision | revisit |
|-------------|------------|--------|---------------|---------|
| D-V2-001 | `beacon-proto` gRPC | v2.0.0 不做远程编排 | **accepted** | post-v2.0.0 |
| D-V2-002 | PGLite/Postgres | 非 v2 默认 | rejected | — |
| D-V2-003 | per-project `beacon.db` | 与全局 Spine 冲突 | rejected | — |
| D-V2-004 | worktree 全模式 parity | 用户拒绝延期 | **rejected**（in-scope **AC-099** P3） | — |
| D-V2-005 | ImplementHarnessBackend 真集成 | 用户拒绝延期 | **rejected**（in-scope **AC-100** P3） | — |
| DEF-loop-006 | Real-world Feedback Loop 闭环 | 需真实反馈源集成（用户反馈/数据/竞品） | **accepted defer** | post-v2.0.0 |

**已移除**：r1 AC-040 空壳 contract test 路径 — 由 AC-045/046 真集成取代；**不 defer** claude/acp/worktree/implement-harness。

## Non-Goals

- 不把 Markdown truth 迁入 DB。
- 不把 QA JSON 升格为 truth authority。
- 不保留 v1 Python/PyO3/33 skills 作为 v2 runtime、fallback 或 closure 依赖。
- 不用 orchestrator 替代 evaluator 裁决。
- 不用空壳/stub/纯文档闭环 作为唯一 AC 验收。

## Freeze Readiness

1. ~~用户确认 Deferral Ledger~~ **已完成**：D-V2-001 accepted；D-V2-004/005 rejected（AC-099/100 in-scope）。
2. `tests.md` 每个 AC 至少一行 **行为级** TC（非仅 `--help`/文件存在）。
3. `tasks.md` P0–P6 与 AC 映射完成。
4. `requirement_clarity` open question 清零或 defer。
5. **无空壳-only AC**；agent/worktree/implement 类 AC 须 integration tier（AC-043–046, AC-099–100）。
6. **v1.6 upstream**（AC-101–103）在对应 phase 有 behavior-level TC，不得仅用「后续移植」一句带过。

**当前状态**：`frozen` / **R9**（revision `r9-skill-surface-disclosure-frozen`）— 2026-07-15 refreeze：在 R8 极简 Rust harness kernel 基础上，补充六 public skill 的 progressive disclosure package contract；明确 branch/workspace governance、doctor/router/hooks/metadata/status/archive/debug 作为 internal module 保留；将 `BranchContext.v1` 与 Harness Boundary 设为 kernel hard gate。

## User Stories

### US-001 Operator 单一 Spine 查询

**AC**：AC-017–021, AC-081–083

### US-002 多项目 registry

**AC**：AC-067–068, AC-021

### US-003 长任务统一编排 + 真 agent 集成

**AC**：AC-040–049, **AC-043–046, AC-099–100**

### US-004 治理门禁写库

**AC**：AC-013, AC-020, AC-073, AC-028

### US-005 v1 无损迁移 + rebuild

**AC**：AC-077–079, AC-092, **AC-011**

### US-006 极简 harness surface

**AC**：AC-059–063, AC-109–130, AC-064–066

## Revision History

| Rev | 变更 |
|-----|------|
| r1 | 初稿 promote 自 plan |
| r2 | planner review 选项 A：AC-042–046 真集成；Diagram Truth Layer；AC 重编号至 098；禁止空壳 AC |
| r3 | Deferral 拍板：D-V2-001 accepted（无 proto）；D-V2-004/005 rejected → AC-099 worktree + AC-100 ImplementHarness P3 |
| r3.1 | User Intent Snapshot + Alignment Surface vs Phased Backlog；明确海级单包不煮干全 plan |
| r4 | tests Alignment Surface 行为级 TC；research version projection binding；**frozen R1** |
| r5 | R2 reopen：v1.6 TIG（AC-101）+ multi-agent planner review（AC-102–103）+ P0 done（AC-104）；upstream frozen inputs 表 |
| r6 | R3 reopen：补 v1.6.3 9 个免疫修复进 upstream 表（语义重现义务）；Truth 规范基准段（v1.5.2 package-authoritative，不生成 prd/user-story 顶层文档）；canonical_refs 字段名对齐 truth/tests/tasks/evidence |
| r7 | R4 reopen：Loop Engineering 三层 Loop 模型（Coding/Developer/Real-world ↔ beacon 生命周期）+ host 运行模式（CLI 进程+checkpoint/resume/信号，无 daemon）+ AC-105/106/107/108 + v1.6 loop upstream（R10 AC-071 → AC-105/106）+ DEF-loop-006 Real-world Loop 延后 |
| r8 | R5 refreeze：v2 minimal Rust harness kernel；六个一等能力；v1 Python/PyO3/33 skills 移出 core closure；intent_snapshot/prompt_snapshot/decision_packet/design_primitives gate；v1.6.4–1.6.6 loop/QA/agent 排查能力以 Rust 语义重现 |
| r9 | R6 refreeze：六 public skill 渐进式披露 contract；内部保留 branch governance / doctor / router / hooks / metadata / status / archive / debug；新增 BranchContext.v1 与 Harness Boundary hard gate（AC-125–130） |
