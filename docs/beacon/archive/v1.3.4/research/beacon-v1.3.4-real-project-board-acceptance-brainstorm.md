# Beacon v1.3.4 真实项目并板验收 Brainstorm

**主题**: `Beacon 管理看板真实项目并板验收`  
**版本**: `v1.3.4`  
**日期**: `2026-04-18`  
**状态**: `research / brainstorm`

## 1. 核心收敛

`v1.3.4` 的验收不能只证明“SQLite 能写、PocketBase 能看”，而必须证明：

- 4 个真实项目可以同时被纳入 Beacon 管理看板
- 显示语义不漂移
- Beacon 源码项目本身也能作为受管项目自并板、自演进、自验收

目标并板项目：

- `rolo`
- `slow_uni_bmtop`
- `shopxo_canada`
- `beacon`

## 2. 用户维度

### CEO 视角要确认什么

- 四个项目都在板上
- 每个项目阶段、进度、blocker、交付状态都看得懂
- 不会把 runtime 噪音当成项目进度

### 项目负责人视角要确认什么

- 点进任一项目都能看到版本、主 PRD、并行 PRD、材料补齐、runtime、git/worktree、下一步
- 不同项目类型不会被错误套用同一模板

## 3. 场景维度

### 场景 A：四项目总览巡检

需要同时看到：

- `rolo`：多服务 workspace
- `slow_uni_bmtop`：单仓 + 已物化 debug issue
- `shopxo_canada`：有运行态但无 debug feed
- `beacon`：源码自演进项目

### 场景 B：项目详情语义校验

每个项目点进去都应能解释：

- 当前在哪个版本线
- 当前主推进 feature 是什么
- 材料齐不齐
- 当前下一步是什么

### 场景 C：debug feed 三态校验

必须能稳定区分：

- `materialized_issue`
- `runtime_feed_only`
- `no_debug_feed`

### 场景 D：Beacon 自并板

Beacon 不能只管别人，不管自己。

需要确认：

- Beacon 项目能作为普通 project 被注册
- Beacon 的 `v1.3.4` 主 PRD、自身运行态、自身 doctor/qa/release 信号可被看板消费

## 4. 业务维度

这组验收的价值不是“多 4 个 demo 项目”，而是证明：

- Beacon 是真正的多项目管理层
- 不同 project shape 都能被统一吸收
- 自己能管自己，说明模型没有只为外部项目定制

## 5. 技术维度

### 5.1 四项目验收矩阵

| 项目 | 期望 project_kind | debug 状态 | 关键验收点 |
|---|---|---|---|
| rolo | multi_repo_workspace | runtime_feed_only | 不能误判成单服务；branch/worktree/source priority 正确 |
| slow_uni_bmtop | single_repo | materialized_issue | 单仓注册正确；issue 能显示 |
| shopxo_canada | single_repo 或 project-local 单根模型 | no_debug_feed | 无 debug feed 但仍显示运行态与 team/handoff |
| beacon | single_repo | Beacon 自身真实状态 | 自并板、自演进、自验收 |

### 5.2 显示正确性的最小定义

显示正确不是“有卡片就算过”，而是：

- project_kind 正确
- lifecycle 正确
- debug 三态正确
- runtime 摘要正确
- 详情下钻正确
- 推荐下一步合理

## 6. 体验维度

### 首页

首页必须能在一眼内看出四个项目差异，不允许所有卡片长得一样、信息一样。

### 详情页

详情页必须能解释“为什么这个项目显示成现在这样”，否则一切聚合都不可信。

## 7. 价值维度

这组场景的核心价值是：

- 让 Beacon 从“理论上可多项目”升级成“真实项目上已经并板成功”
- 让 `beacon` 自身成为最强验收样本

## 8. 风险维度

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| rolo 被误判为单服务 | 高 | 高 | 强制校验 multi_repo_workspace + child repo 证据 |
| shopxo_canada 因无 debug feed 被误判成无状态 | 高 | 中 | 把 debug 三态单独建模 |
| beacon 项目被特殊分支旁路处理 | 中 | 高 | 自并板验收不得使用特殊硬编码 |
| 首页只能看见 runtime 噪音 | 中 | 高 | 强制 lifecycle-first 首页结构 |

## 9. 建议补入主 PRD 的场景结论

1. 把四项目并板写成正式 AC，而不是仅作为验证建议。
2. 把 Beacon 自身写成一等受管项目，而不是隐含前提。
3. 把“显示正确性”定义成 project_kind/lifecycle/debug/runtime/next-step 五件套。
4. 把真实项目并板通过，写成 `v1.3.4` 的正式通过门槛。

## 10. 补充验收场景包

### 场景 E：首页降噪

目标不是把机器日志搬到首页，而是让人类一眼看懂：

- 这 4 个项目分别处于哪条生命周期主轴
- 哪个项目正在推进
- 哪个项目卡住
- 哪个项目需要立项补材料

因此首页验收必须确认：

- 生命周期优先于 runtime 洪流
- blocker 优先于 session 细节
- 下一步优先于内部调度过程

### 场景 F：详情页解释性

详情页不能只显示聚合字段，还要能解释来源：

- 为什么 `rolo` 被判定为 `multi_repo_workspace`
- 为什么 `shopxo_canada` 虽然无 debug feed，但仍有项目状态
- 为什么 `beacon` 当前显示 `v1.3.4` 主线
- 为什么系统推荐当前 skill / next step

### 场景 G：断库后重新并板

如果 SQLite 或 PocketBase 丢失，验收仍必须通过：

- 重新扫描 4 个真实项目
- 重新构建最小 project registry
- 恢复首页卡片与详情下钻
- 不要求恢复历史 projection 主键
- 但要求恢复当前可管理状态

### 场景 H：Beacon 自身不走特殊通道

`beacon` 自身并板的验收重点不是“能显示”，而是：

- 不依赖硬编码 project key
- 不依赖写死版本名
- 不依赖隐藏字段旁路
- 与其他项目一样走 truth -> projection -> board 路径

### 场景 I：多项目差异可见但心智极简

四项目并板后，必须同时满足两件事：

- 差异存在
  - `rolo` 看起来比 `slow_uni_bmtop` 更像 workspace
  - `shopxo_canada` 看起来是“有状态但没 debug feed”
  - `beacon` 看起来是“自演进项目”
- 心智不炸
  - CEO 不需要先理解 tmux / run event / source priority
  - 项目负责人只在详情页才看 git/worktree/runtime 细节
