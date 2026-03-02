# Beacon v1.0.0 技术架构设计

**版本**: v1.0.0
**日期**: 2026-03-02
**状态**: 设计完成

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI 入口层                              │
│                   beacon CLI (Typer)                        │
├─────────────────────────────────────────────────────────────┤
│                      Skill 层                                │
│  /beacon:xxx ←→ skills/xxx/SKILL.md                      │
├─────────────────────────────────────────────────────────────┤
│                    References 层                              │
│                 references/*.md                              │
├─────────────────────────────────────────────────────────────┤
│                    Scripts 层                                │
│              scripts/*.py (Typer CLI)                      │
└─────────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
beacon/
├── beacon/                    # CLI 入口 (Typer)
│   ├── __init__.py
│   ├── main.py               # app = Typer()
│   ├── commands/             # 子命令模块化
│   │   ├── __init__.py
│   │   ├── run.py
│   │   ├── doctor.py
│   │   ├── gate.py
│   │   ├── init.py
│   │   ├── status.py
│   │   └── report.py
│   └── utils/
│       ├── __init__.py
│       ├── context.py
│       └── version.py
├── skills/                    # Skill 定义
│   ├── SKILL.md              # 入口 Skill
│   ├── think/                # 需求澄清
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── socratic-questions.md
│   │   └── scripts/
│   │       └── prompt_generator.py
│   ├── user-story/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── prd/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── test-case/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── workflow/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── next-step-prompts.md
│   │   └── scripts/
│   │       └── workflow_gate.py
│   ├── gate/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── check_gate.py
│   ├── doctor/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── diagnose.py
│   ├── auto-test/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── brainstorm/
│   ├── design/
│   ├── jtbd/
│   ├── kano/
│   ├── persona/
│   ├── analyze/
│   ├── api-design/
│   ├── data-dictionary/
│   ├── wireframe/
│   ├── ui-spec/
│   ├── version/
│   ├── roadmap/
│   ├── moscow/
│   ├── team/
│   ├── ralph-bridge/
│   ├── init/
│   ├── save/
│   ├── resume/
│   ├── remember/
│   ├── recall/
│   ├── release/
│   ├── status/
│   ├── report/
│   ├── debug/
│   └── feedback/
├── docs/
│   └── product/
│       └── v1.0.0/
│           ├── SUMMARY.md
│           ├── prd/
│           ├── user-story/
│           ├── test-cases/
│           ├── execution/
│           │   ├── terminal.json
│           │   └── boundaries.md
│           └── architecture/
├── .beacon/                   # 状态持久化
│   ├── state/
│   ├── memory/
│   └── cache/
└── pyproject.toml             # 项目配置
```

## 3. CLI 命令设计 (Typer)

### 3.1 命令列表

| 命令 | 类型 | 说明 |
|------|------|------|
| `beacon run` | 执行 | 运行工作流 |
| `beacon doctor` | 诊断 | 环境检查 |
| `beacon gate` | 门控 | 阶段检查 |
| `beacon init` | 管理 | 项目初始化 |
| `beacon status` | 运维 | 状态显示 |
| `beacon report` | 运维 | 报告生成 |
| `beacon debug` | 运维 | 调试模式 |
| `beacon feedback` | 运维 | 反馈同步 |
| `beacon resume` | 管理 | 会话恢复 |

### 3.2 Typer 代码示例

```python
# beacon/commands/run.py
import typer
from typing import Optional

app = typer.Typer()

@app.command()
def run(
    workflow: str = typer.Argument(..., help="工作流类型"),
    mode: str = typer.Option("normal", "--mode", "-m", help="运行模式"),
    feature: str = typer.Option("", "--feature", "-f", help="功能名称"),
    version: str = typer.Option("v1.0.0", "--version", "-v", help="版本号"),
    strict: bool = typer.Option(False, "--strict", help="严格模式"),
    json: bool = typer.Option(False, "--json", help="JSON 输出"),
):
    """运行 Beacon 工作流"""
    ...
```

## 4. Skill 定义 (符合最佳实践)

### 4.1 Skill 结构

每个 Skill 遵循:

```
skill-name/
├── SKILL.md              # <500 lines
├── references/           # 补充文档
│   └── *.md
└── scripts/             # 可执行脚本
    └── *.py
```

### 4.2 SKILL.md 模板

```yaml
---
name: beacon-think
description: 产品需求澄清与思考。使用场景...
---

# Beacon Think Skill

## 触发条件
当用户请求需求澄清、问题分析时触发

## 执行步骤

1. 接收用户输入
2. 进行批量提问
3. 检测冲突
4. 产出摘要

## 输出格式

See `references/output-schema.md` for detailed output format.

## 错误处理

See `references/error-handling.md` for error codes.
```

## 5. 兼容性设计

### 5.1 双入口支持

```python
# beacon/main.py
app = Typer()

# beacon 入口
@app.command()
def think(...): ...

# ptk 别名 (兼容)
@app.command("think")
def ptk_think(...):
    """Legacy alias for beacon think"""
    return think(...)
```

### 5.2 配置文件兼容

```yaml
# .beacon/config.yaml
compatibility:
  legacy_mode: true
  aliases:
    ptk: beacon
    .ptk: .beacon
```

## 6. 依赖管理

```toml
# pyproject.toml
[project]
name = "beacon-cli"
version = "1.0.0"
dependencies = [
    "typer>=0.12.0",
    "click>=8.1.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
]
```

## 7. 迁移对照表

| PTK | Beacon | 说明 |
|-----|--------|------|
| ptk_cli.py | beacon/main.py | Typer 重写 |
| .ptk/ | .beacon/ | 状态目录 |
| /product-toolkit: | /beacon: | Skill 入口 |
| skills/*/ | skills/*/ | 保持结构 |

## 8. 实施计划

### Phase 1: CLI 框架
- [ ] 创建 beacon 目录结构
- [ ] 集成 Typer
- [ ] 实现核心命令

### Phase 2: Skills 迁移
- [ ] 迁移 think/user-story/prd/test-case
- [ ] 迁移 workflow/gate/doctor
- [ ] 迁移其他 skills

### Phase 3: 兼容性
- [ ] 添加 ptk 别名
- [ ] 配置兼容模式
- [ ] 文档更新

## 9. 验收标准

- [ ] beacon CLI 可用
- [ ] /beacon:xxx Skill 触发正常
- [ ] references/scripts 结构符合最佳实践
- [ ] ptk 向后兼容
- [ ] SKILL.md <500 lines
