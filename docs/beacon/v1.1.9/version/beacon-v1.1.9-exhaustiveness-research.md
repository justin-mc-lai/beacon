# 版本调研：Beacon v1.1.9 Exhaustiveness / Evidence / Recovery / Evo 演进线

## 版本定位

- target_version: `v1.1.9`
- base_version: `v1.1.8`
- strategy: `bump:patch`
- owner: `Beacon Team`
- generated_at: `2026-03-26`

## 本轮版本调研输入

本轮新增输入包括两类本地源码级调研：

- `docs/beacon/v1.1.9/research/beacon-pua-exhaustiveness-layer-analysis.md`
- `docs/beacon/v1.1.9/research/beacon-karpathy-autoresearch-evo-analysis.md`

两个输入分别提供：

1. **PUA 输入**
   - 给出“失败升级 / 证据硬门禁 / checkpoint / recoverable loop”的执行控制层借鉴
2. **autoresearch 输入**
   - 给出“极小可编辑面 / 固定预算 / 单一主指标 / keep-discard / program surface”的自进化试验台借鉴

其中 PUA 输入的核心结论不是“引入 PUA 话术”，而是：

> 为 Beacon 增加一层正式的 exhaustiveness-controlled execution layer，让 agent 在连续失败、证据不足、准备草率收尾时，自动进入更严格的执行协议。

而 autoresearch 输入的核心结论是：

> Beacon 不应先追求“自改整仓”，而应先建立一个极小、真实、固定预算、可比较的 evo harness。

## v1.1.8 到 v1.1.9 的自然递进

v1.1.8 已经把 Beacon 推进为“项目接管内核”：

- init progressive disclosure
- qa 主入口 / browser acceptance
- debug feedback
- implement technical archive
- prototype baseline

但 v1.1.8 仍有两个明显空档：

### 当前空档 A：执行穷尽层缺失

Beacon 已经很强调：
- 生命周期
- 版本化交付物
- machine-backed truth
- evidence-first

却还没有把下面这件事做成正式能力：

> 当 agent 连续失败、重复试错、证据不足或准备空口完成时，系统如何自动升级执行强度并强制收口？

### 当前空档 B：受控自进化试验台缺失

Beacon 在 v1.1.5 已经提出 `autoresearch-inspired Eval Lab`，但还没有把下列能力做成正式版本线能力：

- subject surface / program surface 分离
- 固定预算实验
- 单一主 KPI + scorecard
- 正式 evo ledger
- keep/discard 裁决纪律

这也是 v1.1.9 值得继续补的层。

## 当前代码级现实补充：不仅是 execution gap，也是 anti-drift gap

本轮进一步对照仓库代码后，v1.1.9 的问题被看得更具体了。

### 当前已经比较强的部分

Beacon 当前正式 release-line 主链已经成立：

- `workflow`
- `freeze / reopen`
- `implement`
- `review`
- `gate`
- `release`

也就是说，Beacon 不是“整体没闭环”，而是：

> **正式交付主链已经较强闭环，但外围控制层、入口端口一致性、QA 语义收口还不够。**

### 当前仍然存在的 4 个真实缺口

#### 1. anti-drift 仍未覆盖所有端口
当前虽然已经有：
- `spec_impl_drift_detected`
- `baseline_snapshot_missing`
- `managed_block_version_drift`
- `installed_skill_copy_drift`

但这些检查点还没有被统一成一个：

```text
full lifecycle + full surface anti-drift contract
```

也就是：
- workflow 主链有检查
- 但 CLI / README / root skill / packaged skill / install copies / managed blocks 还没有被统一收口成版本级 anti-drift requirement

#### 2. baseline 语义还存在多中心
当前 baseline / fingerprint / snapshot 语义分布在：

- `revision_state`
- `story_state`
- `v110_baseline`

这不代表系统不可用，但代表：

> **baseline 的 canonical source / projection / report-layer snapshot 关系仍需收口。**

#### 3. QA 目前还是 matrix-driven，不是 feature-aware / story-sequential
当前已经能做到：

```text
user-story / prd
→ test-case create
→ ac-test-matrix / qa9-matrix
→ auto-test / qa
→ coverage / review / gate
```

但还做不到：

```text
implement done
→ qa run <feature>
→ 自动按 user-story / AC 顺序依次验证
→ per-item verification writeback
```

换句话说：
- 现在的 QA 更像 `matrix execution engine`
- 还不是 `feature-aware sequential verification surface`

#### 4. `qa evolve` 仍停留在设计语义
文档已经把 `qa evolve` 当成目标能力写了出来，但代码层还没有正式命令面。

这意味着 v1.1.9 除了 execution control / evo harness 外，还必须显式把：

- feature-aware QA
- story-sequential QA
- delta-aware `qa evolve`

纳入 requirement scope。

## v1.1.9 建议主题

### 主题

把 Beacon 从：

```text
requirements / evidence / gate kernel
```

推进为：

```text
requirements / evidence / gate / exhaustiveness / evo kernel
```

### 目标

1. 把“失败升级”做成正式状态机
2. 把“无证据不得完成”做成正式硬门禁
3. 把“方法论切换”做成正式执行路由
4. 把“compaction 不清零”做成正式 checkpoint / resume 能力
5. 把“暂停 / 终止 / 真完成”做成正式 loop 控制语义
6. 把“高质量动作固化为默认义务”做成 execution baseline
7. 把“极小可编辑面 + 固定预算 + keep/discard”做成正式 evo harness
8. 把“全端口 anti-drift + feature-aware sequential QA”做成正式 requirement line

## 建议冻结的 6 条设计线

### 线 A：Exhaustiveness Escalation

目标：
- 用 `failure_streak` 和 `escalation_level` 描述连续失败状态
- 明确每一级的 required next action

候选输出：
- `.beacon/state/exhaustion.json`
- `execution/exhaustiveness-policy.md`

### 线 B：Evidence Hard-Stop

目标：
- claim 与 evidence 解绑时直接阻断
- “已完成”必须分成 implementation_done 与 evidence_done

候选输出：
- `execution/evidence-completion-contract.md`

### 线 C：Execution Mode Router

目标：
- task type → execution mode
- failure pattern → next mode

建议 mode：
- debug
- research
- refactor
- architecture
- delivery

候选输出：
- `execution/execution-mode-router.md`

### 线 D：Checkpoint / Resume

目标：
- 保存 tried approaches / excluded causes / next hypothesis / evidence gap
- 恢复时不重复踩同一路线

候选输出：
- `execution/checkpoint-resume-contract.md`
- `.beacon/state/checkpoints/`

### 线 E：Recoverable Loop

目标：
- done / pause / abort 三类信号
- 支持恢复型循环，而不是只支持“直接退出”

候选输出：
- `execution/recoverable-loop-contract.md`

### 线 F：Execution Baseline

目标：
- 让重复的高质量行为升级为默认义务
- 基线只升不降

候选输出：
- `execution/execution-baseline.md`
- `.beacon/state/execution-baseline.json`

### 线 G：Self-Evolution / Evo Harness

目标：
- 定义 subject surface / program surface
- 定义固定预算实验协议
- 定义单一主 KPI + scorecard
- 定义 keep/discard ledger
- 定义真实 benchmark corpus

候选输出：
- `execution/evo-harness-contract.md`
- `execution/evo-program-surface.md`
- `execution/evo-scorecard-contract.md`
- `.beacon/state/evo/`

### 线 H：Anti-Drift Surface Closure

目标：
- 把 lifecycle anti-drift 与 operator-surface anti-drift 编成同一 requirement
- 收敛 README / skill / CLI / runtime / installed copies / managed blocks 的漂移
- 明确 baseline canonical contract

候选输出：
- `execution/anti-drift-surface-contract.md`
- `execution/operator-entry-consistency.md`

### 线 I：Feature-aware Sequential QA

目标：
- 让 `qa run <feature>` 成为正式目标语义
- 让 QA 支持 user-story / AC 顺序验证
- 让 `qa evolve` 进入正式 delta rerun contract

候选输出：
- `execution/feature-aware-qa-contract.md`
- `execution/qa-delta-rerun-contract.md`

## 最值得借鉴的 5 个实现原则

1. **状态机优先于情绪化提示**
2. **执行事实优先于关键词匹配**
3. **证据门禁优先于主观完成感**
4. **checkpoint / resume 优先于重复试错**
5. **结构化失败边界优先于草率放弃**
6. **极小真实试验面优先于整仓自治**
7. **固定预算优先于无限试验**
8. **program surface 优先于直接乱改 subject surface**

## 不应进入 v1.1.9 的范围

### 不建议纳入

- PUA 式高压旁白 / 羞辱表达
- 排行榜 / 支付 / 注册 / 反馈平台化能力
- 只靠 regex 的情绪触发
- 复杂的品牌化 flavor 系统
- 把 Beacon 直接开放成“自改整仓”模式
- 在没有固定预算和 scorecard 前开启大规模 evo

### 原因

Beacon 的核心价值仍然是：
- 需求到交付的 versioned materials
- evidence-first
- machine-backed truth
- release / gate governance

因此 v1.1.9 应只吸收 **穷尽执行机制**，不吸收 **人格化包装层**。

## 推荐实现顺序

如果进入后续编码实现，推荐顺序：

1. `evidence-hard-stop`
2. `exhaustiveness-escalation`
3. `checkpoint-resume-contract`
4. `execution-mode-router`
5. `recoverable-loop-contract`
6. `execution-baseline`
7. `anti-drift-surface-contract`
8. `feature-aware-qa-contract`
9. `qa-delta-rerun-contract`
10. `evo-harness-contract`
11. `evo-scorecard-contract`

原因：
- 先把最危险的“空口完成”堵住
- 再处理连续失败和恢复能力
- 再收口全端口 anti-drift 与 feature-aware QA
- 然后再把高质量动作固化成基线
- 最后再引入更严格的受控自进化试验台

## 一句话版本结论

> v1.1.9 最合理的新增方向，是把 Beacon 补成一个“不会轻易自我宣布完成、不会轻易无边界放弃、也不会无约束自我修改”的执行与自进化内核。

## 追溯

- `docs/beacon/v1.1.9/research/beacon-pua-exhaustiveness-layer-analysis.md`
- `docs/beacon/v1.1.9/research/beacon-karpathy-autoresearch-evo-analysis.md`
- `docs/beacon/v1.1.8/version/beacon-v1.1.8-prototype-baseline.md`
- `docs/beacon/v1.1.8/research/three-track-closure-audit.md`
- `docs/beacon/v1.1.5/prd/beacon-autoresearch-eval-lab.md`
