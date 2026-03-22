# Beacon CLI

> Evidence-first Product Workflow Kernel — 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

[![PyPI version](https://img.shields.io/pypi/v/beacon)](https://pypi.org/project/beacon/)
[![Python](https://img.shields.io/pypi/pyversions/beacon)](https://pypi.org/project/beacon/)

---

## 1. 当前版本是什么

Beacon 当前单一发布口径是 **v1.1.5**。

> 当前发布线：`v1.1.5`

- **CLI 入口**：`beacon <subcommand>`
- **当前包版本**：`1.1.5`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源（source of truth）
- `.beacon/` 是运行时状态，不替代正式交付文档
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径

如果你只记一条：

> **Beacon 现在是 v1.1.5，写文档看 `docs/beacon`，执行命令用 `beacon <subcommand>`。**

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

### 当前发布线摘要（v1.1.5）

- **完整主链工作流**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- **实现适配层**：新增 `skill` / `implement`，支持 runner + skill adapter
- **标准 Skill 包**：新增 `skills/beacon/`，通过脚本包装触发 Beacon CLI
- **人机分层闭环**：`docs/beacon/<version>/execution/` 保持 Markdown-first，人类主读；`docs/beacon/<version>/.machine/` 作为机器正式读取面
- **doctor repair-package**：支持把旧 execution / QA JSON 迁到 `.machine` 并补人类主入口索引
- **prompt first-principles contract**：`prompt catalog / optimize` 暴露 reading order、clarification gate、progressive disclosure、doctor role
- **eval-lab skeleton**：`.beacon/state/eval-lab/` 提供 benchmark surface、editable surface、keep/discard skeleton
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

### 最小工作流

```bash
# 1) 启动需求主链
beacon workflow start "Beacon v1.1.5 layered delivery" --project . --version v1.1.5

# 2) 生成主链文档
beacon think start "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon user-story create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon prd create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5
beacon test-case create "Beacon v1.1.5 layered delivery" --project . --version v1.1.5

# 2.5) 配置并执行实现适配
beacon skill list
beacon implement list-runners --json
beacon doctor repair-package --project-root . --version v1.1.5 --json
beacon implement run "Beacon layered delivery" --runner omx --json

# 2.6) 标准 skill + script 触发
bash skills/beacon/scripts/run_beacon.sh --version
bash skills/beacon/scripts/run_beacon.sh skill list

# 3) 状态 / 验收
beacon status --board --project-root . --version v1.1.5
beacon gate check release --project-root . --version v1.1.5
```

### 自然语言入口

```bash
# 默认只生成计划，不执行
beacon ask "请帮我梳理 Beacon v1.1.5 的人机分层交付闭环" --plan-only --json

# 显式执行（带边界/置信度闸门）
beacon ask "请生成用户故事并给出验收标准" --execute --json
```

### 诊断与报告

```bash
beacon doctor --project-root . --json
beacon doctor verify-materials --project-root . --version v1.1.5 --json
beacon doctor verify-delivery --project-root . --version v1.1.5 --json
beacon report --machine latest --project-root . --version v1.1.5
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

### 当前验收工件（v1.1.5）

- `docs/beacon/v1.1.5/SUMMARY.md`
- `docs/beacon/v1.1.5/execution/index.md`
- `docs/beacon/v1.1.5/execution/boundaries.md`
- `docs/beacon/v1.1.5/execution/human-machine-collaboration-norm.md`
- `docs/beacon/v1.1.5/execution/memory-architecture-and-projection.md`
- `docs/beacon/v1.1.5/execution/doctor-repair-scope.md`
- `docs/beacon/v1.1.5/execution/safe-implementation-plan.md`
- `docs/beacon/v1.1.5/execution/eval-lab-benchmark-surface.md`
- `docs/beacon/v1.1.5/execution/keep-discard-policy.md`
- `docs/beacon/v1.1.5/execution/drift-auditor-minimum-loop.md`
- `docs/beacon/v1.1.5/release/v1.1.5.md`
- `docs/beacon/v1.1.5/.machine/execution/terminal.json`

---

## 5. 当前验证命令

### 最小交付验证

```bash
python3 -m pytest -q
beacon doctor verify-materials --project-root . --version v1.1.5 --json
beacon doctor verify-delivery --project-root . --version v1.1.5 --json
beacon gate check release --project-root . --version v1.1.5 --json
beacon release check v1.1.5 --project .
```

### 自动生成验收审计

```bash
beacon report latest acceptance-audit   --project-root .   --version v1.1.5   --feature beacon-human-machine-artifact-layering   --write
```

这个命令会生成：

- `docs/beacon/v1.1.5/execution/acceptance-regression-audit.{md,json}`

---

## 6. 后续迭代版本文档编写约定

后续版本（如 `v1.1.5`、`v1.2.0`）继续沿用下面这套方案。

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

- [v1.1.5 Summary](./docs/beacon/v1.1.5/SUMMARY.md)
- [v1.1.5 Boundaries](./docs/beacon/v1.1.5/execution/boundaries.md)
- [v1.1.5 Execution Index](./docs/beacon/v1.1.5/execution/index.md)
- [v1.1.5 Human-Machine Collaboration Norm](./docs/beacon/v1.1.5/execution/human-machine-collaboration-norm.md)
- [v1.1.5 Memory Architecture and Projection](./docs/beacon/v1.1.5/execution/memory-architecture-and-projection.md)
- [v1.1.5 Doctor Repair Scope](./docs/beacon/v1.1.5/execution/doctor-repair-scope.md)
- [v1.1.5 Safe Implementation Plan](./docs/beacon/v1.1.5/execution/safe-implementation-plan.md)
- [v1.1.5 Eval Lab Benchmark Surface](./docs/beacon/v1.1.5/execution/eval-lab-benchmark-surface.md)
- [v1.1.5 Keep-Discard Policy](./docs/beacon/v1.1.5/execution/keep-discard-policy.md)
- [v1.1.5 Release Stub](./docs/beacon/v1.1.5/release/v1.1.5.md)

---

**版本**: v1.1.5
