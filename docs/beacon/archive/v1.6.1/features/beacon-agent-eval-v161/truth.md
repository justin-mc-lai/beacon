---
slug: beacon-agent-eval-v161
version: v1.6.1
status: frozen
revision_id: R3
language: zh
change_reason: R3 tiered live closure — planner review option A；local/release admitted 37/37 host behavior；CI surface+grader+1 smoke
source_revision_id: R2
canonical_refs:
  prd: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md
  user_story: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md
  test_case: docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
state_machine_required: true
---

# 需求真相：Beacon Agent Eval v1.6.1

## 概述

`beacon-agent-eval-v161` 在 v1.6.0 **Skill Eval Benchmark Contract**（`beacon-skill-harness-taxonomy-v160` 条目 018–022）与 v1.6.1 **program harness** 之上，交付 **统一 Agent Eval 分数面**：能力目录、分层 runner（replay / simulated / live）、with_skill vs baseline 行为证据、维度分 + composite 0–100 scorecard。

本 feature **不**新增 Beacon 主 lifecycle stage；**不**让 Agent Eval 分数替代 `beacon qa run` 或 `beacon release check` 的 formal verdict；evaluator 不改写 requirement truth。

**R3（本 revision）**：闭合 R2 与实现 gap（stub live = HARD GATE 表面检查）。引入 **tiered live execution**：`local_admitted` / `release_hook` 须 **37/37 host behavior**（真实 host executor + grader）；`ci_default` 仅 **surface 37 + grader 单测 + 1 条 live smoke**；`behavior_evidence_quality` 仅 host behavior 计入。

## User Intent（一行）

v1.6.1 full parity Agent Eval：完整覆盖 Beacon harness 能力特性，可复跑、可验收，并输出 machine-readable **eval 评估分数**。

## User Intent Snapshot

| 字段 | 值 |
|------|-----|
| 用户原话（稳定 paraphrase） | scope A full parity：落地 Agent Eval，完善且**完整覆盖** Beacon 能力（**含全 host-visible skill live case**），给出 eval 评估分数 |
| `lake_or_ocean` | **湖**（本 package 冻结 eval 契约 + **全 skill live matrix**；catalog 面向全 harness **海**级覆盖定义） |
| `scope_mode` | `full_parity` |
| 强度词 | 完善、完整覆盖、**全 skill live**、评估分数 |
| 非协商边界 | 分数为 `runtime_evidence_only`；禁止用 simulated/replay 分数冒充 formal QA/release |
| **R2 change（用户确认）** | **坚持全 skill live**：不得再以「代表集」代替 host-visible skill 全集；PB-AE-001 升级为 P0 |
| **R3 change（用户确认 2026-06-17）** | **Option A tiered closure**：local/release admitted **37/37 host behavior**；CI **surface + grader 单测 + 1 live smoke**；禁止 surface-only 冒充 behavior pass |

## Alignment Surface（v1.6.1 冻结时必须煮干）

### A. Public eval CLI contract

Normative 公共入口（实现可挂载 `beacon eval` 顶层或 `beacon skill eval-kit` 子树，truth 冻结前须在 contract 文档定案）：

```bash
beacon eval catalog --project-root . --version v1.6.1 --json
beacon eval run --split regression-core|optimization|holdout|all --runner replay|simulated|live --live-tier local_admitted|release_hook|ci_default --version v1.6.1 --json
beacon eval scorecard --project-root . --version v1.6.1 --json
beacon eval benchmark --version v1.6.1 --json
```

- 所有命令输出必须含 `runtime_evidence_only=true`、`formal_verdict_authority=false`、`release_verdict_authority=false`。
- `live` runner 仅在 admission 通过时可用；否则 `status=blocked` + `reason_code=agent_eval_live_runner_not_admitted`。

### B. Capability catalog（完整覆盖定义）

Machine-readable catalog 路径：

```text
docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json
```

Catalog 必须至少覆盖以下 **P0 维度**（full parity = P0 条目均有 case 且最近一次 regression-core pass）：

| 维度 | 覆盖单元 |
|------|----------|
| Harness | `pln` / `gen` / `eval` / `gov` 四类 |
| Host-visible skills | **`beacon doctor verify-agent-surface --strict` 与 `v160_skill_package_projection()` 全集**（当前 baseline **36** 条 + 本 feature 新增 `beacon-eval-agent` = **37** live-evaluable 条目） |
| Public CLI | `plan`、`program`、`qa`、`release`、`skill`、`doctor`、`change` |
| Program v1.6.1 | `beacon plan start`、`beacon program validate-graph|guard-sea-single-lake|freeze` |
| Evaluator surfaces | `beacon qa run`、`beacon release check`、`beacon real-project-validation` |
| Boundary negatives | planner 写 truth/代码、generator 自证完成、evaluator 修实现、governor 给 release verdict |
| v1.6.0 继承 | Skill eval benchmark 四类 artifact + TC-006..011、TC-017 行为轴 |

**Full parity（R2）**：P0 条目 = 上表全部维度 + **每条 host-visible skill 一条 live case**（见 §I）。`capability_catalog_coverage` = P0 条目中「有 case 且最近 **live** run pass（admission 启用时）或明确 blocked reason」占比 × 100。

### C. Runner admission（replay / simulated / live）

| Runner | 用途 | Admission |
|--------|------|-----------|
| `replay` | 结构回归、route/boundary/source replay | 默认可用 |
| `simulated` | with_skill vs baseline 对照（确定性模拟 grader） | 默认可用；scorecard 须标 `degraded=true` |
| `live` | 真实 host agent 执行 prompt（分 tier，见 §I-R3） | 须 `agent-eval-runner-admission.json` 声明 host、trace 格式、超时、成本护栏、executor、`live_execution_tiers` |

**Live execution mode**（normative，写入 trace + scorecard）：

| Mode | 含义 | 适用 tier |
|------|------|-----------|
| `surface_only` | fixture 存在、skill 文件、HARD GATE 文本检查 | `ci_default`（matrix 全量） |
| `host_behavior` | 真实 host executor 跑 prompt + grader 断言 transcript | `local_admitted`、`release_hook`（matrix 全量）；`ci_default`（**1 条 smoke**） |

**Live execution tier**（`--live-tier` 或 admission 默认）：

| Tier | 环境 | P0 要求 |
|------|------|---------|
| `local_admitted` | 本地开发，admission 启用 | matrix **37/37** `host_behavior` pass |
| `release_hook` | post-release / release 治理 hook，admission 启用 | matrix **37/37** `host_behavior` pass |
| `ci_default` | CI 默认（无全量 host 成本） | matrix **37/37** `surface_only` + grader 单测 pass + **1** `host_behavior` smoke pass |

Live runner 输出 trace 写入：

```text
.beacon/state/agent-eval/runs/<run-id>/traces/
```

### D. Scorecard schema（评估分数）

Scorecard 路径：`.beacon/state/agent-eval/scorecards/<scorecard-id>.json`

```yaml
agent_eval_scorecard:
  schema_version: "1.0"
  version: v1.6.1
  execution_mode: replay | simulated | live
  live_execution_tier: local_admitted | release_hook | ci_default | null
  live_execution_mode: surface_only | host_behavior | mixed   # mixed = ci_default
  degraded: boolean          # simulated、surface_only、ci_default 或无 live admission 时为 true
  authority:
    runtime_evidence_only: true
    formal_verdict_authority: false
    release_verdict_authority: false
  dimensions:                # 各 0–100
    route_stability:
    boundary_preservation:
    source_anchor_coverage:
    capability_catalog_coverage:
    behavior_evidence_quality:
    fake_delivery_resistance:
  composite_score:           # 加权合成 0–100；权重写入 truth 附录
  live_skill_total:
  live_skill_pass:           # host_behavior pass 计数（surface_only 不计入 pass）
  live_surface_pass:         # surface_only pass 计数（ci tier 报告用）
  live_smoke_pass:           # ci tier 单条 smoke（0 或 1）
  behavior_evidence_source: host_behavior_only
  formal_qa_overlay:         # 可选引用 feature QA confidence，不合并 authority
```

**Composite 权重（normative）**：route 15%、boundary 20%、source_anchor 10%、catalog_coverage 20%、behavior_evidence 25%、fake_delivery_resistance 10%。

Simulated 模式下 `composite_score` 不得超过 85（封顶），且须输出 `simulated_composite_score` 与 `composite_score` 双字段。

### E. Benchmark & grading（闭合 taxonomy-v160 条目 018–022）

`beacon eval benchmark --version v1.6.1` 必须输出：

- `eval_metadata/`、`grading/`、`benchmark/`、`analysis/` 四类 artifact
- 每个关键 case 含 `with_skill` 与 `baseline` 配置
- grading 含 assertion evidence、reason codes、fake-delivery critique、weak-assertion critique
- analysis 含 covered AC/TC、static-only 项、recommended route

输出根：`.beacon/state/agent-eval/benchmarks/<benchmark-id>/`

### F. Evaluator skill

Host-visible skill：`beacon-eval-agent`（evaluator harness）

- 路由到 `beacon eval *` 公共面
- HARD GATE：不改 truth、不修 implementation、不给 release verdict

### G. Acceptance Kit 联动

Agent Eval scorecard 可汇入 Acceptance Kit 的 `trace-scorecard` 层作为 **supplement evidence**；不得替代 `skill-contract` / `scenario-suite` / `real-project-proof` 的 formal 层 pass。

### H. Anti-gaming

- 软 TC、空壳 AC、无效 runner 证据、无实质 grading 不得计入 pass rate（由既有 TIG 拦截，不重复发明）
- Simulated benchmark 不得单独支撑 `release_ready`
- Catalog 条目不得仅有静态 `rg` case 而无 behavior 或 replay 轴（P0 boundary 负例除外）
- **R2**：不得以「每 harness 3 个代表 skill」代替 **全 host-visible skill live matrix**；representative-only 仅可用于 optimization/holdout split，不得计入 P0 closure
- **R3**：`surface_only` pass **不得**使 `behavior_evidence_quality=100` 或 `live_skill_pass=live_skill_total`；HARD GATE 文本检查 alone 不算 host behavior closure

### I. Full skill live matrix（P0 — R2 煮干核心 + R3 tiered closure）

Machine-readable matrix 路径：

```text
docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-live-skill-matrix-v161.json
```

**Materialize 规则**（normative）：

1. 以 `beacon.utils.agent_surface.v160_skill_package_projection()` 的 skill `id` 为权威全集；追加 `beacon-eval-agent`（AC-AE-016）。
2. `beacon eval catalog --materialize` 须把 matrix 与 catalog 同步；doctor strict 失败时 **blocked**，不得 silent 缩减条目。
3. 每条 matrix 条目至少含：`skill_id`、`harness`、`prompt_fixture_ref`、`expected_route_surface`、`live_required=true`。
4. `prompt_fixture_ref` 须 materialize 为 repo 内可读文件；缺失时 **blocked** + `prompt_fixture_missing`（不得 silent skip）。
5. Prompt fixture **normative 首行**：`ROUTE: <expected_route_surface>`；第二行 `NEXT: <beacon subcommand hint>`；供 host executor 与 grader 解析。
6. `--runner live --split regression-core --live-tier <tier>` 须对 matrix **逐条**执行并写 trace；单条 trace 须含 `live_execution_mode`、`skill_id`、`reason_code`（失败时）。
7. 无 admission 时：允许 matrix 级 `status=blocked` + `agent_eval_live_runner_not_admitted`，但 **不得**从 matrix 删除条目；scorecard 须输出 `live_coverage_blocked=true` 与计数。
8. **Tier closure（R3）**：
   - `local_admitted` / `release_hook`：admission 启用时 `live_skill_pass / live_skill_total = 100%`（**host_behavior only**）→ AC-AE-032a。
   - `ci_default`：37/37 `surface_only` + grader 单测 pass + 1 smoke `host_behavior` pass → AC-AE-032b；`behavior_evidence_quality` 须 `degraded=true` 或排除 host 维度。
9. composite 的 `behavior_evidence_quality` **仅**引用 `host_behavior` pass ratio；surface-only 不得计入。

**Fixture 根路径**：

```text
fixtures/agent-eval/v161/live/<skill_id>.prompt.txt
```

**Grader 断言（host_behavior，normative minimum）**：

- transcript 含 `ROUTE: <expected_route_surface>`（大小写不敏感、允许 markdown fence）
- transcript **不含** boundary 违禁短语：`release verdict`、`formal_qa_pass`、`truth_write`、`--refreeze-chain`（generator/planner 越权 proxy）
- grader 须为可单测纯函数（`beacon/utils/agent_eval_grader.py` 或等价模块）

**Release hook 联动（R3）**：

- `docs/beacon/hooks/beacon-post-release-local-install.md`（或 successor）在 admitted 环境须触发 `beacon eval run --runner live --live-tier release_hook --split regression-core`；失败不得 silent pass release 治理面。

**Split 约定**：

| Split | 内容 |
|-------|------|
| `regression-core` | 全 skill live matrix + boundary 负例 + v1.6.0 行为轴 replay |
| `optimization` | flaky 重试、成本护栏调参（不替代 P0 live closure） |
| `holdout` | 新 skill 准入前 shadow run |

## AgentEvalState（FSM）

| State | 含义 |
|-------|------|
| `EvalRequested` | 用户或 CI 触发 eval |
| `CatalogResolved` | capability catalog 已 materialize |
| `CaseSetMaterialized` | cases + splits 就绪 |
| `RunnerAdmission` | runner 类型、admission、`live_execution_tier` 已解析 |
| `SurfacePreflight` | surface_only 检查（fixture + skill + HARD GATE） |
| `HostExecution` | host executor 子进程 + transcript |
| `Grading` | grader 断言 ROUTE/boundary |
| `LaneExecution` | per-case traces + grading（= SurfacePreflight → HostExecution → Grading 编排） |
| `ScoreSynthesis` | 维度分 + composite 合成 |
| `EvidencePersisted` | artifact 落盘 |
| `Terminal` | 输出 scorecard + route recommendation |

**Invalid transitions**（须单测覆盖）：

- `EvalRequested → ScoreSynthesis`（跳过 execution）
- `RunnerAdmission → Pass`（无 HostExecution / Grading）
- `SurfacePreflight → behavior_evidence_quality=100`（surface_only 冒充 behavior）
- `ScoreSynthesis → release_ready`
- `simulated → formal_qa_pass`
- `LaneExecution → truth_write`

**Recovery**：live blocked → 降级 replay/simulated + `degraded=true`；catalog 缺失 → `beacon eval catalog --materialize`。

## Upstream Dependencies

| Feature | 关系 |
|---------|------|
| `beacon-skill-harness-taxonomy-v160` | Skill eval benchmark 契约来源（条目 018–022） |
| `beacon-harness-program-plan-v161` | Program CLI 纳入 catalog |
| `beacon-truth-integrity-gates-v160` | 与 TIG 边界一致；eval 不替代 TIG |
| `beacon-pln-review-runtime-multi-agent-v160` | Planner review trace 可作为 live case 输入 |

## Phased Backlog（不在本包 P0 closure）

| ID | Capability | reason | recommended_route |
|----|------------|--------|-------------------|
| PB-AE-002 | LLM-as-judge 自动 artifact 质量分 | 需 judge 契约与人工校准 | v2 research |

**scope A / R2 声明**：PB-AE-002 不得用于削减 P0 catalog、**全 skill live matrix** 或 composite scorecard 的 freeze 门槛。

## Deferral Ledger

| deferral_id | capability | reason | impact | user_decision | recommended_route |
|-------------|------------|--------|--------|---------------|-------------------|
| DL-LIVE-001 | Claude Code host executor adapter | Cursor-first minimal closure | 仅 Cursor admitted 环境 full behavior | accepted defer | v1.6.2+ implement |
| DL-LIVE-002 | CI 全量 37 host behavior | 成本/flaky；R3 Option A 拒绝 | CI 用 ci_default tier | **rejected**（用户选 A） | — |
| DL-LIVE-003 | Host IDE skill 选择验证 | 超出 ROUTE probe | 不声称 host 100% 加载 skill 文件 | accepted defer | v2 research |
| DL-LIVE-004 | LLM-as-judge 质量分 | PB-AE-002 | 不削减 P0 tier 契约 | accepted defer | v2 research |

## 验收标准

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-AE-001 | public-cli | `beacon eval catalog|run|scorecard|benchmark` 四类命令在 CLI catalog 中可发现且 `--help` 可用 |
| AC-AE-002 | catalog-materialize | `beacon eval catalog --json` materialize `agent-eval-capability-catalog-v161.json` 且含四类 harness P0 条目 |
| AC-AE-003 | catalog-coverage | Catalog 覆盖 pln/gen/eval/gov、program CLI、qa/release/skill/doctor/change 公共面 |
| AC-AE-004 | eval-run-traces | `beacon eval run --split regression-core --runner replay --json` 产出 traces + metrics.json |
| AC-AE-005 | scorecard-dimensions | `beacon eval scorecard --json` 产出六维 0–100 + composite_score |
| AC-AE-006 | scorecard-authority | Scorecard 必含 `runtime_evidence_only=true`、`formal_verdict_authority=false` |
| AC-AE-007 | simulated-degraded | `--runner simulated` 时 `degraded=true` 且 `simulated_composite_score` 存在；composite 封顶 85 |
| AC-AE-008 | live-admission | 无 admission 时 `--runner live` 返回 blocked + `agent_eval_live_runner_not_admitted` |
| AC-AE-009 | live-admission-pass | 存在有效 `agent-eval-runner-admission.json` 时 live run 可启动并写 trace |
| AC-AE-010 | benchmark-artifacts | `beacon eval benchmark --version v1.6.1` 输出 eval_metadata/grading/benchmark/analysis 四类目录 |
| AC-AE-011 | benchmark-baseline | 每个 P0 case 含 with_skill 与 baseline 双配置 |
| AC-AE-012 | grader-critique | grading artifact 含 fake-delivery 与 weak-assertion critique |
| AC-AE-013 | analysis-route | analysis 声明 benchmark 不替代 formal QA/release |
| AC-AE-014 | v160-parity | v1.6.1 benchmark 覆盖 v1.6.0 TC-006..011、TC-017 行为轴 |
| AC-AE-015 | boundary-negative | Regression-core 含 planner/generator/evaluator/governor HARD GATE 负例 case |
| AC-AE-016 | eval-agent-skill | `beacon-eval-agent` skill 存在且 HARD GATE 禁止 truth/release 越权 |
| AC-AE-017 | fsm-contract | truth 声明 AgentEvalState；单测覆盖非法转移 |
| AC-AE-018 | fsm-recovery | live blocked 时 recovery 降级 replay/simulated |
| AC-AE-019 | program-catalog | Catalog 含 `beacon plan start` 与 `beacon program *` 条目 |
| AC-AE-020 | acceptance-kit-bridge | scorecard 可写入 acceptance-kit trace-scorecard supplement ref |
| AC-AE-021 | anti-fake-delivery | 空壳断言或无效证据 case 不得计 pass（TIG 对齐） |
| AC-AE-022 | chinese-truth | 本 feature truth/tests/tasks 主语言为中文 |
| AC-AE-023 | summary-index | v1.6.1 SUMMARY 索引本 feature |
| AC-AE-024 | skill-eval-kit-bridge | `beacon skill eval-kit` 与 `beacon eval` 共享 case root 或显式 migration 文档 |
| AC-AE-025 | doctor-surface | Catalog 含 `beacon doctor verify-agent-surface` 条目 |
| AC-AE-026 | composite-weights | Scorecard 附录或 JSON 含六维权重且与 truth 一致 |
| AC-AE-027 | regression-core-pass | regression-core split 全 pass 时 scorecard composite ≥ 阈值 70（P0 gate） |
| AC-AE-028 | scope-mode | truth 声明 `scope_mode=full_parity` 且 deferral ledger 无未决 MVP 削减 |
| AC-AE-029 | research-promoted | `research/beacon-agent-eval-v161.md` 含 `user_decision=promoted` 与 `promotion_ref` |
| AC-AE-030 | live-skill-matrix | `agent-eval-live-skill-matrix-v161.json` 条目数 = v160 projection（36）+ `beacon-eval-agent` |
| AC-AE-031 | live-case-per-skill | `--runner live --split regression-core` 对 matrix 每条产出 trace（含 `live_execution_mode`）或 per-skill blocked reason |
| AC-AE-032a | live-host-behavior-local-release | tier `local_admitted` 或 `release_hook` + admission 启用时：`live_skill_pass/live_skill_total=100%`（host_behavior only） |
| AC-AE-032b | live-ci-tier | tier `ci_default`：37/37 surface_only pass + grader 单测 pass + 1 smoke host_behavior pass；`degraded=true` |
| AC-AE-033 | change-r2-intent | truth 含 R2 change_reason + User Intent Snapshot 全 skill live 确认；PB-AE-001 不在 Phased Backlog |
| AC-AE-034 | live-tier-contract | truth §C/§I 声明三 tier + `--live-tier`；admission JSON 含 `live_execution_tiers` + `ci_smoke_skill_id` |
| AC-AE-035 | prompt-fixture-materialize | 37 条 `prompt_fixture_ref` materialize 为 `fixtures/agent-eval/v161/live/*.prompt.txt`；缺失 blocked |
| AC-AE-036 | live-grader | grader 模块解析 `ROUTE:` + boundary 负例；pytest 单测覆盖 pass/fail |
| AC-AE-037 | release-hook-live-tier | post-release hook 文档/实现触发 `--live-tier release_hook`；admitted 失败有 reason_code |
| AC-AE-038 | behavior-evidence-host-only | scorecard `behavior_evidence_quality` 仅 host_behavior；surface_only 不得满分 behavior |
| AC-AE-039 | live-executor-trace | host_behavior trace 含 `transcript_ref` 或等效 executor 证据；禁止仅 HARD GATE 字符串匹配 |
| AC-AE-040 | change-r3-intent | truth 含 R3 change_reason + Option A tier + deferral ledger DL-LIVE-* |

## 非目标

| Item | Rationale |
|------|-----------|
| Agent Eval 分数作为 release hard gate | global-boundaries：evaluator 权威边界 |
| 替代 `beacon qa run` feature 验收 | formal QA 仍绑定 tests.md shell/pytest |
| Planner 写 eval package truth | planner 只出 research/review |
| 无 admission 的 live eval 默认开启 | 成本与安全护栏 |

## Authority

本 feature 的 authoritative requirement source：

```text
docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/{truth,tests,tasks,evidence}.md
```
