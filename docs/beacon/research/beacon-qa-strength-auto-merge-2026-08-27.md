# Research: QA 验证强度分析与自动合并审核增强（v1.6.14）

**日期**：2026-08-27
**目的**：自动合入（auto-merge）允许后，QA 验证必须更强——否则 agent 会把"只测 happy path 就当全绿"的变更自动合入 main。本文分析当前 QA 验证强度缺口，提出与自动合并配套的审核增强。
**前置**：`beacon-automerge-first-principles-2026-08-27.md`（自动合并部分采纳）

---

## 1. 当前 QA 验证强度的核查（证据）

### 1.1 三个 lake 的覆盖声明 vs 实际

从 v1.6.14 三个 lake 的 QA scorecard 实测：

| lake | required_scenario_families | covered_scenario_families | coverage_rate | missing |
|------|---------------------------|---------------------------|---------------|---------|
| fsm-mermaid-validate | boundary, compatibility, happy, negative, recovery | **primary** | 1.0 | [] |
| fsm-test-generation | boundary, compatibility, happy, negative, recovery | **primary** | 1.0 | [] |
| feature-map | boundary, compatibility, happy, negative, recovery | **primary** | 1.0 | [] |

**缺口**：系统声明要求 5 类场景族（boundary/negative/recovery/compatibility/happy），但实际只覆盖 `primary`，却判定 `coverage_rate=1.0`、`missing_scenario_families=[]`。

### 1.2 根因（代码级）

`beacon/utils/qa_feature.py`：

- `coverage_rate = executed_scenarios / required_scenarios`（数量覆盖，非类型覆盖）。
- `missing_scenario_families` 依赖 `exhaustiveness.missing_axes`——若 exhaustiveness 未产出轴缺口则恒为 `[]`。
- AC 级 `required_families` 仅在 TC 显式标注非 primary 的 `scenario_family` 时非空（`filtered_required_families` 排除 `primary`）。
- **v1.6.14 的 tests.md 中 TC 均未标注 scenario_family（默认 primary）** → 边界/负向/恢复/兼容四类从未被要求，QA 在只测 happy path 时即判定全绿。

### 1.3 结论

当前 QA 的 `coverage_rate=1.0` 是**数量覆盖**，不保证**类型覆盖**。在"自动合并允许"的语境下，这是不可接受的：agent 会以"6/6 TC 通过"为证据自动合入，但 6 个 TC 全是 happy path，边界/负向未验证。

## 2. 自动合并要求 QA 更强的第一性原理

允许自动合并的合法性 = 合入前验证强度 ≥ 人类把关时会投入的验证强度。若自动合并只要求"数量全绿"，而人类把关会看边界/负向，则自动合并放行的坏变更概率高于人工——**这就是"自动合并是安全违规"而非"效率提升"**。

因此自动合并的前置条件（对照 `global-boundaries.md §4.1`）必须升级：

| 前置条件 | 现状 | 自动合并要求 |
|----------|------|--------------|
| 验证前置 | QA 数量覆盖全绿 | **QA 类型覆盖全绿**（happy+negative+boundary+recovery 等 family 均有通过证据）|
| 可回滚 | git revert 可用 | 不变 |
| 可观测 | evidence/trace 落盘 | 不变 + 覆盖缺口可审计 |

## 3. QA 强度增强方案（落地）

### 3.1 补 scenario_family 标注（最小必需）

v1.6.14 的 TC 缺少 family 标注。增强：tests.md 的 TC 行按语义标注 `scenario_family`：
- 正常路径 → `happy`
- 非法/拒绝路径 → `negative`（如 TC-ILLEGAL）
- 边界/极端值 → `boundary`
- 恢复/重试 → `recovery`
- 兼容 → `compatibility`

这样 `filtered_required_families` 能识别非 primary family，QA 强制要求它们通过。

### 3.2 coverage_rate 语义升级（框架）

`coverage_rate` 从"executed/required 数量"改为**加权类型覆盖**：
```
coverage_rate = (Σ_family covered_family_weight) / Σ_family required_family_weight
```
family 缺失（负向/边界/恢复未覆盖）→ coverage_rate < 1.0 → QA 非全绿 → 自动合入被拦。

### 3.3 自动合并前置门禁（gate）

新增自动合并的 release-adjacent gate：QA passed **且** 类型覆盖达标（`required_scenario_families ⊆ covered_scenario_families`，happy+negative+boundary+recovery 至少 3 类）才允许 merge 回 main。未达标 → 退 `stop_for_repair`。

### 3.4 失败模式回归库联动

自动合并前强制命中「失败模式回归库」（v1.6.13 D3 已建）为 0，且对抗式审查（global-boundaries §5）通过——这两者已是 beacon 资产，接入合并前置即可。

## 4. 分级落地

| 批次 | 动作 |
|------|------|
| 立即（v1.6.14 补丁） | ① v1.6.14 三个 lake 的 tests.md 补 `scenario_family` 标注 + refreeze + 重跑 QA 验证类型覆盖 |
| 下一批（v1.6.15） | ② coverage_rate 语义升级（类型加权）+ 自动合并前置门禁 |
| 下下批 | ③ 失败模式回归库接入合并前置（L2 自动合并）|

## 5. 结论

- 当前 QA 强度**不足以支撑自动合并**：coverage_rate 是数量覆盖，假覆盖已发生（3 lake 全绿但只测 happy path）。
- 自动合并的安全前提是"验证强度 ≥ 人工把关投入"——必须把类型覆盖（negative/boundary/recovery）变成硬条件。
- 落地顺序：先补 family 标注（暴露真实缺口）→ 再升级 coverage_rate 语义 → 最后接入自动合并门禁。这与方法论 M1「验证 > 生成」一致：让 agent 验证得比人更全面，才值得把合入交给 agent。
