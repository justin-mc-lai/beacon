# 页面线框：首页

**页面 ID**: `home`
**平台**: `Web, PC`
**优先级**: `P0`

## 页面职责
- 先回答经营判断，展示项目数、阻塞数、当前交付和介入点。

## 关联 Requirement
- `user-story`: docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md
- `prd`: docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md
- `test-case`: docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md

## 布局草图
```text
+------------------------------------------------------+
| 经营总览条 | 活跃项目 | 阻塞项目 | 活跃 runtime |
+------------------------------------------------------+
| 重点介入区                                      |
+------------------------------------------------------+
| 项目推进摘要列表                                |
+------------------------------------------------------+
| 当前交付 / 下一步                               |
+------------------------------------------------------+
```

## 关键模块
- 经营总览条
- 重点介入区
- 项目推进摘要
- 当前交付卡片
- 下一步建议

## 用户动作
- `查看管理总览`: 点击项目组合入口 -> `management-overview`
- `进入重点项目`: 点击重点项目卡片 -> `project-detail`

## 状态说明
- `ready` / 正常总览: 展示项目数、阻塞数、当前交付和下一步。
- `blocked` / 阻塞高亮: 把阻塞项目和介入点提升到首屏。
- `intervention-needed` / 需介入: 强调需要 CEO / 负责人介入的项目。
- `loading` / 加载中: 首页摘要数据仍在汇总。
- `empty` / 空状态: 当前没有受管项目。
- `error` / 错误: 摘要聚合失败，但提示可以进入详情或 doctor。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
