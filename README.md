# Beacon CLI

> Evidence-first Product Workflow Kernel — 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

[![PyPI version](https://img.shields.io/pypi/v/beacon)](https://pypi.org/project/beacon/)
[![Python](https://img.shields.io/pypi/pyversions/beacon)](https://pypi.org/project/beacon/)

---

## 1. 当前版本是什么

Beacon 当前运行时发布口径是 **v1.2.0**。

> 当前发布线：`v1.2.0`

- **CLI 入口**：`beacon <subcommand>`
- **标准 skill 包**：`skills/beacon/`
- **当前包版本**：`1.2.0`
- **最新已接受文档线**：`v1.2.0`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源（source of truth）
- `.beacon/` 是运行时状态，不替代正式交付文档
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径
- README 下方仍保留部分历史发布线细节作为参考；当前发布请优先以 `docs/beacon/v1.2.0/` 为准

如果你只记一条：

> **Beacon 现在是 v1.2.0，写文档看 `docs/beacon/v1.2.0/`，执行命令用 `beacon <subcommand>`。**

补充说明：

- `v1.2.0` 已正式成为当前 CLI/runtime release line
- v1.2.0 将 mainline command simplification、project-skill discovery、prototype anchoring、QA baseline hardening 与 release truth 一起纳入正式发布口径
- `docs/beacon/v1.2.0/` 是当前 release 主阅读面

---

## 2. 当前能力边界

### In scope

Beacon 当前负责：

1. **需求主链编排**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
2. **证据与放行治理**：`auto-test`、`doctor`、`report`、`gate`、`release`
3. **长期事实源治理**：以 `docs/beacon/<version>/` 作为正式版本包入口
4. **工作流恢复与观测**：`status`、`report`、`resume`、`feedback`、`remember`、`recall`
5. **CLI 分层收口**：默认主叙事聚焦 core/support，labs/bridge 不再占用核心心智预算

### Out of scope

Beacon 默认**不负责**：

- 直接写业务代码
- 直接修生产故障
- 直接做数据库迁移/部署执行
- 浏览器守护进程 / persistent QA runtime
- issue tracker 轮询、workspace 调度、agent scheduler
- 在 core 内维护完整 PM 模板大全

### 当前发布线摘要（v1.2.0）

- **mainline command surface hardening**：默认 CLI help 优先暴露 `think → user-story → prd → test-case → implement → qa → gate → release`
- **project-skill discovery**：新增 `beacon skill discover`，提供 detect → recommend → preview → apply 的 explainable starter-pack workflow
- **shared discovery routing**：`help` / `profile` / `skill doctor` 共享 discovery state，不再把项目绑定建议散落在多个入口
- **QA matrix preference**：feature QA 优先消费 QA9 matrix，保持 v1.2.0 的 AC/test traceability 对齐
- **release truth promotion**：`v1.2.0` 已从 requirement freeze 升级为当前 runtime release line，docs / skills / gate artifacts 统一对齐

### 上一发布线摘要（v1.2.0，历史）

- **QA precision closure 已落地**：`qa run <feature>` 会输出 `closure_outcome`、`confidence_calibrated` 与 feature scorecard
- **project-aware QA mainline**：project profile / verify workflow 可正式并入 QA 主线，而不是旁路验收脚本
- **source architecture anti-drift**：`source-architecture/` 成为正式版本包与 materials/gate 检查对象
- **prototype route closure**：prototype 到 frontend route / tab / jump / state 的闭环被提升为显式合同
- **release/gate precision aware**：release/report/status 可消费 confidence、review-required、needs-replay 等语义
- **human QA docs preservation**：machine refresh 默认不覆盖人工编写的 QA requirement 文档

### v1.2.0 新增闭环（历史发布）

- **single-source version truth**：runtime/package/docs default line/planning line 统一走 machine-readable source
- **profile-aware navigator first**：`help` / `status` 先解 version truth、project mode、profile binding、execution surface，再决定 native fallback
- **project skill boundary**：orchestration 在执行前校验 stage / capability / evidence contract，且执行改成显式 argv 而不是 `shell=True`
- **typed learning plane**：learning surface 拆成 `qa_policy` / `design_policy` / `contract_policy` / `rewrite_policy` / `debug_policy` / `benchmark_policy`
- **takeover baseline gate**：takeover 项目缺 current-state baseline 或未冻结时会阻断 `implement`

### 上一发布线摘要（v1.1.7）

- **完整主链工作流**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- **revision 生命周期闭环**：新增 `freeze` / `reopen`，支持 frozen baseline、supersede 与 reopen
- **原生实现执行面**：`implement` 内建 `native-single` / `native-team` runner，同时保留 adapter runner
- **项目级 skill/profile**：支持 `profile`、`skill bind`、`skill registry`，允许项目声明自己的 verify/delivery/debug skill
- **编排式验证执行面**：支持 `orchestrate run` / `verify run`，让 Beacon 可按项目 profile 调用 skill 执行链路验证
- **强证据验收门禁**：`review quality` / `review accept` 会检查 `required_evidence`、`required_cases` 与 `contract_drift`
- **story item writeback**：implement / verify / accept 会回写 story / AC / TEST item machine state
- **阶段感知导航**：`help` / `doctor advise` / scoring 能输出当前阶段、阻塞原因、下一步命令
- **人机分层闭环**：`docs/beacon/<version>/execution/` 保持 Markdown-first，人类主读；`docs/beacon/<version>/.machine/` 作为机器正式读取面
- **release 语义**：`release` 是 post-gate action，不属于 workflow 内部阶段
- **单一事实源**：`docs/beacon/<version>/` 优先于 `.beacon/`
- **版本包最小闭环**：`SUMMARY / execution / prd / user-story / qa/test-cases / release`

### v1.2.0 为什么重要

v1.2.0 相比 v1.1.11 的核心新增，不是继续堆更多 workflow 节点，而是把 design governance、version truth、execution routing 与 typed learning plane 正式并入 release line：

- design brief + design-system contract
- web guideline review + prototype review writeback
- single-source version truth
- profile-aware execution surface routing
- typed learning-plane governance
- takeover baseline runtime gate
- implement branch preflight

你现在可以从这些入口阅读当前 release line：

- `docs/beacon/v1.2.0/SUMMARY.md`
- `docs/beacon/v1.2.0/execution/index.md`
- `docs/beacon/v1.2.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.2.0/release/v1.2.0.md`

### v1.1.7 为什么重要（历史）

v1.1.7 相比 v1.1.6 的核心新增，不是单纯补命令，而是补：

- **项目级 profile**
- **项目特定 skill 接入**
- **verify / orchestration 编排**
- **required evidence / must-run case gate**

也就是让 Beacon 开始回答：

> “这个项目真正该怎么验？”  
> 而不只是“通用工作流理论上该怎么验？”

像 Rolo 这类多服务项目，可以通过 profile 把：

- `verify`
- `delivery`
- `debug`
- `pipeline`

绑定到外部项目 skill（例如 `rolo-dev`），再把：

- UAT pipeline
- gateway smoke
- interface verify
- logs / SQL evidence
- 核心业务必跑用例

正式纳入 accept gate。

---

## 3. 当前推荐命令

### 安装

```bash
pip install beacon
# 或
cd beacon && pip install -e ".[dev]"
```

### 当前推荐命令风格

```bash
beacon <subcommand> ...
```

### Quick Start / 30-second path

如果你只想用最短路径快速跑通 Beacon v1.2.0，先执行：

```bash
beacon ask "Create a release-ready requirement package" --project-root . --version v1.2.0 --plan-only --json
beacon workflow start "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0
beacon doctor verify-materials --project-root . --version v1.2.0 --json
beacon gate check release --project-root . --version v1.2.0 --json
```

如果你想继续读完整命令文档，请看下面的 Command Docs 入口。

### Command Docs / 命令文档入口

如果你想按当前发布线阅读 v1.2.0 文档，建议从这里进入：

- `docs/beacon/v1.2.0/SUMMARY.md`：当前版本总览
- `docs/beacon/v1.2.0/execution/index.md`：执行面索引与推荐阅读顺序
- `docs/beacon/v1.2.0/execution/architecture-blueprint.md`：架构蓝图主文档
- `docs/beacon/v1.2.0/execution/workflow-usage-guide.md`：完整工作流使用指南
- `docs/beacon/v1.2.0/execution/natural-language-trigger-handbook.md`：稳定可靠的自然语言触发手册
- `docs/beacon/v1.2.0/execution/boundaries.md`：边界与放行约束
- `docs/beacon/v1.2.0/execution/command-surface-simplification-blueprint.md`：command surface simplification blueprint
- `docs/beacon/v1.2.0/execution/project-skill-qa-evolution-blueprint.md`：project skill / QA evolution blueprint
- `docs/beacon/v1.2.0/execution/target-project-kernel-blueprint.md`：target project kernel blueprint
- `docs/beacon/v1.2.0/release/v1.2.0.md`：当前发布说明

如果你关注 v1.2.0 当前闭环增强线，请优先读：

- `docs/beacon/v1.2.0/user-story/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- `docs/beacon/v1.2.0/prd/beacon-v1.2.0-command-simplification-and-project-skill-workflow.md`
- `docs/beacon/v1.2.0/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.2.0/execution/target-project-kernel-blueprint.md`
- `docs/beacon/v1.2.0/source-architecture/index.md`

### 最小工作流

```bash
# 1) 启动需求主链
beacon workflow start "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0

# 2) 生成主链文档
beacon think start "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0
beacon user-story create "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0
beacon prd create "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0
beacon test-case create "Beacon v1.2.0 governance closure baseline" --project . --version v1.2.0

# 2.5) 配置并执行实现适配
beacon skill list
beacon skill registry list --json
beacon profile create demo demo --json
beacon skill bind "Beacon v1.2.0 governance closure baseline" --profile demo --version v1.2.0
beacon implement list-runners --json
beacon doctor repair-package --project-root . --version v1.2.0 --json
beacon implement run "Beacon v1.2.0 governance closure baseline" --runner omx --json
beacon qa run "Beacon v1.2.0 governance closure baseline" --profile demo --json
beacon verify run "Beacon v1.2.0 governance closure baseline" --profile demo --json
beacon orchestrate run "Beacon v1.2.0 governance closure baseline" --profile demo --dry-run --json

# 2.6) 标准 skill + script 触发
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh skill list

# 3) 状态 / 验收
beacon status --board --project-root . --version v1.2.0
beacon qa status --project .
beacon gate check release --project-root . --version v1.2.0
```

### v1.2.0 project-aware 示例（以 Rolo 思路为例）

```bash
beacon profile create rolo rolo-uat --example rolo-uat --json
beacon skill bind "KZFJ-1110 启动页营销内容配置" --profile rolo-uat --version v1.2.0
beacon verify run "KZFJ-1110 启动页营销内容配置" \
  --project . \
  --version v1.2.0 \
  --profile rolo-uat \
  --json
```

这个模式适合：

- 多服务项目
- 需要 UAT / pipeline / gateway / SQL / logs 联合验收
- 需要 Beacon 在 accept 前阻断“关键 case 没跑”的场景

### 自然语言入口

如果用户记不住太多命令，优先只教这 3 个：

```bash
beacon ask "<自然语言目标>" --project-root . --version v1.2.0 --plan-only --json
beacon help --project-root . --version v1.2.0 --feature "<feature>" --json
beacon status --board --project-root . --version v1.2.0
```

推荐配套阅读：

- `docs/beacon/v1.2.0/execution/natural-language-trigger-handbook.md`

```bash
# 默认只生成计划，不执行
beacon ask "请帮我梳理 Beacon v1.2.0 的治理闭环与交付闭环" --plan-only --json

# 显式执行（带边界/置信度闸门）
beacon ask "请生成用户故事并给出验收标准" --execute --json
```

### 诊断与报告

```bash
beacon doctor --project-root . --json
beacon doctor verify-materials --project-root . --version v1.2.0 --json
beacon doctor verify-delivery --project-root . --version v1.2.0 --json
beacon report --machine latest --project-root . --version v1.2.0
```

---

## 4. 当前交付工件

当前正式交付主链只看 `docs/beacon/<version>/`。

### 主链工件

```text
docs/beacon/<version>/
├── SUMMARY.md
├── user-story/
├── prd/
├── qa/test-cases/
├── release/
└── execution/
```

### execution 层最低必备项

```text
docs/beacon/<version>/execution/
├── boundaries.md
├── index.md
└── human-facing markdown docs

docs/beacon/<version>/.machine/execution/
├── delivery-manifest.json
├── change-impact.json
├── config.json
├── source.json
├── git-alignment.json
└── terminal.json
```

### 运行时证据

```text
.beacon/
├── auto-test-status.json
├── gate-report.json
├── evidence-manifest.json
├── coverage-summary.json
├── memory/
└── runs/
```

### 当前验收工件（v1.2.0）

- `docs/beacon/v1.2.0/SUMMARY.md`
- `docs/beacon/v1.2.0/execution/index.md`
- `docs/beacon/v1.2.0/execution/architecture-blueprint.md`
- `docs/beacon/v1.2.0/execution/boundaries.md`
- `docs/beacon/v1.2.0/execution/command-surface-simplification-blueprint.md`
- `docs/beacon/v1.2.0/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.2.0/execution/target-project-kernel-blueprint.md`
- `docs/beacon/v1.2.0/release/v1.2.0.md`
- `docs/beacon/v1.2.0/qa/test-cases/index.md`
- `docs/beacon/v1.2.0/.machine/qa/beacon-v1.2.0-command-simplification-and-project-skill-workflow.story-scenario-map.json`

如果你要看这次补齐的 governance / boundary / learning-plane 收口，请读：

- `docs/beacon/v1.2.0/SUMMARY.md`
- `docs/beacon/v1.2.0/execution/index.md`
- `docs/beacon/v1.2.0/release/v1.2.0.md`
- `docs/beacon/v1.1.11/.machine/execution/beacon-prototype-reference-pack-v2.revision.json`
- `docs/beacon/v1.1.11/.machine/user-story/beacon-prototype-reference-pack-v2.json`
- `docs/beacon/v1.1.11/.machine/qa/beacon-prototype-reference-pack-v2.ac-test-matrix.json`
- `docs/beacon/v1.1.11/.machine/qa/beacon-prototype-reference-pack-v2.story-scenario-map.json`

---

## 5. 当前验证命令

### 最小交付验证

```bash
python3 -m pytest -q
beacon doctor verify-materials --project-root . --version v1.2.0 --json
beacon doctor verify-delivery --project-root . --version v1.2.0 --json
beacon gate check release --project-root . --version v1.2.0 --json
beacon release check v1.2.0 --project .
```

### 自动生成验收审计

```bash
beacon release scorecard v1.2.0 --project . --json
beacon report --human latest --project-root . --version v1.2.0
```

---

## 6. 后续迭代版本文档编写约定

后续版本（如 `v1.1.11`、`v1.2.0`）继续沿用下面这套方案。

### README 编写原则

README 只保留 5 类当前信息：

1. 当前版本是什么
2. 当前能力边界
3. 当前推荐命令
4. 当前交付工件
5. 当前验证命令

历史版本内容不再写成“当前能力说明”，只能放：

- 兼容说明
- 历史参考链接
- 迁移附录

### 每个新版本最少应补齐的文档

```text
docs/beacon/<version>/
├── SUMMARY.md
├── user-story/
├── prd/
├── qa/test-cases/
├── release/
└── execution/
    └── boundaries.md
```

### 版本发布时的文档更新顺序

1. 更新版本元信息
   - `pyproject.toml`
   - `beacon/__init__.py`
   - `SKILL.md`
   - `skills/beacon/SKILL.md`
   - `AGENTS.md`
   - `CLAUDE.md`
2. 更新当前版本 README 口径
3. 生成/刷新当前版本验收文档

### 当前发布线参考文档

- [v1.2.0 Summary](./docs/beacon/v1.2.0/SUMMARY.md)
- [v1.2.0 Execution Index](./docs/beacon/v1.2.0/execution/index.md)
- [v1.2.0 Architecture Blueprint](./docs/beacon/v1.2.0/execution/architecture-blueprint.md)
- [v1.2.0 Boundaries](./docs/beacon/v1.2.0/execution/boundaries.md)
- [v1.2.0 Command Surface Blueprint](./docs/beacon/v1.2.0/execution/command-surface-simplification-blueprint.md)
- [v1.2.0 Project Skill / QA Blueprint](./docs/beacon/v1.2.0/execution/project-skill-qa-evolution-blueprint.md)
- [v1.2.0 Target Project Kernel Blueprint](./docs/beacon/v1.2.0/execution/target-project-kernel-blueprint.md)
- [v1.2.0 Release Notes](./docs/beacon/v1.2.0/release/v1.2.0.md)

---

**版本**: v1.2.0
