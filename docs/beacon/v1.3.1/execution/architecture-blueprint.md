# Beacon v1.3.1 架构蓝图

`v1.3.1` 的核心架构判断不是“继续向外暴露更多命令”，而是：

> **把人类主面压缩成有限闭环，把机器协作自由度保留在 Beacon 内部执行面。**

## 核心判断

Beacon 应把人机协作拆成两层：

### 1. 人类主面

人类只需要稳定理解以下闭环：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

这条闭环必须满足：

- 阶段数有限
- 阶段语义稳定
- 每个阶段都直接对应可交付文档
- 人类不需要理解内部 agent 拆解细节

### 2. 机器执行面

机器内部可以自由调度：

- `brainstorm`
- `implement-team`
- `qa-team`
- learning
- auto research
- help/status/doctor 驱动的恢复与对齐动作

但这些能力都不应增加人类的主认知负担。

## 冻结前的两道刚性前置门

### 1. 需求澄清门

如果需求文档中仍存在以下内容：

- 遗漏点
- 不清晰点
- 问号点
- 未澄清点
- 需求不明点

则 `prd` / `user-story` 不能进入冻结。

也就是说：

```text
需求不明
!=
先 freeze 再实现
```

正确顺序应是：

```text
brainstorm / review 收口问题
→ PRD / user-story 补齐
→ 无关键未决项
→ freeze
```

### 2. 技术评审门

每一个版本在进入实现前，都必须先有技术评审给出确定性实现面，而不是把这些问题推迟到编码阶段才临时决定。

最低必须明确：

- 目标 git 分支
- 是否使用 git worktree
- 隔离开发环境策略
- 实际实现服务目录
- 多仓 / monorepo / multi-service 下的服务边界

对类似 `rolo` 的多服务项目，技术评审必须明确：

- 哪些服务需要改
- 哪些服务只读参考
- 网关 / BFF / 下游服务的边界
- 各服务对应的分支 / worktree / 环境隔离方式

## v1.3.1 的架构方向

### A. `brainstorm` 内嵌到 `prd/user-story`

对人类而言：

- `brainstorm` 不一定需要是单独入口
- `prd` / `user-story` 必须持续携带 brainstorm 结果与未决问题闭环

对机器而言：

- 可以继续显式调用 `brainstorm`
- 但输出应被吸收进 `prd` / `user-story` 正式材料，而不是形成新的独立长期心智面
- 且必须顺带收口未决问题清单，不能把问号保留到 freeze 后

### B. `implement` 对人类保持单入口

对人类而言：

- 只需要执行 `implement`
- 不需要持续区分 `implement-team`、具体角色、内部 runtime

对机器而言：

- Beacon 可继续自由决定是否走 team runtime
- 只要最终交付与冻结文档对齐即可
- 但前提是技术评审已经把 branch/worktree/service scope 定清楚

### C. `qa` 对人类保持单入口

对人类而言：

- 只需要执行 `qa`
- 只关心：
  - 新发现是什么
  - 覆盖有没有提升
  - 边界是否更清晰
  - 当前能否 release

对机器而言：

- 可在 `qa` 内部继续组织 verifier / repair-handoff-writer / learning / auto research
- 但每一轮都必须回到冻结用户故事的 coverage 改善与业务闭环上

### D. 版本升级后旧物料必须可一键同步

如果 Beacon 源码更新而实际项目还停留在旧文档包：

- 必须允许按 `docs version` 指定同步
- 不应要求操作者手动重建 `.machine/user-story` 与 `.machine/qa`

### E. 极简 CLI 是架构目标，不只是文案目标

`v1.3.1` 应探索：

- 人类主命令极简化
- 机器 lane 隐藏化
- help/status/doctor 负责在需要时显式揭示复杂度

## 设计规范

1. 不增加人类必须记忆的主命令数量。
2. 不要求人类直接学习 team runtime 内部角色。
3. 任何需求不明状态不得进入 freeze。
4. 每个版本的实现前必须先完成技术评审并明确 branch/worktree/service scope。
5. QA 每轮必须体现“比上一轮更清晰”的业务边界。
6. learning / auto research 只能围绕冻结用户故事扩展覆盖，不得偏离主需求包。
7. 机器协作可以自由制定，但不得脱离人类主文档交付面。
