# Beacon v1.0.0 技术架构设计

**版本**: v1.0.0
**日期**: 2026-03-02
**状态**: Completed

---

## 1. 架构概览

Beacon 是基于 Python Typer 构建的 AI 产品工作流工具，采用分层架构设计。

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI 入口层                              │
│                   beacon CLI (Typer)                        │
├─────────────────────────────────────────────────────────────┤
│                      Skill 层                                │
│              /beacon:xxx ←→ skills/xxx/SKILL.md            │
├─────────────────────────────────────────────────────────────┤
│                    References 层                             │
│                 references/*.md                             │
├─────────────────────────────────────────────────────────────┤
│                    Commands 层                               │
│              beacon/commands/*.py (Typer CLI)              │
├─────────────────────────────────────────────────────────────┤
│                    Utils 层                                 │
│                   beacon/utils/                              │
└─────────────────────────────────────────────────────────────┘
```

### 设计原则

1. **分层解耦** - CLI、Skill、Commands、Utils 各自独立
2. **模块化** - 每个命令模块单独文件
3. **可扩展** - 新增命令只需添加模块文件
4. **兼容性** - 命令统一为 Beacon，目录保留历史兼容

---

## 2. 目录结构

```
beacon/
├── beacon/                    # CLI 入口 (Typer)
│   ├── __init__.py
│   ├── main.py               # app = Typer() 主入口
│   ├── commands/             # 子命令模块化
│   │   ├── __init__.py
│   │   ├── workflow.py       # 工作流管理
│   │   ├── think.py          # 产品思考
│   │   ├── user_story.py    # 用户故事
│   │   ├── prd.py           # PRD 生成
│   │   ├── test_case.py     # 测试用例
│   │   ├── gate.py          # 门控检查
│   │   ├── doctor.py        # 环境诊断
│   │   ├── status.py        # 状态面板
│   │   ├── report.py        # 报告生成
│   │   ├── debug.py         # 调试模式
│   │   ├── feedback.py      # 反馈同步
│   │   ├── resume.py        # 会话恢复
│   │   ├── init.py          # 项目初始化
│   │   ├── analyze.py       # 需求分析
│   │   ├── brainstorm.py    # 头脑风暴
│   │   ├── design.py        # 设计阶段
│   │   ├── jtbd.py          # Jobs-to-be-Done
│   │   ├── version.py       # 版本管理
│   │   ├── roadmap.py       # 路线图
│   │   ├── persona.py       # 用户画像
│   │   ├── kano.py          # KANO 模型
│   │   ├── moscow.py        # MoSCoW 优先级
│   │   ├── evolution_summary.py  # 演进总结
│   │   ├── auto_test.py     # 自动化测试
│   │   ├── test_progress.py # 测试进度
│   │   ├── release.py       # 发布流程
│   │   ├── api_design.py    # API 设计
│   │   ├── data_dictionary.py  # 数据字典
│   │   ├── ui_spec.py       # UI 规范
│   │   ├── wireframe.py     # 线框图
│   │   ├── save.py          # 保存上下文
│   │   ├── recall.py        # 召回上下文
│   │   ├── remember.py      # 长期记忆
│   │   ├── team.py          # 团队模式
│   │   └── ralph_bridge.py  # Ralph 桥接
│   └── utils/
│       ├── __init__.py
│       ├── context.py        # 上下文管理
│       └── version.py        # 版本管理
├── skills/                    # Skill 定义
│   ├── SKILL.md             # 入口 Skill
│   ├── think/               # 需求澄清
│   ├── user-story/          # 用户故事
│   ├── prd/                 # PRD
│   ├── test-case/           # 测试用例
│   ├── workflow/            # 工作流
│   ├── gate/                # 门控
│   └── ...                  # 其他 skills
├── docs/
│   ├── beacon/              # Beacon 专用文档
│   │   └── v1.0.0/
│   │       ├── prd/
│   │       ├── user-story/
│   │       ├── qa/test-cases/
│   │       ├── execution/
│   │       └── architecture/
│   └── product/             # 历史 PTK 兼容文档
│       └── v1.0.0/
├── .beacon/                 # 状态持久化
│   ├── state/               # 会话状态
│   │   └── think-progress.json
│   ├── memory/              # 长期记忆
│   └── cache/               # 缓存
└── pyproject.toml           # 项目配置
```

---

## 3. CLI 命令设计 (Typer)

### 3.1 命令分类

| 分类 | 命令 | 说明 |
|------|------|------|
| **工作流** | workflow start/status/gate | 完整工作流管理 |
| **思考** | think start/status/confirm/question/conflict/summarize | 产品思考会话 |
| **文档** | user-story generate/list, prd generate/list, test-case generate/list | 文档生成 |
| **分析** | analyze, brainstorm, design, jtbd | 需求分析 |
| **优先级** | version, roadmap, persona, kano, moscow | 优先级划分 |
| **测试发布** | auto-test, test-progress, release | 测试与发布 |
| **运维** | doctor, status, report, debug, feedback, resume, init | 运维命令 |
| **技术** | api-design, data-dictionary | 技术设计 |
| **设计** | ui-spec, wireframe | 设计协作 |
| **记忆** | save, recall, remember | 记忆系统 |
| **协作** | team, ralph-bridge | 团队协作 |

### 3.2 Typer 代码模式

```python
# beacon/commands/workflow.py
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(name="workflow", help="Full product workflow")

@app.command()
def start(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Start full product workflow"""
    project_root = Path(project) if project else Path.cwd()
    typer.echo(f"Starting Beacon Workflow: {feature}")
```

### 3.3 主入口注册

```python
# beacon/main.py
import typer
from beacon.commands.workflow import app as workflow_app
from beacon.commands.think import app as think_app
# ... 其他导入

app = typer.Typer(name="beacon", help="Beacon - AI Product Workflow Toolkit")

app.add_typer(workflow_app, name="workflow")
app.add_typer(think_app, name="think")
# ... 其他注册

if __name__ == "__main__":
    app()
```

---

## 4. 数据模型

### 4.1 ThinkSession

```python
class ThinkSession:
    topic: str
    round: int
    confirmed_facts: List[str]
    assumptions: List[str]
    conflicts: List[Dict]
    open_questions: List[Dict]
```

### 4.2 UserStory

```python
class UserStory:
    id: str
    feature: str
    actor: str
    action: str
    benefit: str
    acceptance_criteria: List[AC]
    priority: str  # P0/P1/P2
    story_points: int
```

### 4.3 TestCase

```python
class TestCase:
    id: str
    us_id: str
    ac_id: str
    scenario: str
    precondition: str
    steps: List[str]
    expected_result: str
    status: str  # Pending/Pass/Fail
```

---

## 5. 状态管理

### 5.1 会话状态

- 位置: `.beacon/state/think-progress.json`
- 格式: JSON
- 操作: ThinkSession 类封装

### 5.2 长期记忆

- 位置: `.beacon/memory/`
- 用途: save/recall/remember 命令

### 5.3 证据链

| 证据类型 | 文件 | 描述 |
|----------|------|------|
| 命令日志 | raw-command-log.jsonl | 所有命令记录 |
| 证据清单 | evidence-manifest.json | 产物完整性 |
| 门控报告 | gate-consistency-report.json | 终态判定 |

---

## 6. 兼容性设计

### 6.1 统一入口（CLI + Skill）

```
# 方式1: beacon CLI
beacon workflow start <feature>

# 方式2: Skill 触发
/beacon:workflow <feature>
```

### 6.2 目录兼容

```
docs/beacon/archive/v1.0.0/     # Beacon 专用
docs/product/v1.0.0/    # 历史 PTK 兼容
.beacon/                # Beacon 状态
.ptk/                   # 历史 PTK 兼容 (可选)
```

### 6.3 历史 PTK 别名（已下线）

迁移自历史 PTK 的项目请统一使用:
```bash
beacon workflow start <feature>  # 统一命令入口
```

---

## 7. 依赖管理

```toml
# pyproject.toml
[project]
name = "beacon-cli"
version = "1.0.0"
requires-python = ">=3.8"

dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
]
```

---

## 8. 实施计划

| 阶段 | 任务 | 状态 |
|------|------|------|
| Phase 1 | CLI 框架搭建 | ✅ Complete |
| Phase 2 | 核心命令实现 | ✅ Complete |
| Phase 3 | 分析命令实现 | ✅ Complete |
| Phase 4 | 运维命令实现 | ✅ Complete |
| Phase 5 | Skill 定义 | ✅ Complete |
| Phase 6 | 文档生成 | ✅ Complete |
| Phase 7 | 兼容性适配 | ✅ Complete |

---

## 9. 验收标准

| 验收项 | 标准 |
|--------|------|
| CLI 可用 | `beacon --help` 正常 |
| 命令注册 | 所有子命令可触发 |
| 状态持久化 | JSON 文件正确读写 |
| 文档生成 | US/PRD/TC 正确输出 |
| Skill 集成 | /beacon:xxx 可触发 |
| 兼容性 | docs/beacon 和 docs/product 双写 |

---

**Completed**: 2026-03-02
**Version**: 1.0.0
