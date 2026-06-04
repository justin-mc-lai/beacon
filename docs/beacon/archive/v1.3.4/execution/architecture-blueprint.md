# Beacon v1.3.4 Architecture Blueprint

## 目标

把 Beacon 从“项目内运行态完整、机器级全局态缺失”的状态，收敛为：

```text
Truth Layer
  = docs/beacon/<version> + .beacon
Projection Layer
  = Beacon Runtime Ledger (machine-local sqlite)
Visual Control Plane
  = Beacon 管理看板 (PocketBase admin/ui/api/backup)
```

核心规则：

> 全局层只做 projection，不做 truth ownership。

## 1. 正式命名与排除边界

本版本应统一使用以下命名：

- `Beacon Runtime Ledger`
  - 机器内部 SQLite 投影账本
  - 保存项目注册、生命周期投影、运行态索引、异常观测
- `Beacon 管理看板`
  - 由 PocketBase 承载的人类可视化层
  - 提供 CEO 总览、项目负责人详情、备份与查询入口

明确排除：

- `omc`
- `omx`
- Beacon 外兼容运行时
- 宿主内部完整交互系统

这些对象可以在项目本地独立存在，但不属于 `v1.3.4` 的 Beacon 正式投影或展示范围。

## 2. Truth Layer

`v1.3.4` 必须继续承认以下本地面才是正式真相：

- `docs/beacon/<version>/`
- `.beacon/`
- 目标项目中的 `AGENTS.md` / `CLAUDE.md` managed context

它们分别承载：

- requirement / version package / release closure
- run-scoped evidence / local state / execution artifacts
- project-level inherited constraints

SQLite 与 PocketBase 不得改写这些文件的正式含义。

## 3. Projection Layer

机器内部 SQLite 应作为全局运行态索引层，至少覆盖：

- `projects`
- `git_scopes`
- `feature_packages`
- `feature_lifecycle`
- `stage_material_status`
- `runs`
- `run_workers`
- `run_targets`
- `run_events`
- `git_workspace_bindings`
- `host_sessions`
- `artifact_refs`
- `health_snapshots`

其职责是：

1. 注册这台机器上接入 Beacon 的项目。
2. 识别项目是 `single_repo` 还是 `multi_repo_workspace`。
3. 聚合同一项目下的多个 git scope。
4. 聚合 `implement` / `qa` / `team` / `ralph` 等关键运行态。
5. 对 stale / failed / blocked / drifted 状态做统一观察。

## 4. Beacon 管理看板

PocketBase 在 `v1.3.4` 中应被视为 `Beacon 管理看板` 的承载层：

- `Beacon Runtime Ledger` 的可视化控制面
- 低门槛后台与 REST API
- 实时订阅与事件看板
- `pb_data` 级备份入口

但它不应被视为：

- requirement truth
- release truth
- project-local evidence authority
- 新的人类主流程入口

正确关系应是：

```text
local truth
→ projector / sync
→ Beacon Runtime Ledger
→ Beacon 管理看板
```

而不是：

```text
operator edits PocketBase
→ PocketBase rewrites Beacon truth
```

## 5. Project Modeling

`v1.3.4` 必须正式支持两类项目：

### `single_repo`

适用示例：

- `slow_uni_bmtop`

特征：

- 项目根就是 git repo
- `docs/beacon` 与 `.beacon` 聚焦于一个仓
- 全局层主要承担跨项目观察、run 历史、异常聚合

### `multi_repo_workspace`

适用示例：

- `rolo`

特征：

- workspace root 不是单一 git repo
- root 仍有 `docs/beacon` 与 `.beacon`
- 多个 child repo 承载不同服务
- 一个 Beacon run 可能同时关联多个 git scope / branch / service

因此 project registry 不能等同于 git repo registry。

## 6. 运营视图模型

`Beacon 管理看板` 必须服务同一个人的两种工作角色，而不是把所有机器细节平铺出来：

### CEO 总览层

优先回答：

- 现在有哪些项目在推进
- 每个项目处于需求阶段还是实现阶段
- 当前交付内容是什么
- 当前立项工作卡在哪
- 哪些项目 blocked

默认字段应收敛为：

- 项目名
- 当前版本
- 当前主 feature
- 生命周期阶段
- 总进度
- 当前交付状态
- blocker
- 下一步

### 项目负责人详情层

优先回答：

- 当前版本线和主 PRD / 并行 PRD
- requirement materials 是否补齐
- implement / qa / release 是否在跑
- runtime 是 `single`、`team` 还是 `ralph`
- git / worktree 是否符合规范
- Codex / Claude session 是否有可追溯引用

### Runtime 下钻层

只在需要时展开：

- `single`
  - active run
  - host runtime ref
- `team`
  - agent count
  - role / status
- `ralph`
  - round count
  - failure streak
  - next action
  - blocker

## 7. Rebuild Contract

`v1.3.4` 必须把“可丢失、可重建”写成正式合同：

1. SQLite 丢失时，允许从 `docs/beacon` 与 `.beacon` 重建最小项目态。
2. PocketBase 丢失时，只影响可视化与管理面，不影响项目继续推进。
3. 同步延迟或失败时，project-local workflow 不得被阻断。
4. 重建过程中必须保留缺失原因、时间戳与不确定性标记，不能伪造已知状态。

## 8. Command Surface Constraint

`v1.3.4` 不应新增新的公开一级主命令来暴露这套能力。

更合理的演进方式是把它们吸收到：

- `status`
- `doctor`
- machine-internal sync / projector routines

也就是说：

> 对人类来说，这是 Beacon 更强的可观测性；不是一套新的数据库产品。

## 9. 完成判定

`v1.3.4` 可以进入实现的前提是：

1. 全局层与 truth layer 的边界已经讲清。
2. `single_repo` 与 `multi_repo_workspace` 都有可落地建模。
3. `Beacon Runtime Ledger` 与 `Beacon 管理看板` 的命名和职责已经统一。
4. `omc` / `omx` 等 Beacon 外运行时已经被明确排除。
5. PocketBase 的能力被正确约束在 control plane。
6. 断库重建和降级合同明确，不会反向绑架项目主流程。
