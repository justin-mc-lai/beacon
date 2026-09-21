# Beacon v1.6.19 — 实现前置门阶段化 + precheck 判定内容寻址

## 定位

`v1.6.19` 接续 `v1.6.18`，修复实现前置门（`standard-execution-precheck`）的两处阻断：实现前就要求 release 产物（鸡生蛋），以及 precheck 判定被当成静态缓存、原因修好后仍显示 blocked。

## Program

- 单 lake：
  - `beacon-precheck-stage-and-bundle-freshness`（阶段化 material 必需性 + precheck 判定内容寻址）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. `build_material_audit` 增加阶段维度：实现阶段 `formal_release_present` 不再必需；release 阶段仍然必需。
2. precheck bundle 写入 `inputs_digest`（git HEAD + feature 包内容 + release 目录清单），判定与输入绑定。
3. `record_standard_execution_precheck` 对陈旧 CLI bundle 自动重跑，不再信任旧结论。

## 发布面

- release notes: `docs/beacon/v1.6.19/release/v1.6.19.md`
- execution: `docs/beacon/v1.6.19/execution/`
- source architecture: `docs/beacon/v1.6.19/source-architecture/`
- feature package: `docs/beacon/v1.6.19/features/beacon-precheck-stage-and-bundle-freshness/`
