# Beacon v1.3.8 PRD Executable Diagram Truth Layer Analysis

**Date**: 2026-04-24  
**Method**: 基于 Rolo 真实项目 `memory-friction-evolution-prd-state-machine-guidance-20260424` 报告、当前 `prd -> implement -> qa` 传导链与 `v1.3.7` truth discipline 做收敛分析  
**Purpose**: 判断 Beacon 是否应在复杂业务 feature 上，把 PRD 从叙述型说明升级为带 branch-flow / state-machine / decision-priority 的实现约束真相面。

---

## 1. Summary

这条调研的核心结论是：

- 对复杂业务 feature，PRD 只写段落不够。
- 当一个 feature 同时牵涉多状态轴、多服务联调、归属与奖励口径切换时，PRD 必须带图层。
- 图层的价值不是“文档更完整”，而是：
  - freeze 前把语义定清
  - implement plan 能读到
  - QA 能覆盖到

一句话：

> `v1.3.8` 应该把复杂业务 PRD 升级成“实现约束真相面”，而不是停留在“可读说明书”。

---

## 2. Problem Statement

当前复杂 feature 的主要风险不是没人写 PRD，而是：

- PRD 没有表达状态迁移
- PRD 没有表达分支优先级
- PRD 没有表达独立状态轴

结果就是：

- 后端压缩字段语义
- 前端用文案反推逻辑
- settlement / read-model / H5 各自补语义
- freeze 之后仍要靠口头解释维持一致

---

## 3. Direct Evidence

来自 Rolo report 的直接结论：

1. 复杂业务需求不能只靠叙述型 PRD。  
2. PRD 中加入 branch flow 和 state machine 后，truth 从“可读”升级成“可执行”。  
3. Beacon 下一版应主动引导，而不是等用户手工补图。  

对应材料：

- `docs/beacon/v1.3.3/prd/partner-rule-adjustment.md`
- `docs/beacon/v1.3.3/user-story/partner-rule-adjustment.md`
- `docs/beacon/v1.3.3/execution/architecture-blueprint.md`

---

## 4. Research Direction

### 4.1 方向 A: 保持 narrative PRD，不新增图层要求

优点：

- 最简单

缺点：

- 无法稳定约束复杂业务实现
- implement 和 QA 继续只能读 acceptance text

结论：

- 不够。

### 4.2 方向 B: PRD 在复杂业务条件下推荐图层

优点：

- 不强迫所有 feature 复杂化
- 只在多状态、多分支、多服务 feature 上开启

缺点：

- 需要一套复杂业务识别规则

结论：

- 推荐。

### 4.3 方向 C: PRD 强制图层，但 implement / QA 不吸收

优点：

- 表面上改善 PRD 质量

缺点：

- 价值停留在文档层
- 无法进入交付内核

结论：

- 不够。

---

## 5. Proposed v1.3.8 Scope

### 5.1 PRD Diagram Truth Layer

对复杂业务 feature，PRD 推荐至少输出：

- branch-flow
- state-machine
- decision-priority

推荐命令形态：

```bash
beacon prd create "<feature>" --include-diagrams branch-flow,state-machine,decision-priority --json
```

### 5.2 Freeze-Readiness Check

`beacon-brainstorm` 或 freeze readiness 应显式检查：

- 是否存在多状态轴
- 是否需要 state machine 才能 freeze
- 是否存在跨服务语义切换

### 5.3 State Axis Modeling

PRD / user-story 应支持显式拆出状态轴，例如：

- relation
- sale
- ownership
- eligibility / permanent binding

### 5.4 Diagram Propagation

图层不是只给人看，还应被：

- implementation-plan 吸收为 tasks / review gates
- QA 吸收为 branch / transition coverage

---

## 6. Boundaries

`v1.3.8` 不应：

- 要求所有 feature 都画复杂图
- 把图层当作美化文档的装饰
- 只改 PRD，不改 implement / QA 传导

`v1.3.8` 应：

- 在复杂业务下主动提示图层
- 让图层进入交付内核
- 把复杂语义从口头解释前移到 freeze 前

---

## 7. Preliminary Conclusion

这条演进值得做，而且它本质上不是“PRD 增强”，而是“truth modeling 增强”：

- 把复杂业务的判定路径显式化
- 把复杂状态迁移前移到 freeze 前
- 把图层继续传导到 implement 和 QA

## 8. Recommended Next Step

基于这份调研，下一步适合起一条正式 feature：

- `beacon-v1.3.8-prd-executable-diagram-truth-layer`

## Source Refs

- `/Users/apple/Developer/Company/rolo/.beacon/analysis/memory-friction-evolution-prd-state-machine-guidance-20260424.md`
- `docs/beacon/v1.3.7/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.7/execution/boundaries.md`
- `skills/beacon/beacon-brainstorm/SKILL.md`
