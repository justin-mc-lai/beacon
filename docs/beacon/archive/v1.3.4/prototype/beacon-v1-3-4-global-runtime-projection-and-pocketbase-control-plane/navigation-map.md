# 导航图：beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

**Primary Entry**: `home`
**Primary Exit**: `project-detail`

## 跳转清单
- `home` -> `management-overview`: 点击项目组合入口 (primary)
- `home` -> `project-detail`: 点击重点项目卡片 (primary)
- `management-overview` -> `project-detail`: 点击项目行/卡片 (primary)
- `management-overview` -> `home`: 点击首页导航 (return)
- `project-detail` -> `runtime-center`: 点击运行态摘要 (drill-down)
- `project-detail` -> `recovery-diagnostics`: 点击恢复诊断入口 (drill-down)
- `project-detail` -> `management-overview`: 点击返回 (return)
- `runtime-center` -> `project-detail`: 点击返回 (return)
- `recovery-diagnostics` -> `project-detail`: 点击返回 (return)

## 返回路径
- `management-overview` 返回 `home`
- `project-detail` 返回 `management-overview`
- `runtime-center` 返回 `project-detail`
- `recovery-diagnostics` 返回 `project-detail`

## 禁止跳转
- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。
- material-viewer 不直接跳 runtime-center，避免跨上下文误导。
