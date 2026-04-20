# 导航图：beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor

**Primary Entry**: `management-overview`
**Primary Exit**: `material-viewer`

## 跳转清单
- `prd` -> `user-story`: 点击跳转 (primary)
- `page-03-93da1608` -> `prd`: 点击跳转 (primary)
- `material-viewer` -> `material-document-detail`: 点击文档列表项 (drill-down)
- `material-document-detail` -> `material-viewer`: 点击返回 (return)

## 返回路径
- `material-document-detail` 返回 `material-viewer`

## 禁止跳转
- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。
- material-viewer 不直接跳 runtime-center，避免跨上下文误导。
