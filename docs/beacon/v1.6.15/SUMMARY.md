# Beacon v1.6.15 — 批次1：QA 类型覆盖升级 + 自动合并前置门禁

## 定位

`v1.6.15` 是当前交付线。批次 1 把「自动合并安全化」落地为框架能力：
L1 coverage_rate 从数量覆盖升级为类型加权（非浏览器场景也展开类型 family），
L2 自动合并前置门禁（类型覆盖 + 失败模式回归 + 对抗式审查三条件）。
另含 v1.6.14 补丁：三个 lake 的 scenario_family 标注 + 重跑 QA 暴露真实类型缺口。

## Program

- 批次 1（2 个新 lake + v1.6.14 补丁）：
  - `beacon-v1615-coverage-type-weighted`（QA 类型覆盖加权）
  - `beacon-v1615-automerge-gate`（自动合并前置门禁）
  - v1.6.14 补丁：`story_scenarios.py` 非浏览器 family 展开 + 3 lake 重跑 QA
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. coverage_rate 类型加权：只测 happy path → rate < 1.0，QA 列出 missing_families。
2. 非浏览器（contract/docs/unit）场景展开类型 family（happy+negative+boundary），不再 primary-only。
3. 自动合并前置门禁：类型覆盖 + 失败模式回归命中 0 + 对抗式审查通过，三条件全过才允许合并 main。
4. release 人类 gate 保持不变（不自动打 tag/部署/发布）。

## 发布面

- runtime: `v1.6.15`（框架代码改动：story_scenarios.py / qa_feature.py / coverage.py + 新 gate）
- 正式版本面：SUMMARY / features truth 已冻结
