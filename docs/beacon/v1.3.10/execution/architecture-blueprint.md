# Beacon v1.3.10 Architecture Blueprint

## 主题

把真实项目中的 monorepo / repo-binding / branch-governance 风险收口成可事务化的项目版本元信息治理能力。

## 核心结构

1. canonical metadata envelope
2. human sink projection
3. machine sink projection
4. sqlite runtime projection
5. resolved metadata view for prompt/runtime/support surfaces

## 执行边界

- 核心 metadata 只表达 topology、service binding、participating services、per-service allowed working branch
- 项目级协作流通过项目内 skill / policy 扩展
- requirement package dual-write gate 属于全局执行门禁，而不是单一 feature 内部约定

## 关键门禁

- `doctor metadata verify`
- `doctor verify-materials --strict`
- `help/status` requirement package remediation routing
- `real-project-validation` remediation proof capture
