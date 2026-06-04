# 预研：UI 假通过与测试覆盖改进（v1.0.1）

- 版本：v1.0.1
- 更新时间：2026-03-03
- 范围：`beacon auto-test` / `workflow verify` / gate 执行完整性

---

## 1. 研究背景

当前 Beacon 已具备 UI guard、关键动作 guard、AC/TC/evidence gate 能力，但在真实项目执行中仍出现：

- UI 层“已通过”不等于“真实操作覆盖”
- CLI 合同测试通过，但浏览器级真实行为覆盖不足

---

## 2. 现状基线（本次实测）

### 2.1 测试总览

- 命令：`python3 -m pytest -q`
- 结果：`150 passed, 1 failed`
- 失败项：`tests/test_compat_regression_docs_examples.py::test_pyproject_should_expose_ptk_console_script`
- 原因：`pyproject.toml` 缺少 `ptk = ...` console script 兼容项

### 2.2 覆盖结构

- 总测试数：151
- 仅断言 `exit_code == 0` 的测试约：72（约 47.7%）
- `-k ui` 收集到的测试多数为 CLI/契约测试，不是浏览器真实 E2E 操作
- 当前仓库未发现 Playwright/Cypress/Selenium 类型 UI 自动化套件

### 2.3 假通过复现场景

1. **默认 UI 流程可直接通过**
   - `beacon auto-test create ui` 在 expectation 未明/断言未显式时，可出现 `ui_expectation_unknown_skipped` 并最终 `passed`

2. **关键动作可被关键词推断绕过**
   - `login/register/browse/submit-form` 可由 URL/文本命中推断为 observed
   - 缺少真实操作证据也可能显示 `missing_actions=[]`

3. **`ui_action_evidence` 未校验文件存在性**
   - 提供不存在路径时仍可能通过 key action guard

---

## 3. 根因分析

### 3.1 判定策略偏“启发式”

当前 `auto_test.py` 的 `_detect_ui_actions` 使用关键词命中推断动作，这在“无真实 UI 执行”时会引入误判空间。

### 3.2 默认策略偏宽松

`ui` 层在无显式断言/无真实命令情况下，存在 fallback 为 `passed` 的路径。

### 3.3 证据未做强验证

`ui_action_evidence` 当前仅记录映射，不强制检查 evidence 文件存在性与最小 schema。

---

## 4. v1.0.1 增强目标

### 4.1 目标

- 将“逻辑通过”升级为“证据通过”
- 降低 UI 假阳性
- 保证 Verify 阶段可审计、可复核

### 4.2 非目标

- 不在 v1.0.1 内完成全链路视觉回归平台建设
- 不改动所有历史文档，仅补齐关键验证链路

---

## 5. 方案建议（分级）

### P0（止血）

1. `auto-test create ui` 在以下条件缺失时直接 `blocked`：
   - 无 `--ui-command`
   - `--strict-ui-assertion` 但无 `--ui-assertion`
2. `--require-ui-actions` 下，必须校验 `ui_action_evidence` 文件存在
3. gate 在 `test-case/release` 严格检查 verify 产物完整性

### P1（防绕过）

1. 关键动作通过条件从“关键词推断”切换为“显式 evidence 文件”
2. `ui_action_evidence` 增加最小 schema 校验（action/run_id/status/timestamp）

### P2（补覆盖）

1. 引入真实 UI 自动化最小集（建议 Playwright）
2. 为 `login/register/browse/submit-form` 建立稳定 case 与 artifact 产出
3. 将 `-k` 过滤逐步迁移为 marker（`@pytest.mark.ui/unit/smoke`）

---

## 6. 验收建议（提炼）

- AC-001：无 `ui-command` 的 UI 验证不得判 `passed`
- AC-002：`require-ui-actions` 时缺失任一动作证据必须 `failed`
- AC-003：引用的 `ui_action_evidence` 文件不存在时必须 `failed`
- AC-004：verify 结果应可追溯到真实 layer evidence 文件

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 严格化导致短期失败率上升 | CI 震荡 | 提供迁移窗口 + 文档示例 |
| 历史脚本依赖 `-k ui` | 误筛选 | 增加 marker 并保留兼容期 |
| 团队尚未具备 UI E2E 基础设施 | 进度延迟 | 先落地 P0/P1，再引入 P2 |

---

## 8. 结论

v1.0.1 应优先完成“假通过止血 + 证据强验证”。

该增强可显著提升 Beacon 在 Verify/Gate 阶段的质量信号可信度，为后续真实 UI 自动化覆盖扩展打基础。
