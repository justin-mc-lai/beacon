# 页面线框：运行中心

**页面 ID**: `runtime-center`
**平台**: `Web, PC`
**优先级**: `P1`

## 页面职责
- 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。

## 关联 Requirement
- `user-story`: docs/beacon/archive/v1.3.5/user-story/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `prd`: docs/beacon/archive/v1.3.5/prd/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md
- `test-case`: docs/beacon/archive/v1.3.5/qa/test-cases/beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor.md

## 布局草图
```text
+-------------------------------------------------------------+
| 模式切换：single | team | ralph                            |
+-------------------------------------------------------------+
| agent/session 引用 | linked run | artifact refs            |
+-------------------------------------------------------------+
| next_action | blocker | recent_result                      |
+-------------------------------------------------------------+
```

## 关键模块
- 运行态摘要头部
- single / team / ralph 模式切换
- agent/session 引用
- artifact 与 linked run
- 最近结果与 blocker

## 用户动作
- `返回管理总览`: 点击面包屑 -> `management-overview`

## 状态说明
- `single-active` / Single 运行: 展示单进程执行摘要和 linked run。
- `team-active` / Team 运行: 展示 agent 数、角色、状态和 host session metadata。
- `ralph-active` / Ralph 闭环: 展示 round_count、failure_streak、next_action、blocker。
- `idle` / 无活跃运行: 当前没有任何 active runtime。
- `loading` / 加载中: 运行态数据仍在读取。
- `error` / 错误: 运行态投影异常，需要回到诊断页。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
