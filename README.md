# Beacon CLI

> AI Product Workflow Toolkit — 将需求澄清、用户故事、PRD、测试用例、交付证据收敛到一个可审计流程。

[![PyPI version](https://img.shields.io/pypi/v/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![Python](https://img.shields.io/python/pyversions/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![License](https://img.shields.io/pypi/l/beacon-cli)](./LICENSE)

---

## 1. 当前版本是什么

Beacon 当前单一发布口径是 **v1.1.2**。

> 当前发布线：`v1.1.2`

- **CLI 入口**：`beacon <subcommand>`
- **当前包版本**：`1.1.2`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源（source of truth）
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径

如果你只记一条：

> **Beacon 现在是 v1.1.2，写文档看 `docs/beacon`，执行命令用 `beacon <subcommand>`。**

---

## 2. 当前能力边界

### In scope

Beacon 当前负责：

1. **需求主链编排**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
2. **自动化测试与门禁治理**：`auto-test`、`gate`、`release`
3. **证据闭环**：coverage、manifest、spec consistency、memory closure、delivery artifacts
4. **记忆与反馈**：`remember`、`recall`、`feedback`、`resume`、`report`
5. **产品分析模板**：`analyze`、`brainstorm`、`design`、`jtbd`、`persona`、`roadmap` 等

### Out of scope

Beacon 默认**不负责**：

- 直接写业务代码
- 直接修生产故障
- 直接做数据库迁移/部署执行
- 让 `research` 直接替代正式交付主链

### 当前发布线摘要（v1.1.2）

- **完整主链工作流**：`think → user-story → prd → [prototype] → test-case → implementation → verify → gate`
- **严格交付治理**：release gate 校验 memory closure、spec consistency、evidence manifest、coverage、delivery artifacts
- **自动化测试闭环**：`auto-test` 支持多层执行证据、QA9、compatibility pair evidence、coverage 回写
- **UI Prototype 生命周期**：支持 `prototype create / preview / freeze / status / list`，默认栈为 Bootstrap 5.3.x

---

## 3. 当前推荐命令

### 安装

```bash
pip install beacon-cli
# 或
cd beacon && pip install -e .
```

### 当前推荐命令风格

```bash
beacon <subcommand> ...
```

### 最小工作流

```bash
# 1) 启动需求主链
beacon workflow start "用户登录功能"

# 2) 产品澄清
beacon think start "用户登录优化"
beacon think confirm "用户需要社交登录"
beacon think question "是否需要支持企业SSO?" --priority high --blocking

# 3) 生成主链文档
beacon user-story create "用户登录"
beacon prd create "用户登录"
beacon test-case create "用户登录" --type all

# 4) 状态 / gate
beacon workflow status
beacon workflow gate
```

### 自然语言入口

```bash
# 默认只生成计划，不执行
beacon prompt optimize "请帮我做登录需求澄清并进入测试验收"

# 显式执行（带边界/置信度闸门）
beacon ask "请生成用户故事并给出验收标准" --execute --json
```

### 自动测试与交付

```bash
# 基础测试执行
beacon auto-test create all --project . \
  --ui-command "python -m pytest -q -k ui" \
  --api-curl-command "bash -lc 'curl -fsS http://127.0.0.1:8000/health'" \
  --unit-command "python -m pytest -q -k unit" \
  --smoke-command "python -m pytest -q -m smoke"

# QA9 / 当前版本矩阵
beacon auto-test create qa9 --project . \
  --version v1.1.2 \
  --qa-matrix-path docs/beacon/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.qa9-matrix.json \
  --ui-runner browser-use \
  --require-fresh-evidence \
  --require-junit \
  --require-assertion-count
```

### 环境与状态

```bash
beacon doctor
beacon doctor setup --dry-run --json
beacon status --board --version v1.1.2
beacon report --machine --version v1.1.2
```

---

## 4. 当前交付工件

当前正式交付主链只看 `docs/beacon/<version>/`。

### 主链工件

```text
docs/beacon/<version>/
├── user-story/
├── prd/
├── qa/test-cases/
└── execution/
```

### execution 层最低必备项

```text
docs/beacon/<version>/execution/
├── boundaries.md
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

### 当前验收工件（v1.1.2）

- `docs/beacon/v1.1.2/execution/boundaries.md`
- `docs/beacon/v1.1.2/execution/acceptance-regression-audit.md`

---

## 5. 当前验证命令

### 最小交付验证

```bash
# 全量回归
python3 -m pytest -q

# 当前 release gate
beacon gate check release --project-root . --version v1.1.2

# 当前 release check
beacon release check v1.1.2 --project .
```

### 自动生成验收审计

```bash
beacon report latest acceptance-audit \
  --project-root . \
  --version v1.1.2 \
  --feature beacon-ui-prototype-lifecycle \
  --run-regression \
  --write
```

这个命令会生成：

- `docs/beacon/v1.1.2/execution/acceptance-regression-audit.{md,json}`

---

## 6. 后续迭代版本文档编写约定

后续版本（如 `v1.1.2`、`v1.2.0`）继续沿用下面这套方案。

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
├── user-story/
├── prd/
├── qa/test-cases/
└── execution/
    ├── boundaries.md
    └── acceptance-regression-audit.md
```

### 版本发布时的文档更新顺序

1. 更新版本元信息
   - `pyproject.toml`
   - `beacon/__init__.py`
   - `SKILL.md`
   - `AGENTS.md`
   - `CLAUDE.md`
2. 更新当前版本 README 口径
3. 生成/刷新当前版本 acceptance audit

### 后续版本推荐沿用的命令

```bash
# 生成当前版本验收文档
beacon report latest acceptance-audit \
  --project-root . \
  --version <next-version> \
  --feature <feature> \
  --run-regression \
  --write
```

### 详细策略文档

- [v1.1.2 文档版本化与编写策略](./docs/beacon/v1.1.2/execution/documentation-versioning-guidelines.md)

---

## 7. 相关链接

- **当前边界定义（v1.1.2）**: [boundaries.md](./docs/beacon/v1.1.2/execution/boundaries.md)
- **当前验收回归审计（v1.1.2）**: [acceptance-regression-audit.md](./docs/beacon/v1.1.2/execution/acceptance-regression-audit.md)
- **当前子命令能力蓝图**: [v1.1.0-subcommand-capability-blueprint.md](./docs/beacon/v1.1.0/execution/v1.1.0-subcommand-capability-blueprint.md)
- **文档版本化与编写策略**: [documentation-versioning-guidelines.md](./docs/beacon/v1.1.2/execution/documentation-versioning-guidelines.md)

---

**版本**: v1.1.2
**最后更新**: 2026-03-13
