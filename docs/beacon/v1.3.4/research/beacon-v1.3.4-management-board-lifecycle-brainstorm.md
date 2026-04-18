# Beacon v1.3.4 管理看板与生命周期展示 Brainstorm

**主题**: `Beacon 管理看板`  
**版本**: `v1.3.4`  
**日期**: `2026-04-18`  
**状态**: `research / brainstorm`

## 1. 核心结论

`v1.3.4` 不应被做成“项目数据库后台”，而应被收敛成：

```text
Beacon 管理看板
  = 生命周期总览
  + 多项目推进管理
  + 真实 runtime 下钻

Beacon Runtime Ledger
  = 机器内部 SQLite 投影账本
```

它们的关系应是：

```text
docs/beacon + .beacon
→ Beacon Runtime Ledger
→ Beacon 管理看板
```

其中：

- `Beacon 管理看板` 面向人类
- `Beacon Runtime Ledger` 面向机器
- `docs/beacon` 与 `.beacon` 仍是正式真相层

## 2. 用户维度

### 2.1 CEO 视角

一人公司场景下，CEO 真正关心的是：

- 现在有哪些项目在推进
- 每个项目推进到哪个版本
- 每个项目当前处于需求阶段还是实现阶段
- 当前有哪些交付内容已经完成
- 当前有哪些立项工作还停留在需求物料阶段
- 哪些项目 blocked，需要介入

CEO 不关心：

- tmux pane
- worker transcript
- run 内部 prompt
- debug 原始事件流

因此 CEO 视图必须极简，只展示：

- 项目
- 当前版本
- 当前主 feature
- 当前生命周期阶段
- 总进度
- 当前交付状态
- 当前 blocker
- 下一步

### 2.2 项目负责人视角

项目负责人关心的是：

- 当前项目有哪些版本线在推进
- 当前版本有哪些主 PRD / 并行 PRD
- 需求物料是否补齐
- implement / qa 是否正在执行
- 当前 runtime 是 `single / team / ralph`
- 如果是 `team`，当前跑了多少代理、各自角色是什么
- 当前 git 分支 / worktree 是否符合规范
- 当前建议下一步是什么

项目负责人需要细节，但仍不应默认暴露机器洪流。

## 3. 场景维度

### 场景 A：CEO 每日巡检

目标：

- 快速判断多项目推进程度
- 判断是否有交付输出
- 判断是否有立项工作卡住

需要的视图：

- 多项目总览
- 当前版本与总进度
- 生命周期阶段分布
- blocked 列表

### 场景 B：项目负责人接力

目标：

- 快速理解某项目当前到底进行到哪
- 判断需求物料是否已经齐备
- 判断 implement / qa 是否正在运行

需要的视图：

- 项目详情
- 版本详情
- 并行 PRD 列表
- 当前 runtime 和建议下一步

### 场景 C：运行中观察

目标：

- 判断当前是 `single`、`team` 还是 `ralph`
- 判断是否仍在实现中 / 验收中
- 判断 team 当前运行代理数

需要的视图：

- 运行态中心
- active runs
- team agent count
- Ralph round / next_action / blocker

## 4. 业务维度

这条线的价值不是商业变现，而是管理闭环：

- 让 Beacon 从“本地材料系统”升级成“可视化项目管理系统”
- 让 CEO 能看工作推进而不看机器细节
- 让项目负责人能从总览下钻到真正可用的进度细节
- 让 git/worktree 规范从“口头约束”升级成“可见治理对象”

差异化点不在“能看到任务”，而在“能看到 Beacon 生命周期 + runtime + 交付 readiness 的统一视图”。

## 5. 技术维度

### 5.1 生命周期是主轴，不是 runtime

看板第一层必须按生命周期组织，而不是先按 `single/team/ralph` 组织。

建议正式分为两大段：

#### 需求阶段

- `prd`
- `user-story`
- `test-case`

判断目标：

- requirement materials 是否补齐
- 是否已冻结到可进入实现

#### 实现阶段

- `implement`
- `qa`
- `release`

判断目标：

- 是否已经开始实现
- 是否正在验收
- 是否具备 release readiness

### 5.2 runtime 只作为实现阶段下钻信息

`single / team / ralph` 不是生命周期阶段，它们只是实现阶段的运行模式。

正确关系应是：

```text
生命周期阶段 = implement / qa / release
runtime 模式 = single / team / ralph
```

### 5.3 子 skill 生命周期映射

子 skill 不应作为主导航，而应映射到生命周期：

#### 需求阶段子 skill

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`

#### 实现阶段子 skill

- `beacon-implement`
- `beacon-qa`
- `beacon-release`

#### 支持观察层

- `beacon-help`
- `beacon-status`
- `beacon-doctor`

因此看板应该先展示：

- 当前生命周期阶段
- 当前建议下一步
- 当前建议 skill

而不是直接展示 skill 列表。

## 6. 体验维度

### 6.1 对外总览：极简人类心智

首页卡片只显示：

- 项目名
- 当前版本
- 当前主 feature
- 并行 PRD 数
- 生命周期阶段
- 总进度
- 当前状态
- runtime 模式
- 下一步

其中：

- 如果当前是 `team`
  - 只显示：`team · 4 agents`
- 如果当前是 `ralph`
  - 只显示：`ralph · round 3`

不直接展开 worker 细节。

### 6.2 对内详情：可下钻但不失控

点进项目或 feature 后，再展示：

1. 生命周期面板
2. 需求物料面板
3. 实现运行态面板
4. git / worktree 规范面板
5. session / artifact refs 面板

### 6.3 对外总进度的正确口径

总进度不应按 run 数量或 agent 数量计算，而应按生命周期 readiness 计算。

建议对外只显示 4 个状态：

- `需求中`
- `实现中`
- `验收中`
- `待发布 / 已完成`

可附带一个简化百分比，例如：

- `20%`：PRD 已建，story/test-case 未齐
- `45%`：需求物料齐，implement 中
- `75%`：implement 完成，qa 中
- `100%`：release ready / released

## 7. 价值维度

### 对 CEO 的价值

- 多项目推进程度一眼可见
- 当前交付内容和立项工作可分开看
- 哪些项目卡在需求，哪些卡在实现，哪些接近交付，一目了然

### 对项目负责人的价值

- 能看清项目的当前情况
- 能看懂版本与并行 PRD 的关系
- 能判断需求物料是否补齐
- 能知道 implement / qa 是否在跑
- 能看到具体 runtime 细节，但不是默认被淹没

## 8. 风险维度

| 风险 | 概率 | 影响 | 应对方案 |
|------|------|------|----------|
| 看板重新暴露机器洪流 | 中 | 高 | 默认只给生命周期摘要，runtime 只在详情层展开 |
| runtime 抢走生命周期主轴 | 中 | 高 | 首页按阶段展示，single/team/ralph 只作为实现阶段附加信息 |
| CEO 视图与项目负责人视图混成一套 | 高 | 高 | 明确双层视图：总览层给 CEO，详情层给项目负责人 |
| 并行 PRD 与主 PRD 关系不清 | 中 | 中 | 在版本详情中显式区分主 PRD / 并行 PRD |
| git/worktree 只记录不治理 | 中 | 高 | 把规范状态做成正式卡片与告警，不只是 metadata |

## 9. 收敛后的展示模型

### 9.1 首页：Beacon 管理看板

只展示有限项目管理信息：

- 项目
- 当前版本
- 当前主 feature
- 并行 PRD 数
- 生命周期阶段
- 总进度
- runtime 模式
- 当前状态
- 下一步

### 9.2 项目详情

展示：

- 项目信息
- 当前版本线
- 主 PRD / 并行 PRD
- 当前生命周期阶段
- 需求物料补齐情况
- 当前活跃 run
- git/worktree 规范状态

### 9.3 运行态详情

只在下钻层展示：

- `single`
  - active run
  - host runtime
  - blocker
- `team`
  - active agents
  - roles
  - worker statuses
- `ralph`
  - round_count
  - failure_streak
  - next_action
  - current_blocker

## 10. 建议写回 v1.3.4 主 PRD 的收敛点

1. `Beacon 管理看板` 必须以生命周期为主轴展示项目状态。
2. 看板必须区分 CEO 总览视图与项目负责人详情视图。
3. 需求阶段必须明确展示：
   - PRD 是否补齐
   - user-story 是否补齐
   - test-case 是否补齐
4. 实现阶段必须明确展示：
   - 是否正在 implement
   - 是否正在 qa
   - 当前 runtime 模式
5. `single / team / ralph` 必须作为实现阶段下钻信息，而不是生命周期阶段。
6. 子 skill 必须通过生命周期映射展示，而不是作为主导航暴露。
7. git 分支 / worktree 必须作为正式治理对象进入详情视图。

## 11. 一句话收口

`Beacon 管理看板` 应该是：

> 一个按 Beacon 生命周期组织的多项目管理看板。  
> 对外给 CEO 极简进度与交付视图；  
> 对内给项目负责人版本、并行 PRD、需求物料补齐情况、实现 runtime、git/worktree 规范和下一步建议。
