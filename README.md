# Beacon CLI

> Evidence-first Product Workflow Kernel — 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

[![PyPI version](https://img.shields.io/pypi/v/beacon)](https://pypi.org/project/beacon/)
[![Python](https://img.shields.io/pypi/pyversions/beacon)](https://pypi.org/project/beacon/)

---

## 1. 当前版本是什么

Beacon 当前单一发布口径是 **v1.1.6**。

> 当前发布线：`v1.1.6`

- **CLI 入口**：`beacon <subcommand>`
- **标准 skill 包**：`skills/beacon/`
- **当前包版本**：`1.1.6`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源（source of truth）
- `.beacon/` 是运行时状态，不替代正式交付文档
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径

如果你只记一条：

> **Beacon 现在是 v1.1.6，写文档看 `docs/beacon`，执行命令用 `beacon <subcommand>`。**

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

### 当前发布线摘要（v1.1.6）

- **完整主链工作流**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- **revision 生命周期闭环**：新增 `freeze` / `reopen`，支持 frozen baseline、supersede 与 reopen
- **原生实现执行面**：`implement` 内建 `native-single` / `native-team` runner，同时保留 adapter runner
- **story item writeback**：implement / verify / accept 会回写 story / AC / TEST item machine state
- **阶段感知导航**：`help` / `doctor advise` / scoring 能输出当前阶段、阻塞原因、下一步命令
- **人机分层闭环**：`docs/beacon/<version>/execution/` 保持 Markdown-first，人类主读；`docs/beacon/<version>/.machine/` 作为机器正式读取面
- **release 语义**：`release` 是 post-gate action，不属于 workflow 内部阶段
- **单一事实源**：`docs/beacon/<version>/` 优先于 `.beacon/`
- **版本包最小闭环**：`SUMMARY / execution / prd / user-story / qa/test-cases / release`

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

如果你只想用最短路径快速跑通 Beacon v1.1.6，先执行：

```bash
beacon ask "Create a release-ready requirement package" --project-root . --version v1.1.6 --plan-only --json
beacon workflow start "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon doctor verify-materials --project-root . --version v1.1.6 --json
beacon gate check release --project-root . --version v1.1.6 --json
```

如果你想继续读完整命令文档，请看下面的 Command Docs 入口。

### Command Docs / 命令文档入口

如果你想按不同深度阅读 v1.1.6 的命令文档，建议从这里进入：

- `docs/beacon/v1.1.6/COMMANDS.md`：命令文档总入口
- `docs/beacon/v1.1.6/getting-started-10-minutes.md`：新手 10 分钟上手教程
- `docs/beacon/v1.1.6/execution/command-guide-readme.md`：README 风格命令指南
- `docs/beacon/v1.1.6/execution/scenario-quick-reference.md`：按典型场景整理的速查表
- `docs/beacon/v1.1.6/execution/command-reference.md`：完整命令树与命令说明
- `docs/beacon/v1.1.6/execution/command-reference-bilingual.md`：中英双语版

### 最小工作流

```bash
# 1) 启动需求主链
beacon workflow start "Beacon v1.1.6 layered delivery" --project . --version v1.1.6

# 2) 生成主链文档
beacon think start "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon user-story create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon prd create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6
beacon test-case create "Beacon v1.1.6 layered delivery" --project . --version v1.1.6

# 2.5) 配置并执行实现适配
beacon skill list
beacon implement list-runners --json
beacon doctor repair-package --project-root . --version v1.1.6 --json
beacon implement run "Beacon layered delivery" --runner omx --json

# 2.6) 标准 skill + script 触发
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh skill list

# 3) 状态 / 验收
beacon status --board --project-root . --version v1.1.6
beacon gate check release --project-root . --version v1.1.6
```

### 自然语言入口

```bash
# 默认只生成计划，不执行
beacon ask "请帮我梳理 Beacon v1.1.6 的人机分层交付闭环" --plan-only --json

# 显式执行（带边界/置信度闸门）
beacon ask "请生成用户故事并给出验收标准" --execute --json
```

### 诊断与报告

```bash
beacon doctor --project-root . --json
beacon doctor verify-materials --project-root . --version v1.1.6 --json
beacon doctor verify-delivery --project-root . --version v1.1.6 --json
beacon report --machine latest --project-root . --version v1.1.6
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

### 当前验收工件（v1.1.6）

- `docs/beacon/v1.1.6/SUMMARY.md`
- `docs/beacon/v1.1.6/execution/index.md`
- `docs/beacon/v1.1.6/execution/boundaries.md`
- `docs/beacon/v1.1.6/execution/human-machine-collaboration-norm.md`
- `docs/beacon/v1.1.6/execution/memory-architecture-and-projection.md`
- `docs/beacon/v1.1.6/execution/doctor-repair-scope.md`
- `docs/beacon/v1.1.6/execution/safe-implementation-plan.md`
- `docs/beacon/v1.1.6/execution/eval-lab-benchmark-surface.md`
- `docs/beacon/v1.1.6/execution/keep-discard-policy.md`
- `docs/beacon/v1.1.6/execution/drift-auditor-minimum-loop.md`
- `docs/beacon/v1.1.6/release/v1.1.6.md`
- `docs/beacon/v1.1.6/.machine/execution/terminal.json`

---

## 5. 当前验证命令

### 最小交付验证

```bash
python3 -m pytest -q
beacon doctor verify-materials --project-root . --version v1.1.6 --json
beacon doctor verify-delivery --project-root . --version v1.1.6 --json
beacon gate check release --project-root . --version v1.1.6 --json
beacon release check v1.1.6 --project .
```

### 自动生成验收审计

```bash
beacon report latest acceptance-audit   --project-root .   --version v1.1.6   --feature beacon-human-machine-artifact-layering   --write
```

这个命令会生成：

- `docs/beacon/v1.1.6/execution/acceptance-regression-audit.{md,json}`

---

## 6. 后续迭代版本文档编写约定

后续版本（如 `v1.1.7`、`v1.2.0`）继续沿用下面这套方案。

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

- [v1.1.6 Summary](./docs/beacon/v1.1.6/SUMMARY.md)
- [v1.1.6 Boundaries](./docs/beacon/v1.1.6/execution/boundaries.md)
- [v1.1.6 Execution Index](./docs/beacon/v1.1.6/execution/index.md)
- [v1.1.6 Human-Machine Collaboration Norm](./docs/beacon/v1.1.6/execution/human-machine-collaboration-norm.md)
- [v1.1.6 Memory Architecture and Projection](./docs/beacon/v1.1.6/execution/memory-architecture-and-projection.md)
- [v1.1.6 Doctor Repair Scope](./docs/beacon/v1.1.6/execution/doctor-repair-scope.md)
- [v1.1.6 Safe Implementation Plan](./docs/beacon/v1.1.6/execution/safe-implementation-plan.md)
- [v1.1.6 Eval Lab Benchmark Surface](./docs/beacon/v1.1.6/execution/eval-lab-benchmark-surface.md)
- [v1.1.6 Keep-Discard Policy](./docs/beacon/v1.1.6/execution/keep-discard-policy.md)
- [v1.1.6 Release Stub](./docs/beacon/v1.1.6/release/v1.1.6.md)

---

**版本**: v1.1.6
