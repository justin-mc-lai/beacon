# Test Cases: Beacon 闭环控制层、恢复层与学习层增强（v1.1.9）

**Feature**: beacon-closure-control-learning-overlay  
**Version**: v1.1.9

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已有 v1.1.8 能力现状、v1.1.9 requirement + machine materials + research 输入）
- Gate1 冲突未决判定：Pass（v1.1.9 被收敛为 overlay，而不是另起平行主链）
- Gate2 AC→TC 映射：Pass（覆盖 overlay、debug、qa、trace、writeback、learning、evo boundary）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | strategy | 读取 v1.1.9 PRD / US / execution docs | 明确 v1.1.9 是 overlay，不是新造平行 lifecycle |
| TC-002 | architecture | 对照现有 Beacon 主命令面 | delivery plane 明确保留 `workflow / implement / qa / review / gate / release / debug` |
| TC-003 | contract | 定义 debug exhaustion state | 存在 `failure_streak / escalation_level / attempted_strategies / evidence_gap` 等最小语义 |
| TC-004 | recovery | 中断后 resume / continue | 恢复语义包含 tried approaches / excluded causes / next hypothesis / blocker |
| TC-005 | completion | 实现完成但未补证据 | Beacon 能区分 `implementation_done` 与 `evidence_done`，不误判闭环完成 |
| TC-006 | qa | 需求或实现变化后执行 QA | 能定义 targeted rerun，而不是笼统全量重跑或完全不重跑 |
| TC-007 | traceability | requirement → implementation → evidence 对齐 | story/AC/test-case、technical archive、verification/gate evidence 三层关系清晰 |
| TC-008 | writeback | implement / review 产出 artifact_updates | 被定义为正式 writeback obligation，而非仅摘要提示 |
| TC-009 | learning | technical archive 进入 version/requirement rewrite 输入 | 可解释如何从 archive 提炼风险、缺口与模板补强项 |
| TC-010 | learning | debug harvest 进入 issue / idea / baseline uplift | 可解释如何从 friction 提炼下一轮改进输入 |
| TC-011 | boundary | evo harness 边界检查 | 定义 keep/discard discipline 与 benchmark corpus，但不声称整仓自治 |
| TC-012 | regression | 对照 v1.1.8 发布线语义 | v1.1.9 设计不破坏现有已发布命令面与发布线 |
| TC-013 | scope | 当前 v1.1.9 是否与实现一致 | 文档、machine artifacts、tests、command surface 一致，不再保留 design-only 叙事 |
| TC-014 | skill-docs | 读取 root `SKILL.md` 与 `skills/beacon/SKILL.md` | 明确一主一辅角色，不存在定位冲突 |
| TC-015 | skill-structure | 对照两份 skill 文档 section | 发布线、产品定位、适用范围、快速上手、workflow 模型、产品面、阅读顺序、命令入口、导航规则、故障排查等结构稳定镜像 |
| TC-016 | operator-entry | 用户从任一 skill 入口进入 | 能清晰知道当前正式 release line、下一探索线、该看哪份 docs、该跑哪些命令 |
| TC-017 | anti-drift-ports | 对照 CLI / README / root skill / packaged skill / runtime state / installed copies / managed blocks | anti-drift requirement 明确覆盖这些端口，而不是只覆盖 workflow/gate |
| TC-018 | baseline-contract | 对照 `revision_state` / `story_state` / `v110_baseline` | requirement 明确 baseline / fingerprint / drift 的 canonical source 与 projection 边界 |
| TC-019 | qa-feature-entry | 以 `qa run <feature>` 为目标语义审查需求 | requirement 明确 QA 需支持 feature-aware 入口，而不是只保留 scope-driven alias |
| TC-020 | qa-story-sequence | 审查“实现完成后依次验证用户故事/AC”能力 | requirement 明确 QA 需支持 user-story / AC 顺序推进，而不是仅 layer/matrix 驱动 |
| TC-021 | qa-evolve | 审查 `qa evolve` | requirement 明确 `qa evolve` 进入正式 scope，用于 delta-aware rerun |
| TC-022 | per-item-writeback | 对照 verification/accept writeback | requirement 明确未来需支持 AC / TEST item 粒度 writeback，而不是只做整体汇总 |
| TC-023 | scenario-expansion | 对 browser-relevant AC 运行 scenario expansion | 每个 AC 不再只对应一个 TC，而是被展开为最小 scenario families |
| TC-024 | scenario-map | 检查 `.machine/qa/<feature>.story-scenario-map.json` | 存在 AC→scenario 映射、family、dependency、browser_required 等字段 |
| TC-025 | story-exhaustive | 执行 `qa run <feature> --mode story-exhaustive` | QA 按 user-story / AC / scenario 顺序推进，而不是只按 layer 执行 |
| TC-026 | browser-exploration | 用 agent-browser / browser-use 执行 browser scenario | 产生 action transcript、URL、DOM、screenshot、console 等探索证据 |
| TC-027 | browser-replay | 对 P0/P1 browser scenario 执行 deterministic replay | 关键浏览器 claim 可被 Playwright/Cypress/项目定义 runner 重放验证 |
| TC-028 | browser-evidence-pack | 检查 browser scenario evidence 目录 | evidence pack 完整且可被 gate / review 消费 |
| TC-029 | story-gate | 前置 AC 失败后继续推进后续 AC | Beacon 能按 dependency-aware 语义 block / skip / reroute，而不是盲目继续 |
| TC-030 | scenario-writeback | browser QA 完成后检查 writeback | scenario / AC / TEST item 状态都能被正式回写 |
| TC-031 | scenario-delta-rerun | requirement / implementation 变化后执行 `qa evolve` | 输出受影响 scenario ids / browser paths / stale evidence 范围 |
| TC-032 | exhaustiveness-score | 审查 QA exhaustiveness report | 存在 missing_axes、coverage score、required_next_action、escalation level |
| TC-033 | escalation | 同一 browser scenario 连续失败 | Beacon 进入 escalation，要求切换 runner/方法或补齐证据，而不是重复原路径重试 |
| TC-034 | non-agent-only-pass | 仅有 agent 探索，没有 replay evidence | Beacon 不得把该 feature 标记为 browser gate-ready |
| TC-035 | compatibility-family | browser compatibility 为 required family | 至少能表达 required browser/device pairs，并校验其 evidence 完整性 |
| TC-036 | release-gate | 进入 release / acceptance gate | gate 因 scenario families 缺失、replay 缺失或 exhaustiveness 不足而正确阻断 |

## 样板场景

### 场景 A：Debug 连续失败后继续推进
- 某 feature 在 implement/verify 间连续失败两到三次
- 预期：系统不只是记录失败，而是进入 escalation，要求切换策略或补足证据/假设验证

### 场景 B：QA 通过但证据不完整
- 实现已完成，局部测试也跑了，但缺少关键 evidence refs / quality review 输入
- 预期：只能算 `implementation_done`，不能算 `evidence_done` 或 gate-ready

### 场景 C：需求变化导致 targeted rerun
- user-story/AC 更新后，只影响部分页面/API/数据路径
- 预期：QA 定义能识别受影响范围，并对失效 evidence 做 targeted rerun

### 场景 D：技术归档反哺下一轮需求
- `technical-implementation-*` 显示某类 artifact_updates、rollback_notes 和 risk 多次重复出现
- 预期：这些信息会进入下一轮 PRD/test-case/version research，而不是只留在归档里

### 场景 E：Evo 边界受控
- 团队希望引入自进化机制
- 预期：先定义 small editable surface、fixed budget、main KPI、keep/discard ledger，而不是直接放开整仓自治

### 场景 F：从 skill 入口直接开始使用 Beacon
- 用户或 agent 先读 root `SKILL.md`，也可能先读 `skills/beacon/SKILL.md`
- 预期：两者都能把用户稳定导向同一 release line、同一 workflow 模型与同一下一步动作

### 场景 G：README / CLI / QA 心智一致
- README/skill 文档把 QA 描述为 feature-oriented、workflow-aware
- 预期：v1.1.9 requirement 明确要把实现语义也向该心智收敛，不能长期停留在 scope-only alias

### 场景 H：baseline 多中心收敛
- revision_state、story_state、v110_baseline 都涉及 baseline/fingerprint/drift
- 预期：v1.1.9 requirement 明确三者主从边界，避免继续多中心漂移

### 场景 I：一个 AC 自动展开为多条浏览器场景
- 某 user-story AC 涉及表单、权限与页面跳转
- 预期：Beacon 自动生成 happy / invalid input / unauthorized / refresh recovery / browser compatibility 等 scenario families，而不是只留一个 smoke case

### 场景 J：探索执行与确定性回放分层
- agent-browser 成功走通页面，但 deterministic replay 尚未补齐
- 预期：该 feature 最多只能算“探索通过”，不能算 browser gate-ready

### 场景 K：浏览器场景连续失败触发升级
- 同一 scenario 连续两到三次失败
- 预期：Beacon 不再重复同一路径，而是提升 escalation level，并要求切 runner、补 DOM/console/network 证据或进入结构化失败边界

### 场景 L：穷尽度不足阻断放行
- happy path 全绿，但 negative / recovery / compatibility families 缺失
- 预期：QA / gate 因 exhaustiveness 不足而阻断，而不是把“happy path 通过”误当成 requirement closure

## 执行语义

- `Pass`：v1.1.9 被清晰定义为 control + recovery + learning overlay，四个闭环已在实现与验证面落地
- `Pass`：skill 文档也被纳入 operator clarity 范围，一主一辅结构清晰
- `Pass`：防漂移 requirement 已覆盖 lifecycle + surface 两层，且 QA feature-aware/story-sequential 缺口已进入正式 requirement
- `Pass`：Beacon 已把 browser-relevant user stories 编译为 scenario families，并能以 story-exhaustive 方式执行、回写与 rerun
- `Pass`：关键 browser claims 同时具备 exploratory evidence 与 deterministic replay evidence
- `Pass`：exhaustiveness score、missing axes、escalation contract 已进入正式 QA / gate 语义
- `Fail`：仍停留在功能堆叠或抽象研究，没有落成正式 requirement 物料
- `Fail`：仍停留在 AC→单一 TC 或 layer-only QA，无法支撑按用户故事发散测试
- `Fail`：browser QA 只有 agent 探索，没有可回放证据，却仍被判定为 gate-ready
- `Blocked`：overlay 策略、completion contract、writeback contract 或 evo boundary 仍存在关键冲突
- `Blocked`：scenario families / dependency rules / replay evidence / exhaustiveness threshold 之间仍存在关键 contract 冲突
