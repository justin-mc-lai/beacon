# PRD: Beacon v1.3.9 execution projection convergence and QA acceptance dual-write

**Feature**: `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`  
**Version**: `v1.3.9`

## 1. Problem

`v1.3.8` 已经把 `implement` 侧收敛到一条更强的 canonical delivery baseline：

- `architecture-blueprint.md`
- deterministic implementation contract
- git workflow contract
- implementation plan

这些 artifacts 已经开始具备两个重要特征：

1. machine truth 来自一个 canonical source
2. human-readable 文档开始承担“如何调用 / 为什么这样做”的正式说明面

但 Beacon 其余 public subcommands 仍存在三类问题：

1. **execution 目录模板化膨胀**
   - `docs/beacon/<version>/execution/` 下仍存在过多低信号模板文档
   - 很多文档既不承担 canonical truth，也不承担稳定的人类操作说明

2. **QA acceptance 没有默认事务双写**
   - 真实项目里，QA 已能拿到 evidence-backed verdict
   - 但 Beacon 默认不会自动产出同一笔 acceptance transaction 的 machine sink + human sink
   - 操作者仍需要手工把 runtime evidence 转成 `docs/beacon/<version>/execution/...`

3. **release / gate / support surface 仍是多源拼接**
   - `release`、`gate`、`help/status/doctor/archive` 还没有统一消费同一组 acceptance / readiness truth
   - human-readable execution 文档与 machine payload 之间仍可能漂移

4. **prototype 仍可能退化成固定模板产出**
   - `prototype` 虽然已经具备 requirement-driven 与 semantic compile 能力
   - 但当前默认路径仍允许在 host/LLM 不可用或 contract 校验失败时静默回退到 rule/template path
   - 这会让人类生命周期中的 `prototype` 阶段重新退化成“固定页面骨架 + 结构化填空”，而不是 requirement truth 推导出的闭环推理产物

5. **QA acceptance dual-write 仍停留在二写，不是完整事务**
   - 当前 acceptance writeback 已能生成 machine sink 与 human-readable markdown
   - 但尚未把 runtime projection sink（SQLite / ledger）纳入同一 acceptance transaction
   - 结果是 `qa`、`release`、`gate`、`status/doctor` 仍可能读取到不同步的 acceptance/readiness 面

6. **promised surface 与 shipped surface 之间仍缺正式 drift gate**
   - 当前 Beacon 已记录 implementation-summary、review-spec、review-quality 等实现/审核产物
   - 但对 PRD、change brief、release/readiness 文档中承诺的 operator-visible surface，仍缺少一条正式的 promised-vs-shipped drift gate
   - 这会让 requirement promise 超前于实现闭环，直到 QA/release 阶段才暴露为后置阻断

7. **`beacon prd create` 仍可能退化成 generic placeholder template**
   - 当前 PRD 生成路径仍可能输出通用占位结构
   - 成功返回并不总是意味着 version-aware、boundary-aware、scenario-aware requirement compile 已完成
   - 这会把 requirement truth 的上游入口重新退化成模板填空，而不是从当前 docs line 和 feature intent 编译出的正式骨架

## 2. Goal

`v1.3.9` 的目标不是继续增加 execution 模板文件，而是把除 `implement` 之外的剩余 public subcommands 收敛到与 `architecture-blueprint.md` 同一类方案：

```text
one canonical envelope
-> machine sink
-> human-readable projection
-> public command usage note
-> gate/release/read-model convergence
```

## 3. Expected Result

完成后，Beacon 应满足：

1. `qa` 在 evidence-backed verdict 后，自动生成一笔 acceptance dual-write transaction。
2. `release` 与 `gate` 消费同一 acceptance/readiness envelope，而不是各自产生平行 truth。
3. `help/status/doctor/archive` 只承担解释层，不再默认扩张 execution 模板文件。
4. execution 目录中的 human-readable 文档只保留高信号投影，能直接回答：
   - 这个命令为什么存在
   - 人类应该怎么调用
   - machine truth 从哪里来
   - 当前事务与证据如何对齐
5. 旧的模板型低信号文件被合并、降级为按需生成，或直接废弃。
6. `prototype` 默认不再静默退化成固定模板产出；任何 rule/template 降级都必须显式暴露为 downgrade，而不是伪装成正常 requirement compile。
7. `prototype` 与 `qa acceptance` 都共享同一类 canonical transaction contract，至少覆盖 human sink、machine sink、runtime projection sink 与失败事务阻断语义。
8. Beacon 在 `implement / qa / gate / release` 前后，能够正式比较 promised surface 与 shipped surface，并在 drift 未收敛时阻断 pass/release。
9. `beacon prd create` 的成功路径只能对应 requirement-aware compile；generic placeholder 只能作为显式 downgrade 或失败信号，而不能算 requirement truth ready。

## 3A. Real Project Friction Signals

`storyverse-studio` 的真实运行摩擦表明，这条线不仅是“execution 文档减模板化”，还需要覆盖非代码型长任务执行面：

- 参考分析：
  - `/Users/apple/Developer/Personal/products/storyverse-studio/.beacon/analysis/memory-friction-evolution-storyverse-inkos-skill-integration-20260427.md`

提炼出的四个有效信号：

1. `implement --skill` 需要正式 contract
   - Beacon 已能接受 `--skill`
   - 但对“项目级 skill 托管一个非代码 deliverable surface”仍缺正式 contract

2. Ralph 需要长任务 batch contract
   - 长任务不能只回答“done / not done”
   - 需要批次窗口、stop_state、next_focus_window 等语义

3. workbench state sync 需要 artifact family contract
   - 某些实现不是“写一个文件”，而是一组 workbench artifacts 共同构成可恢复状态

4. fresh friction capture 需要增强
   - `memory-friction-evolution` 当前更容易吃到 stale memory artifact
   - 对新鲜 scenario friction 的捕获还不够强

这些信号说明：

- execution projection convergence 不应只覆盖传统代码交付
- 还应允许 skill-backed implement surfaces 进入同一 execution/readiness/projection 模型

## 3B. Fresh Friction Signals For R3

当前摩擦扫描还额外暴露两条必须进入 requirement delta 的信号：

1. promised-vs-shipped drift gate 缺失
   - 参考：
     - `.beacon/debug/issues/beacon-core--prd-implement-delivery-drift-gate-missing.json`
   - 说明 Beacon 已有实现与审核 evidence，但还缺一条正式 gate 来比较“承诺的交付面”与“实际已交付的 surface”。

2. PRD 生成仍可成功退化为 generic placeholder
   - 参考：
     - `.beacon/debug/issues/beacon-core--prd-create-generic-template-only.json`
   - 说明 requirement compile 的上游入口仍可能把模板壳误判为成功生成。

## 4. Scope

### In Scope

- `qa` acceptance envelope 与双写事务
- `prototype` 在人类生命周期中的非模板化收紧
- `release` readiness envelope 与 human projection 收口
- `gate` verdict 投影收口
- `help/status/doctor/archive` 的 execution 文档说明面收敛
- execution artifact taxonomy 简化
- canonical envelope / transaction / writeback 复用
- promised-surface vs shipped-surface drift gate
- PRD create 的 requirement-aware compile boundary

### Out of Scope

- 新增新的 public 一级命令
- 改写主生命周期 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- 重做 `implement` 已有 canonical baseline 体系
- 引入新的外部持久化系统替代当前 Beacon transaction / writeback 机制

## 5. Command Family Model

### 5.1 Implement Family

`implement` 继续作为已成型的参考样板源，不是本线主改造对象。

保留：

- `architecture-blueprint.md`
- deterministic implementation contract
- git workflow contract
- implementation plan

要求：

- 继续作为“canonical source -> human-readable projection”的基准模式

### 5.2 QA Family

`qa` 是本线第一优先级。

新增核心对象：

- `qa-acceptance-envelope`

必须支持：

1. 记录 requirement refs、test-case refs、evidence refs、verdict、accepted_by、transaction metadata
2. 在同一事务内三写：
   - machine sink
   - `docs/beacon/<version>/execution/qa-acceptance-<feature>.md`
   - runtime projection sink（SQLite / runtime ledger / 等价受管投影）
3. human projection 必须带：
   - public command invocation note
   - evidence source list
   - verdict summary
   - mapped AC / TC
   - operator next step

### 5.2A Prototype Family Delta

`prototype` 虽然不属于本线最初的主改造对象，但因其位于人类主生命周期中，本轮 requirement delta 需要明确补齐两条边界：

1. `prototype auto` 不得把 rule/template fallback 伪装成正常 compile 成功
2. 若 host/LLM compile 不可用或 contract 校验失败，系统必须：
   - 显式标记 downgrade
   - 或阻断 freeze / implement planning
   - 而不能继续以“固定模板产物”替代 requirement-derived prototype truth

### 5.3 Release Family

`release` 不应再维护独立平行模板体系，而应单向消费：

- requirement truth
- implementation baseline
- qa acceptance envelope
- gate verdict

保留两个主要 human 面：

1. `release/<version>.md`
2. `execution/release-readiness-<feature-or-version>.md`

### 5.4 Gate Family

`gate` 只做判定，不再承担独立 execution 模板扩张。

要求：

- 默认输出 machine verdict
- fail / warn 时可按需生成 human-readable gate summary
- 不得与 release / qa 形成新的平级 truth

### 5.5 Support Family

`help / status / doctor / archive` 统一收敛为解释层。

要求：

- 优先消费 read-model / canonical envelope / acceptance envelope
- 仅保留必要说明文档
- 不再为每个 support command 默认扩张 execution 模板文件

## 6. Artifact Taxonomy

`v1.3.9` 必须把 execution artifacts 明确分成四类：

1. **canonical envelope**
   - 唯一 truth source

2. **required human projection**
   - 必须存在，且面向操作者

3. **optional derived projection**
   - 只在 fail / warn /专项场景下生成

4. **deprecated template artifact**
   - 不再默认生成，待迁移/清退

## 7. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | `v1.3.9` 必须把 `qa / release / gate / support` 的 execution delivery 收敛到统一 artifact taxonomy，而不是继续扩张低信号模板文件。 |
| FR-002 | AC-002 | `qa` 必须在 evidence-backed verdict 后自动生成 canonical acceptance envelope。 |
| FR-003 | AC-003 | 同一笔 QA acceptance transaction 必须双写 machine sink 与 human-readable execution artifact。 |
| FR-004 | AC-004 | `release` 与 `gate` 必须消费同一 acceptance/readiness envelope，不得各自产生平级 readiness truth。 |
| FR-005 | AC-005 | human-readable projected docs 必须包含最小 public command invocation / operator usage note。 |
| FR-006 | AC-006 | `help / status / doctor / archive` 必须作为解释层复用 canonical/read-model truth，不再默认扩张模板 execution 文档。 |
| FR-007 | AC-007 | execution 目录中的旧模板型低信号文件必须被标记为保留、合并、按需生成或废弃。 |
| FR-008 | AC-008 | 全链路必须复用 Beacon 已有 transaction、writeback、canonical projection、host-native orchestration 能力，不引入平行 truth pipeline。 |
| FR-009 | AC-009 | `prototype auto` 默认不得静默回退到固定模板产出；任何 rule/template fallback 必须显式标记 downgrade 或阻断后续 freeze / implement planning。 |
| FR-010 | AC-010 | QA acceptance transaction 必须把 runtime projection sink 纳入同一事务元数据与 sink checksum 合约，而不是停留在 machine/human 二写。 |
| FR-011 | AC-011 | `status / doctor / gate / release` 必须消费与检查同一 acceptance/prototype transaction contract，在发现 transaction drift 或 failed transaction 时阻断 pass verdict。 |
| FR-012 | AC-012 | Beacon 必须把 requirement/change/release 面承诺的 operator-visible surface 与实现/审核/evidence 面已交付的 surface 做正式比对，并在 drift 未闭合时阻断 pass / release-ready verdict。 |
| FR-013 | AC-013 | `beacon prd create` 成功路径必须产出 version-aware、boundary-aware、scenario-aware requirement scaffold；generic placeholder output 只能被标记为 downgrade/fail，不能直接进入 freeze-ready 流程。 |

## 8. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | artifact-taxonomy | `v1.3.9` 明确 execution artifacts 的 canonical / required-human / optional-derived / deprecated 四层分类。 |
| AC-002 | qa-envelope | QA verdict 达成后会生成 machine-readable acceptance envelope。 |
| AC-003 | qa-dual-write | 同一笔 QA acceptance transaction 会自动生成 human-readable execution 验收文档，不再需要默认手工转写。 |
| AC-004 | release-gate-convergence | `release` 与 `gate` 消费同一 acceptance/readiness truth，并能在 machine 与 human 面上保持一致。 |
| AC-005 | operator-facing-docs | 所保留的高信号 execution human docs 都必须直接说明 public command 入口、用途、输入、输出与 next step。 |
| AC-006 | support-surface-simplification | `help / status / doctor / archive` 以解释层方式复用 read-model truth，而不是继续产生模板型 execution 文档。 |
| AC-007 | template-reduction | 至少存在一份明确迁移/清退策略，把 execution 目录里的低信号模板文档降级、合并或改为按需生成。 |
| AC-008 | capability-reuse | 新方案继续复用 Beacon 既有 writeback、transaction lineage、canonical projection 与 host-native LLM 能力。 |
| AC-009 | prototype-non-template | `prototype auto` 在 host/LLM 不可用或 contract 校验失败时，不会静默产出固定模板结果；系统会显式 downgrade，且该 downgrade 可被 review/gate 检测。 |
| AC-010 | qa-three-sink-transaction | 同一笔 QA acceptance transaction 共享 `source_hash / projection_seq / transaction_id / committed_at / sink_checksums`，并覆盖 machine sink、human sink、runtime projection sink。 |
| AC-011 | transaction-contract-consumers | `status / doctor / gate / release` 读取同一 transaction contract，并在 acceptance/prototype drift、failed transaction、missing runtime projection 时阻断 pass verdict。 |
| AC-012 | promised-vs-shipped-drift-gate | 当 PRD / change / release 面承诺了 operator-visible surface，但 implement / review / evidence 面缺少对应 shipped trace 时，Beacon 会给出正式 blocking drift verdict，而不是等到人工比对才发现。 |
| AC-013 | prd-non-generic-compile | `beacon prd create` 成功结果必须表现为 version-aware、requirement-aware PRD 骨架；若只能生成 generic placeholder，系统会显式 downgrade 或失败，不允许把占位壳误判为 requirement truth ready。 |

## 9. Risks

- 如果 QA dual-write 只写 human 文档，不写 canonical machine envelope，会继续退化成手工验收笔记。
- 如果 release / gate 继续各自维护 readiness truth，会出现“都看起来正确，但彼此不一致”的多源漂移。
- 如果 support surfaces 继续产出模板文件，execution 目录膨胀问题不会实质缓解。
- 如果清退策略过于激进，可能误删仍被真实操作者依赖的文档面。
- 如果 skill-backed implement surfaces 不进入统一 contract，长任务/非代码 deliverable 会继续停留在 Beacon 外围人工流转。
- 如果 `prototype auto` 继续静默模板回退，人类生命周期会在 `prototype` 阶段重新退化成固定模版产出，并掩盖真实 requirement compile 失败。
- 如果 QA acceptance 继续缺少 runtime projection sink，`release / gate / status / doctor` 看到的 acceptance truth 将继续存在跨面不一致风险。
- 如果 promised surface 与 shipped surface 缺少 formal gate，Beacon 仍会允许 requirement promise 漂移到实现前面，并把阻断延后到 release 末端。
- 如果 `beacon prd create` 继续把 generic placeholder 视为成功，后续 user-story / test-case / prototype 都会建立在被稀释的 requirement truth 上。

## 10. Release Guard

- `v1.3.9` requirement line 冻结前必须明确：
  - 哪些 artifacts 是 canonical
  - 哪些 human projection 必须保留
  - QA acceptance 双写事务的最小 contract
  - release / gate / support 的收敛边界
  - `prototype auto` 的 downgrade / block contract
  - acceptance/prototype transaction 的 runtime projection sink contract
  - promised-vs-shipped drift gate 的 blocking contract
  - `beacon prd create` 的 non-generic compile success contract
- 只有当 AC-001 到 AC-013 都存在对应 user-story 与 test-case 覆盖时，才能进入 implement planning。
