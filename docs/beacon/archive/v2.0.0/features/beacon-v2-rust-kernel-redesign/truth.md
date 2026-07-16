---
slug: beacon-v2-rust-kernel-redesign
version: v2.0.0
status: frozen
language: zh
revision: r15-dual-track-unified-skill-score
canonical_refs:
  truth: docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/truth.md
  tests: docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/tests.md
  tasks: docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/tasks.md
  evidence: docs/beacon/archive/v2.0.0/features/beacon-v2-rust-kernel-redesign/evidence.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
source_plan: docs/plans/beacon-v2-redesign.md
planner_review: beacon-pln-review option-A true-integration
change_reason: "UD-B long-term dual-track product; unified skill score in v2.0.0 contract usable for v1; score-only human-edit (no auto SKILL.md mutation)"
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

**User Intent（冻结锚点，一行）**：v2.0.0 交付 **Rust 极简 harness kernel + 六个一等能力（loop / truth / design / implement / qa-evidence / release）+ 全局 `beacon.db` + Operator Spine + 跨 harness loop 闭环**；与 **v1 产品轨长期双轨并存（UD-B）**；**统一 skill 评分**（结构+实效，只评人改）写入合同且可用于 v1；v1 不得作为 v2 runtime 静默 fallback，亦不得被 v2 closure 强制退休。

**需求真相** 仍只存在于 Markdown feature package（`docs/beacon/archive/v2.0.0/` + `features/<slug>/truth.md`）。  
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
| 用户原话（稳定 paraphrase） | v2 使用 Rust 重写极简 Beacon harness；保留六个一等能力；plan 阶段强识别意图、保存提示词快照、反复对齐，产出 loop 可一键跑闭环的决策包；实现前必须有视觉/设计原语绑定。**R15 用户拍板**：产品为 **长期双轨（选项 B）**——v1 与 v2 并存且合并互不影响；**统一 skill 评分**写入 v2.0.0 合同且对 v1 同样可用；评分模式为 **只评分、人改**（禁止优化器自动改 SKILL.md） |
| `lake_or_ocean` | **海**（见 research）— 单包 truth **不**等于全量实现 closure；按 phase 煮干 |
| 强度词 | 极简 harness、长期双轨、统一稳定评分、只评人改、强感知识别、一键决策跑闭环、视觉设计实现前前置 |
| 非协商边界 | 需求不进 DB 当权威；orchestrator 不裁决 QA/release；无空壳验收；**v2 runtime 路径不得静默 fallback 到 v1 Python**（反之亦然）；**不得以 P6「切默认」退休 v1 产品轨**；design_required 时未绑定设计原语不得 implement；skill 评分不得冒充 QA/release；评分器不得自动改写 SKILL.md |

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

### Program Orchestration Surface（R14）

`v2-0-0-rust` 是 v2.0.0 Rust 重构的 canonical program 编排面，落地于：

- `docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-manifest.md`
- `docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/phase-graph.md`
- `docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/admission-gates.md`
- `docs/beacon/archive/v2.0.0/programs/v2-0-0-rust/program-run-state.json`

program intent 来自已接受的 planner support advisory 与 stash 中的 P0 intent capture；升级后以 main/master canonical truth branch 上的 program surface 为准，stash 不再作为 requirement authority。

program phase graph 将海级实现拆成湖级 slices：P0 core/store、P1 spine/projects、P2 orchestrator/TraceSpine/standard flow、P3 gate/migration/agent parity、P4 six-ability harness surface、P6 benchmark/release closure。进入 implement 前，program admission 必须证明 program surface 存在、canonical refreeze 已提交、feature branch 已合入 truth baseline、workspace admission 产出 `BranchContext.v1`、`decision_packet.v1` 可用且 TraceSpine 前置条件完整。

R13 曾暴露 reason-only / machine-only refreeze 漂移风险；R14 的要求是把 program 编排写入 canonical truth/package surface 后再 refreeze，避免 machine revision 与人类叙事再次断开。

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
| `loop` | 跨 harness 编排 truth -> design? -> implement -> qa-evidence -> release；支持 auto-decide、checkpoint/resume、worktree lane 并行推进 | 不替代 truth/implement/QA/release；缺 decision_packet 或 TraceSpine 不得进入 implement；release 必须人工确认 |
| `truth` | plan/pre-freeze intent 捕获、prompt snapshot、brainstorm/review synthesis、truth gap scan、freeze/refreeze | low-confidence intent、未拍板 deferral、状态机缺失时不得 freeze |
| `design` | UI/视觉/交互交付的 design primitive contract；产出 tokens/components/layout/state/a11y/visual evidence baseline | `design_required=true` 且未绑定 `design_primitives.v1` 时不得 implement |
| `implement` | 只消费 frozen truth + bound design + admitted worktree + decision_packet + TraceSpine；运行 agent/backend loop | 不改 frozen truth，不自证 QA/release pass，不接受 static-only evidence；缺 trace append fail-closed |
| `qa-evidence` | 行为证据导入、confidence chain、business FSM coverage、defect repair regression、trace/stagnation/remediation 报告 | 缺行为证据链、回归链、trace event 绑定或断链时 release block |
| `release` | 最终 go/no-go gate，检查 truth/design/qa/evidence/TraceSpine/human confirmation | 不允许 auto-decide 越过 human release gate；trace incomplete 不得 release |

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

### TraceSpine Kernel Contract（R10）

v1.6.6 的 `agent_trace.v1` / stagnation detector / remediation sandbox 只算局部能力，不能在 v2 继续降级为 advisory signal。v2 必须把 TraceSpine 作为 kernel authority：

- `TraceSpine.v1` 是 run 级 append-only authority；`lifecycle_events`、read model、evidence manifest、loop-readiness 都是 projection，不得成为唯一真相源。
- 每个 `loop start` 必须创建 `TraceContext.v1`，字段至少包含：

```text
trace_id, run_id, feature_slug, version, harness, phase,
iteration, BranchContext_ref, decision_packet_ref,
intent_snapshot_ref, truth_hash, design_primitives_ref?,
parent_span_id?, event_hash, prev_event_hash
```

- `loop`、`implement`、`qa-evidence`、`release` 必须消费同一 `TraceSpine.v1`。缺失 trace spine、trace append failure、trace context 与 BranchContext/decision_packet 不一致时 fail-closed。
- `stagnation-report.v1` 必须引用 trace event range 与 reason_code / failure catalog 交叉引用；不得只基于 loose JSONL 或无 run 归属的 report。
- `remediation-report.v1` 必须引用 stagnation report、overlay artifact、eval evidence、rollback evidence 与 human review decision；成功 remediation 仍不得自动 release。
- evidence manifest 每条行为证据必须能回溯到 trace event id；无法回溯的证据只能作为 support_advisory，不能满足 closure。
- `loop-audit` 可以保留 advisory mode，但 loop/implement/qa-evidence/release admission 必须使用 strict trace completeness gate。

### Truth Canonical Branch Contract（R10）

需求真相只能在 canonical truth branch 上编写、冻结、提交，再由开发分支合入消费。默认 canonical truth branch 为 `main`，仓库无 `main` 时使用 `master`。

- `truth` / `change` / `refreeze` 写入 package truth 时，当前分支必须等于 `truth_canonical_branch`；否则 fail-closed：`reason_code=truth_canonical_branch_mismatch`。
- feature/dev worktree 不得单独 bump requirement `revision_id`，不得产生 reason-only refreeze；它只能合入 canonical branch 上已经 frozen 的 truth。
- refreeze transaction 必须证明 canonical markdown truth/test/task/evidence 至少一个 requirement surface 发生内容变化；仅 `change_reason` 或 machine projection 变化必须 block：`reason_code=empty_refreeze_reason_only`。
- implement/qa-evidence/release admission 必须验证当前 branch 包含 canonical truth branch 最新 frozen commit；否则 block：`reason_code=truth_baseline_not_merged`。
- machine revision、人类 evidence 中的 revision narrative、truth frontmatter 必须同源生成或同源校验；发现 `R7/R8/R9` 类 drift 时 block：`reason_code=revision_authority_drift`。

### Standard Execution Flow Contract（R11）

Beacon v2 必须把“需求真相在 main/master 冻结，再合入 feature worktree 执行”的场景规范成一条标准执行流，而不是依赖操作者记忆或临时命令顺序。该 flow 是六能力与 internal governance 的编排 contract，不是第七个 public skill。

标准状态顺序：

```text
support_advisory
  -> canonical_truth_authoring
  -> canonical_refreeze
  -> canonical_commit
  -> feature_worktree_reconcile
  -> governance_verify
  -> workspace_admission
  -> implement_resume
```

执行规则：

- `support_advisory`（例如 planner/review/doctor finding）只能提出 route，不得直接改 frozen truth；用户确认后才进入 canonical truth authoring。
- `canonical_truth_authoring` 必须在 `truth_canonical_branch`（默认 main，缺失时 master）修改 `features/<slug>/{truth,tests,tasks,evidence}.md`；feature/dev worktree 不得写入 requirement revision。
- `canonical_refreeze` 必须通过 `beacon change <feature> --refreeze-chain` 完成；如遇 `legacy_cutover_required`，只能按 CLI 给出的 `truth-cutover run ... --resume-intent refreeze` 路由恢复。
- `canonical_commit` 是 refreeze 的生效边界；未提交的 refreeze artifact 不得被 feature branch 当成 baseline。提交必须只包含 canonical truth package、refreeze projection 与必要 evidence manifest，不能混入无关 runtime dirty files。
- `feature_worktree_reconcile` 必须先检查 feature worktree 是否存在 stale feature-local refreeze。发现本地 revision/projection dirty 时，必须 scoped stash/archive 并记录 stash/artifact ref；不得把 feature-local bump merge 或 commit 为 authority。
- `governance_verify` 必须确认 feature branch 已包含 canonical `truth_baseline_commit`，且 `truth-map verify`、`verify-materials --strict`、`branch-governance verify`、`git diff --check` 均通过。
- `workspace_admission` 由 `implement check-branch` / `workspace admit` 产生，必须绑定 `truth_baseline_commit`、`BranchContext.v1`、feature worktree path 和 clean/dirty policy。
- `implement_resume` 只能在 refreeze summary complete、canonical commit merged、workspace admission pass 后进入；若重复执行标准流，已对齐步骤必须报告 `up_to_date` / `pass`，不得再次 bump revision。

标准失败 reason_codes：

```text
standard_flow_order_violation,
canonical_refreeze_not_committed,
stale_feature_local_refreeze,
truth_baseline_commit_missing,
truth_baseline_not_merged,
workspace_admission_missing,
unscoped_dirty_state,
standard_flow_verification_incomplete
```

Public skill 呈现规则：`truth` 暴露 canonical author/refreeze 示例；`loop` 暴露 decision_packet 到 lifecycle 的一键 flow；`implement` 暴露 branch/admission 前置；`qa-evidence` / `release` 只消费 verification/admission 结果。doctor/branch/status/hooks 仍是 internal module，通过 progressive disclosure example 加载，不得成为 public top-level skill。

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
- **AC-003**：v1 Python / Node / v1 skill 面与 v2 Rust / 六能力面为 **长期双轨对等产品轨**（UD-B）；v2 新能力与 v2 runtime **不得** fallback 到 Python/v1 路由；v1 轨 **不得** 被 v2 core closure 要求退休或降为唯一 archive-only。跨轨调用必须显式、可审计，禁止静默混跑。

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
- **AC-060**：双轨运行时选择必须 **显式**（例如独立 `beacon-v2` 二进制，或 `beacon --runtime v2` / 等价显式 flag）。禁止用「环境默认偷偷切轨」替代用户/CI 的显式选择；`BEACON_V2=1` 若保留，只能作为 **显式选择的别名**，不得暗示 v1 已退役。
- **AC-061**：`BEACON_STORE_PATH` 测试隔离；生产默认 `~/.beacon/beacon.db`。
- **AC-062**：在 **v2 runtime 路径内**，任何把 v1 Python/legacy skill 当执行后端的请求必须 fail-closed，返回 `reason_code=cross_track_fallback_forbidden`（或等价），stdout/stderr **不得** 含 `compat_route=python`。v1 runtime 路径内对 v1 skills 的正常调用 **不受** 本条退休。
- **AC-063**：`beacon harness list --version v2.0.0 --json`（或等价 CLI）只返回六个一等能力及其 contract metadata；不得要求 33/37 skills smoke 作为 v2 closure；v1 skill 矩阵验收留在 v1 轨。

## CLI 面

- **AC-064**：spine/projects/workflow/truth-map/implement/qa/release/run 子命令可解析且 `--help` snapshot 稳定。
- **AC-065**：spine/projects/run 支持 `--json` 且 schema 可校验。
- **AC-066**：v1 reason_codes 对齐：`gate_results.reason_codes_json` 失败样例须含 documented code；`docs/beacon/archive/v2.0.0/execution/reason-codes.md` 与 **集成测试** 中至少 5 个 code 往返一致。

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

| Phase | 交付物 | v1 共存（长期双轨 UD-B） |
|-------|--------|---------|
| P0 | core + store + schema + migration **skeleton**（非 production migration） | v1 全功能；合并互不影响 |
| P1 | Spine read + projects | v1 JSON/CLI 仍可写；分轨 CI |
| P2 | orchestrator MVP + **AC-043/044** codex/subprocess 真集成 | beacon-loop / v1 CLI 并行 |
| P3 | gate 写库 + **AC-045/046** claude/acp 真集成 + migration 完成 | 迁移为可选对照，不强迫退役 v1 |
| P4 | 六能力 harness surface + **v2 路径内**禁止 cross-track fallback | v1 37-skill 面继续作为 v1 产品轨 |
| P5 | ~~proto~~ **v2.0.0 跳过**（D-V2-001） | v1 无 gRPC 亦可 |
| P6 | v2 benchmark / 成熟度门禁 | **不**以 P6 退休 v1；双轨继续 |

- **AC-084**..**AC-090**：P0–P6 阶段出口（见 tests.md TC-084–090）；**P5 在 v2.0.0 以 D-V2-001 accepted defer 跳过**；P6 是 v2 成熟度出口，**不是** v1 产品轨关停开关。

## 风险与缓解（Plan §9）

- **AC-091**：CI **必须**执行 `cargo build/test` for `beacon-rs` matrix（macOS + Linux 至少）；非仅 README 声明。
- **AC-092**：migration 前自动备份 runtime-ledger 与既有 DB。
- **AC-093**：双写期 **单一写者**；双向同时写须测试失败。
- **AC-094**：v2 harness surface / cross-track isolation 回归失败 → `beacon-gov-doctor`（或 v2 等价诊断），禁止静默 cross-track fallback。
- **AC-095**：v2 benchmark 相对 baseline 回退 >10% 阻断 **v2 P6 成熟度出口**；不授权、不要求关停 v1 轨。

## 验收总则（Plan §10）

- **AC-096**：每 phase 跑 tests.md 对应 TC 子集 + phase integration job。
- **AC-097**：全量 AC closure 由 evaluator 裁决；generator/implementer 不得自证 release ready。
- **AC-098**：frozen package 权威高于 plan；plan 变更须 promote。

### v1.6 治理与 Planner Runtime 移植（R2 增补）

- **AC-101**（P3）：`beacon-gate` 在 freeze/refreeze 前执行 **Truth Integrity Gate**，语义对齐 v1.6 `build_truth_integrity_gate`：空缺 AC、软 TC、未拍板 deferral、假交付、package validation 失败 → hard block + `repair_route`；已 frozen 历史包默认 `audit_only` 不阻断。
- **AC-102**（P2）：`beacon-orchestrator` 的 `planner_review()` 必须产出 v1.6 multi-agent runtime 同构字段（`reviewer_lanes`、`findings`、`synthesis`、`execution_mode`、`fallback_reason`、`runtime_evidence_only=true`）；artifact 写入 `artifact_refs`；无 subagent 时 **禁止** 声称 parallel execution。
- **AC-103**（P3）：`beacon doctor verify-truth-integrity` 在 v2 路由到 Rust gate；`--mode block` exit code 与 v1.6 一致，不使用 PyO3 compat。
- **AC-104**（历史 P0 证据）：2026-06-13 的 `packages/beacon-rs/` scaffold 与 12 个 P0 unit tests 是 implementation candidate evidence；R8 minimal-kernel closure 需重新验证 AC-002/022/059/063 后才可算 P0/P4 完成。

### Minimal Kernel AC Extensions（AC-109–144）

- **AC-109**：v2 public kernel surface 明确定义并只允许六个一等能力：loop / truth / design / implement / qa-evidence / release。
- **AC-110**：v1 Python / Node / v1 skill 面 **不进入 v2 core closure 的验收依赖**；它们作为 **并行产品轨** 继续交付。v2 closure 不得把「全量 v1 skill 回归」或「PyO3 兼容层」列为必过项；也不得把「删除 v1 轨」列为 v2.0.0 必过项。
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
- **AC-131**：`TraceSpine.v1` 是 run 级 append-only authority；`lifecycle_events`、read model、evidence manifest、loop-readiness 均为 projection，不得作为唯一权威源。
- **AC-132**：`loop start` 必须创建 `TraceContext.v1` 并绑定 BranchContext、decision_packet、intent_snapshot、truth_hash 与 design_primitives（当 required）；缺失或不一致 fail-closed。
- **AC-133**：`implement` / `qa-evidence` / `release` 必须验证 trace completeness；trace missing、append failure、event hash chain invalid 或 event->evidence 断链均不得继续闭环。
- **AC-134**：`stagnation-report.v1` 必须引用 trace event range、reason_code、failure catalog / pattern registry；无 trace 归属不得触发 remediation。
- **AC-135**：`remediation-report.v1` 必须引用 stagnation report、overlay/eval/rollback evidence 与 human review decision；成功 remediation 仍需人工裁决，不得自动 release。
- **AC-136**：truth/change/refreeze 只能在 `truth_canonical_branch`（默认 main，缺失时 master）写入与冻结；feature/dev worktree 不得 bump requirement revision。
- **AC-137**：refreeze transaction 必须拒绝 reason-only / machine-only 变化；revision id、人类 narrative 与 machine projection 发生漂移时 fail-closed。
- **AC-138**：Beacon v2 必须提供 Standard Execution Flow 状态机，顺序固定为 support_advisory -> canonical_truth_authoring -> canonical_refreeze -> canonical_commit -> feature_worktree_reconcile -> governance_verify -> workspace_admission -> implement_resume；跳步必须 fail-closed。
- **AC-139**：canonical refreeze 只有在 canonical branch 提交后才成为可消费 baseline；未提交 refreeze artifact 不得被 feature branch、loop、implement、qa-evidence 或 release 采信。
- **AC-140**：feature worktree 中发现 stale feature-local refreeze/projection dirty 时，必须 scoped stash/archive 并记录引用；不得作为 requirement authority commit/merge。
- **AC-141**：feature/dev branch 进入 implement 前必须包含 canonical `truth_baseline_commit`，且不得有违反 dirty policy 的工作区状态；否则 blocked。
- **AC-142**：标准流 admission evidence bundle 必须包含 truth-map verify、verify-materials strict、git diff check、branch-governance verify、workspace admission 五类结果；缺任一项不得进入 implement。
- **AC-143**：标准流必须可 idempotent resume；已对齐步骤重复执行时返回 `up_to_date` / `pass`，不得因重复执行产生新的 requirement revision。
- **AC-144**：标准执行流通过六 public skill 的 progressive examples 暴露，不得新增第七个 public skill 或绕过 Harness Boundary。

### Long-term Dual-Track + Unified Skill Score（R15 / UD-B）

用户 2026-07-16 拍板：**选项 B 长期双轨产品**；**统一 skill 评分进入 v2.0.0 合同且可用于 v1**；**只评分、人改**（禁止自动改 SKILL.md）。

- **AC-147**：Beacon 产品策略为长期双轨：`track_v1`（Python CLI + v1 skill 面）与 `track_v2`（Rust kernel + 六 public skill）对等并存；任一轨的 release/成熟度门禁 **不得** 隐含关停另一轨。
- **AC-148**：双轨隔离契约——代码树、CLI 入口、skill 根、docs version tree、CI job 必须可分轨合并；同一 PR 若同时修改两轨「发布真源」，必须显式 `dual_track_shared_contract` admission，否则 fail-closed（`reason_code=dual_track_mixed_source`）。
- **AC-149**：运行时选择必须显式（对齐 AC-060）；禁止 v2 路径执行 v1 backend，禁止 v1 路径把请求静默升级为 v2 并改写用户未请求的行为。
- **AC-150**：迁移/导入工具可以只读对照另一轨状态，但不得在双写期成为第二写者（延续 AC-093 单写者原则，按轨分别强制）。
- **AC-151**：v2.0.0 合同包含 **统一 skill 评分面**（`beacon skill-score` 或扩展现有 `beacon eval`），同一套维度 schema 必须能对 **v1 skill 包**与 **v2 六 public skill 包**打分；禁止为两轨维护互相不可比的私有满分制。
- **AC-152**：统一评分必须包含 **结构质量**（SKILL.md/package/HARD GATE/progressive 合规，对齐 skill-creator / Beacon skill-package-standard）与 **实效质量**（固定 test-prompts 上的路由/边界/越权 negative；with_skill vs baseline 或等价对照），参考 Anthropic skill-creator 与 darwin-skill 的双评思想。
- **AC-153**：skill 评分产物权威为 `runtime_evidence_only`；**不得**替代 `qa-evidence` formal QA，**不得**替代 `release` 人放行；scorecard 必须声明该边界。
- **AC-154**：**只评分、人改**——评分/优化建议可以产出 diff 建议与维度短板，但 **禁止** 自动编辑、自动 commit、自动 revert 任何 `SKILL.md` 或 skill package 文件；保留/回滚由人执行。
- **AC-155**：评分执行者与被评 skill 的「修改建议作者」在流程上必须可分离（独立评分会话或独立 grader）；禁止同一无审计步骤既改 skill 又自评涨分。
- **AC-156**：v1 `beacon eval` 既有 scorecard 维度可映射进统一 schema，但发布门必须以统一 schema 的稳定字段为准；字段漂移须走 change，不得静默改权重冒充同比。

## Parity Matrix（Plan 场景复刻索引）

| Plan 章节 | AC 范围 | 场景 |
|-----------|---------|------|
| §1 缺陷 | AC-001–010, D-01..10 | 结构性消除 |
| §2 存储+Spine+rebuild | AC-004–021 | 三层+Spine+projection rebuild |
| §3 Crate | AC-022–025 | workspace |
| §4 FSM+性能 | AC-026–036, AC-051–058 | 双 FSM+benchmark |
| §5 Orchestrator+Agent | AC-040–050, **AC-042–046/099/100 真集成** | 无空壳 AC；worktree+implement 不 defer |
| §6 极简 Harness+CLI | AC-059–066, AC-109–144 | 六能力 surface + legacy removal + progressive disclosure + BranchContext + TraceSpine + canonical truth branch + standard execution flow |
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
| UD-dual-B | 长期双轨产品（选项 B） | v1/v2 skill+CLI 语言分叉，需合并互不影响 | **accepted**（2026-07-16）→ AC-003/060/062/110/147–150 | in-scope v2.0.0 |
| UD-skill-score | 统一 skill 评分进 v2.0.0 且可用于 v1 | 落地稳依赖可测 skill 资产 | **accepted**（2026-07-16）→ AC-151–156 | in-scope v2.0.0 |
| UD-score-human-edit | 只评分、人改 | 禁止 Darwin 式自动改 SKILL.md | **accepted**（2026-07-16）→ AC-154–155 | in-scope v2.0.0 |

**已移除**：r1 AC-040 空壳 contract test 路径 — 由 AC-045/046 真集成取代；**不 defer** claude/acp/worktree/implement-harness。

**R15 废止叙事**：凡将「P4/P6 legacy removal / 默认切 v2 / v1 仅 archive」理解为 **关停 v1 产品轨** 的表述，以 UD-B + AC-147–150 为准废止；保留的是 **v2 路径内禁止 cross-track fallback**，不是退休 v1。

## Non-Goals

- 不把 Markdown truth 迁入 DB。
- 不把 QA JSON 升格为 truth authority。
- 不把 v1 Python/PyO3/v1 skills 当作 **v2 runtime fallback** 或 **v2 core closure 必过依赖**（v1 作为并行产品轨继续存在，见 UD-B）。
- 不用 orchestrator 替代 evaluator 裁决。
- 不用空壳/stub/纯文档闭环 作为唯一 AC 验收。
- 不用 skill 评分自动改写 SKILL.md，或用 scorecard 冒充 QA/release。

## Freeze Readiness

1. ~~用户确认 Deferral Ledger~~ **已完成**：D-V2-001 accepted；D-V2-004/005 rejected（AC-099/100 in-scope）；**UD-dual-B / UD-skill-score / UD-score-human-edit accepted（2026-07-16）**。
2. `tests.md` 每个 AC 至少一行 **行为级** TC（非仅 `--help`/文件存在）——R15 新增 AC-147–156 须补 TC。
3. `tasks.md` P0–P6 与 AC 映射完成——R15 须补双轨隔离与统一评分任务。
4. `requirement_clarity` open question 清零或 defer。
5. **无空壳-only AC**；agent/worktree/implement 类 AC 须 integration tier（AC-043–046, AC-099–100）。
6. **v1.6 upstream**（AC-101–103）在对应 phase 有 behavior-level TC，不得仅用「后续移植」一句带过。

**当前状态**：`frozen` / **R15**（revision `r15-dual-track-unified-skill-score`）— 2026-07-16 refreeze：长期双轨（B）+ 统一 skill 评分入 v2.0.0 且可用于 v1 + 只评分人改。

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

**AC**：AC-059–063, AC-109–144, AC-064–066

### US-007 长期双轨 + 统一 skill 评分

**AC**：AC-003, AC-060, AC-062, AC-110, AC-147–156

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
| r10 | R7 refreeze：TraceSpine.v1 / TraceContext.v1 成为 run authority；loop/implement/qa-evidence/release 绑定 trace completeness；stagnation/remediation 报告绑定 trace event range；truth/change/refreeze 只能在 canonical truth branch 执行；阻断 reason-only/machine-only refreeze 与 revision narrative drift（AC-131–137） |
| r11 | R8 refreeze：将 canonical truth author/refreeze/commit -> feature worktree reconcile -> governance verify -> workspace admission -> implement resume 固化为 Standard Execution Flow；新增 baseline commit、stale feature-local refreeze quarantine、verification bundle 与 idempotent resume contract（AC-138–144） |
| r14 | R13 repair refreeze：materialize `v2-0-0-rust` program orchestration as canonical surface；补 phase graph、lake slices、admission gates、run-state；修复 reason-only / machine-only refreeze 造成的 revision authority drift 风险 |
| r15 | R14 change（reopened）：UD-B 长期双轨；统一 skill 评分入 v2.0.0 且可用于 v1；只评分人改；重写 AC-003/060/062/110 与共存表；新增 AC-147–156 |
