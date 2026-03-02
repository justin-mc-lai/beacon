# Beacon CLI

> AI Product Workflow Toolkit — 需求澄清、用户故事、PRD、测试用例的完整工作流

[![PyPI version](https://img.shields.io/pypi/v/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![Python](https://img.shields.io/python/pyversions/beacon-cli)](https://pypi.org/project/beacon-cli/)
[![License](https://img.shields.io/pypi/l/beacon-cli)](./LICENSE)

---

## 1. Beacon 是什么

Beacon 是面向 AI 时代的智能产品工作流工具，帮助团队将「需求想法」稳定地转化为「可交付证据」。

### 核心价值

| 价值 | 说明 |
|------|------|
| **效率提升** | 一键生成 US/PRD/TC 产物链，减少手工切换 |
| **范围保障** | 越界检测与预警，避免范围漂移 |
| **交付确定性** | 明确的终态判定（Pass / Blocked / Cancelled） |
| **证据可信** | 完整证据链，支持审计与复盘 |

### 与 PTK 的关系

Beacon 从 product-toolkit (PTK) 升级而来，是 PTK 的 Python/Typer 重构版本：

- **CLI**: `beacon` 命令（原有 `ptk` 别名兼容）
- **文档**: `docs/beacon/` 为主，`docs/product/` 为 PTK 兼容
- **状态**: `.beacon/` 目录（原有 `.ptk/` 别名兼容）
- **Skill**: `/beacon:` 触发（原有 `/product-toolkit:` 别名兼容）

---

## 2. 快速开始

### 2.1 安装

```bash
# 通过 pip 安装
pip install beacon-cli

# 或从源码安装
cd beacon
pip install -e .
```

### 2.2 5 个核心命令速览

```bash
# 1. 启动完整工作流
beacon workflow start "用户登录功能"

# 2. 产品思考
beacon think start "用户登录优化"
beacon think confirm "用户需要社交登录"
beacon think question "是否需要支持企业SSO?" --priority high --blocking

# 3. 生成用户故事
beacon user-story create "用户登录"

# 4. 生成 PRD
beacon prd create "用户登录"

# 5. 生成测试用例
beacon test-case create "用户登录"
```

### 2.3 完整示例：做一个"用户登录"功能

```bash
# === 步骤 1: 产品思考 ===
# 启动思考会话，探索需求细节
beacon think start "用户登录功能"
beacon think confirm "用户需要账号密码登录"
beacon think confirm "用户需要社交账号登录（Google/GitHub）"
beacon think question "是否需要支持企业 SSO?" --priority high --blocking
beacon think question "登录会话有效期多长?" --priority medium

# 查看思考进度
beacon think status

# 生成思考总结
beacon think summarize

# === 步骤 2: 生成用户故事 ===
beacon user-story create "用户登录"

# === 步骤 3: 生成 PRD ===
beacon prd create "用户登录"

# === 步骤 4: 生成测试用例 ===
beacon test-case create "用户登录" --type all

# === 步骤 5: 检查工作流状态 ===
beacon workflow status

# === 步骤 6: 运行门控检查 ===
beacon workflow gate
```

---

## 3. 核心概念

### 3.1 工作流阶段

```
┌─────────┐   ┌────────────┐   ┌──────┐   ┌───────────┐   ┌──────┐
│  Think  │ → │ User Story │ → │ PRD  │ → │ Test Case │ → │ Gate │
└─────────┘   └────────────┘   └──────┘   └───────────┘   └──────┘
   需求澄清    用户故事        需求文档     测试用例        交付门控
```

| 阶段 | 命令 | 产出 |
|------|------|------|
| Think | `beacon think *` | 确认事实、开放问题、冲突记录 |
| User Story | `beacon user-story *` | 用户故事文档 |
| PRD | `beacon prd *` | 产品需求文档 |
| Test Case | `beacon test-case *` | 测试用例文档 |
| Gate | `beacon workflow gate` | Pass / Blocked / Cancelled |

### 3.2 文档输出结构

```
项目根目录/
├── docs/
│   ├── beacon/                    # Beacon 专用
│   │   └── v1.0.0/
│   │       ├── prd/
│   │       ├── user-story/
│   │       └── qa/test-cases/
│   └── product/                   # PTK 兼容
│       └── v1.0.0/
│           └── ...
├── .beacon/                      # 状态目录
│   ├── state/
│   │   └── think-progress.json
│   └── memory/
└── beacon (CLI 入口)
```

### 3.3 门控检查

| 阶段 | 门控项 | 判定标准 |
|------|--------|---------|
| Think | 收敛门 | 无 `blocking=true` 的未决项 |
| User Story | AC门 | 七维 AC 完整 |
| PRD | 风险门 | critical/high 冲突已解决 |
| Test Case | 覆盖门 | AC→TC 覆盖矩阵完整 |
| Release | 测试门 | 冒烟测试 100% 通过 |

---

## 4. 命令参考

### 4.1 工作流命令

#### `beacon workflow`

完整产品工作流管理。

```bash
# 启动工作流
beacon workflow start <feature>
beacon workflow start "用户登录" --auto          # 自动执行所有阶段
beacon workflow start "用户登录" --skip think    # 跳过 think 阶段

# 查看状态
beacon workflow status
beacon workflow status --version v1.0.0

# 门控检查
beacon workflow gate
beacon workflow gate think        # 只检查 think 阶段

# 运行任意子命令
beacon workflow run kano "功能A"
beacon workflow run analyze
```

| 子命令 | 说明 |
|--------|------|
| `start` | 启动完整产品工作流 |
| `status` | 显示工作流各阶段状态 |
| `gate` | 运行阶段门控检查 |
| `run` | 运行任意 beacon 子命令 |

#### `beacon gate`

门控检查工具。

```bash
# 检查所有阶段
beacon gate

# 检查指定阶段
beacon gate think
beacon gate user-story
beacon gate prd
beacon gate test-case
beacon gate release
```

---

### 4.2 思考命令

#### `beacon think`

产品思考 vNext — 使用苏格拉底式提问探索需求。

```bash
# 启动思考会话
beacon think start "用户登录优化"

# 查看状态
beacon think status

# 确认事实
beacon think confirm "用户需要社交登录"

# 添加问题
beacon think question "是否需要企业SSO?" --priority high --blocking
beacon think question "会话有效期?" --priority medium

# 记录冲突
beacon think conflict semantic "安全和易用性冲突"
beacon think conflict boundary "边界条件定义不清"

# 生成总结
beacon think summarize
```

| 子命令 | 说明 | 参数 |
|--------|------|------|
| `start` | 启动新思考会话 | `<topic>` |
| `status` | 显示思考状态 | - |
| `confirm` | 确认一个事实 | `<fact>` |
| `question` | 添加开放问题 | `<question>` |
| `conflict` | 记录冲突 | `<type> <description>` |
| `summarize` | 生成思考总结 | - |

---

### 4.3 文档命令

#### `beacon user-story`

用户故事生成与管理。

```bash
# 生成用户故事
beacon user-story create "用户登录"

# 列出已有用户故事
beacon user-story list
```

#### `beacon prd`

PRD（产品需求文档）生成与管理。

```bash
# 生成 PRD
beacon prd create "用户登录"

# 列出已有 PRD
beacon prd list
```

#### `beacon test-case`

测试用例生成与管理。

```bash
# 生成测试用例
beacon test-case create "用户登录"
beacon test-case create "用户登录" --type smoke   # 只生成冒烟测试
beacon test-case create "用户登录" --type new     # 新功能测试
beacon test-case create "用户登录" --type all     # 全部测试

# 列出已有测试用例
beacon test-case list

# 门控检查
beacon test-case gate "用户登录"
```

---

### 4.4 分析命令

#### `beacon analyze`

需求分析。

```bash
beacon analyze
beacon analyze --feature "用户登录"
```

#### `beacon brainstorm`

头脑风暴模式。

```bash
beacon brainstorm "用户登录"
beacon brainstorm "用户登录" --mode creative
```

#### `beacon design`

设计阶段。

```bash
beacon design "用户登录"
beacon design "用户登录" --type ui
```

#### `beacon jtbd`

Jobs-to-be-Done 分析。

```bash
beacon jtbd "用户登录"
```

#### `beacon kano`

KANO 模型分析 — 需求分类（基本型、期望型、兴奋型）。

```bash
beacon kano "用户登录"
beacon kano "用户登录" --add "社交登录"
beacon kano "用户登录" --list
```

#### `beacon moscow`

MoSCoW 优先级划分 — Must/Should/Could/Won't。

```bash
beacon moscow "用户登录"
beacon moscow "用户登录" --add "账号密码" must
beacon moscow "用户登录" --add "社交登录" should
```

#### `beacon roadmap`

路线图规划。

```bash
beacon roadmap
beacon roadmap v2.0.0
beacon roadmap --timeline 2026-Q1,2026-Q2
```

#### `beacon persona`

用户画像。

```bash
beacon persona "用户登录"
beacon persona list
```

#### `beacon version`

版本管理。

```bash
beacon version create v2.0.0
beacon version list
beacon version current
```

#### `beacon evolution-summary`

版本演进总结。

```bash
beacon evolution-summary v1.0.0
```

---

### 4.5 运维命令

#### `beacon doctor`

环境诊断与修复。

```bash
beacon doctor
beacon doctor --fix
```

#### `beacon status`

状态面板。

```bash
beacon status
beacon status --verbose
```

#### `beacon report`

生成报告。

```bash
beacon report
beacon report --format json
beacon report v1.0.0
```

#### `beacon debug`

调试模式。

```bash
beacon debug
beacon debug --trace
```

#### `beacon feedback`

测试反馈同步。

```bash
beacon feedback
beacon feedback --sync
```

#### `beacon resume`

恢复会话。

```bash
beacon resume
beacon resume session-123
```

#### `beacon init`

项目初始化。

```bash
beacon init
beacon init --template minimal
```

---

### 4.6 测试与发布命令

#### `beacon auto-test`

自动化测试。

```bash
beacon auto-test
beacon auto-test --type smoke
beacon auto-test --type regression
beacon auto-test --type all
```

#### `beacon test-progress`

测试进度跟踪。

```bash
beacon test-progress
beacon test-progress --verbose
```

#### `beacon release`

发布流程。

```bash
beacon release v1.0.0
beacon release v1.0.0 --dry-run
```

---

### 4.7 技术设计命令

#### `beacon api-design`

API 设计。

```bash
beacon api-design "用户登录"
beacon api-design "用户登录" --format openapi
```

#### `beacon data-dictionary`

数据字典。

```bash
beacon data-dictionary
beacon data-dictionary "用户"
```

---

### 4.8 设计协作命令

#### `beacon ui-spec`

UI 规范。

```bash
beacon ui-spec "用户登录"
beacon ui-spec "用户登录" --theme dark
```

#### `beacon wireframe`

线框图。

```bash
beacon wireframe "登录页面"
beacon wireframe "登录页面" --export png
```

---

### 4.9 记忆系统命令

#### `beacon save`

保存上下文。

```bash
beacon save "当前思考"
beacon save "当前思考" --tags work,login
```

#### `beacon recall`

召回上下文。

```bash
beacon recall
beacon recall "当前思考"
beacon recall --tag work
```

#### `beacon remember`

长期记忆。

```bash
beacon remember "用户偏好"
beacon remember list
```

---

### 4.10 协作命令

#### `beacon team`

团队模式。

```bash
beacon team start
beacon team add @user1
beacon team status
```

#### `beacon ralph-bridge`

Ralph 桥接。

```bash
beacon ralph-bridge connect
beacon ralph-bridge status
```

---

## 5. 使用示例

### 5.1 完整产品工作流

```bash
# 方式一：手动分步执行
beacon think start "点赞功能"
beacon think confirm "用户需要对内容点赞"
beacon think summarize
beacon user-story create "点赞功能"
beacon prd create "点赞功能"
beacon test-case create "点赞功能"
beacon workflow gate

# 方式二：自动执行
beacon workflow start "点赞功能" --auto
```

### 5.2 KANO 需求优先级

```bash
# 1. 启动 KANO 分析
beacon kano "用户登录"

# 2. 添加需求并分类
beacon kano "用户登录" --add "账号密码" must
beacon kano "用户登录" --add "社交登录" should
beacon kano "用户登录" --add "生物识别" could
beacon kano "用户登录" --add "语音登录" wont

# 3. 查看分析结果
beacon kano "用户登录" --list

# 4. 生成报告
beacon kano "用户登录" --report
```

### 5.3 团队协作

```bash
# 1. 启动团队会话
beacon team start "登录功能评审"

# 2. 添加团队成员
beacon team add @product-manager
beacon team add @developer
beacon team add @qa

# 3. 记录讨论
beacon save "登录功能评审结论" --tags team,login

# 4. 生成会议纪要
beacon report --type meeting
```

---

## 6. 配置说明

### 6.1 .beacon 目录

```
.beacon/
├── state/
│   ├── think-progress.json    # 思考会话状态
│   └── workflow-state.json   # 工作流状态
├── memory/                    # 长期记忆
│   └── ...
└── config.yaml               # 配置文件
```

### 6.2 配置文件

```yaml
# .beacon/config.yaml
version: "1.0.0"

# 文档输出目录
docs:
  primary: "docs/beacon"      # 主要目录
  compatibility: "docs/product"  # PTK 兼容

# 工作流配置
workflow:
  auto_gate: true            # 自动门控
  strict_mode: false         # 严格模式

# 输出格式
output:
  format: "markdown"
  template: "default"
```

### 6.3 环境变量

```bash
# 指定项目根目录
BEACON_PROJECT=/path/to/project

# 指定版本
BEACON_VERSION=v1.0.0

# 调试模式
BEACON_DEBUG=1
```

---

## 7. 目录结构

### 7.1 项目文件组织

```
beacon/
├── beacon/                    # CLI 源码
│   ├── main.py               # 入口
│   ├── commands/             # 命令模块
│   │   ├── workflow.py
│   │   ├── think.py
│   │   ├── user_story.py
│   │   ├── prd.py
│   │   ├── test_case.py
│   │   └── ... (37 个命令)
│   └── utils/
├── docs/
│   ├── beacon/               # Beacon 文档
│   └── product/             # PTK 兼容
├── references/               # 参考文档
│   ├── socratic-questioning.md
│   └── acceptance-criteria.md
├── scripts/                  # 脚本
├── SKILL.md                 # Skill 定义
└── pyproject.toml           # 项目配置
```

### 7.2 文档输出示例

```
项目根目录/
├── docs/
│   └── beacon/
│       └── v1.0.0/
│           ├── prd/
│           │   └── 用户登录.md
│           ├── user-story/
│           │   └── 用户登录.md
│           ├── qa/
│           │   └── test-cases/
│           │       └── 用户登录.md
│           └── execution/
│               ├── boundaries.md
│               └── terminal.json
└── .beacon/
    └── state/
        └── think-progress.json
```

---

## 8. 常见问题

### Q1: 如何升级 Beacon？

```bash
pip install --upgrade beacon-cli
```

### Q2: 如何查看版本？

```bash
beacon --version
# 或
beacon version current
```

### Q3: 如何迁移 PTK 数据？

Beacon 自动兼容 PTK 目录结构。如需迁移：

```bash
# PTK 数据位于 .ptk/，Beacon 使用 .beacon/
# 两者自动兼容，无需手动迁移
```

### Q4: 如何自定义文档模板？

在项目中创建 `references/` 目录，Beacon 会优先使用项目本地的模板。

### Q5: 如何获取帮助？

```bash
# 查看帮助
beacon --help

# 查看子命令帮助
beacon workflow --help
beacon think --help

# 运行环境诊断
beacon doctor
```

---

## 9. 相关链接

- **文档**: [docs/beacon/](./docs/beacon/v1.0.0/)
- **PRD**: [PRD](./docs/beacon/v1.0.0/prd/beacon-core.md)
- **用户故事**: [User Story](./docs/beacon/v1.0.0/user-story/beacon-core.md)
- **测试用例**: [Test Cases](./docs/beacon/v1.0.0/qa/test-cases/beacon-core.md)
- **架构设计**: [Architecture](./docs/beacon/v1.0.0/architecture/beacon-v1.0.0-design.md)

---

**版本**: v1.0.0
**最后更新**: 2026-03-02
