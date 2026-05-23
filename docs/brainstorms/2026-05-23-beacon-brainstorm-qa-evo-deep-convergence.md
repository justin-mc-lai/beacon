# Beacon Brainstorm: qa-evo-deep 收敛结论

**Version**: `v1.4.9`  
**Mode**: `requirement-convergence`  
**Date**: `2026-05-23`  
**Input Research**: `docs/beacon/v1.4.9/research/qa-evo-deep-human-subskill-and-implementation-qa-closure-gap.md`  
**Status**: `brainstorm-closed-route-to-change-refreeze`

## 1. 收敛问题

本轮不是要判断 BMTOP 的规则百科是否通过，而是要从 BMTOP 暴露出的 Beacon runtime 缺陷中收敛 v1.4.9 的产品演进方向：

- `implement -> qa` 机器闭环是否完整
- QA 是否真正基于 PRD / user-story / test-case 验收
- 是否需要新增 `qa-evo-deep` 人类面子 skill
- 如果需要，是否会扩张 Beacon 主生命周期

## 2. 事实锚点

从 BMTOP case 得到的关键事实：

- Human docs 存在完整 PRD / US / QA：`rules-encyclopedia-admin-closure`
- 实现摘要和代码证据存在
- `beacon implement status <feature>` 返回 `implementation_run_not_found`
- `.machine/qa/<feature>.ac-test-matrix.json` 退化为 `AC-001 Acceptance criteria TBD`
- `beacon qa run <feature>` 因 implementation marker 缺失阻断
- 人工定向验收可以证明目标链路，但 Beacon runtime 不能原生承认这组证据

因此问题不是单纯“多加 QA”，而是：

```text
truth projection + implementation evidence binding + project runner admission
```

三处机器闭环断裂。

## 3. 第一性判断

Beacon 的主链必须保持：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

不应新增 `qa-evo-deep` 作为主生命周期 stage。原因：

- `qa` 已经是唯一正式验收入口
- `deep` 已经是 support surface
- 新增主 stage 会扩大人类心智负担
- 需求整体面深挖只应产出 routeable findings，不应产生 truth 或 gate verdict

但常规 QA 当前缺一个“需求整体面深挖”的人类面入口。这个入口应存在，但必须被定义为：

```text
QA support subskill / deep profile
```

而不是：

```text
new lifecycle stage / release gate / truth source
```

## 4. qa-evo-deep 收敛定义

推荐新增人类面子 skill：

```text
$beacon:beacon-qa-evo-deep
```

或 CLI profile：

```bash
beacon qa evo-deep <feature> --project . --version <version>
```

它的定义：

> `qa-evo-deep` 是 QA 之下的深度需求闭环分析 support surface，用于发现状态机、数据源一致性、跨端闭环、权限边界、测试增量和证据绑定缺口，并输出可路由 findings。

它不允许：

- 改 PRD / user-story / test-case
- 写入 canonical truth
- 代替 `beacon qa run`
- 代替 `beacon release`
- 直接给 release pass
- 成为主生命周期 stage

## 5. 应进入 change-refreeze 的范围

本 brainstorm 建议进入 `$beacon:beacon-change-refreeze v1.4.9`，但范围必须拆清楚。

### 5.1 Must: runtime 闭环修复

这些是 P0，不解决则 QA 主链不可信：

1. **Implementation evidence writeback**
   - implement 完成后必须写入 QA 可识别的 implementation marker
   - 支持受控导入已有实现证据
   - QA 前能检查 summary / technical archive / progress / marker 一致性

2. **Markdown QA -> machine matrix 编译**
   - 如果 `qa/test-cases/<feature>.md` 已存在，不允许静默 fallback 到 `Acceptance criteria TBD`
   - 编译失败要 fail closed，并给出 parser reason
   - machine matrix 必须保留 TC ID、AC ID、command、assertion、evidence path

3. **Evidence binding blocker taxonomy**
   - 明确区分 `implementation_missing`、`evidence_binding_missing`、`truth_projection_gap`、`coverage_gap`
   - 不能把 runtime admission 问题伪装成产品失败

### 5.2 Should: qa-evo-deep support surface

冻结 `qa-evo-deep` 的边界和输出：

- 输入：PRD / US / QA / implementation evidence / QA evidence / machine projections
- 输出：routeable findings、test delta、blocked admissions、release supplement
- findings route：`change` / `test-case` / `implement` / `qa` / `release-waiver` / `backlog`
- 不写 truth，不给 release verdict

### 5.3 Should: project runner profile

为真实项目提供 runner profile，至少要让 Beacon 可表达：

- Go backend target tests
- UniApp frontend type-check / build / route-check
- Playwright E2E
- Docker / testcontainers admission check
- Node version pinning 或 PATH override

这不一定要在 `qa-evo-deep` 中实现，但必须被 QA runtime 承认。

## 6. 不应进入本次冻结的范围

以下内容不建议纳入本次 v1.4.9 scope：

- 把 `qa-evo-deep` 做成 release gate
- 重写整个 QA runner 框架
- 自动修复所有项目测试脚本
- 让 `deep` 直接改 PRD / US / TC
- 建一个通用 BI 式 QA dashboard
- 为所有语言一次性做完整 runner adapter

本次目标应聚焦“闭环可信”，不是扩平台。

## 7. Routeable Findings

| ID | Severity | Family | Finding | Route |
|---|---|---|---|---|
| QED-001 | P0 | evidence_binding | 实现存在但 implementation marker 缺失，QA runtime 不认 | `implement` / runtime fix |
| QED-002 | P0 | truth_projection | Markdown QA 未进入 machine matrix，退化成 `Acceptance criteria TBD` | `test-case` / compiler fix |
| QED-003 | P1 | runner_admission | QA fallback runner 与 Go + UniApp 项目不匹配 | `qa` |
| QED-004 | P1 | test_delta | 前端 rules UI 自动化命令不存在，冻结矩阵不可执行 | `test-case` |
| QED-005 | P2 | environment_blocked | Docker/testcontainers 失败应归类为环境 admission blocker | `qa` |
| QED-006 | P1 | support_surface_gap | 缺少需求整体面深挖入口，常规 QA 无法系统识别状态机/数据源/权限/跨端缺口 | `change` |

## 8. 推荐冻结包结构

建议新 feature slug：

```text
qa-evo-deep-and-implement-qa-evidence-closure
```

冻结材料应包含：

- Research: 使用现有 `qa-evo-deep-human-subskill-and-implementation-qa-closure-gap.md`
- PRD:
  - 问题：implement/qa evidence closure 不可信，QA deep support surface 缺失
  - 目标：QA 基于 frozen truth 和 implementation evidence 形成可解释闭环
  - 非目标：不新增主生命周期 stage，不改 release gate
- User Story:
  - Beacon operator 可运行 `qa-evo-deep`
  - QA runtime 能识别 implementation evidence
  - QA matrix 不静默 fallback
  - Runner blocker 可分层
- Test Cases:
  - BMTOP fixture 不再 fallback
  - implementation marker missing 时 reason code 正确
  - Markdown QA matrix 编译失败时 fail closed
  - `qa-evo-deep` 输出 findings 但不改 truth
  - findings route 到 change/test-case/implement/qa

## 9. 最小可验收实现切片

如果要控制 v1.4.9 scope，推荐最小切片：

1. 新增 `beacon-qa-evo-deep` skill 文档。
2. 新增 `beacon qa evo-deep` 或 `beacon deep run --profile qa-evo` 入口。
3. 修复 implementation status 读取，使已有 implementation summary / technical archive 可以被 QA 受控导入或识别。
4. 修复 test-case Markdown 编译 fallback：有 QA 文档但解析失败时必须 blocked。
5. 用 BMTOP `rules-encyclopedia-admin-closure` 作为 regression fixture。

## 10. 最终收敛

本轮建议：

```text
route: beacon-change-refreeze v1.4.9
feature: qa-evo-deep-and-implement-qa-evidence-closure
priority: P0 runtime closure + P1 support surface
```

`qa-evo-deep` 应进入 v1.4.9 变更冻结，但只能作为 QA support 子 skill / deep profile。它的价值是让 QA 在正式验收前后具备需求整体面深挖能力，并把发现稳定路由回 `change`、`test-case`、`implement` 或补 QA。

同时，必须把 BMTOP 暴露的 runtime 闭环缺陷纳入同一冻结包，否则新增 `qa-evo-deep` 只会变成更漂亮的人工分析，而不能解决 Beacon QA 不认 PRD/US/TC 和 implementation evidence 的根因。
