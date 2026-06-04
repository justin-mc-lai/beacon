# Beacon v1.3.4 一人公司运营视角看板模型 Brainstorm

**主题**: `Beacon 管理看板`  
**版本**: `v1.3.4`  
**日期**: `2026-04-18`  
**状态**: `research / brainstorm`

## 1. 核心结论

一人公司不是“只有一个视角”，而是同一个人同时承担两种角色：

- `CEO`
  - 关心多项目推进、交付、立项、阻塞
- `项目负责人`
  - 关心某个项目当前版本、物料补齐、运行态、治理状态

因此 `Beacon 管理看板` 不能做成一层平铺后台，而应是：

```text
首页 = CEO 汇总层
项目详情 = 项目负责人层
运行态抽屉 = runtime 下钻层
```

这三层都必须由 `Beacon Runtime Ledger` 提供投影数据，但都不得越过 `docs/beacon` 与 `.beacon` 的真相边界。

## 2. 一人公司运营模型

### 2.1 对上汇报面

CEO 只需要回答四个问题：

- 现在有哪些项目在推进
- 每个项目推进到哪里
- 当前有哪些交付已经产出
- 当前有哪些立项工作卡住

这意味着首页不应展示：

- tmux pane
- worker transcript
- raw debug event
- 全量本地 session 内幕

### 2.2 对下执行面

项目负责人需要回答六个问题：

- 当前项目推进到哪个版本
- 当前主 PRD 和并行 PRD 是什么
- `prd / user-story / test-case` 是否补齐
- 当前是否在 `implement / qa / release`
- 当前 runtime 是 `single / team / ralph`
- 当前 git / worktree / session 引用是否正常

这意味着项目详情页必须可下钻，但默认仍要极简。

## 3. 页面模型

### 3.1 首页：CEO 汇总层

每个项目卡片只建议显示：

- 项目名
- 当前版本
- 当前主 feature
- 生命周期阶段
- 总进度
- 当前交付状态
- 当前 blocker
- 下一步

必要时补两个轻量信号：

- 并行 PRD 数
- runtime 摘要

其中 runtime 摘要只能压缩成：

- `single`
- `team · 4 agents`
- `ralph · round 3`

### 3.2 项目详情：项目负责人层

项目详情页建议固定为五块：

1. 项目信息
2. 版本与 PRD 轨道
3. 需求物料补齐情况
4. 实现阶段运行态
5. git / worktree / session 治理状态

项目详情页必须能明确区分：

- 主 PRD
- 并行 PRD
- 当前主推进 feature
- 当前 blocker 属于需求阻塞还是执行阻塞

### 3.3 运行态中心：runtime 下钻层

runtime 下钻不是生命周期导航，而是实现阶段详情。

展示规则：

- `single`
  - active run
  - linked host session
  - blocker
- `team`
  - agent count
  - role list
  - worker status
  - linked artifacts
- `ralph`
  - round count
  - failure streak
  - next action
  - blocker

## 4. 生命周期与子 skill 展示模型

### 4.1 生命周期主轴

首页与项目详情必须先按生命周期组织：

- 需求阶段
  - `prd`
  - `user-story`
  - `test-case`
- 实现阶段
  - `implement`
  - `qa`
  - `release`

`single / team / ralph` 只属于实现阶段的运行模式。

### 4.2 子 skill 映射

子 skill 不应成为主导航，而应成为“当前建议动作”：

| 生命周期状态 | 推荐 skill | 向人类表达 |
|---|---|---|
| PRD 缺失或未冻结 | `beacon-prd` | 补需求定义 |
| user-story 未齐 | `beacon-user-story` | 补用户故事 |
| test-case 未齐 | `beacon-test-case` | 补验收用例 |
| implement 进行中 | `beacon-implement` | 继续实现 |
| qa 进行中 | `beacon-qa` | 继续验证 |
| release 前检查 | `beacon-release` | 做发布判断 |
| 状态不明或阻塞 | `beacon-help` / `beacon-status` / `beacon-doctor` | 先诊断与恢复 |

## 5. 信息分层规则

### 5.1 可以默认给人看的信息

- 项目
- 版本
- feature
- 生命周期阶段
- 总进度
- 当前交付状态
- blocker
- 下一步
- runtime 摘要
- 需求物料补齐状态
- git / worktree 规范状态

### 5.2 只能在详情中给人看的信息

- 主 PRD / 并行 PRD 列表
- team roles
- Ralph round / next action
- Codex / Claude session 引用
- artifact refs

### 5.3 不应作为默认展示的信息

- 完整 transcript
- 全量 raw events
- tmux pane 噪音
- host 内部调度细节
- 私有凭证路径

## 6. Host Session 展示原则

`Beacon 管理看板` 可以展示 `Codex`、`Claude` 的 session 引用，但只能展示有限元数据：

- host runtime
- session id / thread id
- linked run
- linked feature
- transcript ref
- started / ended
- 当前状态

不应把宿主本身的完整 session 系统搬进 Beacon。

## 7. Git / Worktree 治理原则

项目负责人真正需要的不是“看见 branch 名称”，而是“看见是否合规”。

因此详情页应优先显示：

- 当前 repo / worktree 绑定
- 预期分支规则
- 当前是否 dirty
- 当前是否符合 Beacon 规范
- 当前是否需要切换或整理

`rolo` 这类多服务项目中，这一层尤其重要，因为同一版本推进可能同时关联多个 child repo。

## 8. 排除边界

本版本必须明确排除：

- `omc`
- `omx`
- Beacon 外兼容运行时

原因不是它们不存在，而是：

- 它们不属于 Beacon 的正式生命周期
- 它们不属于 Beacon 的正式运行态模型
- 把它们并入看板会破坏产品边界

正确口径是：

> `Beacon 管理看板` 只展示 Beacon-owned 或 Beacon-observed 的项目运行态。  
> 非 Beacon runtime 即使与项目同机共存，也不进入正式总览。

## 9. 对实现的约束

对 `Beacon Runtime Ledger` 的约束：

- 必须以项目、版本、feature、生命周期为主键思路
- 不得先以 worker / pane / event 为主入口
- 必须允许从本地 truth 重建

对 `Beacon 管理看板` 的约束：

- 必须首页先给 CEO 汇总
- 必须详情页再给项目负责人
- 必须把 runtime 作为下钻层
- 必须把 skill 作为推荐动作，而不是主导航

## 10. 一句话收口

`Beacon 管理看板` 在一人公司场景下，本质上不是“内部管理后台”，而是：

> 一个先给 CEO 看多项目推进，再给项目负责人看项目细节，并在实现阶段允许下钻 runtime 的 Beacon 生命周期管理面。
