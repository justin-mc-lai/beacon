# Beacon v1.6.12 — 测试现代化 + Goal LoopX 混合能力

## 定位

`v1.6.12` 是当前运行时交付线。本版本把存量测试资产按失败分类清单迁移到现行规范，
并把 LoopX（本地长程 agent 控制平面）最有价值的 5 项能力蒸馏进 beacon goal：
配额内核、todo 所有权、具体 user gate、有界回合预算、模式目录与事故档案。

## Program

- slug: `beacon-goal-loopx-hybrid-v1612`
- status: `program_frozen`（单 feature 一次煮干，5 个能力组 CAP-1..CAP-5）
- truth canonical: `main`
- 关联 feature：
  - `beacon-goal-loopx-hybrid-v1612`（实现并验收通过，26 个 canary 全绿）
  - `beacon-test-modernization-v1612`（696 失败迁移 truth 已冻结，批次实现进行中）

## 核心结果

1. 失败分类清单：704 个存量失败机器分类为 27 类（CSV/JSON/MD 已入库）。
2. 双轴版本规则 fail-closed：外部项目 docs 版本不得等于 runtime。
3. 全部写路径命令接入双轴守卫；doctor 诊断对塌缩/污染 fail-closed。
4. goal 长程能力强化：quota should-run、todo claim/lease/supersede、
   gate 卡片与决策缓存、有界回合预算、模式目录与事故档案。
5. 生命周期门禁保持不变（护栏验收通过，零新增失败）。

## 发布面

- runtime: `v1.6.12`（version-truth / `__init__` / pyproject / skill metadata 已同步）
- 正式版本面：SUMMARY / boundaries / source-architecture / release checklist
