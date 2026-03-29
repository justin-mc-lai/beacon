# Test Cases: Beacon QA 置信度、closure outcome 与 autoresearch 精准度闭环（v1.1.10）

**Feature**: beacon-qa-confidence-autoresearch-closure  
**Version**: v1.1.10  
**Machine AC Matrix**: `docs/beacon/v1.1.10/.machine/qa/beacon-qa-confidence-autoresearch-closure.ac-test-matrix.json`  
**Machine QA9 Matrix**: `docs/beacon/v1.1.10/.machine/qa/beacon-qa-confidence-autoresearch-closure.qa9-matrix.json`  
**Machine Story Scenario Map**: `docs/beacon/v1.1.10/.machine/qa/beacon-qa-confidence-autoresearch-closure.story-scenario-map.json`

当前生成状态：

- AC matrix entries: `20`
- QA9 entries: `28`
- scenario entries: `63`
- required browser families: `happy / negative / boundary / recovery / compatibility`

## 前置 Gate 结论

- Gate0 输入完整性：Pass
  已有 `SUMMARY / user-story / PRD / boundaries / project-skill blueprint / data contract / phasing / machine story / machine QA matrices`
- Gate1 锚点一致性：Pass
  QA 设计锚定在 `status != closure != confidence != release decision`、`audit truth > self-score`、`project workflow reality` 与 `implement/archive feedback`
- Gate2 覆盖策略：Pass
  覆盖分成锚点验证、发散场景、边界阻断、项目 workflow、学习反馈五层
- Gate3 兼容性：Pass
  v1.1.10 明确 additive extend v1.1.9 QA surface、v1.1.7 project skill orchestration、v1.1.8 technical archive loop

## 锚点地图

| Anchor | Fact Point | Why it matters |
| --- | --- | --- |
| Anchor-A | v1.1.9 already has feature QA, story-scenario-map, exhaustiveness-report, release scorecard, keep/discard skeleton | 保证 v1.1.10 是加法演进，不是另起炉灶 |
| Anchor-B | `status` 不是 `closure_outcome`，`confidence` 也不是 release truth | 防止“跑过一次”直接被误判成“可以放行” |
| Anchor-C | 高风险 browser pass 仍需要 replay 与 browser evidence pack | 防止 agent exploratory false pass |
| Anchor-D | 低置信度必须 abstain，而不是 bluff | 防止系统性乐观误判 |
| Anchor-E | sampled audit label 是 benchmark truth | 防止 learning plane 被自评分污染 |
| Anchor-F | keep/discard 只能优化小策略面 | 防止 autoresearch 演化成不受控自治 |
| Anchor-G | 目标项目可能通过 profile/skill/orchestration 表达真实 QA 路径 | 防止 Beacon 在真实项目里只跑通用 QA |
| Anchor-H | 浏览器鉴权记录应保存为 manifest/refs 而不是文档层 secret 扩散 | 保证可复用和可审计，同时不破坏边界 |
| Anchor-I | QA 缺陷必须进入 implement、technical archive 与 architecture feedback | 保证缺陷不是死胡同，而是闭环输入 |

## 锚点式发散覆盖策略

本线 QA 不是“只围着一个 happy path 打转”，也不是“无限发散到脱离事实”。

采用的覆盖法则是：

1. 先用 anchor 锁定必须成立的事实。
2. 再围绕每个 anchor 向 happy / negative / boundary / recovery / compatibility 发散。
3. 对目标项目再额外围绕 profile / skill / orchestration / session / archive feedback 发散。
4. 发散出的场景只有在能回挂到 requirement、evidence、closure、confidence、audit 或 project workflow anchor 时才保留。
5. 超出事实边界的推演不进入正式 QA set。

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | anchor-contract | 读取 scenario-result-v2 contract | 明确同时包含 `status / closure_outcome / confidence_raw / confidence_calibrated / requires_human_review / root_cause_type` |
| TC-002 | anchor-derivation | 对照 AC closure 规则 | AC closure 来自 scenario family、replay、evidence sufficiency、confidence threshold 与 unresolved outcomes |
| TC-003 | anchor-release | 读取 feature-qa-scorecard / release policy | release decision 使用 calibrated confidence、review count、open outcomes，而不是 status-only |
| TC-004 | browser-truth | 高风险 browser scenario 通过但缺 replay | 结果必须 `blocked` 或 `needs_replay`，不得 auto-accept |
| TC-005 | browser-truth | 高风险 browser scenario 通过但缺 browser evidence pack | 结果必须阻断放行，且产生 evidence gap 语义 |
| TC-006 | abstain | `0.60 <= confidence_calibrated < 0.85` | 系统产出 `review_required` 或等价 abstain，不直接 accepted |
| TC-007 | abstain | `confidence_calibrated < 0.60` | feature 不可 release-ready，需 block 或 reopen |
| TC-008 | closure-action | scenario 发现真实实现缺口 | `closure_outcome=implementation_reopened` 或 `bug_filed` |
| TC-009 | closure-action | scenario 暴露 spec 模糊 | `closure_outcome=needs_requirement_clarification` 或 requirement rewrite |
| TC-010 | root-cause | 缺 evidence 但实现未证伪 | `root_cause_type=evidence_gap`，不误记为 implementation gap |
| TC-011 | root-cause | 浏览器 runner 不稳定导致误阻断 | `root_cause_type=runner_gap` 或 `flake`，不误记为 spec gap |
| TC-012 | audit-label | sampled audit 发现 auto-pass 其实为 false pass | 生成 `qa-audit-label=false_pass`，并进入 benchmark truth |
| TC-013 | audit-label | sampled audit 发现 auto-block 其实为 false block | 生成 `qa-audit-label=false_block`，并进入 benchmark truth |
| TC-014 | corpus | 读取 benchmark corpus 设计 | 至少覆盖 false complete、false block、stale evidence、missing replay、wrong delta rerun、trace mismatch |
| TC-015 | learning-boundary | 审查 allowed optimization surface | 只能优化 scenario expansion、impact selection、evidence sufficiency、confidence calibration、abstain threshold、release threshold |
| TC-016 | compatibility | 对照 v1.1.9 / v1.1.7 / v1.1.8 contracts | QA、project skill、technical archive 三层都保持 additive compatibility |
| TC-017 | operator-surface | 审查 status / report / release scorecard | 能显示 confidence floor、review count、unresolved outcomes、training readiness、project workflow path |
| TC-018 | divergent-coverage | 读取 machine story-scenario-map | browser-relevant coverage 至少包含 happy / negative / boundary / recovery / compatibility |
| TC-019 | mixed-evidence | 同一 AC 下 evidence 有强有弱 | 结果不得直接 accepted，应进入 review-required 或 mixed sufficiency 分支 |
| TC-020 | unresolved-outcome | scenario 已通过但 open outcome 未消除 | feature 仍不得 `release_ready=true` |
| TC-021 | review-is-success | 系统在低置信度下主动 review-required | 记为正确行为，不因“未自动通过”而判失败 |
| TC-022 | stale-evidence | 旧 evidence 被用于新 revision | 系统识别 stale evidence，不得沿用旧 confidence claim |
| TC-023 | delta-rerun | requirement/implementation 变化后选择 rerun 范围 | 能衡量 `delta_rerun_precision`，且 wrong selection 会进入 corpus |
| TC-024 | trace-mismatch | scenario 与 story/AC trace 不一致 | 进入 trace mismatch corpus，不得继续 claim closure |
| TC-025 | calibration | 审查 qa-calibration-model contract | 至少有 sample_count、ECE、Brier score、risk bands |
| TC-026 | audit-agreement | sampled audit labels 与自动 judgement 对比 | 能计算 `human_audit_agreement` |
| TC-027 | keep-discard | QA precision candidate 进入 evo harness | 以 real benchmark truth 评估 keep/review/discard，而非凭主观改好像更好 |
| TC-028 | feedback-loop | 读取 release/test feedback 文档 | 测试反馈被明确写回 benchmark truth、audit drift signal、next experiment set |
| TC-029 | project-skill-registry | 读取 target project profile / skill registry / binding contract | Beacon 能表达目标项目的专属 verify/workflow，而不是只靠通用 QA |
| TC-030 | project-verify-orchestration | 审查 `verify run <feature> --profile <profile>` 路径 | verify-stage orchestration 与 required evidence gate 被纳入 precision loop |
| TC-031 | browser-auth-session | 审查 `qa session save|use|show` contract | session manifest 至少保存 `profile_ref / cookies_ref / storage_state_ref / scopes / expiry` |
| TC-032 | browser-auth-boundary | 浏览器鉴权记录进入 QA workflow | 保存的是 artifact refs 与 scope metadata，而不是无约束 raw secret 扩散 |
| TC-033 | implement-feedback | QA 发现 implementation gap 后进入 implement | 能路由到 `beacon implement` 并生成 `technical-implementation-*` |
| TC-034 | architecture-feedback | implement 完成后检查技术归档回流 | QA 缺陷可反哺 requirement rewrite input 与 architecture feedback 文档 |
| TC-035 | project-workflow-evolution | target project workflow 进入 keep/discard | 只允许演进 profile/orchestration/evidence contract 等小策略面 |
| TC-036 | end-to-end-closure | 从 user-story 到 project verify 到 QA 到 implement/archive | 闭环路径清晰，可持续演进到稳定交付 |

## 样板场景

### 场景 A：happy path 通过，但 replay 缺失

- exploratory browser run 走通主路径
- replay artifact 缺失
- 预期：系统承认“看到了一些 evidence”，但 closure 不能 accepted

### 场景 B：negative path 被正确拦截，但 evidence 混合

- negative scenario assertion 成功
- console/network/browser pack 缺一部分
- 预期：进入 mixed sufficiency review，不得直接高置信 accepted

### 场景 C：spec gap 而非 implementation gap

- scenario 在 requirement 解释层出现歧义
- 预期：closure 指向 requirement clarification，而不是直接 reopen implementation

### 场景 D：false complete 进入 benchmark truth

- auto-accept case 经 sampled audit 被认定为 false pass
- 预期：落 `qa-audit-label`、更新 benchmark corpus、进入下轮 keep/discard 候选

### 场景 E：threshold 调优造成 false-block 上升

- 新阈值减少 false complete
- 同时显著增加 false block
- 预期：不能只看单次收益，必须按 supporting metrics 做 keep/review/discard

### 场景 F：trace mismatch 阻断放行

- scenario evidence 无法稳固映射回 AC / story
- 预期：不能靠“像是相关”继续放行，必须作为 trace mismatch 真值样本处理

### 场景 G：目标项目通过 profile/skill 表达真实 QA 路径

- 目标项目存在自己的 verify skill / orchestration graph
- 预期：Beacon 通过 profile 绑定与 verify orchestration 跟随真实项目路径，而不是退回通用 smoke

### 场景 H：浏览器鉴权记录在后续 QA 中被复用

- 首轮 QA 保存 session manifest
- 后续 story-exhaustive rerun / delta rerun 复用 `profile_ref / cookies_ref / storage_state_ref`
- 预期：减少重复登录、保持证据连续性，同时不在文档层扩散敏感信息

### 场景 I：QA 缺陷进入 implement 并产出技术归档

- QA 判定 `implementation_reopened`
- 实现修复后产出 `technical-implementation-*`
- 预期：技术归档与 requirement rewrite input 都可追溯到该 QA finding

### 场景 J：技术归档反哺架构演进

- 同类 QA 缺陷在多个 feature 重复出现
- 预期：反馈不只停在单 feature 修补，而会进入 architecture feedback / baseline uplift

## 测试反馈回写规则

| Finding Type | Writeback Target | Expected Follow-up |
| --- | --- | --- |
| confirms anchor | release feedback / docs evidence | 记录为设计成立，不进入训练异常集 |
| false complete | benchmark corpus / qa-audit-label / next experiment set | 降低 false-complete risk |
| false block | benchmark corpus / qa-audit-label / threshold review | 降低 false-block regression |
| evidence gap | closure outcome / gate block / rerun plan | 补 replay 或补 evidence pack |
| trace mismatch | benchmark corpus / requirement rewrite input | 修正 trace contract |
| review-required | operator surface / sampled audit queue | 人工审阅而非自动放行 |
| project-workflow gap | profile/orchestration contract / evidence gate | 补齐目标项目 skill workflow 或 required evidence |
| implementation gap | `beacon implement` / technical archive | 修复实现并写回技术归档 |
| architecture feedback | architecture blueprint / baseline uplift | 把重复缺陷提升为结构化架构改进 |

## 执行语义

- `Pass`: QA 同时覆盖 anchor truth、divergent scenario families、project workflow reality、boundary blocks 与 learning feedback
- `Pass`: coverage 发散但不脱离 requirement/evidence/replay/audit/project-workflow anchors
- `Fail`: 仍把 status 当 closure，把 exhaustiveness 当 confidence，把 exploratory pass 当 release truth
- `Blocked`: sampled audit strategy、truth labels、release thresholds、project workflow gate 或 architecture feedback 路径仍有关键冲突
