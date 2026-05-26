# 调研：Beacon 历史包袱减负与可审计重构行动方案

**Version**: `v1.4.11`  
**Status**: `research-input`  
**Date**: `2026-05-26`  
**Source Research**: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`

## 1. 目标

这份文档把 v1.4.11 的 Markdown-first authority / legacy-retirement 调研，整理成一套可执行、可验收、可审计的减负重构方案。

目标不是删除 Beacon 能力，也不是为了少几行代码牺牲 gate、QA、release 的可靠性。

真正目标是：

```text
保留完整能力。
移除隐式 fallback。
把固定流程下沉成工具、gate、schema、test。
让 Skill 回到判断、解释、路由、挑战边界的位置。
```

## 2. 核心判断

用户提出的疑问成立：

> Skill 的致命缺陷是效率低、不稳定还费钱。它本质是给 AI 讲思路、提供小工具，但缺乏硬约束。每次执行 Skill，AI 都得重新理解一遍再操作，没法保证每次理解和执行效果一致，有时甚至不执行。既然是既定流程，为什么不直接固化成工具？

Beacon 应接受这个判断，并做出职责切分：

| Surface | 职责 |
| --- | --- |
| Skill | 判断、framing、路由、挑战边界、人类解释 |
| Tool | 确定性执行固定流程 |
| Gate | fail-closed 阻断带病继续 |
| Schema | 固定输入输出契约 |
| Test | 防止行为回归 |
| Markdown | requirement truth |
| `.machine` | projection / evidence / read model |
| `.beacon` | runtime state / evidence |

因此，v1.4.11 不应继续把固定流程写进更厚的 Skill 脚本里，而应把反复执行的硬流程下沉为 runtime code、工具、gate、schema 和测试。

## 3. 不可突破的边界

- 不删除 `.machine`；它仍是 projection / evidence / read model。
- 不削弱 QA、release、projection、evidence、git、metadata、version gate。
- 不允许 support skill、hook、learning、memory、browser adapter、compat path 直接给出 gate verdict。
- 不把 legacy mirror 当作 current truth。
- 不让 v1.4.11+ 的 current flow 静默使用 fallback path。
- 不把 compatibility registry 变成新的人类主流程阶段。
- 不把 implement、QA、prototype、memory、intent、browser、command catalog 的重构塞进一个超大 feature。

## 4. 目标架构

### 4.1 Authority Kernel

建立一个小而稳定的权威模型模块。

候选模块：

```text
beacon/utils/authority.py
```

职责：

- 定义根目录：
  - `truth_root = docs/beacon/<version>`
  - `projection_root = docs/beacon/<version>/.machine`
  - `runtime_evidence_root = .beacon`
- 定义 artifact role：
  - `truth`
  - `projection`
  - `evidence`
  - `runtime_state`
  - `compat_mirror`
  - `historical_fixture`
- 为 status / help / report 输出提供统一措辞。
- 阻止新代码重新引入 `machine-as-truth` 语义。

验收证据：

- forbidden phrase 静态扫描。
- artifact role 分类单测。
- status / help / report 输出快照测试。

### 4.2 Projection Kernel

把分散的 projection 生成、校验、transaction 写入逻辑收敛到确定性 API。

候选模块：

```text
beacon/utils/projection_kernel.py
```

职责：

- 从 Markdown truth 重建 projection。
- 校验 projection integrity。
- 写入 projection transaction metadata。
- 区分 projection drift 与 truth drift。
- 给 gate / release / doctor / status 提供统一 projection result model。

验收证据：

- projection transaction fixture。
- source hash / projection hash 测试。
- drift 分类测试：
  - Markdown truth 变化。
  - projection 过期。
  - projection 缺失。
  - runtime evidence 缺失。

### 4.3 Compatibility Registry

把 legacy / fallback / compat 从隐式代码路径变成显式 registry。

候选文件：

```text
beacon/compat_registry.py
beacon/compatibility/registry.json
```

registry 字段：

```yaml
compat_id: string
surface: command | qa | prd | prototype | skill | browser | memory | intent
owner: string
reason: string
introduced_before: string
allowed_version_range: string
default_behavior: disabled | warn | blocked | explicit_admission_required
current_replacement: string
retirement_route: string
evidence_required: [string]
```

首批应登记：

- `implement-legacy-cli-loader`
- `qa-auto-test-status-legacy-mirror`
- `skill-admission-legacy-inline`
- `prototype-legacy-wireframe-source`
- `browser-fallback-command-name`
- `prd-legacy-machine-mirror`
- `memory-legacy-projection`
- `intent-legacy-router`
- deprecated / compat command alias，例如 `think`、`workflow`、`auto-test`、`verify`、`gate`、`work`、`prompt`、`save`

验收证据：

- registry schema validation。
- 已知 legacy / fallback / compat surface 都有 registry entry。
- v1.4.11+ hidden fallback 默认 blocked，除非显式 admission。

### 4.4 Gate Registry

建立 gate 身份、stage、阻断级别、reason code、repair route 的统一 registry。

候选模块：

```text
beacon/utils/gate_registry.py
```

gate 分类：

- Requirement package gate。
- Requirement clarity gate。
- AC / test coverage gate。
- Projection transaction gate。
- Evidence chain gate。
- QA evidence gate。
- Release scorecard gate。
- Git governance gate。
- Project metadata gate。
- Version context gate。
- Compatibility admission gate。
- Hook side-effect gate。

验收证据：

- gate registry schema test。
- gate output snapshot test。
- 每个 blocking gate 都有 fail-closed 测试。
- repair route 测试。

## 5. 分阶段行动方案

### Phase 0: Baseline Inventory

目标：

- 在改变行为前，先冻结当前事实。

动作：

- 生成 authority wording、legacy / fallback / compat 引用、command catalog、gate output 清单。
- 记录 implement、QA、PRD、prototype、browser、memory、intent 当前行为。
- feature 冻结后，在 v1.4.11 execution 材料下生成 baseline report。

验收：

- inventory 包含 source file、symbol/function、current behavior、risk、proposed owner、proposed phase。
- 本阶段不改变行为。

审计证据：

- inventory markdown。
- machine-readable inventory JSON。
- 静态扫描输出或确定性 scanner 输出。

### Phase 1: Authority Vocabulary

目标：

- 修掉 machine-as-truth 文案，但不改变核心 runtime 行为。

动作：

- 将 `machine artifacts remain source of truth` 等文案替换为 truth / projection / evidence 词汇。
- 更新 status / help / report 输出。
- 增加 forbidden phrase 测试。
- 引入 authority role helper。

验收：

- v1.4.11 current user-facing output 不再声称 `.machine` 是 requirement truth。
- `.machine` 一致表达为 projection / evidence / read model。
- 现有 projection gates 继续启用。

审计证据：

- forbidden phrase tests。
- status / help / report output snapshot。
- diff 证明没有删除 gate。

### Phase 2: Compatibility Registry，先登记不改行为

目标：

- 先让历史包袱可见，再逐步改变行为。

动作：

- 新增 compatibility registry。
- 登记所有已知 legacy / fallback / compat surface。
- 增加校验：每个 compat alias 或 legacy fallback 都必须映射到 registry。
- 除新增 diagnostics 外，不改变 runtime 行为。

验收：

- registry 覆盖 implement legacy loader、QA legacy mirror、PRD mirror、prototype legacy source、skill legacy inline、browser fallback naming、memory / intent legacy path、compat commands。
- 未登记 fallback 使用时输出 warning 或 diagnostic。
- 本阶段不破坏用户已有 workflow。

审计证据：

- registry validation test。
- known compat surfaces coverage report。
- status / help 输出将 compat surface 标成 compat，而不是 current truth。

### Phase 3: Command Catalog Validation

目标：

- 让命令面显式分层，减少重复和隐藏语义。

动作：

- 将 command catalog 拆分为 current、advanced、compat、deprecated、internal。
- 去重；能从 registry 生成的由 registry 驱动。
- compat / deprecated 命令只能作为兼容面可发现，不作为主线 next route。

验收：

- public mainline 保持紧凑。
- 必要 compat commands 仍可调用，但标记为 compat / deprecated。
- help / status 不把 compat commands 推荐为默认下一步。

审计证据：

- command catalog validation test。
- help snapshot。
- route stability tests。

### Phase 4: QA Legacy Mirror Policy

目标：

- 阻止 legacy auto-test status 继续充当 current QA authority。

动作：

- QA status loading 默认 `allow_legacy=False`。
- legacy auto-test status 只作为 historical evidence，除非显式 admission。
- v1.4.11+ current flow 默认不再双写 legacy QA mirror。
- 为历史项目保留显式 compat mode。

验收：

- current QA status 优先读取 canonical status；只有 legacy status 时 fail closed。
- 显式 legacy admission 会写 compatibility evidence。
- release 不能仅凭 legacy-only QA status pass。

审计证据：

- canonical status pass 测试。
- legacy-only blocked / historical status 测试。
- explicit compat admission 测试。
- release scorecard 测试证明 legacy-only 不能 pass。

### Phase 5: PRD Legacy Mirror Policy

目标：

- 保留 PRD mirror 的兼容证据价值，但不让 stale legacy mirror 成为 current blocker。

动作：

- 将 `.beacon/prd/<slug>.json` 分类为 compat mirror。
- 保留 `.machine/prd/*.canonical.json` 作为 projection。
- v1.4.11+ 下，material audit 将 legacy mirror mismatch 从 `truth_drift` 改为 `compat_mirror_stale`。

验收：

- Markdown PRD 仍是 requirement truth。
- projection stale 仍然阻断。
- legacy mirror stale 降级为 compat warning，除非显式 historical mode 要求它阻断。

审计证据：

- projection stale vs compat mirror stale 的 material audit 测试。
- status 输出能分开 truth / projection / compat findings。

### Phase 6: Implement Package Migration

目标：

- 去掉隐藏 `_implement_legacy_cli` 动态加载，同时保持用户可见的 implement 能力。

动作：

- 把旧 sibling `beacon/commands/implement.py` 中仍需要的函数迁移到 package modules。
- 删除 `_load_legacy_cli_module`。
- 测试改为使用 public app / helper API，不再依赖 `_legacy_cli`。
- 保持 `beacon implement ...` public commands 稳定。

验收：

- `beacon implement` public commands 仍正常路由。
- 测试不再 import 或 assert `_legacy_cli`。
- 不再存在动态 sibling CLI loading。

审计证据：

- import tests。
- CLI smoke tests。
- `_implement_legacy_cli` / `_load_legacy_cli_module` 静态扫描。

### Phase 7: Prototype Legacy Inspector Split

目标：

- 保留历史 prototype 可读性，但不让 legacy source 暗示 current closure。

动作：

- 拆分 current prototype projection / status 与 legacy inspector。
- 将 `legacy_source_only` 改名为 `migration_input_present`。
- 只有 `--include-legacy` 或 compat mode 才展示历史 source details。

验收：

- current prototype gate 默认忽略 legacy source，除非显式 admission。
- 历史 prototype artifacts 仍可检查。
- release 不能因为存在 legacy wireframe file 就 pass。

审计证据：

- prototype status tests。
- release gate tests。
- compat inspector tests。

### Phase 8: Browser Fallback Rename

目标：

- 保留确定性项目命令执行能力，但避免把 fallback 误读为 browser agent 成功执行。

动作：

- 新增推荐参数 / 模型名：`deterministic_command` 或 `explicit_project_command`。
- 保留 `--fallback-cmd` 作为 compat alias。
- evidence 中将 `execution_mode=fallback` 改为 `execution_mode=deterministic_command`。
- 明确区分 browser agent unavailable 与 deterministic project command executed。

验收：

- explicit project command 仍可执行。
- evidence 不会在 browser agent 未运行时声称 browser agent 执行成功。
- compat alias 会产生 compatibility evidence。

审计证据：

- browser adapter tests。
- evidence snapshot tests。
- compat alias tests。

### Phase 9: Memory / Intent Historical Migration Boundary

目标：

- 阻止历史 memory / intent projection 静默影响 current 行为。

动作：

- 将 legacy intent router 标记为 compat router。
- legacy memory 只迁移一次，并写 transaction evidence。
- 默认停止持续双写 legacy projection。
- memory 影响 route 前必须经过 governed recall / admission。

验收：

- current route 不依赖 historical intent fallback，除非显式 admission。
- memory influence 只能是 advisory 且 evidence-bound。
- migration 写入 transaction evidence。

审计证据：

- intent route tests。
- memory migration tests。
- learning influence audit tests。

### Phase 10: Test Directory / Marker Re-Layering

目标：

- 防止测试把 legacy behavior 强行拉回 current contract。

动作：

- 将测试分层：
  - `current_contract`
  - `projection_integrity`
  - `compat_contract`
  - `historical_fixture`
  - `migration`
  - `deprecated`
- current tests 不允许依赖 legacy fallback。
- compat tests 必须绑定 registry entry。

验收：

- test markers 能清晰区分 current behavior 与 compat behavior。
- current test 失败代表 current regression，不是 legacy default 被移除。
- compat behavior 在退场前仍有覆盖。

审计证据：

- test marker validation。
- CI matrix summary。
- registry-bound compat test report。

## 6. 审计矩阵

| Phase | 必须保留 | 必须移除 / 限界 | 必需证据 |
| --- | --- | --- | --- |
| 0 | 当前行为 | 无 | inventory report |
| 1 | projection gates | machine-as-truth 文案 | forbidden phrase tests |
| 2 | compat behavior | 未登记 fallback | registry validation |
| 3 | public commands | 重复 / 隐藏 command catalog 语义 | catalog tests |
| 4 | QA evidence | legacy-only QA pass authority | QA / release tests |
| 5 | PRD projections | legacy mirror 作为 truth blocker | material audit tests |
| 6 | `beacon implement` UX | `_implement_legacy_cli` dynamic loader | CLI / import tests |
| 7 | historical prototype inspection | legacy source 作为 current closure | prototype gate tests |
| 8 | deterministic command execution | browser fallback 语义混淆 | adapter evidence tests |
| 9 | governed memory / intent influence | historical projection 静默影响 current | migration / admission tests |
| 10 | compat coverage | legacy behavior 混入 current tests | marker validation |

## 7. 完成定义

一个 phase 只有同时满足以下条件，才算完成：

- 行为变化已记录。
- 被触碰 artifact 的 authority role 清楚。
- 至少有一个确定性测试覆盖。
- 保留的兼容行为已登记 registry。
- 缺证据时 gate fail closed。
- status / help / report 输出给出 repair route。
- support skill、hook、memory、learning、browser adapter、compat path 都不能直接声称 QA pass、release pass、freeze authority 或 gate verdict。

## 8. 推荐 Feature 切片

不要把整套方案作为一个 feature 实现。推荐切片如下：

1. `authority-vocabulary-and-projection-kernel-contract`
2. `compatibility-registry-and-command-catalog-contract`
3. `qa-prd-legacy-mirror-retirement-contract`
4. `implement-package-legacy-loader-retirement-contract`
5. `prototype-browser-memory-intent-compat-boundary-contract`
6. `test-layering-and-compat-contract-governance`

每个切片都必须独立走：

```text
change/refreeze -> PRD -> user-story -> test-case -> implement -> QA -> release
```

## 9. 明确不建议做的事

不建议：

- 直接删除 `.machine`。
- 直接删除 `auto-test`、`workflow`、`think`、`verify`、`gate` 等历史命令。
- 在一个 feature 里同时重写 implement、QA、prototype、memory、intent、browser 和 command catalog。
- 为了减少代码行数牺牲 QA / release / projection gate 的可校验性。
- 把 compatibility registry 做成新的人类主流程 stage。
- 明知流程是确定性的，还继续把它留在 Skill 文本里让 AI 每次重新理解执行。

## 10. 立即下一步

推荐下一条 change/refreeze：

```bash
beacon change-refreeze "authority-vocabulary-and-projection-kernel-contract" --project . --version v1.4.11
```

这应该是第一刀，因为它风险最低，并且为后续 compatibility registry、gate registry、legacy mirror policy、implement migration 等工作提供统一词汇和投影语义。
