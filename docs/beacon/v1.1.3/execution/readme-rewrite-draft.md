# Beacon README 重写草案（面向 v1.1.3 收口）

> **说明**  
> 以下是 Beacon 根 README 的 **v1.1.3 草案口径**。  
> 本草案用于统一边界与叙事，不代表当前已发布运行时包版本已经升级。

---

# Beacon CLI

> Evidence-first Product Workflow Kernel — 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

---

## 1. 当前版本是什么

Beacon 的下一步演进目标版本是 **v1.1.3（Boundary Consolidation Draft）**。

当前需要记住的只有一条：

> **Beacon 的核心不是模板大全，而是需求交付闭环。**

对外统一命令入口仍然是：

```bash
beacon <subcommand>
```

文档主源仍然是：

```text
docs/beacon/<version>/
```

---

## 2. 当前能力边界

### In Scope

Beacon 当前负责：

1. **需求主链编排**  
   `think -> user-story -> prd -> [prototype] -> test-case -> workflow -> auto-test -> gate -> release`

2. **证据与放行治理**  
   coverage、manifest、spec consistency、gate reason codes、release check

3. **工作流恢复与观测**  
   `status`、`report`、`doctor`、`resume`、`feedback`、memory writeback

4. **版本化交付物管理**  
   所有正式产物统一沉淀在 `docs/beacon/<version>/`

### Out of Scope

Beacon 默认不负责：

- 直接写业务代码
- 直接修生产故障
- 数据库迁移与生产部署执行本身
- 浏览器守护进程 / persistent QA runtime
- issue tracker 轮询、workspace 调度、agent scheduler
- 在 core 内维护完整 PM 模板大全

> 如果你需要浏览器 QA / 角色化开发流程，请参考 gstack。  
> 如果你需要 issue/workspace/agent 编排，请参考 symphony。  
> Beacon 更适合做规格、证据、gate 与 release contract。

---

## 3. 当前推荐命令

### 最小主链

```bash
# 1) 启动需求收敛
beacon think start "Beacon v1.1.3 边界收口" --project /abs/path/to/project

# 2) 生成正式主链文档
beacon user-story create "Beacon v1.1.3 边界收口" --project /abs/path/to/project --version v1.1.3
beacon prd create "Beacon v1.1.3 边界收口" --project /abs/path/to/project --version v1.1.3
beacon test-case create "Beacon v1.1.3 边界收口" --project /abs/path/to/project --version v1.1.3

# 3) 查看状态 / 推进 workflow
beacon status --board --project-root /abs/path/to/project
beacon workflow start "Beacon v1.1.3 边界收口" --project /abs/path/to/project --version v1.1.3
```

### 验证与放行

```bash
beacon auto-test create all --project /abs/path/to/project --version v1.1.3
beacon gate check release --project-root /abs/path/to/project --version v1.1.3
beacon release check v1.1.3 --project /abs/path/to/project
```

### 报告与诊断

```bash
beacon report latest --human --project-root /abs/path/to/project --version v1.1.3
beacon doctor --project-root /abs/path/to/project --json
beacon resume continue --project-root /abs/path/to/project --version v1.1.3
```

### 自然语言入口

```bash
# 默认只出计划，不直接执行
beacon ask "请帮我梳理 Beacon v1.1.3 的边界与主链物料" --plan-only --json
```

---

## 4. 当前交付工件

正式交付主链只看：

```text
docs/beacon/<version>/
```

核心目录：

```text
docs/beacon/<version>/
├── SUMMARY.md
├── user-story/
├── prd/
├── qa/test-cases/
└── execution/
```

`execution/` 最低应包含：

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

运行时证据位于：

```text
.beacon/
├── auto-test-status.json
├── gate-report.json
├── evidence-manifest.json
├── coverage-summary.json
├── memory/
└── runs/
```

---

## 5. 当前验证命令

### 最小验证

```bash
python3 -m pytest -q
beacon gate check release --project-root . --version v1.1.3
beacon release check v1.1.3 --project .
```

### 审计报告

```bash
beacon report latest acceptance-audit \
  --project-root . \
  --version v1.1.3 \
  --feature beacon-vnext-boundary-consolidation \
  --write
```

---

## README 改写原则（随版本发布执行）

根 README 只保留 5 类当前信息：

1. 当前版本是什么
2. 当前能力边界
3. 当前推荐命令
4. 当前交付工件
5. 当前验证命令

历史版本与兼容说明只能进入：

- release notes
- migration notes
- appendix
