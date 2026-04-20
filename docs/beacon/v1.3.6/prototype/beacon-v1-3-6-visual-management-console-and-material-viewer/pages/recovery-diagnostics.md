# 页面线框：恢复诊断

**页面 ID**: `recovery-diagnostics`
**平台**: `Web, PC`
**优先级**: `P2`

## 页面职责
- 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。

## 关联 Requirement
- `user-story`: docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md
- `prd`: docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md
- `test-case`: docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md

## 布局草图
```text
+----------------------------------------------------+
| truth 来源说明：docs/beacon + .beacon              |
+----------------------------------------------------+
| degraded / rebuild / doctor 诊断卡                 |
+----------------------------------------------------+
| 恢复步骤 | 风险提示                                |
+----------------------------------------------------+
```

## 关键模块
- truth 来源说明
- degraded / rebuild / doctor 诊断卡
- 恢复步骤
- 风险提示

## 用户动作
- `返回项目详情`: 点击返回 -> `project-detail`
- `前往运行中心`: 点击运行态关联 -> `runtime-center`

## 状态说明
- `healthy-warning` / 健康但预警: 当前系统可用但存在恢复风险提示。
- `degraded` / 降级: SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。
- `rebuild-suggested` / 建议重建: 投影层需要重建。
- `doctor-suggested` / 建议 doctor: 推荐执行 doctor 修复上下文。
- `loading` / 加载中: 诊断结果仍在采集。
- `error` / 错误: 诊断页本身无法完成聚合。

## 实现接力备注
- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。
- 实现阶段必须回链本页与 navigation-map / wireframe-summary。
