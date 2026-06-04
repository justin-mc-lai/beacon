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

### F. 极简主面必须对应 host-visible skills

如果 `v1.3.1` 只在文档里说“人类只记 6+3”，但在 Codex / Claude 中仍然只有一个宽泛 `beacon` 入口，这条线就没有真正落地。

因此还需要：

1. 一个 umbrella skill：
   - `using-beacon`
2. 九个 public host-visible skills：
   - `beacon-prd`
   - `beacon-user-story`
   - `beacon-test-case`
   - `beacon-implement`
   - `beacon-qa`
   - `beacon-release`
   - `beacon-help`
   - `beacon-status`
   - `beacon-doctor`
3. `brainstorm`、`implement-team`、`qa-team` 继续保留在隐藏 machine lanes

### G. 同一版本必须支持多个并行 feature package

`v1.3.1` 不应继续隐含“一个版本只对应一份 PRD”的单体假设。

更小、更稳的模型是：

- `version` 是交付容器
- `feature package` 是并行工作单元
- 每个 `feature package` 通过同一个 `feature slug` 串起：
  - `prd/<slug>.md`
  - `user-story/<slug>.md`
  - `qa/test-cases/<slug>.md`
  - `execution/technical-implementation-<slug>.md`

也就是说：

```text
同一 docs/beacon/archive/v1.3.1/
  可以同时存在 feature-a / feature-b / feature-c
  但每个 feature 仍保持自己的一对一文档链
```

这样做的好处是：

- 不增加新的公开命令
- 不引入新的目录心智
- 直接复用 Beacon 当前按 `feature slug` 写文件的实现
- 让并行需求包变成正式 contract，而不是隐式碰运气

### H. `change` 文档必须成为独立交付面

`implementation-summary` 与 `technical-implementation` 已经能记录实现细节，
但它们更偏执行摘要和技术归档，不是人类交付视角下的“本次版本改了什么”。

因此 `v1.3.1` 需要补一层更轻的独立 change 面：

- feature 级 `change/<feature-slug>.md`
- version 级 `change/<version>.md`

它们的目标不是替代技术归档，而是回答：

- 新增了什么
- 删除 / 收敛了什么
- 修复 / 校正了什么
- 这些变化由哪些 feature package 贡献
- release 当前到底在放行什么

## 设计规范

1. 不增加人类必须记忆的主命令数量。
2. 不要求人类直接学习 team runtime 内部角色。
3. 任何需求不明状态不得进入 freeze。
4. 每个版本的实现前必须先完成技术评审并明确 branch/worktree/service scope。
5. QA 每轮必须体现“比上一轮更清晰”的业务边界。
6. learning / auto research 只能围绕冻结用户故事扩展覆盖，不得偏离主需求包。
7. 机器协作可以自由制定，但不得脱离人类主文档交付面。
8. 同一个版本必须允许多个并行 feature package 共存。
9. 每个 feature package 必须通过相同 `feature slug` 串起自己的 `prd / user-story / test-case`。
10. 交付完成后必须有独立 `change` 文档，不要求人类自己去拼装 technical archive。
