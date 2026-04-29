# PRD: Beacon v1.3.10 project topology and version-branch metadata transaction governance

**Feature**: `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`  
**Version**: `v1.3.10`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Prior version summary: `docs/beacon/v1.3.9/SUMMARY.md`
- Prior friction intake PRD: `docs/beacon/v1.3.9/prd/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- Prior execution projection convergence PRD: `docs/beacon/v1.3.9/prd/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- Prior agents/runtime compatibility PRD: `docs/beacon/v1.3.9/prd/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- Brainstorm inputs:
  - `docs/brainstorms/2026-04-29-from-rolo-monorepo-friction-evidence:-project-root-has-no-.git,-service-repo-roo.md`
  - `docs/brainstorms/2026-04-29-treat-the-rolo-monorepo-friction-as-a-metadata-governance-problem,-not-a-frictio.md`
- Real-project evidence:
  - `/Users/apple/Developer/Company/rolo/.beacon/analysis/friction-intake-fit-20260429T134524Z.md`
  - `/Users/apple/Developer/Company/rolo/.beacon/debug/friction-captures/d0e3703a6a13.json`

## 1. 问题

Beacon 已经具备全局 sqlite runtime ledger、git scope 投影、以及事务驱动的多写原则，但真实项目执行仍然依赖重复的运行时推断来判断项目拓扑、目标服务仓与目标分支。

`rolo` 的 monorepo 摩擦把这条缺口暴露得很清楚：

1. Beacon 能判断目标项目根目录没有 `.git`，但不能把 `project_root -> service repo roots` 固化成可复用、可强校验的契约真相。
2. Beacon 还没有一套可直接被 `implement / qa / release` 消费的强校验 `version -> service set -> canonical branch` 元数据模型。
3. 因此提示层、运行层、以及面向人类的 support surface 仍会反复依赖 LLM 或启发式判断：
   - 该项目是 monorepo 还是 single-repo
   - 当前执行目标到底是哪一个 service repo
   - 当前 Beacon 版本线对应的 canonical 可写分支是什么
4. 即便 sqlite 中已经存在部分 git 投影表，它们也还没有上升为一套“项目版本元信息契约”，并通过人类面、机器面、sqlite 面共享同一事务一致性。
5. 人类操作者目前也缺少一套显式的元信息 support surface 来做增删改查与校验，因此文档、运行投影、执行行为之间会持续累积 drift。

当前 `rolo` 真实证据还暴露出四个已经可复现的缺口：

1. `friction-intake` 的 human/json 输出没有显式包含绝对 `project_root`。
2. `.beacon/state/friction-intake/latest.json` 只有相对 `payload_path` / `markdown_path`，缺少 `project_root` 与绝对 artifact path。
3. 人类提示中的“落盘位置”仍打印相对路径，在 cross-project / monorepo 场景下容易误判产物归属。
4. domain classifier 缺少 `monorepo / branch-governance / repo-binding` 规则，导致该类元信息治理问题被错误打到 `prompt`。

因此问题不只是 friction-intake 输出歧义，更严重的是确定性执行漂移：

- implement 可能在错误的 service repo 启动
- implement 可能在错误的开发分支继续推进
- protected branch 可能被误写
- 版本绑定交付可能沿着过期或不匹配的 branch contract 继续执行
- 后续 QA / release 需要重新重建本应已经固化成元信息真相的上下文

## 2. 目标

### 2.1 主要目标

- 定义一套面向 Beacon 的项目版本元信息模型，用于项目拓扑与分支治理。
- 将该元信息作为 canonical truth，通过同一事务投影到：
  - human-readable sink
  - machine-readable sink
  - sqlite runtime projection sink
- 让 prompt/runtime/support surface 直接消费该元信息，减少后续执行过程中重复的 LLM 推断。
- 增加面向人类的元信息 support surface 或子 skill，支持显式增删改查与校验，并纳入同一多写事务契约。
- 让 `implement / qa / release` 在 repo、service、branch 与 contract 不匹配时确定性阻断。

### 2.2 非目标

- 不新增新的公开主生命周期 stage。
- 不把 sqlite 变成唯一 truth source。
- 不允许 human-readable docs 反向驱动 machine truth。
- 不在没有明确操作者意图的前提下自动修改 service repo 或自动切换分支。
- 不把本 feature 扩张成泛化的项目编排系统；本次只收口项目拓扑与分支治理元信息。

## 3. 设计原则

### 3.1 元信息是契约，不是提示

项目拓扑、service 映射、canonical branch 规则必须成为固定模型值并具备显式校验语义，不能继续作为后续 prompt 的宽松提示。

### 3.2 Canonical first，projection second

所有元信息写入都必须先形成单一 canonical envelope，再向 human、machine、sqlite 三个 sink 投影。

### 3.3 事务级一致性

元信息变更必须遵循 `prepare -> validate -> commit -> publish -> verify`，并让所有 sink 共享同一事务元数据：

- `transaction_id`
- `source_hash`
- `projection_seq`
- `committed_at`
- `sink_checksums`

### 3.4 Runtime 读取元信息，不再重造元信息

`implement`、`qa`、`release`、prompt 生成与 support skills 应直接读取已经解析完成的元信息契约，而不是反复推断 repo 拓扑和 branch 意图。

### 3.5 人类变更必须显式

元信息变更属于治理动作，必须显式、可审计、可回滚，并通过 support surface 暴露，而不是依赖隐藏副作用。

## 4. 范围

### In scope

- 面向项目拓扑与分支治理的 project-version metadata schema
- canonical metadata envelope 与 projection contract
- 面向元信息的人类面、机器面、sqlite 投影
- 元信息增删改查与校验 support command / 子 skill
- `implement`、`qa`、`release` 前的元信息硬校验
- 元信息消费或变更时的 cross-project / monorepo 安全路径报告

### Out of scope

- 完整的 service 依赖图编排
- 任意 CI/CD pipeline 管理
- 超出“确定性阻断 + 显式修复指引”之外的脏 git 状态自动修复
- 用完全无关的新存储模型替换现有 git/runtime 表

## 5. 功能需求

### FR-001 Beacon 必须定义项目拓扑与分支治理的 project-version metadata schema

该 schema 至少必须支持：

- `global_project_metadata`
- `version_scoped_metadata`
- `topology_kind`: `single_repo | monorepo`
- `project_root`
- `service_repo_roots[]`
- `default_execution_service`
- `service_bindings[]`
- `version_contracts[]`
- `protected_branch_rules[]`
- `metadata_status`

每条 `service_binding` 至少必须表达：

- service key
- repo root
- role
- writable vs reference-only intent
- worktree path policy

每条 `version_contract` 至少必须表达：

- Beacon version
- participating service set
- per-service canonical branch
- expected branch rule
- branch guard mode
- violation behavior

同时，Beacon 必须把元信息明确拆成两层：

1. 全局项目级元信息
   - 跨版本共享
   - 描述项目公共事实
   - 至少包括：
     - `project_root`
     - `topology_kind`
     - `service_repo_roots`
     - `service bindings`
     - `default_execution_service`
     - 全局 protected branch baseline policy

2. 版本级元信息
   - 与某个明确的 `vX.Y.Z` 绑定
   - 描述该版本线的交付契约
   - 至少包括：
     - `version -> service set`
     - `version -> per-service canonical branch`
     - `version-specific writable scope`
     - `version-specific branch guard mode`
     - `version-specific validation state`

### FR-002 Beacon 必须把拓扑与分支元信息持久化为 canonical transaction truth

元信息写入不得按 sink 分头散写。Beacon 必须构建单一 canonical metadata envelope，并将其投影到：

- human-readable documentation
- machine-readable material
- sqlite runtime projection

事务必须可审计，并在 sink 不一致时 fail closed。

### FR-003 Beacon 必须提供确定性的人类面元信息 skill，并支持增删改查与校验

Beacon 必须暴露确定性的人类面元信息 skill，名称固定为：

- `beacon:beacon-project-metadata`

同时，其宿主命令面必须保持 Beacon 的极简人类操作面设计，不新增新的一级公开命令，而是收敛在现有 support surface 下。默认命令形态固定为：

- `beacon doctor metadata show`
- `beacon doctor metadata create ...`
- `beacon doctor metadata update ...`
- `beacon doctor metadata delete ...`
- `beacon doctor metadata list ...`
- `beacon doctor metadata verify ...`

该 skill / command 组合的能力覆盖至少包括：

- 查询当前 metadata
- 新增 topology / service / version contract
- 修改 topology / service binding / branch contract
- 删除已失效的 service binding 或 version contract
- 列表查看当前版本与服务映射
- 校验当前 runtime state 是否满足 metadata contract

这些操作必须走同一 canonical metadata transaction path，而不是直接补丁某一个 sink。

### FR-004 Prompt 层与 runtime 层必须确定性消费元信息

当 metadata 已存在时，Beacon 的 prompt/runtime 流程必须把它作为以下事实的主来源：

- 目标项目是 monorepo 还是 single-repo
- 当前执行目标是哪一个 service repo
- 当前版本线对应的 canonical 可写分支是什么
- 当前 repo / branch / worktree 状态是否有效

后续 prompt 可以解释为什么这样判定，但不能重新决定已经被 metadata contract 固定下来的事实。

进一步要求：

- 当用户以 `beacon:子skill + vX.Y.Z`、或等价的显式 `--version vX.Y.Z` 调用 Beacon 相关子 skill 时，提示层不得自己重新推断这些事实。
- 提示层必须通过 Beacon 运行层读取：
  - 全局项目级元信息
  - 对应 `vX.Y.Z` 的版本级元信息
- Beacon 运行层必须产出一份 resolved metadata view，供 prompt 层、runtime 层、support surface 直接消费。
- prompt 层只能消费 resolved metadata view，不能绕过运行层自行再决策。

同时，`friction-intake`、`brainstorm`、`change` 等 Beacon 相关 support skill 在显式带上 `vX.Y.Z` 时，也必须走同一 resolved metadata view，不能各自重新决定 topology、service repo 或 canonical branch。

### FR-005 `implement`、`qa`、`release` 必须在 metadata contract 违例时硬阻断

执行继续之前，Beacon 至少必须校验：

- 当前项目拓扑满足 metadata contract
- 目标 service repo 能被确定性解析
- 当前 branch 满足目标 service 的 version contract
- protected-branch 规则未被违反
- worktree 与 writable service scope 满足 contract

发生违例时，Beacon 必须以确定性错误输出与修复指引停止执行。

### FR-006 元信息投影必须保持 human、machine、sqlite 三面一致

Beacon 的 `status / review / doctor / gate` 等 surface 必须能检测并报告：

- metadata sink 缺失
- sink 间 checksum drift
- 相对 canonical metadata 已过期的 runtime projection
- failed / partial metadata transaction

任何一个 sink 都不允许静默独占权威性。

### FR-007 Cross-project artifact reporting 必须是 metadata-safe

当 Beacon 报告元信息产物或基于元信息做出决策时，输出必须清晰标识：

- 绝对 `project_root`
- 解析后的 service repo root
- human sink path
- machine sink path
- sqlite projection transaction identifiers

这样做是为了避免多项目 / monorepo 操作中的 cross-workspace 歧义。

### FR-008 `friction-intake` 输出契约必须显式携带绝对路径元信息

`friction-intake` 的 human-readable output 与 json output 必须显式包含：

- 绝对 `project_root`
- human artifact 的绝对路径
- machine artifact 的绝对路径
- capture evidence 的绝对路径

其中：

- human/json 输出不得只输出相对路径
- `.beacon/state/friction-intake/latest.json` 除保留相对路径外，还必须补充：
  - `project_root`
  - `payload_abs_path`
  - `markdown_abs_path`
- 在 cross-project 模式下，“落盘位置”必须打印绝对路径；在 single-project 模式下也应优先打印绝对路径以保持一致性

### FR-009 domain classifier 必须新增元信息治理规则

Beacon 必须把以下问题优先识别为元信息治理域，而不是宽泛 `prompt`：

- `monorepo`
- `branch-governance`
- `repo-binding`

分类器至少必须支持：

- 依据原始 note、evidence、resolved metadata mismatch 命中上述 domain
- 将该类项路由到 project-version metadata governance 语义，而不是普通 prompt 优化语义
- 在 `friction-intake -> brainstorm/change/prd` 链路中保留该 domain，不得被后续流程静默改写回 `prompt`

## 6. 边界 / 分层 / 恢复

### 6.1 边界

- requirement truth 不会单独下沉为 sqlite 真相
- sqlite projection 不能反向成为 docs 或 machine truth 的写入源
- metadata governance 只覆盖 topology 与 version-branch execution contract，不扩张为完整交付编排

### 6.2 分层

- canonical metadata envelope 是唯一写入源
- human sink 是面向评审与操作者理解的层
- machine sink 是面向确定性 runtime 与校验的层
- sqlite sink 是面向快速查询与治理投影的层

### 6.3 恢复

- failed metadata transaction 必须保持可检查
- sqlite projection 必须能从 canonical metadata truth 重建
- drifted sink 必须通过 replay canonical transaction 修复，而不是分别手工补丁

## 7. Data and projection model

### 7.1 Canonical metadata envelope

Beacon 必须定义面向 project-version governance 的 canonical metadata envelope，至少包含：

- schema version
- project key
- project root
- topology kind
- service bindings
- version contracts
- branch guard rules
- transaction metadata

### 7.2 Human-readable sink

Beacon 必须投影一份可供人类评审的 metadata 文档，至少解释：

- project topology classification
- service repo mapping
- version to service set mapping
- per-service canonical branches
- protected branch rules
- current validation status
- 绝对 `project_root`
- 各关键 artifact 的绝对路径

### 7.3 Machine-readable sink

Beacon 必须投影 machine-consumable metadata，供 prompt/runtime/status/doctor/gate 消费；该 sink 必须稳定且适合后续自动化消费。

对于 `latest.json` 这类 machine pointer 文件，必须同时保存：

- `project_root`
- 相对 artifact path
- 对应绝对 artifact path
- 生成该 pointer 的 transaction / run metadata

### 7.4 SQLite runtime projection sink

Beacon 必须扩展或复用 runtime ledger 表来物化快速查询和校验所需的 metadata。现有 `git_scopes` 与 `git_workspace_bindings` 可以复用，但只有被纳入新的 canonical metadata contract 后才算满足要求。

### 7.5 Versioned mutation history

Metadata mutation 必须留下足够的 append-only transaction history，用于：

- audit
- rollback guidance
- drift diagnosis
- sqlite projection rebuild 后的 replay

## 8. 验收标准

### AC-001 元信息双层模型冻结

- Beacon 明确定义全局项目级元信息与版本级元信息两层模型。
- `topology_kind`、`service bindings`、`version contracts`、`canonical branch`、`branch guard mode` 都有固定字段边界。

### AC-002 提示层按版本读取 resolved metadata view

- 当用户使用 `beacon:子skill + vX.Y.Z` 或显式 `--version vX.Y.Z` 时，提示层通过运行层读取：
  - 全局项目级元信息
  - 该版本对应的版本级元信息
- 提示层不再自行重推断 monorepo / service / branch 事实。

### AC-003 人类面 metadata support surface 闭环成立

- `beacon:beacon-project-metadata` 名称固定。
- `beacon doctor metadata show/create/update/delete/list/verify` 命令面固定。
- 增删改查与校验都走 canonical transaction。

### AC-004 Cross-project 输出无歧义

- human/json 输出显式显示绝对 `project_root`。
- “落盘位置”至少在 cross-project 模式下打印绝对路径。
- `latest.json` 同时给出相对与绝对 artifact path。

### AC-005 元信息类 friction 不再误分到 `prompt`

- `monorepo / branch-governance / repo-binding` 命中新增 domain classifier 规则。
- 该类问题进入 project-version metadata governance 语义线，而不是普通 prompt 优化线。

### AC-006 分支与仓绑定违例时硬阻断

- `implement / qa / release` 在 repo/service/branch/worktree 与 metadata contract 不一致时停止执行。
- 错误输出包含确定性修复指引与关联 metadata artifact 定位。

## 7. 风险与缓解

| Risk | Impact | Mitigation |
|------|------|------|
| Metadata becomes a second informal hint layer instead of hard contract | High | Force runtime consumers to read canonical metadata first and hard-block on violations |
| Human sink and sqlite sink drift | High | Shared transaction metadata, checksum verification, and doctor/gate drift reporting |
| Operators bypass metadata commands and patch one sink directly | High | Expose explicit support commands and make verification surfaces detect out-of-band drift |
| Model is too loose for monorepo realities | High | Require topology kind, service bindings, version contracts, and protected branch rules as structured fields |
| LLM continues to re-infer service/branch facts even when metadata exists | High | Prompt/runtime contract must treat metadata as fixed truth inputs |

## 8. 验收标准

### AC-001 Structured metadata truth exists

Beacon 能持久化 project-version metadata，并以确定性方式表达 monorepo / single-repo 拓扑、service repo bindings、以及 version-branch contracts。

### AC-002 Canonical transaction governs all metadata writes

A metadata mutation results in one canonical transaction whose human sink, machine sink, and sqlite sink share the same transaction lineage and consistency metadata.

### AC-003 Human metadata skill exists for explicit governance

操作者能通过 `beacon:beacon-project-metadata` 以及 `beacon doctor metadata ...` 显式新增、查询、修改、删除、校验 topology / service / branch metadata，而不是手改各类 sink。

### AC-004 Runtime contract consumption is deterministic

When metadata exists, Beacon prompt/runtime flows use it as the primary truth source and no longer require repeated service/branch inference for normal operation.

### AC-005 Execution gates block on metadata mismatch

`implement`, `qa`, and `release` stop deterministically when runtime repo/branch/worktree state violates the active metadata contract.

### AC-006 Multi-sink drift is auditable

`status`、`doctor`、`gate` 或等价治理 surface 能检测 failed metadata transaction 与 sink drift。

### AC-007 Cross-project reporting is unambiguous

Human-visible metadata outputs identify the absolute project root and artifact locations clearly enough to avoid cross-workspace confusion.

## 9. Success metrics

- 降低真实项目执行中的重复 LLM / service / branch 推断
- 降低错误分支或错误 service 启动 implement 的概率
- 提升 branch / topology mismatch 的确定性阻断速度
- 降低 Beacon 核心仓与目标项目仓并行操作时的人类歧义

## 10. Dependencies and open questions

- Decide whether metadata human sink lives under `docs/beacon/<version>/execution/` or another version-scoped governance path
- Decide whether current git ledger tables are extended or wrapped by a new canonical projection layer
- Decide exact public naming for metadata support commands
- Define rollback semantics for metadata transactions that partially validate but fail to publish
