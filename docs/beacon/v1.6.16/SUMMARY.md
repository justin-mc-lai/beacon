# Beacon v1.6.16 — 批次1：能力验证补强（对抗式审查落地）

## 定位

`v1.6.16` 是当前交付线。批次 1 把 2026-08-27 对抗式审查的 5 个缺口补齐：
P1 skill 级 live 冒烟（37 skill 全跑真实执行）、P2 eval 案例集外部锚点、
P3 gate 判定独立裁判、P4 失败模式库 5→20+、P5 bad-merge 率基线。

## Program

- 批次 1（5 个 lake）：
  - `beacon-v1616-live-skill-smoke`（skill live 冒烟）
  - `beacon-v1616-eval-external-anchor`（eval 外部锚点）
  - `beacon-v1616-gate-independent-judge`（gate 独立裁判）
  - `beacon-v1616-failure-mode-expansion`（失败模式库扩充）
  - `beacon-v1616-bad-merge-baseline`（bad-merge 基线）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. eval live_skill_pass 从 1/37 → ≥30/37（真实执行，非 surface 检查）。
2. eval 案例集引入外部锚点（真实失败/社区标准），来源可追溯。
3. coverage_rate 等关键 gate 值由独立裁判重算比对，偏差可审计。
4. 失败模式目录从 5 条扩到 20+ 条，支撑对抗式审查。
5. auto-merge 后 bad-merge 率基线数据可对比。

## 发布面

- runtime: `v1.6.16`（框架代码改动：agent_eval_kit / 独立裁判 / 目录 / git 统计）
- 正式版本面：SUMMARY / features truth 已冻结
