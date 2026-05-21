# Beacon 调研：执行材料严肃性与版本治理恢复

> 日期：2026-05-21
> 调研版本线：`v1.4.8`
> 状态：仅调研
> 范围：执行文档严肃性、版本治理漂移，以及生成型执行材料契约的恢复要求
> 来源引用：
> - `https://mp.weixin.qq.com/s/PkVYEf1QbaAqtx4Qbpknsw`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.5/execution/architecture-blueprint.md`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.5/execution/index.md`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.5/execution/current-state-service-map.md`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.5/execution/service-slice-map.md`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/branch-governance-msq-part1-dossier.md`
> - `/Users/apple/Developer/Company/rolo/docs/beacon/v2.0.0/execution/revision-delta-msq-part1-dossier.md`
> - `docs/beacon/global-boundaries.md`
> - `docs/beacon/v1.4.7/SUMMARY.md`
> - `docs/beacon/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`

---

## 1. 调研目标

本文分析一个已经在真实项目中暴露的 Beacon 失败模式：

- 执行材料生成不再足够严苛
- 版本与治理信息发生漂移或碎片化
- 过去存在的固定文档生成契约没有被可靠强制执行

本调研的目标是明确：`v1.4.8` 必须恢复什么，才能让执行材料重新成为严格治理下的交付物，而不是可有可无或只生成一部分的说明笔记。

本文仅为调研材料。
它不是 canonical truth。

## 2. 触发证据

### 2.1 外部工程信号

引用文章：

- `Harness Engineering：从"驯马"到"造车"——我用这套驾驭工程让AI稳定输出了23000行代码`

提供了一个与 Beacon 直接相关的工程经验：

> 长时间 AI 工程输出是否稳定，不只取决于模型能力，也取决于外围执行系统是否足够严格。只要执行系统松散、记忆碎片化、护栏弱、状态不可见，输出就会快速失稳。

文章中的 7 部分框架本身不是 Beacon truth，但它强化了一个核心判断：

```text
可靠输出不是靠更用力地提问；
可靠输出来自更严格的运行 harness。
```

这对 Beacon 很关键，因为执行材料是 Beacon harness 的一部分，不是装饰性文档。

### 2.2 真实 Beacon 项目的回退信号

`rolo` 项目的 `v1.3.5` 与 `v2.0.0` 展示了一个具体的契约回退。

#### `v1.3.5` 证据

`/Users/apple/Developer/Company/rolo/docs/beacon/v1.3.5/execution/architecture-blueprint.md` 中包含明确的 `Implementation Delivery Host` 区块，里面包括：

- feature baselines
- revision
- branch
- writable services
- baseline refs

它还把执行上下文绑定到：

- `current-state-service-map.md`
- `service-slice-map.md`

这说明 `v1.3.5` 仍然把执行材料当作结构化的 delivery host，而不是一堆按 feature 分散生成的笔记。

#### `v2.0.0` 证据

到了 `v2.0.0`，execution 文件夹仍然存在，但出现了这些问题：

- `execution/architecture-blueprint.md` 缺失
- `execution/index.md` 缺失
- 执行面碎片化成多个 feature 级笔记，例如：
  - `branch-governance-msq-part1-dossier.md`
  - `revision-delta-msq-part1-dossier.md`
  - `miniapp-integration-msq-part1-dossier.md`
  - `miniapp-page-state-machine-msq-part1-dossier.md`

branch governance 笔记确实保留了一些 branch / worktree 事实，但它只是一个独立补丁式笔记。
它不再位于一个权威的 execution host contract 之内。

关键回退是：

```text
执行事实仍然存在，
但 execution host contract 不再保证这些事实应该住在哪里。
```

这正是 Beacon 必须视为系统失败的严肃性丢失。

## 3. 收敛诊断

问题不是简单的“少生成了一个文件”。

更深层的问题是：

> 当 execution-host truth 不完整时，Beacon 没有持续 fail closed。

这会制造四类失败模式。

### 3.1 位置漂移

过去应当出现在固定文档里的执行事实，现在可能出现在任意 side document 中。

结果：

- 人不知道该去哪里找
- 自动化不能依赖一个稳定来源
- 项目团队开始发明本地约定

### 3.2 表面碎片化

branch facts、writable services、service slices、baseline refs 不再以一个连贯的 execution-host projection 出现。

结果：

- 读者只能靠人工拼接恢复真相
- 错误更容易发生

### 3.3 治理降级

当 `architecture-blueprint.md` 过去带有固定区块时，branch / service 信息缺失更容易暴露。
一旦 host contract 消失，同样的缺失就不再像 failure，而会被误看成“正常差异”。

结果：

- Beacon 从 governed generator 静默降级成 permissive note emitter

### 3.4 抗漂移失败

Beacon 声称命令会读取固定文档、固定输出。
如果这些固定输出不再被保证，那么 command-to-document determinism 就被破坏。

结果：

- execution truth 不再强可寻址
- 后续阶段可能读取到陈旧或局部材料

## 4. 为什么这是 Harness Engineering 问题

文章中的实践经验在这里是适用的：

- 只靠行为规则不够
- 只靠记忆不够
- 只靠 prompt 不够
- 运行 harness 必须定义：
  - 哪些 artifact 必须存在
  - 它们住在哪里
  - 哪些字段必须出现
  - 缺失时阻断什么

映射到 Beacon：

```text
execution materials 是 harness 的一部分
```

所以如果：

- architecture host 文件是可选的
- delivery service facts 散落在多个地方
- branch governance 脱离 canonical execution host

那就说明 Beacon 的 harness 没有被充分定义。

## 5. 最强恢复主张

本调研中最强的恢复主张是：

> Beacon `v1.4.8` 应恢复严格的 execution-host contract，并把 execution-host surface 缺失视为 execution-facing flows 的 fail-closed 条件。

这比“改进文档”更强。
它意味着：

- execution host surface 重新成为必需项
- 它们的位置重新变得确定
- 它们的最低 schema 重新显性化
- 下游流程在这些材料缺失时必须阻断

## 6. 必须恢复的契约

Beacon 应为每条版本线恢复固定的 execution-host package。

最低要求如下。

### 6.1 必需文件

- `execution/index.md`
- `execution/architecture-blueprint.md`

对于 takeover 或 multi-service 项目，还应要求：

- `execution/current-state-service-map.md`
- `execution/service-slice-map.md`

### 6.2 `architecture-blueprint.md` 中的必需 host 字段

execution host 应重新包含 `Implementation Delivery Host` 区块，或等价的 canonical block，至少包含：

- version
- feature count
- transaction id
- source hash
- registered feature baselines
- revision
- canonical branch 或 per-service branch mapping
- writable services
- baseline refs

### 6.3 takeover 必需绑定

对于 takeover 项目，blueprint 还必须绑定：

- current state service map
- service slice map
- 每个 feature 的显式 delivery change surface

### 6.4 branch governance 集成

per-feature branch governance 笔记仍然可以存在。
但它不能成为 canonical execution branch facts 的唯一位置。

execution host 必须包含或链接到唯一权威的 branch / worktree mapping surface。

## 7. 必须 fail closed 的条件

Beacon `v1.4.8` 应把以下情况视为 execution-host failure：

- `execution/architecture-blueprint.md` 缺失
- 必需 host section 缺失
- execution-bound feature 缺少 feature baseline entries
- multi-service delivery 缺少 branch / worktree mapping
- writable services 未声明
- takeover 项目在需要时缺少 current-state-service-map 或 service-slice-map

这些至少应阻断：

- implement planning
- execution readiness
- downstream delivery projection generation

## 8. 命令恢复方向

如果 Beacon 仍然期望命令读取固定文档，那么命令行为应遵守：

1. 先解析 execution-host contract
2. 校验必需文件与必需区块存在
3. 当 execution-host truth 不完整时 fail closed
4. 之后才允许生成或更新下游 execution notes

换句话说：

```text
当 execution host contract 已经损坏时，
不要让下游 execution docs 继续生成。
```

## 9. 推荐的 `v1.4.8` Feature 方向

本调研建议新增一个恢复导向的 feature line，例如：

- `beacon-v1.4.8-execution-host-contract-recovery-and-fail-closed-generation`

它的范围应包括：

- 恢复必需的 execution host 文件
- 恢复 delivery-host truth 的确定性位置
- 恢复按版本校验 execution-host schema
- 当 host truth 不完整时恢复 fail-closed generation

这不应被表述为文档润色任务。
它是治理恢复任务。

## 10. 调研结论

核心判断是：

> Beacon 当前的问题不只是生成文档弱，而是 execution-harness 严肃性被削弱。

`rolo v1.3.5` 证明 Beacon 曾经有更强的 execution-host contract。
`rolo v2.0.0` 说明这个 contract 现在可以退化成碎片化 note generation，而且没有强阻断。

因此 `v1.4.8` 应把执行材料严肃性作为一等恢复目标。

配套的子 skill 闭环调研进一步扩展了这个结论：

```text
只恢复 execution host 还不够；
每个人类面的子 skill 也必须声明自己的 material effect，
否则它仍然可能生成 advisory output 并 fail open。
```

## 11. 下一步路由

推荐下一跳：

1. `beacon-change`
2. 冻结 execution-host recovery contract
3. 编译进入：
   - PRD
   - user-story
   - test-case
4. 之后再实现 generator 与 validator 变更
