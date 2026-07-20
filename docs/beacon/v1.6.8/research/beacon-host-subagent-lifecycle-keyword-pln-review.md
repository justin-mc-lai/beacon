---
slug: beacon-host-subagent-lifecycle-keyword-pln-review
version: v1.6.8
also_covers: v2.0.0
brands: [beacon, loom]
status: support_advisory
authority: beacon-pln-review
kind: planner_review
date: 2026-07-20
runtime_evidence: .beacon/state/planner-review/beacon-host-subagent-lifecycle-v168/pln-review-20260720t022827z.json
recommended_route: beacon-gen-change
user_decision_required: true
---

# Planner Review：Host 子代理生命周期（Codex + Claude）· 关键词触发 · 默认单线程

## intent_snapshot

| 字段 | 用户原意（锁定） |
|------|------------------|
| 宿主 | **Codex** + **Claude Code** 子代理能力 |
| 版本 | **v1.6.8**（生产 ops 线）与 **v2.0.0**（Loom 进化线）双覆盖 |
| 品牌 | **Beacon** + **Loom** 生命周期同构；Loom 不默认替换 Beacon |
| 阶段 | **pln-review / 调研分析 / 实现 / 验收** 可增强；**非**新主链 stage |
| 触发 | **仅关键词（或显式 flag）** 才 spawn；**非触发不调用** |
| 默认 | **保留单线程**；子代理是 **增强方案** |
| 交付物 | skill 规范 + 示例 + **直接引入开源库运行机制** + **评分方案** |
| 禁止 | 子代理自证 complete/release；第二公共入口；无关键词自动并行 |

## scope_mode

- `full_parity` 对用户承诺面（关键词门闩 + 四阶段增强 + 双宿主 + 双品牌）
- **湖级**交付：建议 1 个 program / 2 轨镜像 feature，不是「装 150+ 角色」的海

## lake_or_ocean

| 判断 | 理由 |
|------|------|
| **湖** | 边界清晰：触发门闩 + 最小角色包 + skill 规范 + 评分 |
| 若扩到「全量 VoltAgent 目录同步」 | **超纲** → defer / 插件包 |

建议 feature slug（truth 待写，本 review 不 freeze）：

| 版本 | 建议 slug |
|------|-----------|
| v1.6.8 | `beacon-host-subagent-lifecycle-keyword-v168` |
| v2.0.0 / Loom | `loom-host-subagent-lifecycle-keyword-v200`（parity mirror） |

Program 建议：挂在现有 GoalRun 主轴旁，**不**新开公共 skill 入口。

---

## 现状审计（source_evidence + runtime）

### 已有能力（可复用）

| 能力 | 位置 | 缺口 |
|------|------|------|
| 单入口 goal | `beacon-goal` / `loom-goal` | 未统一「阶段 × 角色 × 关键词」矩阵 |
| 可选 fan-out | `beacon/utils/loom_subagent.py` `detect_subagent_intent` | 关键词偏「并行/多湖」；**缺** review/research/qa 阶段角色词 |
| team/tmux worker | `beacon/utils/subagent_runtime.py` | 偏 implement team，非 host-native Codex/Claude agent 文件 |
| readiness | `beacon doctor verify-subagent-runtime --host-runtime codex\|claude` | 只验 skill root/context，**不验** agents 目录与角色清单 |
| planner multi-reviewer | `beacon planner-review run` | 默认 `single_process_multi_reviewer`；真并行须 host 可用时才可声明 |
| Agent Eval 六维 | `beacon/utils/agent_eval_kit.py` | 无 subagent keyword / non-trigger 维度 |
| OSS 镜像 | oss-sync: awesome-codex-subagents, awesome-claude-code-subagents, pi-subagents, Skill_MAS, dbskill | **未** vendoring 到 `.codex/agents` / `.claude/agents` 合同 |

### 本机 readiness（runtime_evidence）

- `verify-subagent-runtime --host-runtime codex` → **PASS**
- `verify-subagent-runtime --host-runtime claude` → **PASS**
- planner-review 本 feature → `recommended_route: beacon-gen-change`，`user_decision_required: true`

### 开源运行机制（直接引入的「机制」而非全文拷贝）

| 来源 | 引入机制 | 不引入 |
|------|----------|--------|
| **awesome-codex-subagents** | `.toml` agent 形态；`sandbox_mode`；model 分档；**显式委派** | 171 角色全装 |
| **awesome-claude-code-subagents** | `.md` agents；plugin 分类；meta-orchestration | 154 角色全装 |
| **pi-subagents** | 角色链 scout→researcher→planner→worker→reviewer→oracle；**并行 reviewer 切片**；默认 off | Pi runtime 绑定内核 |
| **Trellis**（既有 research） | class-1 push / class-2 pull 上下文注入；具名 agent 非 generic | 全平台 14 适配器一次做完 |
| **Skill_MAS** | 对比反思 / 多轨迹（评分侧旁路） | 自动 rewrite 生产 skill |
| **gstack / superpowers**（全局 research） | specialist workflow + review-before-accept | 第二 truth plane |

---

## 推荐架构（增强面，非新主链）

```text
默认路径（无关键词）:
  $beacon-goal | $loom-goal
    → 单线程 progressive skills
    → 零 host subagent spawn
    → reason_code=subagent_default_off

触发路径（关键词 or --subagent / --with-agents）:
  stage detector → keyword gate → role pack select
    → host adapter (codex | claude)
    → bounded spawn (read-only / workspace-write per role)
    → result artifact under .beacon/state/subagent/<run_id>/
    → parent integrates → truth/gate 仍归 Beacon
```

### 生命周期覆盖矩阵（Must）

| 阶段 | harness | 允许的最小角色（关键词触发后） | 禁止 |
|------|---------|--------------------------------|------|
| **pln-review** | planner | `oracle`, `architect-reviewer`, multi-reviewer lanes | 写 truth/code；QA verdict |
| **调研分析** | planner / source | `search-specialist`, `docs-researcher`, `scout` | 搜索结果当 freeze 真值 |
| **实现** | generator | `worker` / lang specialists；可选 satellite fan-out | 卫星写 main truth；自 complete |
| **验收** | evaluator | `reviewer`×切片, `qa-expert`, `test-automator` | 子代理 release 绿灯 |

**单线程保留**：无关键词时 `execution_mode=single_thread` 强制；触发后默认 **有界并行**（最大 N 角色 / 写集互斥），仍由 parent 串行集成。

---

## 关键词门闩（稳定触发合同）

### 设计原则

1. **fail-closed 默认 off**（对齐 `loom_subagent.REASON_DEFAULT_OFF`）
2. **显式 > 关键词 > 默认 false**
3. 关键词分 **全局开关** 与 **阶段角色** 两层
4. 匹配必须 **可审计**（记录 matched_tokens 到 execution.jsonl / subagent session）
5. **否定词**可关：`单线程` / `不要子代理` / `--no-subagent` 优先于正向词

### 全局开关词（任一命中才允许后续角色匹配）

| 语言 | tokens |
|------|--------|
| en | `subagent`, `sub-agents`, `with agents`, `fan-out`, `fanout`, `parallel agents` |
| zh | `子代理`, `多代理`, `并行代理`, `开子代理`, `启用子代理` |

可选 CLI：

```bash
beacon goal run "..." --subagent
beacon goal run "..." --no-subagent
beacon implement run FEATURE --runner codex-subagents --host-runtime codex   # 仍须意图/flag
```

### 阶段角色词（在全局开关已开后生效）

| 阶段 | 正向 tokens（示例） | 默认角色包 id |
|------|---------------------|---------------|
| review | `全面审查`, `多角度 review`, `pln-review subagent`, `oracle`, `challenge plan` | `pack-review` |
| research | `调研`, `搜索`, `竞品`, `search-specialist`, `先搜再造` | `pack-research` |
| implement | `并行实现`, `satellite`, `多湖`, `team implement`, `worker` | `pack-implement` |
| qa | `并行验收`, `多 reviewer`, `correctness+tests`, `qa subagent` | `pack-qa` |

### 非法 / 不触发

| 情况 | 行为 |
|------|------|
| 无全局开关词且无 flag | **不 spawn**；`reason_code=subagent_default_off` |
| 有「子代理」但无阶段词 | 仅允许 **pack-default**（scout+reviewer 只读）或要求澄清；**禁止**默认 team 写代码 |
| 仅有「并行」无「子代理/subagent」 | **可**触发 worktree satellite（现有语义），**不**自动装 host agent 角色（防误伤）——UD 待用户锁 |
| 子代理失败 | fallback parent 单线程；`fallback_reason` 必填；禁止假绿 |

**User decision 待锁（UD 候选）**：

| ID | 选项 A（推荐） | 选项 B |
|----|----------------|--------|
| UD-SA-001 | 「并行」仅 satellite；host agents 必须 subagent 词 | 「并行」同时开 host agents |
| UD-SA-002 | 最小角色包 **6** 个 | 最小 **10** 个 |
| UD-SA-003 | Codex/Claude **vendoring** 到项目 `.codex/agents` + `.claude/agents` | 仅文档指引用户手动 cp |
| UD-SA-004 | v1.6.8 与 v2.0.0 **同 AC 镜像** | v2 先做 Loom 再回 port |

---

## 最小角色包（直接映射开源库）

建议 **Beacon 官方 curated pack**（从 oss-sync 同步机制 + 路径引用，不 1:1 拷贝全部）：

| pack_id | 角色 | Codex 源 | Claude 源 | sandbox |
|---------|------|----------|-----------|---------|
| pack-research | search-specialist | categories/10-research-analysis/search-specialist.toml | categories/10-research-analysis/search-specialist.md | read-only |
| pack-research | docs-researcher | docs-researcher.toml | 对应 md | read-only |
| pack-review | architect-reviewer / oracle | quality-security + meta | meta-orchestration | read-only |
| pack-implement | backend/frontend 或 worker | core-development | core-development | workspace-write |
| pack-qa | reviewer + qa-expert | reviewer.toml, qa-expert.toml | 对应 | read-only 为主 |
| pack-coord | multi-agent-coordinator | 09-meta-orchestration | 09-meta-orchestration | read-only |

安装命令面（implement 后，非本 review）：

```bash
beacon doctor install-subagent-pack --host-runtime codex --pack minimal --project .
beacon doctor install-subagent-pack --host-runtime claude --pack minimal --project .
beacon doctor verify-subagent-runtime --host-runtime codex --require-agents --json
```

---

## Skill 规范补齐（package standard）

对齐 `skills/beacon/beacon-pln-review/references/skill-package-standard.md` + host 双轨：

### A. 公共 skill 薄入口（禁止新公共交付入口）

| Skill | 变更类型 | 内容 |
|-------|----------|------|
| `beacon-goal` / `loom-goal` | 增补章节 | 关键词门闩；默认单线程；示例链到 examples |
| `beacon-pln-review` | 增补 | 触发后可 host multi-reviewer；无 runtime 仍 single_process |
| `beacon-pln-source` | 增补 | research pack 关键词 → search-specialist |
| `beacon-gen-implement` | 增补 | team/codex-subagents **仅** keyword/flag |
| `beacon-eval-qa` | 增补 | pack-qa 只产 evidence，不 release |
| `beacon-loop-goal` / `loom-loop-goal` | 明确 | **不得**因关键词变成公共入口 |

### B. 新增 support skill（可选，非公共交付）

`beacon-gov-subagent`（governor）：

- 职责：install-pack / verify / 解释 keyword gate / 列 reason_code
- HARD GATE：不 implement、不 QA verdict

### C. agents 元数据

- Codex：`agents/*.toml` 或项目 `.codex/agents/`
- Claude：`.claude/agents/*.md`
- 每个角色 frontmatter：`name`, `description`（含 when to invoke）, `sandbox_mode`, `beacon_stage`, `keyword_tags`

### D. 示例（examples，implement 时写）

| 文件 | 内容 |
|------|------|
| `skills/beacon/examples/subagent-keyword-off-30s.md` | 无关键词 → 确认无 spawn |
| `skills/beacon/examples/subagent-review-on-30s.md` | 「子代理 + 全面审查」→ pack-review |
| `skills/beacon/examples/subagent-research-on-30s.md` | 「子代理 + 调研搜索」→ pack-research |
| `skills/beacon/examples/subagent-implement-qa-on-30s.md` | 实现+验收并行 reviewer |
| `skills/loom/examples/...` | 镜像 Loom 文案 |

示例模板（skill 文案草稿，非已落地）：

```text
$beacon-goal
目标：… 启用子代理做调研搜索与实现后并行验收
# → matched: 子代理, 调研, 搜索, 并行验收
# → packs: research + qa
# → single_thread_default=false, parent_integrates=true
```

```text
$beacon-goal
目标：…做完验收
# → no keyword → subagent_default_off → 单线程
```

---

## 状态机（state_model 摘要）

```text
idle
  → keyword_gate
       ├ miss → single_thread_continue
       └ hit  → pack_select → host_ready_check
                    ├ not_ready → fallback_single + reason
                    └ ready → spawn_bounded → integrate → parent_continue
spawn 失败 → fallback_single
integrate 后 → 禁止 subagent_complete_goal
```

非法转移：

- `keyword_miss → spawn`
- `subagent_session → goal_completed`
- `satellite → write_main_truth`
- `pack-qa → release_confirmed`
- `fallback → claim_parallel_subagent_success`

---

## 评分方案（scoring）

### 分层权威（不可混）

| 层 | 用途 | 权威 |
|----|------|------|
| L1 Keyword Gate Suite | 触发/非触发正确率 | **feature QA AC** |
| L2 Host Pack Suite | install/verify/spawn artifact | feature QA |
| L3 Agent Eval overlay | skill 路由健康 | **runtime_evidence_only** |
| L4 Release scorecard | 版本可发 | formal release |

### L1 建议 AC（freeze 时落入 tests.md）

| AC | 断言 |
|----|------|
| AC-SA-KW-001 | 无关键词 + 无 flag → spawn=false, reason=subagent_default_off |
| AC-SA-KW-002 | 仅「子代理」→ 可开 gate；无写路径角色默认 read-only |
| AC-SA-KW-003 | 「子代理+调研+搜索」→ pack-research 非空 |
| AC-SA-KW-004 | 「子代理+全面审查」→ pack-review |
| AC-SA-KW-005 | 「子代理+并行验收」→ pack-qa |
| AC-SA-KW-006 | 「不要子代理」覆盖正向词 |
| AC-SA-KW-007 | 否定/flag 优先序：`--no-subagent` > 否定词 > 正向词 > default |
| AC-SA-ST-001 | 默认路径无 host agent 调用痕迹 |
| AC-SA-BD-001 | subagent 不可 complete GoalRun |
| AC-SA-BD-002 | satellite 不可写 main truth |
| AC-SA-FB-001 | host 不可用时 fallback + fallback_reason，不假称 parallel |

### L3 建议新增维度（Agent Eval overlay，权重总和仍 1.0 或独立 scorecard）

| 维度 | 建议权重（overlay） | 计算 |
|------|---------------------|------|
| `subagent_keyword_precision` | 0.25 | non-trigger 误 spawn 率 → 0 分倒扣 |
| `subagent_keyword_recall` | 0.15 | 应触发未触发（在 golden 集） |
| `single_thread_preservation` | 0.20 | 默认 off 用例全过 |
| `host_pack_readiness` | 0.15 | verify-subagent-runtime + agents present |
| `boundary_no_self_complete` | 0.15 | 禁 complete/release 用例 |
| `fallback_honesty` | 0.10 | 无 runtime 时不宣称 parallel |

复合：`subagent_composite`；**不得**替代 formal QA。  
模拟分仍受 `SIMULATED_COMPOSITE_CAP=85` 约束（若并入主 composite 需 change 权重表并人审）。

### Golden prompt 语料（skill-score 扩展）

对齐 `docs/beacon/v2.0.0/skill-score/skill-score-corpus.v1.json`：

| id | prompt | expect |
|----|--------|--------|
| P-SA-OFF | 实现并验收登录 | no_subagent |
| P-SA-RES | 子代理调研搜索竞品后再写需求 | pack-research |
| P-SA-REV | 子代理多角度 review 该方案 | pack-review |
| P-SA-QA | 子代理并行验收 correctness 与 tests | pack-qa |
| N-SA-AUTO | 无词自动 team | illegal |

---

## Findings（schema）

```text
finding_id: SA-001
reviewer: intent-fidelity
severity: P0
confidence: 100
authority_level: user_quote
issue: 用户要求关键词触发才调用、默认单线程；现状 intent 检测偏并行/多湖，未覆盖 review/research/qa 角色词与否定词优先级。
evidence_refs: user prompt; beacon/utils/loom_subagent.py detect_subagent_intent
affected_truth_surface: 待写 truth keyword gate + tests
recommended_route: beacon-gen-change
user_decision_required: false
autofix_allowed: false
```

```text
finding_id: SA-002
reviewer: source-parity
severity: P0
confidence: 75
authority_level: source_evidence
issue: 开源库已在 oss-sync，但缺少「机制引入」合同：pack 安装路径、sandbox、显式委派、class-1/2 上下文；易退化成文档-only。
evidence_refs: oss-sync awesome-codex-subagents; pi-subagents; docs/beacon/v2.0.0/research/beacon-host-skill-multi-agent-review-trellis.md
affected_truth_surface: install-subagent-pack CLI + agents vendoring tasks
recommended_route: beacon-gen-change
user_decision_required: true
autofix_allowed: false
```

```text
finding_id: SA-003
reviewer: state-machine
severity: P1
confidence: 100
authority_level: user_quote
issue: 四阶段 lifecycle 增强缺统一 FSM（keyword_gate → pack_select → spawn → integrate）；非法转移与 TC 未冻结。
evidence_refs: user prompt; pln-review state_model recovery_paths
affected_truth_surface: truth State Model + tests illegal walks
recommended_route: beacon-gen-change
user_decision_required: false
autofix_allowed: false
```

```text
finding_id: SA-004
reviewer: coverage-shape
severity: P1
confidence: 75
authority_level: package_truth
issue: 评分需 L1 keyword suite（行为证据）与 L3 overlay 分离；仅有 readiness PASS 不能证明「非触发不调用」。
evidence_refs: agent_eval_kit COMPOSITE_WEIGHTS; verify-subagent-runtime PASS
affected_truth_surface: tests.md AC-SA-KW-*; skill-score corpus
recommended_route: beacon-gen-change
user_decision_required: false
autofix_allowed: false
```

```text
finding_id: SA-005
reviewer: route-boundary
severity: P0
confidence: 100
authority_level: package_truth
issue: 不得新增与 beacon-goal 并列的公共交付 skill；subagent 只能是增强面/gov support。
evidence_refs: global-boundaries; beacon-goal 唯一入口
affected_truth_surface: skill surface table
recommended_route: beacon-gen-change
user_decision_required: false
autofix_allowed: false
```

```text
finding_id: SA-006
reviewer: performance-boundary
severity: P2
confidence: 50
authority_level: assumption
issue: 并行 spawn 需 max_agents / timeout / token budget；未指定易拖垮 longrun。
evidence_refs: goal durable budget defaults
affected_truth_surface: budget fields on SubagentSession
recommended_route: beacon-gen-change
user_decision_required: true
autofix_allowed: false
```

```text
finding_id: SA-007
reviewer: deferral-sovereignty
severity: P1
confidence: 75
authority_level: user_quote
issue: 全量 150+ 角色不在本湖；必须 deferral ledger 显式「curated minimal pack only」。
evidence_refs: user 增强方案 + 关键词触发
affected_truth_surface: deferral_ledger in truth
recommended_route: beacon-gen-change
user_decision_required: true
autofix_allowed: false
```

```text
finding_id: SA-008
reviewer: dual-track-parity
severity: P1
confidence: 75
authority_level: user_quote
issue: v1.6.8 与 v2.0.0/Loom 需同 AC 镜像；禁止只做一边导致 goal 行为分裂。
evidence_refs: user v1.6.8\v2.0.0; dual-track research
affected_truth_surface: dual feature packages + axis mount
recommended_route: beacon-gen-change
user_decision_required: true
autofix_allowed: false
```

---

## parity_matrix（相对开源「机制」）

| 机制 | 开源 | Beacon 现状 | 目标 |
|------|------|-------------|------|
| 显式委派 | Codex subagents | 部分 team runner | 关键词门闩后才委派 |
| 角色文件 | .toml / .md | 未 curated install | install-subagent-pack |
| sandbox | read-only vs write | 弱 | 角色级强制 |
| 默认 off | pi-subagents | loom 已有 | 扩展阶段词 |
| 并行 review 切片 | pi | 无 | pack-qa |
| 上下文 push/pull | Trellis | 无 | P1 adapter |
| skill 自动进化 | Skill_MAS | 无 | **defer** |

## deferral_ledger

| 项 | 决定 | 理由 |
|----|------|------|
| 全量 VoltAgent 角色同步 | **defer** | 噪声与维护成本；与「关键词稳定触发」冲突 |
| Skill_MAS 自动 rewrite skill | **defer** | 撞 truth 权威 |
| Pi runtime 内嵌 | **out of scope** | 机制蒸馏即可 |
| class-1 push hooks 全宿主 | **P1** | 先 Codex pull + Claude agents 文件 |
| 商业 dbskill 角色 | **out of scope** | 另包 beacon-biz |

---

## recommended_route

```text
User locks UD-SA-001..004
  → beacon-gen-change
       features:
         - beacon-host-subagent-lifecycle-keyword-v168  (v1.6.8)
         - loom-host-subagent-lifecycle-keyword-v200    (v2.0.0 mirror)
  → freeze truth/tests/tasks（含 keyword FSM + AC-SA-* + scoring）
  → beacon-gen-implement（doctor install-pack, detect gate, examples, tests）
  → beacon-eval-qa（L1 suite 必须绿）
  → release 人工门
```

**本 pln-review 停止点**：不写 truth、不改代码、不给 QA/release pass。

### 用户需确认（再 change）

1. UD-SA-001：「并行」是否自动 host agents？**推荐否**  
2. UD-SA-002：最小包 6 vs 10？**推荐 6**  
3. UD-SA-003：项目内 vendoring agents？**推荐是**  
4. UD-SA-004：双版本同发？**推荐是**  

---

## 附录：runtime evidence

- `.beacon/state/planner-review/beacon-host-subagent-lifecycle-v168/pln-review-20260720t022827z.json`
- `beacon doctor verify-subagent-runtime` codex/claude PASS
