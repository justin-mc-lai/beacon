# Research: QA Evo Deep 人类面子 Skill 与 Implement-QA 闭环缺陷

**Feature**: `qa-evo-deep-human-subskill-and-implementation-qa-closure-gap`  
**Version**: `v1.4.9`  
**Status**: `research-input`  
**Date**: `2026-05-23`  
**Source Project**: `/Users/apple/Developer/Personal/products/slow_uni_bmtop`

## 1. 背景

本研究来自 BMTOP 项目 `rules-encyclopedia-admin-closure` 的一次真实 Beacon QA 验收。

该项目在实现层面已经完成了规则百科闭环：

- 小程序规则百科在线主源与离线兜底
- 后台 `/admin/rules` 搜索、查看、更新
- admin/editor/viewer 权限边界
- 后台保存后公开 rules service 回读同一份数据
- dashboard 本月活跃 / 本月新增用户真实取数

但 Beacon runtime 在 `implement -> qa` 机器闭环上暴露出缺陷：

- 代码与人工 implementation summary 已存在，但 `beacon implement status <feature>` 返回 `implementation_run_not_found`
- `beacon qa run <feature>` 因 implementation marker 缺失 fail-closed
- `.machine/qa/<feature>.ac-test-matrix.json` 没有吸收 Markdown QA 中的 REC001-REC005 用例，而是退回到 `AC-001 Acceptance criteria TBD`
- QA runner 没能识别 Go + UniApp 项目的真实命令矩阵
- 环境 admission blocker 与产品失败没有充分分层

这说明 Beacon 的主生命周期边界是正确的，但当前 runtime 对实现证据、测试矩阵和项目 runner 的机器投影仍不够严肃。

## 2. Source Anchors

### 2.1 BMTOP 暴露的证据

- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/prd/rules-encyclopedia-admin-closure.md`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/user-story/rules-encyclopedia-admin-closure.md`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/qa/test-cases/rules-encyclopedia-admin-closure.md`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/implementation-summary-rules-encyclopedia-admin-closure.md`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/execution/qa-acceptance-rules-encyclopedia-admin-closure.md`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/.machine/qa/rules-encyclopedia-admin-closure.ac-test-matrix.json`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/.machine/qa/rules-encyclopedia-admin-closure.story-scenario-map.json`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/.machine/execution/implementation-plan-rules-encyclopedia-admin-closure.progress.json`
- `/Users/apple/Developer/Personal/products/slow_uni_bmtop/docs/beacon/v1.0.0/.machine/execution/rules-encyclopedia-admin-closure.revision.json`

### 2.2 Beacon 源码锚点

- `skills/beacon/beacon-qa/SKILL.md`
- `skills/beacon/beacon-deep/SKILL.md`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`
- `beacon/utils/qa_feature.py`
- `beacon/utils/test_contract_governance.py`
- `beacon/utils/requirement_clarity.py`
- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.9/research/better-harness-skill-eval-kit-and-source-driven-regression-core.md`

## 3. 暴露的问题

### 3.1 Implement evidence writeback 不可靠

`rules-encyclopedia-admin-closure` 已有人工实现摘要和实际代码证据，但 Beacon runtime 没有登记正式 implementation run。

表现：

```text
beacon implement status rules-encyclopedia-admin-closure
-> implementation_run_not_found
```

影响：

- `qa run` 无法进入真实 feature-aware 验证
- 已存在实现证据不能被 QA runtime 识别
- 人类看到“代码已验收”，机器面仍认为“implementation missing”

这是 implementation evidence writeback 缺陷，不是产品功能缺陷。

### 3.2 Test-case machine projection 退回 fallback

人工 QA 文档中已经有 REC001-REC005 的完整矩阵，但机器矩阵退化为：

```text
AC-001 Acceptance criteria TBD
TC-001 python3 -m pytest -q -k unit
```

影响：

- PRD / user-story / test-case 三件套没有被 QA runtime 正确编译
- `qa evolve` 和 `qa run` 无法基于真实 acceptance 执行
- 后续 release gate 的 trace scorecard 会失真

这是 test-case compiler / projection 缺陷，不是 QA 执行失败。

### 3.3 Project runner adapter 不理解真实技术栈

BMTOP 的真实栈是：

- 后端：Go + Gin + GORM
- 前端：Vue 3 + UniApp + TypeScript + Wot Design Uni
- 验证命令：`go test`、`pnpm type-check`、`pnpm build:mp-weixin`、`pnpm check:routes`、Playwright E2E

但 Beacon fallback QA 仍偏向：

- `python3 -m pytest`
- browser-use / generic Playwright
- 缺省 web-full profile

影响：

- QA 执行命令与项目现实脱节
- 有效技术证据被人工补证，不被 runtime 原生承认
- runner admission blocker 和产品 failure 容易混淆

### 3.4 环境 blocker 与产品失败分层不足

`go test ./...` 在 BMTOP 中失败于 Docker / testcontainers 启动 MySQL 容器超时。

这类失败应归类为：

```text
runner_admission_blocked / environment_blocked
```

而不是：

```text
product_failed
```

目标包 `internal/module/rules`、`internal/admin/handler`、`internal/admin`、`internal/admin/middleware` 已通过，说明本 feature 目标链路有有效证据。

### 3.5 QA 缺少“需求整体面深挖”人类面

常规 QA 主要回答：

> 当前测试证据是否足够支持 acceptance？

但真实项目常需要在 QA 之前或 QA blocked 后回答：

- 状态机是否完整？
- 数据源是否一致？
- 管理端到小程序是否真的共用主源？
- 权限边界是否被遗漏？
- 测试矩阵是否漏掉关键状态或跨端闭环？
- 当前问题应该回 `change`、`test-case`、`implement`，还是只是补 QA runner？

这些问题不应该靠 release 阶段才发现，也不应强行扩张 QA 主入口。

## 4. 核心判断

Beacon 主链不应新增生命周期 stage。

推荐保持：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

但需要在 QA 下新增一个人类面子 skill：

```text
qa-evo-deep
```

它是 QA 的深度分析 support surface，不是 release gate，不是 truth source，不是新的 lifecycle stage。

## 5. `qa-evo-deep` 定位

### 5.1 定义

`qa-evo-deep` 是 QA 基础上的人类面深度验收分析子 skill。

它的职责是从需求整体面识别结构性缺口，并输出可路由 findings：

- 状态机缺口
- 数据源一致性缺口
- 跨端闭环缺口
- 权限边界缺口
- 测试增量缺口
- runner admission / evidence binding 缺口

它不直接判定 release pass。

### 5.2 它可以做什么

`qa-evo-deep` 可以：

- 读取 frozen PRD / user-story / test-case
- 读取 implementation evidence 与 QA evidence
- 对比 human docs 和 machine projections
- 识别 state / data / permission / cross-surface gaps
- 生成 deep test delta
- 生成 routeable findings
- 建议下一跳：`change`、`test-case`、`implement`、补 QA
- 生成 release supplement input

### 5.3 它不可以做什么

`qa-evo-deep` 不可以：

- 改 PRD / user-story / test-case
- 直接改 `.machine` truth
- 代替 `beacon qa run`
- 代替 `beacon release`
- 直接给 release pass
- 把自己升级成主生命周期 stage

## 6. 输入契约

`qa-evo-deep` 应读取：

```text
docs/beacon/<version>/prd/<feature>.md
docs/beacon/<version>/user-story/<feature>.md
docs/beacon/<version>/qa/test-cases/<feature>.md
docs/beacon/<version>/.machine/prd/<feature>*.json
docs/beacon/<version>/.machine/user-story/<feature>.json
docs/beacon/<version>/.machine/qa/<feature>*.json
docs/beacon/<version>/.machine/execution/implementation-*.json
docs/beacon/<version>/execution/implementation-summary-<feature>.md
docs/beacon/<version>/execution/qa-acceptance-<feature>.md
.beacon/qa/features/<feature>/*
.beacon/state/implementation-<feature>.json
```

缺失输入不应静默忽略，必须记录为 admission finding。

## 7. 输出契约

建议输出人类面 Markdown：

```text
docs/beacon/<version>/qa/evo-deep/<feature>.md
```

建议输出机器面 JSON：

```text
docs/beacon/<version>/.machine/qa/evo-deep-<feature>.json
```

输出必须包含：

| Field | 说明 |
| --- | --- |
| `feature` | feature slug |
| `version` | docs version |
| `source_refs` | 读取的 truth / evidence refs |
| `findings` | 可路由发现 |
| `test_delta` | 建议补充的测试 |
| `route_recommendations` | change / test-case / implement / qa |
| `blocked_admissions` | runner / evidence / session blocker |
| `release_supplement` | release 可读补充，但不含 pass verdict |

## 8. Finding Schema

建议每条 finding 使用稳定分类：

```json
{
  "id": "QED-001",
  "severity": "P0|P1|P2|P3",
  "family": "state_machine|data_source|cross_surface|permission|test_delta|runner_admission|evidence_binding|truth_drift",
  "title": "...",
  "evidence_refs": ["..."],
  "impact": "...",
  "route": "change|test-case|implement|qa|release-waiver|backlog",
  "recommended_next_action": "...",
  "blocks_release": true
}
```

重要规则：

- `truth_drift` 必须 route 到 `change`
- `acceptance_missing` 必须 route 到 `test-case`
- `implementation_gap` 必须 route 到 `implement`
- `runner_admission` 或 `evidence_binding` 必须 route 到补 QA runtime / evidence import
- `release-waiver` 只能作为显式人类决策输入，不能由 `qa-evo-deep` 自动通过

## 9. Suggested Human Skill

建议新增：

```text
skills/beacon/beacon-qa-evo-deep/SKILL.md
```

Skill 描述：

```text
Use when the user wants deep QA analysis beyond normal execution results: state machine, data source consistency, cross-surface closure, permission boundaries, test deltas, and routeable findings. This is a QA support surface, not a lifecycle stage, truth source, or release gate.
```

人类面行为：

- 先说明它不会改 frozen truth
- 读取 PRD / US / QA / implementation / QA evidence
- 按五类深挖：
  - state machine
  - data source consistency
  - cross-surface closure
  - permission boundary
  - test delta
- 输出 findings 和 route
- 若发现 runtime 绑定缺陷，也要作为 `evidence_binding` finding

## 10. Suggested CLI Shape

推荐不新增主阶段命令，优先挂到 QA 下：

```bash
beacon qa evo-deep <feature> --project . --version <version> --json
```

或保留 support surface：

```bash
beacon deep run <feature> --profile qa-evo --project . --version <version>
```

如果同时提供人类面 skill 和 CLI，边界应保持一致：

- skill 负责判断框架和可读输出
- CLI 负责读取材料、生成 JSON、写入 evidence
- 两者都不直接改 truth，不直接 release pass

## 11. 与现有 `beacon-deep` 的关系

`beacon-deep` 已经定义为 support surface。

`qa-evo-deep` 不应复制一个新的 deep stage，而应成为：

```text
deep profile for QA closure
```

关系：

| Surface | 职责 |
| --- | --- |
| `beacon-qa` | 正式验收入口，执行或评估 acceptance evidence |
| `beacon-deep` | 通用深度分析 support surface |
| `qa-evo-deep` | 面向 QA 的深度需求闭环分析 profile / human subskill |
| `beacon-release` | 唯一发布门禁面 |

## 12. 对 Beacon runtime 的修复建议

### 12.1 P0: implementation evidence writeback

Implement 完成后必须写入可被 QA 识别的 evidence marker。

需要支持：

- 正常 implement run 写入
- 人工实现后受控导入：`beacon implement import-evidence <feature>`
- QA 前检查 implementation marker、summary、technical archive、progress completed 是否一致

### 12.2 P0: test-case Markdown -> machine matrix 编译

机器矩阵不能在 Markdown QA 已存在时退回 `Acceptance criteria TBD`。

需要：

- 解析 Markdown test case tables
- 保留原 TC ID、AC ID、command、assertion、evidence path
- 编译失败时 fail closed 并说明 parser reason
- 不允许静默 fallback

### 12.3 P1: project runner adapter

Beacon QA 应支持项目级 runner profile：

```json
{
  "backend": "go",
  "frontend": "uniapp",
  "commands": {
    "backend_target": "cd tournament-service && go test ./internal/module/rules ./internal/admin/handler ./internal/admin ./internal/admin/middleware",
    "frontend_typecheck": "cd tournament_miniapp && pnpm type-check",
    "frontend_build": "cd tournament_miniapp && pnpm build:mp-weixin",
    "route_check": "cd tournament_miniapp && pnpm check:routes"
  }
}
```

### 12.4 P1: admission blocker taxonomy

QA runtime 必须区分：

- `product_failed`
- `test_failed`
- `runner_admission_blocked`
- `environment_blocked`
- `auth_session_blocked`
- `evidence_binding_missing`
- `coverage_gap`
- `truth_projection_gap`

### 12.5 P2: qa-evo-deep reporting

在 feature QA blocked 或 release 前，可生成：

- state machine gap report
- data source closure report
- cross-surface route report
- permission boundary report
- deep test delta
- route recommendations

## 13. BMTOP Case 的示例 Findings

### QED-001: implementation marker missing

- severity: `P0`
- family: `evidence_binding`
- evidence: `beacon implement status rules-encyclopedia-admin-closure -> implementation_run_not_found`
- impact: `qa run` 无法进入真实 feature-aware 验证
- route: `implement`
- recommended action: 补 implementation evidence writeback 或 import-evidence
- blocks release: yes

### QED-002: QA machine matrix fallback

- severity: `P0`
- family: `truth_projection`
- evidence: `.machine/qa/rules-encyclopedia-admin-closure.ac-test-matrix.json` 只包含 `AC-001 Acceptance criteria TBD`
- impact: PRD / US / QA 三件套未进入机器验收
- route: `test-case`
- recommended action: 修 Markdown QA -> machine matrix compiler，禁止静默 fallback
- blocks release: yes

### QED-003: project runner mismatch

- severity: `P1`
- family: `runner_admission`
- evidence: fallback command 使用 `python3 -m pytest`，项目真实命令为 Go + UniApp
- impact: QA 自动化证据和项目现实脱节
- route: `qa`
- recommended action: 增加 project runner adapter / command profile
- blocks release: conditional

### QED-004: frontend rules unit command unavailable

- severity: `P1`
- family: `test_delta`
- evidence: `pnpm test -- rules -> ERR_PNPM_NO_SCRIPT Missing script: test`
- impact: 冻结矩阵中的 UI 单测层不可执行
- route: `test-case`
- recommended action: 要么补 Vitest rules tests，要么 refreeze 测试矩阵到真实可执行命令
- blocks release: conditional

### QED-005: full backend suite environment blocked

- severity: `P2`
- family: `runner_admission`
- evidence: `go test ./...` fail at Docker/testcontainers MySQL startup timeout
- impact: 全量 suite 未形成 release-grade 证据，但目标包通过
- route: `qa`
- recommended action: 标记 environment blocker；补 testcontainers admission check 或可跳过标签
- blocks release: conditional

## 14. 收敛建议

`qa-evo-deep` 值得进入 v1.4.9 调研，但不应直接冻结成新 lifecycle stage。

推荐下一步：

1. 先作为 research input 保留本文件。
2. 进入 `beacon-change-refreeze` 时，把它收敛为 QA support surface / human subskill。
3. 同步冻结 P0 runtime 修复：
   - implementation evidence writeback
   - Markdown QA matrix compiler fail-closed
4. 再实现 `qa evo-deep` 或 `deep --profile qa-evo`。
5. 最后用 BMTOP case 作为 regression fixture，确保不再出现 implementation 已存在但 QA 不认、QA 文档已存在但 matrix fallback 的问题。

核心原则：

> `qa-evo-deep` 增强 QA 的需求整体面分析能力，但不改变 Beacon 主链、不改 frozen truth、不直接给 release verdict。它只产出可路由 findings，让 change、test-case、implement、qa、release 各自完成自己的闭环。
