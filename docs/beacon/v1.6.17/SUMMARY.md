# Beacon v1.6.17 — 批次1：能力验证兑现 + 分层边界审计

## 定位

`v1.6.17` 是当前交付线。批次 1 把 v1.6.16 对抗式审查的优先推荐落地：
A1 全量 live benchmark（验证 P1 live 冒烟真实生效）、A2 分层边界审计（可维护性风险判断）。

## Program

- 批次 1（2 个 lake）：
  - `beacon-v1617-live-benchmark-verify`（全量 live benchmark 验证）
  - `beacon-v1617-layering-audit`（分层边界审计）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. eval live_skill_pass 从 1/37 提升到 ≥30/37（补齐 prompt fixture + surface 解析，真实执行）。
2. 分层审计产出 import 依赖图 + God Module 清单，判断可维护性风险。

## 发布面

- runtime: `v1.6.17`
- 正式版本面：SUMMARY / features truth 已冻结
