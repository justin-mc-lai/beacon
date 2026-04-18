# PRD：Beacon v1.3.4 Runtime Evidence 分层与噪音治理

**Feature**: `beacon-v1.3.4-runtime-evidence-layering-and-noise-governance`  
**Version**: `v1.3.4`  
**Date**: `2026-04-18`  
**Status**: `planning line`

## 1. 问题

随着 Beacon 在 `v1.3.x` 持续增强机器内部能力，当前版本线已经出现一个越来越明显的产品噪音：

1. `docs/beacon/<version>/` 与 `docs/beacon/<version>/.machine/` 已开始承载正式 requirement / gate / implementation evidence。
2. `.beacon/` 同时承载大量本地 runtime、debug、team HUD、input audit、checkpoint、session 派生状态。
3. `status / help / qa / release` 既会参考正式 evidence，也会读取部分 `.beacon` 本地状态。

结果是：

### 1.1 机器面没有被正式分层

当前 Beacon 虽然事实上已经存在两类机器材料，但产品语义还没有正式冻结：

- 一类是应该进入 git、参与评审、参与 gate 的 machine evidence。
- 一类是只应本地存在、允许缺失、允许重建的 runtime cache / debug stream。

如果这两类不被正式分层，就会出现：

- git 工作区长期脏
- 人类看见大量版本与 runtime 噪音
- stale runtime 误导 release / qa / status
- 宿主局部状态被误当作 Beacon 正式真相

### 1.2 `status` / `help` 输出噪音高于决策价值

从当前 `v1.3.4 docs` + `v1.3.3 runtime` 的状态可以看到：

- docs version
- runtime version
- context managed version
- planning line
- feature gate
- local runtime state

这些字段机器上是必要的，但人类默认只需要：

- 当前 truth line
- 当前 revision
- 当前阶段
- blocker
- 下一步
- runtime 是否可作为辅助佐证

现在的问题不是信息不够，而是：

> 人类默认面正在被机器内部解释层淹没。

### 1.3 `qa / release` 对 runtime 的使用规则还不清

当前应该被明确冻结的判断是：

- runtime 信息存在时，是否参与验证？
- runtime 信息缺失时，是否阻断 release？
- stale runtime 是否能覆盖已冻结 docs / machine evidence？
- 是否应该把 `.beacon` 整体提交到 git？

如果这些规则不被正式写成版本内合同，后续实现会不断在以下两种错误之间摇摆：

- 错误 A：什么都不提交，导致 gate 缺少可复现机器证据
- 错误 B：把完整 runtime / debug / session 洪流都提交到 git，造成长期噪音与边界破坏

## 2. 目标

`v1.3.4` 需要正式冻结 Beacon 机器面的提交边界与噪音治理规则。

### 2.1 正式区分两类机器材料

Beacon 必须在产品层面明确区分：

- `formal machine evidence`
- `ephemeral runtime cache`

### 2.2 只让前者进入 git

必须进入 git 的，应是：

- 参与 freeze / implement / qa / release gate 的规范化 machine evidence
- 可复现、可评审、可被版本包引用的机器产物

不应整体进入 git 的，应是：

- 高频 runtime 状态
- 调试流
- HUD
- input audit
- checkpoint
- 原始 session / transcript 洪流

### 2.3 明确 runtime 在 `status / qa / release` 中的角色

runtime 只能作为：

- `corroboration`
- `observation`
- `rebuild hint`

而不能成为：

- requirement truth
- acceptance truth
- release truth

### 2.4 定义“有 runtime 用 runtime，没有 runtime 重新验证”的正式合同

规则必须收口为：

> runtime 有则利用，但只能作为符合 revision/freshness 的辅助证据；runtime 无则允许回到 Beacon 正式材料重新验证，不得把 runtime 缺失误判为项目不可继续。

## 3. 设计原则

### 3.1 Truth / Evidence / Cache 三层必须分开

Beacon 在 `v1.3.4` 之后必须承认三层不同对象：

1. `truth`
   - `docs/beacon/<version>/`
   - `.beacon/` 中被正式声明为 truth 的本地证据面
2. `formal machine evidence`
   - `docs/beacon/<version>/.machine/`
3. `ephemeral runtime cache`
   - `.beacon/state/`
   - `.beacon/implement/`
   - `.beacon/team/`
   - `.beacon/debug/`
   - 其他本地运行流

### 3.2 不提交完整机器面，只提交规范化证据

本 PRD 的核心判断不是“机器面要不要进 git”，而是：

- 不提交完整机器面
- 只提交参与 gate 的规范化 machine evidence

### 3.3 Runtime 可以帮助判断，但不能反向劫持 gate

runtime 如果存在，只能在满足下列条件时参与正式判断：

- 与当前 `revision_id` 对齐
- 与当前 `baseline_hash` 对齐
- 在 freshness 窗口内
- 来源路径与生成时间明确

否则只能被标记为：

- `stale`
- `partial`
- `advisory`

### 3.4 缺失 runtime 不得阻断项目继续

如果 runtime cache 不存在、被清理、未提交、已失效，系统必须允许：

- 从 `docs/beacon` + `docs/beacon/.machine` + 项目本地正式材料继续
- 触发重验或 rebuild

而不是直接把项目判为不可继续。

### 3.5 人类默认输出必须降噪

`status / help / release` 默认输出必须优先回答：

- 当前版本线
- 当前 revision
- 当前阶段
- blocker
- 下一步
- runtime corroboration 状态

而不是默认输出大段 `version_context`、raw paths、local runtime internals。

## 4. 范围

### In scope

- Beacon 机器面的正式分层定义
- `docs/beacon/<version>/.machine/` 的 git 提交定位
- `.beacon/` 本地 runtime cache 的非提交定位
- `status / qa / release` 对 runtime 的使用规则
- stale / missing runtime 的降级与重验规则
- runtime corroboration summary 的升格合同

### Out of scope

- 改写 `docs/beacon` 作为 truth 的地位
- 把 `.beacon/` 全量迁移进 SQLite 或 git
- 把宿主完整 session / transcript 系统纳入正式版本包
- 新增新的公开一级主命令

## 5. 功能需求

### FR-001 Beacon 必须正式定义 `formal machine evidence`

以下对象必须被收口为正式 machine evidence，并默认允许进入 git：

- requirement clarity report/state
- deterministic implementation contract
- implementation plan / progress
- git workflow contract
- QA matrix / story-scenario mapping
- technical implementation archive
- release-facing scorecard / closure artifacts

默认路径应保持在：

- `docs/beacon/<version>/.machine/`

### FR-002 Beacon 必须正式定义 `ephemeral runtime cache`

以下对象必须被收口为本地 runtime cache，不默认进入 git：

- `.beacon/state/*` 高频运行态
- `.beacon/implement/*`
- `.beacon/team/*`
- `.beacon/debug/*`
- HUD
- input audit
- checkpoints
- raw session / transcript refs
- 原始 stdout / stderr / command artifacts

### FR-003 `status` 必须对人类默认降噪

`status` 默认输出必须优先显示：

- `truth_line`
- `revision_id`
- `current_stage`
- `blocked_reason`
- `next_step`
- `runtime_corroboration_status`

默认不得把以下内容展开给人类：

- 大段 `version_context`
- local runtime root 细节
- raw run state 路径
- 调试/诊断洪流

### FR-004 `qa` 必须把 runtime 视为可选辅助证据

`qa` 执行时：

- 如果存在对齐当前 revision 的 runtime evidence，可作为辅助佐证
- 如果不存在，则必须回落到正式材料和重验路径
- 不得因为缺失 runtime cache 就直接判定无法 QA

### FR-005 `release` 必须只信正式 evidence，不信 raw runtime

`release` gate 判断必须遵循：

- 以 truth + committed machine evidence 为主
- runtime 只作为 corroboration
- raw runtime 不能单独放行 release
- stale runtime 不能推翻已冻结 docs / .machine 结论

### FR-006 必须定义 runtime corroboration 的升格规则

如果某类 runtime 信息需要参与正式版本判断，必须先升格为 summary evidence，而不是直接引用 raw cache。

该 summary 至少必须带：

- `feature`
- `version`
- `revision_id`
- `baseline_hash`
- `observed_at`
- `freshness_status`
- `source_scope`
- `source_runtime_paths`
- `summary_conclusion`

### FR-007 缺失 runtime 时必须有标准回退路径

当 runtime 缺失时，系统必须给出标准动作，而不是只报错：

- `re-verify from docs/beacon and .machine`
- `doctor rebuild`
- `sync-materials`
- `status` 标记 `runtime_corroboration=missing`

### FR-008 `.gitignore` 与 artifact policy 必须反映分层

Beacon 必须让 `.gitignore`、artifact language policy 与版本文档一致表达：

- 什么进 git
- 什么不进 git
- 什么只能按 summary evidence 升格后再进 git

## 6. 候选实现方向

### Slice A：Machine Evidence Policy

- 在 execution 文档中冻结正式 machine evidence 名录
- 统一 `docs/beacon/<version>/.machine/` 的定位

### Slice B：Runtime Corroboration Policy

- 定义 runtime observation summary
- 定义 freshness / revision binding 规则
- 定义 stale / missing / partial 的状态机

### Slice C：Noise Governance

- `status` 人类默认输出收口
- `help` 阻断原因与下一步收口
- `release` 只展示决策必需字段

### Slice D：Git Commit Policy

- 梳理 `.beacon/` 哪些永不提交
- 哪些允许按 summary 升格提交
- 哪些必须转写到 `.machine`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 把 `.beacon` 全量提交到 git，长期制造脏工作区与历史噪音 | 高 | 正式冻结 machine evidence / runtime cache 分层 |
| 什么都不提交，导致 freeze / release 缺少可复现机器证据 | 高 | 要求 gate 依赖的 machine evidence 固定落到 `docs/beacon/<version>/.machine/` |
| stale runtime 误导 QA / release | 高 | 增加 revision/freshness/source 绑定，stale 只能 advisory |
| `status` 默认继续向人类输出机器洪流 | 中 | 默认人类模式只保留 6 个关键字段 |
| 宿主 session / debug 产物误入正式版本包 | 高 | 明确只允许 summary refs，禁止 raw host interaction 进入 truth/gate |

## 8. 验收标准

### AC-001 正式分层明确

版本文档必须明确区分：

- truth
- formal machine evidence
- ephemeral runtime cache

### AC-002 Git 提交边界明确

版本文档必须明确：

- `docs/beacon/<version>/.machine/` 中哪些产物默认提交
- `.beacon/` 中哪些产物默认不提交

### AC-003 `status` 默认降噪

人类默认查看 `status` 时，不应再被大段 version/runtime 解释信息淹没，只应看到阶段判断所需最小字段。

### AC-004 `qa` 可在无 runtime 情况下继续

runtime 缺失时，`qa` 必须允许回退到正式材料与重验路径，不得把 runtime 缺失误判成 feature 无法继续。

### AC-005 `release` 不信 raw runtime

`release` gate 必须只以 truth + committed machine evidence 为主，runtime 只能作为辅助 corroboration。

### AC-006 Runtime Summary 升格合同明确

如果 runtime 信息需要进入版本判断，必须先转成带 revision/freshness/source 的 summary evidence，而不是直接把 raw `.beacon` 状态纳入 git。

## 9. 成功指标

- Beacon 工作区不再因为高频 runtime 缓存而长期脏掉
- `status / help / release` 的默认人类输出明显收敛
- QA 与 release 在无 runtime 时仍可继续推进
- runtime 有值时能提供辅助判断，但不会反向绑架 truth/gate
- 团队能明确知道“哪类机器面该提交，哪类不该提交”

## 10. 与主 PRD 的关系

这是一条 `v1.3.4` 并行 PRD，不替代主 PRD：

- 主 PRD 负责 `Beacon Runtime Ledger`、`Beacon 管理看板`、multi-project projection 与可视化控制面
- 本并行 PRD 负责 Beacon 自身的机器证据分层、runtime 噪音治理、git 提交边界与 gate 判断规则

两者关系应是：

```text
主 PRD
  = 管 Beacon 的多项目态与可视化管理面
并行 PRD
  = 管 Beacon 自己怎样不被 runtime 噪音拖垮
```

---

**Created**: 2026-04-18  
**Version**: v1.3.4  
**Status**: planning line  
**Memory Context**: N/A
