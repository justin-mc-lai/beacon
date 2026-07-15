---
program_slug: beacon-qa-capability-hardening-v164
version: v1.6.4
plan_mode: auto
scope_mode: full_parity
lake_or_ocean: 海
program_phase: P3
p4_ack: false
source_refs:
  - https://developer.chrome.com/docs/extensions/how-to/test/end-to-end-testing
intent: 让 beacon qa 具备 Chrome 扩展 e2e 验收能力 + qa skill 健壮性（truth/业务状态机边界 QA、单例→端到端置信度链、验收置信度真实有效、及时修 bug）+ 第一性原理/对抗式审查方法论
---

# Feature Graph — v1.6.4 QA Capability Hardening

## 第一性原理拆解

回到根本问题：**beacon qa 当前能验证什么，缺什么？**

- 现状：9 个 non-browser QA 层 + 1 个 browser_e2e 层（通用 Web e2e，非扩展）
- 缺口根因：
  1. browser runner 不支持加载扩展包（结构性）
  2. 无 truth→业务状态机→边界用例 管道（结构性）
  3. QA 层间无置信度传递（unit pass ≠ e2e pass 不可见）
  4. QA finding 无 defect 分类/修复路由（闭环断裂）
  5. 方法论（第一性/对抗式）未写入 skill 行为契约

每个缺口是独立可验证单元 → 5 个 feature。拓扑序由依赖关系决定。

## 多 Feature 清单（拓扑序）

### Phase 1 — `beacon-qa-chrome-extension-e2e-v164`
**解决**：browser_e2e 层无法验收 Chrome 扩展（结构性 gap 最深，用户原话重点）。

Scope：
- `BROWSER_RUNNER_REGISTRY` 增 `playwright-extension` runner（或扩展现有 playwright runner）
- adapter 透传 `--load-extension` / `--headless=new`
- extension ID 固定与管理（key 生成或 manifest key field）
- `chrome-extension://<id>/` 页面导航支持
- popup 测试（`action.openPopup()` 或 tab-ID URL 注入）
- service worker target 检测（`waitForTarget(type==='service_worker')`）
- `BROWSER_EVIDENCE_AXES` 增 extension 维度（`extension_page` / `service_worker` / `popup`）
- fail-closed：扩展加载失败 / ID 不匹配 / SW 未就绪 → block，不记 false pass

AC 草案（8 条）：
- AC-001 runner 注册 `playwright-extension` + 默认命令生成
- AC-002 `--load-extension` 透传到 adapter
- AC-003 `--headless=new` 扩展模式
- AC-004 extension ID 固定（manifest key 或 computed）
- AC-005 `chrome-extension://` 页面导航
- AC-006 popup 测试（openPopup / tab 注入）
- AC-007 service worker target 检测 + SW 终止测试
- AC-008 fail-closed：加载失败/ID 不匹配/SW 未就绪 block
- AC-009 evidence axes 增 extension 维度

依赖：无（独立基础设施）。源 parity：Chrome 官方 e2e 文档。

### Phase 2 — `beacon-qa-coverage-confidence-chain-v164`
**解决**：单例→端到端置信度不可见（层间 gap 无传递）。

Scope：
- QA 层置信度传递模型（unit→interface→...→browser_e2e 的 coverage 继承/缺口）
- 置信度链 gap 检测（哪一层断链）
- `qa_acceptance` 增 confidence_chain 字段
- 与 Phase 1 的 browser_e2e 集成（e2e 置信度依赖下层）

AC 草案（5 条）：
- AC-001 置信度传递模型定义
- AC-002 层间 gap 检测
- AC-003 confidence_chain 字段 + projection
- AC-004 断链 block（不假交付）
- AC-005 与 browser_e2e 集成

依赖：Phase 1（browser_e2e 是链终点）。

### Phase 3 — `beacon-qa-business-state-machine-v164`
**解决**：无 truth→业务状态机→边界用例管道。

Scope：
- truth.md AC → FSM 提取（状态集 + 转换集 + 边界态 + 不可达态）
- 状态覆盖 QA 模型（转换覆盖 / 边界态 / 不可达态拒绝）
- `qa_acceptance` 增 state_machine_coverage 字段
- 边界用例自动推导（从 FSM 生成边界 TC）

AC 草案（6 条）：
- AC-001 truth→FSM 提取（状态/转换/边界/不可达）
- AC-002 状态覆盖模型
- AC-003 state_machine_coverage 字段 + projection
- AC-004 边界态覆盖
- AC-005 不可达态拒绝（fail-closed）
- AC-006 与 confidence_chain 集成（状态覆盖是置信度输入）

依赖：Phase 2（状态覆盖纳入置信度链）。

### Phase 4 — `beacon-qa-defect-repair-loop-v164`
**解决**：QA finding 无 defect 分类/修复路由，闭环断裂。

Scope：
- QA finding → defect 分类（bug / truth-drift / coverage-gap / execution-gap）
- `qa_acceptance` 增 `repair_route` + `defect_classification` 字段
- defect 路由：bug→implement, truth-drift→change, coverage-gap→truth, execution-gap→implement
- 修复后回归 QA 闭环

AC 草案（5 条）：
- AC-001 defect 分类 taxonomy
- AC-002 `repair_route` / `defect_classification` 字段
- AC-003 路由规则（4 类 defect → 对应 harness）
- AC-004 修复后回归 QA 触发
- AC-005 闭环 evidence 链

依赖：Phase 2/3（defect 来自各 QA 层 finding）。

### Phase 5 — `beacon-qa-methodology-contract-v164`
**解决**：第一性原理 + 对抗式审查未写入 skill 行为契约。

Scope：
- `global-boundaries.md` §5 skill 哲学边界增「第一性原理」+「对抗式审查」条款
- qa skill 行为契约增「交付前对抗式审查」强制（列 3-5 翻车点 + 验证证据）
- planner-review 增 adversarial lane（已有 multi-reviewer，强化对抗式）

AC 草案（4 条）：
- AC-001 global-boundaries §5 增方法论条款
- AC-002 qa skill 契约增对抗式审查强制
- AC-003 planner-review adversarial lane
- AC-004 「列 3-5 翻车点 + 验证证据」evidence 形状

依赖：无（cross-version 哲学，但归 v1.6.4 落地）。注意：此 feature 改 global-boundaries（cross-version canonical），scope 需在 truth 显式声明。

## 拓扑序

```
Phase 1 (chrome-ext-e2e) ──┐
                           ├──> Phase 2 (confidence-chain) ──> Phase 3 (state-machine) ──┐
                           │                                                                ├──> Phase 4 (defect-repair-loop)
                           └────────────────────────────────────────────────────────────────┘
Phase 5 (methodology) — 独立，可与任一 phase 并行
```

执行序：1 → 2 → 3 → 4，Phase 5 可与 Phase 1 并行。

## deferral_ledger（待 P4 ack 拍板）

| ID | 项 | user_decision |
|---|---|---|
| UD-1 | Phase 顺序 1→2→3→4，Phase 5 并行 | pending |
| UD-2 | Phase 1 runner 命名：新增 `playwright-extension` vs 扩展现有 `playwright` | pending |
| UD-3 | Phase 5 改 global-boundaries 是否需 cross-version change（影响 v1.6.3） | pending |
| UD-4 | 每 phase 独立 freeze 还是批量 | pending（建议独立，HARD GATE） |

## P4 ack 要求

P4 ack 前，本 feature-graph 需经 `beacon-pln-review`（P2）intent-parity 校验。ack 后按拓扑序逐个路由 `beacon-gen-truth`，每 feature 走完整 Truth Freeze Intent Loop R0-R7。

## Source Parity Inventory (Phase 1 — Chrome extension e2e)

Source: Chrome official e2e testing docs (已拉取).

| Source capability | Beacon 现状 | Parity gap | Phase 1 AC |
|---|---|---|---|
| `--load-extension` 加载扩展包 | ❌ 零代码 | 结构性 | AC-002 |
| `--headless=new` 扩展模式 | ❌ | 缺 | AC-003 |
| 固定 extension ID | ❌ | 缺 | AC-004 |
| `chrome-extension://` 页面导航 | ❌ | 缺 | AC-005 |
| popup 测试 (openPopup / tab 注入) | ❌ | 缺 | AC-006 |
| service worker target 检测 + 终止测试 | ❌ | 缺 | AC-007 |
| 工具: Puppeteer/Playwright/Selenium/WebDriverIO | ✅ playwright in registry (无默认命令) | runner 命令缺 | AC-001 |
| evidence axes (function/ui/ux/compatibility/session/state_data) | ✅ 有 | 无 extension 维度 | AC-009 |

Parity matrix verdict: **结构性 parity gap**——beacon browser_e2e 是通用 Web e2e，非扩展 e2e。Phase 1 实现 9 AC 达 source parity。

## State Machine (Phase 3 — 业务状态机 QA)

truth→FSM 提取的状态机模型（Phase 3 落地）:
```
[truth.md AC] --extract--> [FSM: states + transitions + boundary + unreachable]
[FSM] --coverage--> [boundary TC: transition / boundary / unreachable-reject]
[boundary TC] --execute--> [state_machine_coverage verdict]
```
Phase 3 AC-001..006 覆盖此状态机在 qa 层的落地。

## P4 Ack 前置完成

- ✅ source parity inventory (Phase 1)
- ✅ state machine model (Phase 3)
- ✅ deferral_ledger (UD-1..4)
- ✅ intent-parity reviewed (4 P1 已在 feature-graph 显式处理)
