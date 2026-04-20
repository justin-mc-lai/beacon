# 页面线框：项目详情

**页面 ID**: `project-detail`
**平台**: `Web, PC, App`
**优先级**: `P0`

## 页面职责
- 成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。

## 关联 Requirement
- `user-story`: docs/beacon/v1.3.4/user-story/beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md
- `prd`: docs/beacon/v1.3.4/prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md
- `test-case`: docs/beacon/v1.3.4/qa/test-cases/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md

## 布局草图
```text
+------------------------------------------------------------+
| 项目头部摘要 | 当前版本 | git/worktree                    |
+------------------------------------------------------------+
| 主 PRD / 并行 PRD | 生命周期 / 总进度                     |
+------------------------------------------------------------+
| prd / user-story / test-case / prototype 冻结状态         |
+------------------------------------------------------------+
| 最近交付 | 下一步 | 推荐 skill | runtime 摘要             |
+------------------------------------------------------------+
```

## 关键模块
- 项目头部摘要
- 版本与分支信息
- 主 PRD 与并行 PRD
- 需求物料闭环状态
- 最近交付与下一步
- 运行态摘要卡

## 用户动作
- `查看运行中心`: 点击运行态摘要 -> `runtime-center`
- `查看恢复诊断`: 点击恢复诊断入口 -> `recovery-diagnostics`
- `查看项目物料`: 点击文档查看入口 -> `material-viewer`
- `返回管理总览`: 点击返回 -> `management-overview`

## 状态说明
- `ready` / 可接力: 版本、PRD、需求闭环和下一步信息完整。
- `requirement-missing` / 需求缺口: PRD / user-story / test-case 存在缺口。
- `draft` / 需求草稿: 需求已建立但未冻结。
- `frozen` / 需求冻结: 需求链与 prototype 都已冻结。
- `runtime-active` / 运行中: 存在 single / team / ralph 运行摘要。
- `loading` / 加载中: 项目详情正在聚合。
- `error` / 错误: 详情聚合失败但给出恢复链路。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
