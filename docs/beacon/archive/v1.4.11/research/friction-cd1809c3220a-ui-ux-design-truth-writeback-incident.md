# Friction `friction:cd1809c3220a`：UI/UX Design Truth Writeback 事故记录

日期：2026-05-26  
版本：v1.4.11  
状态：research-only / friction analysis  
来源：`beacon-friction-intake`  
记录类型：单独事故文档 / UI-UX design truth gap / 后续冻结输入

## 1. 事故摘要

本事故记录了一个 P0 级 Beacon truth gap：

> `ui-ux-dev` 已验收通过的 UI/UX 事实没有进入 Beacon requirement truth，导致 `beacon-implement` / `beacon-qa` 按旧冻结需求执行，把已验收前端事实当作 drift，并回滚到旧 UI/UX baseline。

这不是单纯的前端实现 bug，而是 Beacon 源码侧的 truth intake / gate 问题。

大白话描述：

```text
人已经验收了新的 UI/UX，
但 Beacon 仍只看旧的冻结需求，
所以越自动化、越严格执行，越会把正确的新界面回滚成旧界面。
```

该事故的关键不是“ui-ux-dev 是否好用”，而是：

```text
accepted UI/UX facts 必须成为 Beacon 可审计的需求真相；
如果没有写回 truth，implement / QA / release 必须停住。
```

## 2. Friction 元信息

- Friction ID: `friction:cd1809c3220a`
- Severity: `P0`
- Priority: `emergency-highest`
- Queue status: `queued`
- Item class: `improvement`
- Domain: `implement`
- Source run id: `fit-20260526T100129Z`
- Docs version: `v1.0.0`
- Source project: `/Users/apple/Developer/Personal/products/slow_uni_bmtop`
- Global sqlite: `/Users/apple/.beacon/runtime-ledger/runtime-ledger.sqlite3`
- Local report: `/Users/apple/Developer/Personal/products/slow_uni_bmtop/.beacon/analysis/friction-intake-fit-20260526T100129Z.md`
- Evidence capture: `/Users/apple/Developer/Personal/products/slow_uni_bmtop/.beacon/debug/friction-captures/1136e1db0255.json`

Global sqlite record confirms:

```text
project_key: slow_uni_bmtop--bd0e82265e
item_id: friction:cd1809c3220a
severity: P0
queue_status: queued
requirement_route_status: queue_only
summary: UI/UX approved facts were not written back into Beacon requirement truth...
```

## 3. 原始事故事实

来自 capture 原文的核心事实：

- slow_uni_bmtop 的前端 UI/UX 改进通过封装的 `ui-ux-dev` 能力产出。
- 这些改进被视为已验收或已接受的前端事实。
- 结果没有稳定写入：
  - `PRODUCT.md`
  - `DESIGN.md`
  - `docs/beacon/v1.0.0/prd`
  - `docs/beacon/v1.0.0/user-story`
  - `docs/beacon/v1.0.0/qa/test-cases`
- 由此形成 truth gap：
  - operator / ui-ux-dev 层认为新 UI/UX 已接受；
  - Beacon frozen requirement truth 仍保留旧 baseline；
  - `beacon-implement` / `beacon-qa` 按旧 truth 运行。
- 结果：
  - validated frontend UI/UX improvements 被视为 drift；
  - 自动化把产品回滚到旧 baseline；
  - 影响包括 global visual baseline 和 fee-calculator capabilities。

事故要求：

> Beacon must prevent implement / QA / release from using stale UI truth when a ui-ux-dev review / polish / explore result is accepted.

## 4. 事故链路复盘

### 4.1 触发前置条件

事故成立至少需要以下条件同时出现：

- 项目存在 Beacon frozen requirement truth。
- 项目又通过 `ui-ux-dev` 或同类 UI/UX design 能力形成了新的 accepted frontend facts。
- accepted facts 影响产品或设计真相，而不是纯粹的临时探索。
- accepted facts 没有写回 `PRODUCT.md` / `DESIGN.md` / PRD / user-story / test-cases。
- 后续继续触发 `beacon-implement`、`beacon-qa` 或 release gate。

### 4.2 错误执行链

```text
ui-ux-dev produces UI/UX improvements
  -> operator accepts the frontend behavior
  -> no Beacon truth writeback happens
  -> frozen PRD / user-story / test-cases remain stale
  -> beacon implement follows old truth
  -> beacon qa validates against old truth
  -> accepted UI/UX changes are treated as drift
  -> automation rolls product back toward stale baseline
```

### 4.3 正确闭环链

```text
ui-ux-dev produces UI/UX improvements
  -> operator accepts the frontend behavior
  -> Beacon records accepted design result reference
  -> prototype adapt or change/refreeze binds it into truth
  -> PRODUCT.md / DESIGN.md / PRD / user-story / test-cases are updated when affected
  -> implement / QA / release continue from current truth
```

### 4.4 必须 fail closed 的链

```text
accepted UI/UX result exists
  -> affected truth refs are missing
  -> no prototype adapt transaction
  -> no change/refreeze truth update
  -> implement / QA / release requested
  -> accepted_ui_ux_truth_gap blocks execution
```

## 5. UI/UX Design 能力边界

### 5.1 `ui-ux-dev` 的角色

`ui-ux-dev` 是 UI/UX 执行与探索能力，不是 Beacon canonical truth source。

它适合产出：

- visual baseline；
- layout；
- interaction handoff；
- page state；
- component behavior；
- design review result；
- visual polish result；
- design exploration result；
- UX acceptance notes；
- screenshots / prototype artifacts。

但它不能直接成为 Beacon truth。它的 accepted output 必须通过 Beacon truth-binding route 写回。

### 5.2 UI/UX design 能力应覆盖什么

Beacon 需要承认 UI/UX design 不是简单“截图好看不好看”，它至少会影响：

- 产品定位：页面信息优先级、主次行动、关键承诺。
- 视觉基线：布局、间距、色彩、字体、组件密度。
- 交互行为：输入、校验、反馈、禁用态、空态、错误态。
- 业务能力：某些 UI/UX 改动本身会暴露或隐藏业务能力，例如 fee calculator。
- 验收标准：AC、测试用例、QA scorecard 都可能需要随 UI/UX acceptance 更新。
- 回归边界：后续实现不能把 accepted visual/product behavior 当作 drift。

因此 accepted UI/UX output 不是普通 support note。只要它影响 product/design/requirement behavior，就必须进入 Beacon truth-binding。

### 5.3 UI/UX design 能力不能直接做什么

为了避免把工具输出误当 truth，Beacon 不能允许：

- `ui-ux-dev` 直接覆盖 Beacon frozen requirement。
- design review support note 自动成为 release truth。
- 截图或临时 polish 结果绕过 PRD / user-story / test-case。
- automation 根据旧 PRD 自动否定已被人接受的 UI/UX 事实。
- `.machine` 或 runtime evidence 代替 PRODUCT / DESIGN / versioned Markdown truth。

### 5.4 Beacon 现有相关能力

源码中已经存在相关方向：

- `beacon/commands/prototype.py`
  - `prototype` 当前定位包含 accepted UI/UX result binding。
  - CLI 文案已有：UI/UX execution routes to `ui-ux-dev`，then bind accepted output through `prototype adapt`。
- `beacon/utils/design_review_surface.py`
  - 可将 UI/UX execution need 路由到 `ui-ux-dev`。
  - 提供 `writeback_command` 指向 `beacon prototype adapt ... --design-result-ref <ui-ux-dev-output>`。
- `beacon/utils/prototype_support.py`
  - 管理 `ui-ux-dev-*` skill routing。
  - 有 `source_surface: ui-ux-dev` 和 design result source 语义。
- `skills/beacon/beacon-prototype/SKILL.md`
  - 明确 `ui-ux-dev` 负责探索、系统推荐、review、polish、extract、library lookup。
  - 明确 Beacon prototype 用于 accepted `ui-ux-dev` result intake。

所以事故不是“Beacon 完全没有通道”，而是：

```text
accepted UI/UX result -> Beacon truth writeback
```

这个桥没有被 gate 强制执行。

## 6. Root Cause

根因可以拆成四层：

1. **事实接收缺口**：Beacon 没有稳定识别“某个 UI/UX output 已被接受”。
2. **写回缺口**：accepted UI/UX facts 没有强制进入 PRODUCT / DESIGN / PRD / user-story / test-cases。
3. **门禁缺口**：implement / QA / release 没有在 accepted facts unbound 时 fail closed。
4. **解释缺口**：status/help 没有把修复路由明确提示为 `prototype adapt` 或 change/refreeze。

这四层中，最危险的是第三层。因为只要 gate 不拦，Beacon 的自动化越稳定，回滚 stale truth 的能力越强。

## 7. Truth Gap 结构

事故中至少存在三层 truth surface：

```text
ui-ux-dev accepted result
  = operator accepted UI/UX facts

PRODUCT.md / DESIGN.md
  = project-level product and design truth

docs/beacon/<version>/prd + user-story + test-cases
  = versioned Beacon requirement truth
```

问题不是 `.machine` 是否是 truth，而是 accepted human UI/UX facts 没有进入任何正式 truth surface。

错误状态：

```text
accepted ui-ux-dev result = true in operator context
old PRD / US / TC = true in Beacon execution
implement / QA = follows old Beacon truth
```

正确状态：

```text
accepted ui-ux-dev result
  -> prototype adapt or change/refreeze
  -> PRODUCT.md / DESIGN.md and versioned requirement truth updated
  -> implement / QA / release continue
```

或：

```text
accepted ui-ux-dev result unbound
  -> implement / QA / release fail closed
  -> route to truth writeback
```

## 8. 为什么这是 Beacon v1.4.11 问题

v1.4.11 当前主线是 Markdown-first projection authority 和 legacy 退场。

这条事故说明 Markdown-first 还有一个更现实的边界：

> Markdown-first 不能等于“盲信旧 Markdown”。它必须确保当前 accepted human facts 被写回正确 Markdown truth surface。

如果只清理 `.machine` authority，却不处理 accepted UI/UX facts 未绑定的问题，Beacon 仍会出现：

- machine 不再被称为 truth；
- 但旧 Markdown 仍被自动化当作唯一 truth；
- 新 accepted UI/UX facts 被看成 drift；
- implement / QA / release 继续回滚已验收 UI。

因此这条 friction 应进入 v1.4.11 后续候选：

```text
accepted-ui-ux-truth-writeback-gate-contract
```

## 9. 候选 Gate

建议 gate 名称：

```text
accepted_ui_ux_truth_gap_gate
```

### 9.1 Gate 输入

- accepted UI/UX output ref；
- design result source，例如 `ui-ux-dev`；
- affected feature；
- affected pages / components / flows；
- whether output affects:
  - product identity；
  - visual baseline；
  - page state；
  - interaction handoff；
  - PRD promise；
  - user-story AC；
  - test-case coverage；
  - `PRODUCT.md`；
  - `DESIGN.md`。

### 9.2 Gate 判定

Fail closed when:

- accepted UI/UX result exists；
- result affects product/design/requirement behavior；
- no `prototype adapt` transaction exists；
- no change/refreeze package updated PRD / user-story / test-cases；
- no `PRODUCT.md` / `DESIGN.md` update exists when those files are project-level truth；
- implement / QA / release is requested.

Pass when:

- accepted UI/UX result is bound through Beacon truth route；
- affected truth refs are explicit；
- downstream implementation/QA references updated truth；
- no unbound accepted design facts remain.

### 9.3 Gate 输出

Recommended blocker codes:

```text
accepted_ui_ux_truth_gap
ui_ux_truth_writeback_required
accepted_design_result_unbound
```

Recommended repair route:

```bash
beacon prototype adapt "<feature>" \
  --project <project-root> \
  --version <version> \
  --design-result-ref <ui-ux-dev-output>
```

or:

```bash
beacon change "<feature>" \
  --project <project-root> \
  --version <version> \
  --reason "bind accepted UI/UX facts into requirement truth" \
  --refreeze-chain
```

## 10. 对 implement / QA / release 的影响

### 10.1 Implement

`beacon implement` 不应在 accepted UI/UX facts unbound 时继续。

原因：

- implement 会按 frozen truth 工作；
- frozen truth 是 stale；
- implement 越“忠实”，越可能回滚 accepted UI/UX facts。

### 10.2 QA

`beacon qa` 不应按旧 UI baseline 出 verdict。

原因：

- QA 的 pass/fail 必须绑定当前 accepted truth；
- stale UI truth 会让已验收 UI 被判定为 drift；
- QA 会制造错误的 release confidence。

### 10.3 Release

`beacon release` 必须把 unbound accepted UI/UX facts 当作 P0 blocker。

原因：

- release 是承诺面；
- unbound UI/UX facts 意味着 human accepted product state 与 Beacon release truth 不一致；
- 这类 release 不可审计。

## 11. 事故影响面

### 11.1 对项目的直接影响

- 已验收 UI/UX 改动可能被后续自动化覆盖。
- QA 的 pass/fail 可能基于 stale requirement。
- release report 可能错误声明当前行为已按需求闭环。
- 用户侧看到的是产品体验反复或能力倒退。

### 11.2 对 Beacon 的系统性影响

- Markdown-first 可能退化成“旧 Markdown-first”。
- UI/UX support skill 的产物无法稳定进入需求生命周期。
- project-level truth 与 versioned truth 之间缺少 accepted design fact 的绑定协议。
- runtime / automation / Foghorn 类调度系统如果复用 Beacon，也会放大该事故。

### 11.3 对后续设计能力建设的影响

Beacon 需要把 UI/UX design 能力纳入生命周期治理，但不能把它变成直接写 truth 的黑盒。

推荐定位：

```text
ui-ux-dev = design execution / review / exploration producer
beacon prototype adapt = accepted design result intake
change/refreeze = requirement truth update and audit trail
gate = prevents stale truth automation
```

## 12. 需要补齐的 Beacon 能力

### 12.1 Accepted UI/UX Result Ledger

需要有一个可审计记录，表达：

- 哪个 UI/UX output 被接受；
- 由谁或哪个流程接受；
- 影响哪些页面、组件、流程、业务能力；
- 是否影响 PRODUCT / DESIGN / PRD / user-story / test-cases；
- 对应 writeback transaction 是否完成。

该 ledger 是 evidence，不是 truth；truth 仍在 Markdown requirement materials。

### 12.2 Truth Writeback Contract

需要明确 accepted UI/UX facts 的写回路径：

- product/design 层：`PRODUCT.md` / `DESIGN.md`。
- version requirement 层：`docs/beacon/<version>/prd/<feature>.md`。
- acceptance 层：`docs/beacon/<version>/user-story/<feature>.md`。
- QA 层：`docs/beacon/<version>/qa/test-cases/<feature>.md`。
- change trace：`docs/beacon/<version>/change/<feature>.md` 或 refreeze summary。

### 12.3 Gate Registry Integration

`accepted_ui_ux_truth_gap_gate` 应进入 gate registry，并至少被以下命令消费：

- `beacon implement`
- `beacon qa`
- `beacon release`
- `beacon status`
- `beacon help`

### 12.4 Repair Route

当 gate blocked 时，Beacon 不应只输出 blocker code，还要给出可执行修复路由：

```bash
beacon prototype adapt "<feature>" \
  --project <project-root> \
  --version <version> \
  --design-result-ref <ui-ux-dev-output>
```

或进入变更冻结：

```bash
beacon change-refreeze "accepted-ui-ux-truth-writeback-gate-contract" \
  --project . \
  --version v1.4.11
```

## 13. 非目标

- 不把 `ui-ux-dev` 嵌入 Beacon 源码。
- 不让 `ui-ux-dev` 直接写 Beacon truth。
- 不让 automation 自行改写 `PRODUCT.md` / `DESIGN.md` / PRD。
- 不恢复 legacy wireframe 作为 current truth。
- 不把 design review support surface 变成 lifecycle stage。

## 14. 后续需求候选

Feature candidate:

```text
accepted-ui-ux-truth-writeback-gate-contract
```

Suggested scope:

- accepted UI/UX result registry / locator；
- prototype adapt transaction evidence；
- project-level `PRODUCT.md` / `DESIGN.md` truth participation；
- implement / QA / release fail-closed gate；
- status/help repair route；
- regression test preventing stale UI truth execution。

Suggested AC:

- AC-001: Given accepted `ui-ux-dev` output that affects product/design/requirements, implement fails closed until truth writeback exists.
- AC-002: QA fails closed on the same condition and does not produce pass/fail against stale UI baseline.
- AC-003: Release gate treats unbound accepted UI/UX facts as P0 blocker.
- AC-004: `prototype adapt` or change/refreeze creates explicit truth refs for affected PRD / user-story / test-case / PRODUCT / DESIGN materials.
- AC-005: status/help displays `accepted_ui_ux_truth_gap` and a concrete writeback command.
- AC-006: legacy prototype wireframe sources remain migration input only and cannot satisfy accepted UI/UX truth writeback.

## 15. 路由建议

当前文档仍是 research-only。

推荐下一步：

```bash
beacon change-refreeze "accepted-ui-ux-truth-writeback-gate-contract" --project . --version v1.4.11
```

该 feature 不应混入 Foghorn v0.0.1。它属于 Beacon 源码的 UI/UX truth writeback gate。
