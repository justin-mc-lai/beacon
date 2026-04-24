# 导航图：Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking

**Primary Entry**: `home`
**Primary Exit**: `material-viewer`

## 跳转清单
- `home` -> `management-overview`: 点击项目组合入口 (primary)
- `home` -> `project-detail`: 点击重点项目卡片 (primary)
- `management-overview` -> `project-detail`: 点击项目行/卡片 (primary)
- `management-overview` -> `home`: 点击首页导航 (return)
- `project-detail` -> `runtime-center`: 点击运行态摘要 (drill-down)
- `project-detail` -> `recovery-diagnostics`: 点击恢复诊断入口 (drill-down)
- `project-detail` -> `material-viewer`: 点击文档查看入口 (drill-down)
- `project-detail` -> `management-overview`: 点击返回 (return)
- `runtime-center` -> `project-detail`: 点击返回 (return)
- `runtime-center` -> `management-overview`: 点击面包屑 (return)
- `recovery-diagnostics` -> `project-detail`: 点击返回 (return)
- `recovery-diagnostics` -> `runtime-center`: 点击运行态关联 (drill-down)
- `material-viewer` -> `project-detail`: 点击返回 (return)
- `material-viewer` -> `material-document-detail`: 点击文档列表项 (drill-down)
- `material-document-detail` -> `material-viewer`: 点击返回 (return)

## 返回路径
- `management-overview` 返回 `home`
- `project-detail` 返回 `management-overview`
- `runtime-center` 返回 `project-detail`
- `runtime-center` 返回 `management-overview`
- `recovery-diagnostics` 返回 `project-detail`
- `material-viewer` 返回 `project-detail`
- `material-document-detail` 返回 `material-viewer`

## 禁止跳转
- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。
- material-viewer 不直接跳 runtime-center，避免跨上下文误导。
