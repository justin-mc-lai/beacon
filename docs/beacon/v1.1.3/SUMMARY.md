# Beacon v1.1.3 Summary

**主题**: Beacon 边界收口与 CLI 分层重构（Draft）  
**状态**: Requirement Materials Only  
**日期**: 2026-03-19

---

## 本版目标

v1.1.3 不先扩功能，而是先收口 Beacon 的产品边界与命令边界，回答四个问题：

1. Beacon vNext 到底负责什么，不负责什么。
2. 现有 40 个子命令哪些应该保留、迁出或废弃。
3. 根 README 应如何改写，才能回到单一事实源与当前能力口径。
4. CLI 应如何按层重构，避免 core / labs / bridge 长期混写。

## 当前结论

- Beacon 的核心定位应收口为：**evidence-first 的需求交付闭环内核**。
- Beacon 不应继续膨胀成通用 PM 模板大全。
- Beacon 不应与 `gstack` 的浏览器/角色化开发工作流重叠。
- Beacon 不应与 `symphony` 的 issue/workspace/agent scheduler 重叠。
- `docs/beacon/<version>/` 继续是唯一主源；本版文档全部只落该目录。

## 来自 rolo 实战高强度使用的 4 个改进点（新增）

rolo 的实际使用表明，Beacon 在复杂多服务仓库里最容易被高强度使用的不是“模板生成”，而是“版本化交付真相管理”。

因此，v1.1.3 还应吸收以下 4 个直接改进点：

1. **一个发布线只保留一个正式版本根目录**  
   版本应该代表发布单元，不应该再同时承担“主题容器”语义。

2. **正式交付文档与 raw evidence 强制分层**  
   人类决策文档应与 JSON / log / export / xlsx 等原始证据分开，避免执行层被机器文件淹没。

3. **每个正式版本包强制满足最小闭环**  
   `SUMMARY.md / execution/boundaries.md / prd / user-story / qa/test-cases / release` 必须齐全，缺任一项都不应视为完整 Beacon workflow 交付包。

4. **`docs/beacon/` 是长期事实源，`.beacon/` 只是运行时临时状态**  
   对 docs-heavy 的企业项目，当前版本真相必须优先读取 `docs/beacon/<version>/`，而不是依赖易过期的本地 runtime 状态。

> 这 4 点不是额外扩题，而是 Beacon 在真实项目中要保持“唯一决策面 / 唯一验收面 / 唯一发布面”所必须具备的文档治理能力。

## 当前阶段记录（新增）

- 当前 `v1.1.3` 的定位仍是：**需求草稿阶段 / requirement materials only**。
- 现阶段重点是把问题、边界、优先级和实施顺序定义清楚。
- 因此，相比 `v1.1.2` 代码实现仍存在明显缺口是**正常现象**，不应被误判为“需求稿失败”或“版本偏差”。
- 当前版本的正确判断标准不是“是否已实现”，而是：
  1. 调整主线是否被明确；
  2. 优先级是否被排序；
  3. 后续实现是否能按最短路径推进。

## 实施阶段（按最短路径补充）

### 必须先做

1. 彻底去掉 `docs/product` 主路径语义
2. 把最小闭环变成 `init / doctor / gate / report` 的代码规则
3. 把版本根目录语义做成可检查的治理规则
4. 把 formal docs vs raw evidence 做成明确目录契约
5. 真正收口 CLI surface
6. 真正收口 NL router
7. 把 `docs/beacon > .beacon` 的长期事实源优先级写进状态系统

### 其次再做

8. 补“代码迁移矩阵”
9. 同步 `README / SKILL / AGENTS / help / reason codes`
10. 再考虑 active version index 之类增强项

## 闭环设计合理性复审（新增）

基于再次按第一性原理审视，v1.1.3 当前可以确认：

### 设计上合理的部分
- `think -> user-story -> prd -> [prototype] -> test-case` 作为需求收敛主链是合理的；
- `verify` 与 `gate` 分离是合理的：前者生成证据，后者做阻断判断；
- `docs/beacon/<version>/` 作为唯一长期主源的方向是正确的；
- core / support / labs / bridge 的产品分层方向是正确的。

### 仍然需要补齐的闭环问题
1. 闭环状态机还不是单一真相；
2. `implementation` 阶段语义仍然过于模糊；
3. `release` 的语义需要明确为 **post-gate action**，而不是 workflow 内部阶段；
4. `doctor / report / gate` 的职责边界还需进一步产品化；
5. 单一主源、最小闭环、长期事实源优先级仍未完全进入代码行为。
6. 实现阶段还缺少顶层 `review spec|quality` 机制，无法像 OPSX 一样把“发现偏差 -> 回写物料 -> 继续推进”做成正式闭环。

> 结论：v1.1.3 的闭环方向是对的，但当前仍属于“文档先行、代码待收口”的需求草稿阶段。

## 本版文档物料

### 主链文档

- `docs/beacon/v1.1.3/user-story/beacon-vnext-boundary-consolidation.md`
- `docs/beacon/v1.1.3/prd/beacon-vnext-boundary-consolidation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-vnext-boundary-consolidation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-vnext-boundary-consolidation.ac-test-matrix.json`

### 原型深化物料

- `docs/beacon/v1.1.3/user-story/beacon-prototype-professional-ui-generation.md`
- `docs/beacon/v1.1.3/prd/beacon-prototype-professional-ui-generation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-prototype-professional-ui-generation.md`
- `docs/beacon/v1.1.3/qa/test-cases/beacon-prototype-professional-ui-generation.ac-test-matrix.json`

### 执行层文档

- `docs/beacon/v1.1.3/execution/boundaries.md`
- `docs/beacon/v1.1.3/execution/command-consolidation-matrix.md`
- `docs/beacon/v1.1.3/execution/readme-rewrite-draft.md`
- `docs/beacon/v1.1.3/execution/cli-layering-refactor-plan.md`

## 版本说明

- 本稿是 **v1.1.3 文档层草案**。
- 本稿不等同于已经完成 `pyproject.toml` / `beacon/__init__.py` / `SKILL.md` 的运行时版本升级。
- 本稿的目标是先统一边界与叙事，再指导后续 CLI/代码收口实现。
