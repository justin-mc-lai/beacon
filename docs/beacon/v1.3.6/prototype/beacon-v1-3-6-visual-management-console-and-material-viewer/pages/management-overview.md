# 页面线框：管理总览

**页面 ID**: `management-overview`
**平台**: `Web, PC`
**优先级**: `P0`

## 页面职责
- 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。

## 关联 Requirement
- `user-story`: docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md
- `prd`: docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md
- `test-case`: docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md

## 布局草图
```text
+--------------------------------------------------------------------+
| 筛选栏 | 版本 | 阶段 | 健康态 | debug | 推荐 skill                |
+--------------------------------------------------------------------+
| 项目注册表：项目名 / 类型 / 当前版本 / 主 feature / 进度 / 下一步 |
+--------------------------------------------------------------------+
```

## 关键模块
- 筛选与排序条
- 项目注册表
- 阶段分布摘要
- 风险与调试摘要
- 推荐 skill 区

## 用户动作
- `进入项目详情`: 点击项目行或卡片 -> `project-detail`
- `返回首页`: 点击首页导航 -> `home`

## 状态说明
- `ready` / 多项目已加载: 密集展示多项目当前状态。
- `filtered` / 已筛选: 按阶段、版本、健康态筛选项目。
- `empty` / 无项目: 没有任何受管项目进入注册表。
- `loading` / 加载中: 项目注册表正在聚合。
- `error` / 错误: 总览聚合失败但保留恢复提示。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
