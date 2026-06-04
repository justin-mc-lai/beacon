# 导航图：Beacon Operator Workbench And Board Launcher

**Primary Entry**: `recovery-diagnostics`
**Primary Exit**: `review-surface`

## 跳转清单
- `recovery-diagnostics` -> `portfolio-board`: 点击跳转 (primary)
- `portfolio-board` -> `execution-board`: 点击跳转 (primary)
- `execution-board` -> `feature-detail`: 点击跳转 (primary)
- `feature-detail` -> `run-detail`: 点击跳转 (primary)
- `run-detail` -> `review-surface`: 点击跳转 (primary)

## 返回路径

## 禁止跳转
- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。
- material-viewer 不直接跳 runtime-center，避免跨上下文误导。
