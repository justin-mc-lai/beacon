# 导航图：beacon-v1.3.6-visual-management-console-and-material-viewer

**Primary Entry**: `home`
**Primary Exit**: `material-viewer`

## 跳转清单
- `management-overview` -> `project-detail`: 点击跳转 (primary)
- `material-viewer` -> `material-document-detail`: 点击文档列表项 (drill-down)
- `material-document-detail` -> `material-viewer`: 点击返回 (return)

## 返回路径
- `material-document-detail` 返回 `material-viewer`

## 禁止跳转
- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。
- material-viewer 不直接跳 runtime-center，避免跨上下文误导。
