# Beacon v1.3.6 Execution Index

## Current Focus

- 基于 `v1.3.5` wireframe freeze artifact 实现 Beacon 管理端产品面。
- 把看板页面、项目详情、运行中心、恢复诊断和 Markdown 只读查看器做成正式产品承诺。
- 保持与 `v1.3.4` runtime projection / PocketBase 控制面兼容，但不回退到 HTML 原型探索阶段。

## Execution Tracks

1. 上游对齐：
   - 以 `v1.3.5` wireframe 包作为页面、路由和状态说明的冻结输入。
2. 产品化实现：
   - 实现首页、总览、详情、运行中心、恢复诊断、文档查看器的信息架构与交互。
3. 交付约束：
   - 所有页面只消费 projection / truth，不在 UI 层改写正式真相。
