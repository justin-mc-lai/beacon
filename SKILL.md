---
name: beacon
version: 1.2.0
description: Evidence-first Product Workflow Kernel for product thinking, user stories, PRDs, test cases, and release workflows
---

# Beacon - Evidence-first Product Workflow Kernel

> **Skill Version**: v1.2.0
> **CLI Version**: v1.2.0
> **Last Updated**: 2026-04-10

Beacon 是 AI 产品工作流内核，提供需求澄清、用户故事、PRD、测试用例、证据闭环与发布门禁的统一工作流。

## 文档角色与固定结构模板

### 文档角色

- `SKILL.md`（root）= **主文档 / product primary**
  - 面向人类与通用 skill reader 的完整产品说明入口
  - 负责讲清楚 Beacon 是什么、适合谁、怎么上手、怎么读 docs、怎么排障
- `skills/beacon/SKILL.md` = **辅文档 / package supplementary**
  - 面向标准 `skills/<name>/` 目录的包装入口
  - 必须镜像主文档的核心结构，但允许更短、更偏 wrapper/operator 视角

### 主辅同步规则

1. 任何产品定位、版本口径、workflow 主模型变化，必须同时更新 root 与 packaged skill。
2. 如果两者发生冲突：
   - **产品内容以 root `SKILL.md` 为准**
   - **标准 skill 打包入口以 `skills/beacon/SKILL.md` 为准**
3. packaged skill 不是自由发挥版；它必须按主文档的固定结构做缩写镜像。

### 固定结构模板

为避免后续继续漂移，两个 skill 文档都必须稳定覆盖以下 **结构槽位**（允许在 packaged 版本里做压缩或合并，但不能缺项）：

1. 当前版本 / 发布线
2. 产品定位（Beacon 是什么）
3. 适合谁 / 不适合谁
4. Quick Start / 快速上手
5. Workflow Model / 主工作流模型
6. Current Product Surfaces / 当前产品面
7. Why This Skill Matters / 为什么重要
8. Recommended Reading Order / 推荐阅读顺序
9. Common Usage Modes / 常见使用场景
10. Command Surface / How to Use / 命令入口
11. Lifecycle Navigation Rules / 阶段导航规则
12. Docs / Troubleshooting / Examples / References

后续若新增 section，应优先挂到以上 12 段中的一个，而不是随意插入新层级。

## 当前版本与发布线

- **当前发布线**：`v1.2.0`
- **当前包版本**：`1.2.0`
- **最新已接受文档线**：`v1.2.0`
- **当前已落地实现线**：`v1.2.0`（mainline command simplification / project-skill discovery / shared discovery routing / prototype anchoring / QA baseline hardening 已在仓内落地，并有实现测试覆盖）
- **当前补充增强线**：`v1.2.1`（Codex `UserPromptSubmit` → Beacon debug prompt adaptation / guidance / debug evidence ingress 已落地）
- **上一稳定基线**：`v1.1.12`（design governance / version truth / profile-aware routing / typed learning plane / takeover baseline gate）

如果你只记一条：

> **正式包版本现在是 `v1.2.0`，当前实现与文档主线统一阅读 `docs/beacon/v1.2.0/`；历史闭环增强线可回看 `docs/beacon/v1.1.9/`。**

`v1.2.0` 说明：

- `v1.2.0` 已正式成为 current runtime release line
- command-surface simplification、project-skill discovery、prototype anchoring 与 QA baseline bundle 已进入正式发布口径
- 当前最稳妥的阅读方式是直接以 `docs/beacon/v1.2.0/` 作为 current line
- `docs/beacon/v1.2.1/` 是当前针对 Codex hook / debug prompt adaptation 的 supplement line

## Beacon 到底是什么

Beacon 不是单一命令，也不是“帮你写几份 PM 文档”的模板集合。

它更像一个面向 AI/人协作的软件交付内核，把下面这些东西收敛到同一套版本化材料中：

- 需求澄清（think / ask）
- 用户故事（user-story）
- PRD（prd）
- 测试用例与验收覆盖（test-case / qa）
- 实现摘要与技术归档（implement / review）
- gate / release 放行治理
- memory / status / report / resume 等恢复与观测面

一句话说：

> **Beacon 是把“需求 → 实现 → 证据 → gate / release”压成可审计闭环的 CLI 内核。**

## 这套 skill 适合谁

### 适合
- 想把需求、测试、实现、发布统一到一套版本化材料里的 AI 产品团队
- 想让 Agent 在项目里遵循固定 lifecycle，而不是每次从空白 prompt 开始的人
- 想做 evidence-first / machine-backed truth / gate-driven release 的项目
- 正在做项目接管、feature delivery、release readiness、version planning 的团队

### 不适合
- 只想让工具直接写业务代码，不关心 requirement material / verification / release governance 的场景
- 只需要一个简单模板生成器，不需要 lifecycle / traceability / gate 的场景
- 把 Beacon 当成通用运维平台、部署平台或浏览器自动化平台本体的场景

## 10 分钟快速上手

### 最短路径

```bash
beacon workflow start "My feature" --project . --version v1.2.0
beacon think start "My feature" --project . --version v1.2.0
beacon user-story create "My feature" --project . --version v1.2.0
beacon prd create "My feature" --project . --version v1.2.0
beacon test-case create "My feature" --project . --version v1.2.0
beacon help --project-root . --version v1.2.0 --feature "My feature" --json
```

### 如果你已经有实现与验证链

```bash
beacon implement list-runners --json
beacon implement plan "My feature" --project . --version v1.2.0 --json
beacon implement run "My feature" --project . --version v1.2.0 --runner auto --json
beacon implement run "My feature" --project . --version v1.2.0 --runner auto --auto-qa --auto-qa-follow-handoff --auto-qa-max-rounds 3 --json
beacon qa run "My feature" --project . --version v1.2.0 --json
beacon review quality "My feature" --project . --version v1.2.0 --json
beacon gate check release --project-root . --version v1.2.0 --json
```

### 如果你只想看当前该做什么

```bash
beacon status --board --project-root . --version v1.2.0
beacon help --project-root . --version v1.2.0 --feature "My feature" --json
```

### 如果你要把 Codex 原始用户输入接入 Beacon debug

```bash
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"请帮我梳理登录需求并进入 Beacon 主链"}' \
  | beacon debug codex-user-prompt-submit --project-root . --version v1.2.1 --json
```

## Beacon 的主工作流模型

Beacon 当前的标准主链是：

```text
think
→ user-story
→ prd
→ [prototype]
→ test-case
→ implementation
→ verify / qa
→ gate
→ release
```

其中：

- `docs/beacon/<version>/` 是**正式版本包**
- `.beacon/` 是**运行时状态**
- `execution/` 是**人类主读执行面**
- `.machine/` 是**机器正式读取面**

这也是 Beacon 与普通 prompt 模板最大的区别：

> **它不是只生成内容，而是要求内容、执行、证据、放行都对齐。**

## 当前产品面（v1.2.0）

当前正式发布线的几个关键能力面：

1. **完整需求主链**
   - `workflow / think / user-story / prd / test-case`
2. **项目接管入口**
   - `init`
3. **实现技术归档**
   - `implement`
   - `implement plan / compile-plan`
   - implementation-plan gate / task progress / writeback closure
   - `technical-implementation-*`
4. **Feature-aware QA 与状态化验收**
   - `qa run <feature>`
   - `qa evolve <feature>`
   - `qa session`
   - `story-exhaustive`
5. **Debug / Recovery / Control Plane**
   - `debug`
   - `resume`
   - control / exhaustion / checkpoint semantics
   - `debug codex-user-prompt-submit`
6. **Review / Gate / Release / Learning 治理**
   - `review`
   - `gate`
   - `release`
   - `release scorecard`
   - keep/discard + evo harness

### QA 的 skill 提示词必须遵守第一性原则

对 `qa` 主链来说，Beacon 不允许“为了显得更努力而继续跑测试”。

正确顺序只能是：

```text
user story / AC order
→ scenario divergence
→ current-round execution
→ evidence pack
→ coverage_current / coverage_gap
→ continue_decision
→ severe blocker? stop_for_repair
→ repair handoff
→ beacon help resume
→ next QA round with test-case backfill
→ release guidance
```

执行规则：

1. **先顺序，后发散**
   - 必须先按 user story / AC 顺序推进
   - 再发散到 happy / negative / boundary / recovery / compatibility

2. **先证据，后结论**
   - 没有 evidence pack、replay、coverage snapshot，不得 claim closure

3. **阻塞严重就停**
   - 遇到 auth/session 失效、required replay 缺失、project evidence gate 不满足、contract drift、environment instability
   - 本轮 QA 应 `stop_for_repair`
   - 不允许继续堆无效 case 制造“覆盖率上升”

4. **每轮都要告诉人类下一步**
   - QA 输出必须给 blocker summary、repair handoff、`resume_command`
   - 修复后优先通过
     `beacon help --project-root . --version v1.2.0 --feature "<feature>" --json`
     获取下一轮命令

5. **下一轮必须先补缺口**
   - 若上一轮仍有 coverage gap / missing test cases / missing replay obligations
   - 则先补 `test-case` / matrix，再继续 QA

6. **浏览器 QA 默认继承用户态**
   - 默认 browser path 以 `browser-use` 为主
   - 必须保留 session manifest、profile ref、cookies ref、storage-state ref
   - 让下一轮 QA 复用同一用户上下文

## 为什么这套 skill 重要

如果没有 Beacon，很多团队会把这些东西拆散在：

- 对话记录里
- 临时文档里
- 实现日志里
- QA 表格里
- release 口头结论里

Beacon 的价值在于把它们重新并成同一个系统：

```text
requirement material
→ implementation result
→ verification evidence
→ gate decision
→ release readiness
```

这也是为什么 Beacon skill 不只是命令包装，而是一个**产品工作流入口**。

## 推荐阅读顺序

1. `docs/beacon/v1.2.0/SUMMARY.md`
2. `docs/beacon/v1.2.0/execution/index.md`
3. `docs/beacon/v1.2.0/execution/architecture-blueprint.md`
4. `docs/beacon/v1.2.0/execution/workflow-usage-guide.md`
5. `docs/beacon/v1.2.0/execution/natural-language-trigger-handbook.md`
6. `docs/beacon/v1.2.0/execution/qa-autoresearch-usage-guide.md`
7. `docs/beacon/v1.2.0/execution/autoresearch-module-evolution.md`
8. `docs/beacon/v1.2.0/execution/requirement-anchor-implementation-blueprint.md`
9. `docs/beacon/v1.2.0/release/v1.2.0.md`

如果你关注上一轮闭环增强基线，再看：

1. `docs/beacon/v1.1.9/SUMMARY.md`
2. `docs/beacon/v1.1.9/execution/closure-loop-blueprint.md`
3. `docs/beacon/v1.1.9/prd/beacon-closure-control-learning-overlay.md`
4. `docs/beacon/v1.1.9/release/v1.1.9.md`

如果你关注下一轮 QA 精准度 / 自动训练增强，再看：

1. `docs/beacon/v1.2.0/SUMMARY.md`
2. `docs/beacon/v1.2.0/prd/beacon-version-truth-profile-boundary-governance.md`
3. `docs/beacon/v1.2.0/prd/beacon-prototype-design-governance-loop.md`
4. `docs/beacon/v1.2.0/execution/requirement-anchor-implementation-blueprint.md`

## 常见使用场景

### 场景 A：从 0 到 1 建需求包
- 用 `workflow` 启主链
- 生成 think / user-story / prd / test-case
- 用 `help` 看下一步

### 场景 B：已经有 feature，想进入实现与验收
- 用 `implement plan`
- 用 `implement`
- 用 `qa`
- 用 `review quality`
- 用 `gate`

### 场景 C：项目接管 / 多人协作
- 用 `init`
- 用 `project lifecycle onboarding`
- 用 `status / report / resume`

### 场景 D：版本迭代与闭环复盘
- 用 `report / release / evolution-summary / version`
- 读取 `docs/beacon/<version>/execution/` 与 `.machine/`

## 命令入口（Command Surface）

主入口：

- `beacon <subcommand>`

兼容入口：

- `python3 -m beacon.main <subcommand>`
- `bash skills/beacon/scripts/run_beacon.sh <subcommand> ...`
- `python3 scripts/check_skill_drift.py --project-root . --json`

## 阶段导航规则

当你不确定当前 feature 下一步该做什么时，优先按下面顺序走：

1. `beacon status --board --project-root . --version <version>`
2. `beacon help --project-root . --version <version> --feature "<feature>" --json`
3. 如果 revision 未冻结，先 `beacon freeze ...`
4. 如果已冻结但 implementation plan 缺失或漂移，先 `beacon implement plan ...`
5. 如果 revision 已 superseded 或 change request 未处理，先 `beacon reopen ...`
6. 如果状态不一致或卡住，运行 `beacon doctor --project-root . --json`

不要在 Beacon 已经能计算下一步时靠猜。

## 文档入口与故障排查

### 文档入口
- `docs/beacon/v1.2.0/SUMMARY.md`
- `docs/beacon/v1.2.0/execution/index.md`
- `docs/beacon/v1.2.0/execution/workflow-usage-guide.md`
- `docs/beacon/v1.2.0/execution/natural-language-trigger-handbook.md`
- `docs/beacon/v1.2.0/execution/qa-autoresearch-usage-guide.md`
- `docs/beacon/v1.2.0/execution/autoresearch-module-evolution.md`
- `docs/beacon/v1.2.0/release/v1.2.0.md`
- `docs/beacon/v1.2.0/prd/beacon-version-truth-profile-boundary-governance.md`

### 常见问题
- 不确定当前阶段下一步做什么：
  - `beacon help --project-root . --version v1.2.0 --feature "<feature>" --json`
- 觉得材料状态不一致：
  - `beacon doctor --project-root . --json`
  - `beacon doctor verify-materials --project-root . --version v1.2.0 --json`
- 不确定 release/gate 是否已闭环：
  - `beacon gate check release --project-root . --version v1.2.0 --json`
- 旧版本 package 想补到当前 runtime 能力：
  - `beacon doctor upgrade-package --project-root . --version <old-version> --json`
- 想看当前全局状态：
  - `beacon status --board --project-root . --version v1.2.0`

## 命令触发（CLI/Skill 单一事实源）

**命令口径（统一）**：
- `beacon <subcommand>`（推荐）
- 脚本方式（兼容）：`python3 -m beacon.main <subcommand> ...`
- 历史模块入口（兼容）：`python3 -m beacon.think ...`（保留兼容，但不作为推荐入口）

> 注意：对外建议统一使用 `beacon <subcommand>`；正式交付文档统一读取 `docs/beacon/<version>/`。
> 标准 skill 包目录位于 `skills/beacon/`；根 `SKILL.md` 保留为兼容入口。

命令清单由 `beacon/command_catalog.py::SUPPORTED_SUBCOMMANDS` 自动生成，使用：

```bash
python3 scripts/sync_skill_commands.py
```

或校验：

```bash
python3 scripts/sync_skill_commands.py --check
```

<!-- AUTO-COMMANDS:START -->
### 可触发关键词（自动同步）

| 关键词 | 对应子命令 |
|--------|------------|
| `beacon ask` | `ask` |
| `beacon analyze` | `analyze` |
| `beacon api-design` | `api-design` |
| `beacon auto-test` | `auto-test` |
| `beacon qa` | `qa` |
| `beacon brainstorm` | `brainstorm` |
| `beacon data-dictionary` | `data-dictionary` |
| `beacon debug` | `debug` |
| `beacon design` | `design` |
| `beacon doctor` | `doctor` |
| `beacon evolution-summary` | `evolution-summary` |
| `beacon feedback` | `feedback` |
| `beacon freeze` | `freeze` |
| `beacon help` | `help` |
| `beacon gate` | `gate` |
| `beacon implement` | `implement` |
| `beacon init` | `init` |
| `beacon jtbd` | `jtbd` |
| `beacon kano` | `kano` |
| `beacon moscow` | `moscow` |
| `beacon persona` | `persona` |
| `beacon prototype` | `prototype` |
| `beacon prompt` | `prompt` |
| `beacon profile` | `profile` |
| `beacon prd` | `prd` |
| `beacon qa` | `qa` |
| `beacon orchestrate` | `orchestrate` |
| `beacon ralph-bridge` | `ralph-bridge` |
| `beacon recall` | `recall` |
| `beacon release` | `release` |
| `beacon reopen` | `reopen` |
| `beacon remember` | `remember` |
| `beacon report` | `report` |
| `beacon review` | `review` |
| `beacon resume` | `resume` |
| `beacon roadmap` | `roadmap` |
| `beacon run` | `run` |
| `beacon save` | `save` |
| `beacon skill` | `skill` |
| `beacon status` | `status` |
| `beacon team` | `team` |
| `beacon test-case` | `test-case` |
| `beacon test-progress` | `test-progress` |
| `beacon think` | `think` |
| `beacon ui-spec` | `ui-spec` |
| `beacon user-story` | `user-story` |
| `beacon verify` | `verify` |
| `beacon version` | `version` |
| `beacon wireframe` | `wireframe` |
| `beacon work` | `work` |
| `beacon workflow` | `workflow` |

### 完整子命令清单（自动同步）

| 子命令 | 推荐触发 |
|-------|----------|
| `ask` | `beacon ask` |
| `analyze` | `beacon analyze` |
| `api-design` | `beacon api-design` |
| `auto-test` | `beacon auto-test` |
| `qa` | `beacon qa` |
| `brainstorm` | `beacon brainstorm` |
| `data-dictionary` | `beacon data-dictionary` |
| `debug` | `beacon debug` |
| `design` | `beacon design` |
| `doctor` | `beacon doctor` |
| `evolution-summary` | `beacon evolution-summary` |
| `feedback` | `beacon feedback` |
| `freeze` | `beacon freeze` |
| `help` | `beacon help` |
| `gate` | `beacon gate` |
| `implement` | `beacon implement` |
| `init` | `beacon init` |
| `jtbd` | `beacon jtbd` |
| `kano` | `beacon kano` |
| `moscow` | `beacon moscow` |
| `persona` | `beacon persona` |
| `prototype` | `beacon prototype` |
| `prompt` | `beacon prompt` |
| `profile` | `beacon profile` |
| `prd` | `beacon prd` |
| `qa` | `beacon qa` |
| `orchestrate` | `beacon orchestrate` |
| `ralph-bridge` | `beacon ralph-bridge` |
| `recall` | `beacon recall` |
| `release` | `beacon release` |
| `reopen` | `beacon reopen` |
| `remember` | `beacon remember` |
| `report` | `beacon report` |
| `review` | `beacon review` |
| `resume` | `beacon resume` |
| `roadmap` | `beacon roadmap` |
| `run` | `beacon run` |
| `save` | `beacon save` |
| `skill` | `beacon skill` |
| `status` | `beacon status` |
| `team` | `beacon team` |
| `test-case` | `beacon test-case` |
| `test-progress` | `beacon test-progress` |
| `think` | `beacon think` |
| `ui-spec` | `beacon ui-spec` |
| `user-story` | `beacon user-story` |
| `verify` | `beacon verify` |
| `version` | `beacon version` |
| `wireframe` | `beacon wireframe` |
| `work` | `beacon work` |
| `workflow` | `beacon workflow` |
<!-- AUTO-COMMANDS:END -->

### CLI 调用示例（workflow）

```bash
# 推荐
beacon workflow start "Beacon v1.2.0 release line" --project /abs/path/to/project --version v1.2.0

# 兼容
python3 -m beacon.main workflow start "Beacon v1.2.0 release line" --project /abs/path/to/project --version v1.2.0
```

## Gate 检查

| 阶段 | 门控项 | 判定标准 |
|------|--------|---------|
| think | 收敛门 | 无 blocking=true 的未决项 |
| user-story | AC门 | 七维 AC 完整 |
| prd | 风险门 | critical/high 冲突已解决 |
| test-case | 覆盖门 | AC→TC 覆盖矩阵完整 |
| release | 放行门 | formal package / delivery / evidence / gate contract 通过 |

## 输出目录

```
docs/beacon/{version}/
├── SUMMARY.md
├── prd/{feature}.md
├── user-story/{feature}.md
├── qa/test-cases/{feature}.md
├── release/{version}.md
├── execution/index.md
├── execution/boundaries.md
├── execution/*.md              # human-readable execution docs only
└── .machine/execution/*.json   # machine-readable execution artifacts only
```

## 参考文档

- `docs/beacon/v1.1.9/SUMMARY.md`
- `docs/beacon/v1.1.9/execution/index.md`
- `docs/beacon/v1.1.9/execution/architecture-blueprint.md`
- `docs/beacon/v1.1.9/execution/closure-loop-blueprint.md`
- `docs/beacon/v1.1.9/research/beacon-pua-exhaustiveness-layer-analysis.md`
- `docs/beacon/v1.1.9/research/beacon-karpathy-autoresearch-evo-analysis.md`
- `docs/beacon/v1.1.9/release/v1.1.9.md`
- `skills/beacon/SKILL.md`
- `references/acceptance-criteria.md`
- `references/user-story-mapping.md`

### Skill 同步校验

一键检查 repo / Claude / Codex 三处 skill 是否漂移：

```bash
python3 scripts/check_skill_drift.py --project-root . --json
beacon skill sync-check --project-root . --json
```

---

**版本**: v1.2.0
