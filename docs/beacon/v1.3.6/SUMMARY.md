# Beacon v1.3.6 Summary

## Line Intent

- `v1.3.6` 在 `v1.3.5` wireframe freeze 的基础上，正式进入 Beacon 管理端看板与项目物料查看器的产品化线。
- 本线关注 Beacon 管理端 UI 展示项、数据视图、交互收口与 Markdown 物料只读查看体验。
- 正式真相仍然是项目本地 `docs/beacon` 与 `.beacon`；`v1.3.6` 只做消费 truth 的展示产品面。

## Upstream Dependency

- 上游 freeze line：
  - `docs/beacon/v1.3.5/prd/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- 本线实现必须基于 `v1.3.5` 产出的 wireframe package，而不是重新回到 HTML 原型叙事。

## Current Package

- 主 PRD：
  - `docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md`

## Output Boundary

- In scope：
  - Beacon 管理端首页
  - 管理总览、项目详情、运行中心、恢复诊断
  - 项目物料 Markdown 只读查看器
  - 角色化信息组织与交互收口
- Out of scope：
  - 替代 requirement truth
  - 重写 `prototype` wireframe 规范
  - HTML 高保真原型
  - 在线编辑 Markdown
