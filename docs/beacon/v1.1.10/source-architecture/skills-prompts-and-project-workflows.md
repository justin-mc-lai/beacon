# Beacon v1.1.10 Skills, Prompts, And Project Workflows

## 这层解决什么问题

Beacon 并不假设所有项目都通过同一种实现或验证路径完成交付。

源码层已经有几套关键机制：

- implement skill adapters
- project skill registry
- profiles
- feature/profile binding
- verify orchestration

## 关键源码入口

| Responsibility | Main Source |
| --- | --- |
| implement skill adapters | `beacon/utils/implement_adapters.py`, `beacon/commands/implement.py` |
| skill config | `beacon/utils/skill_config.py`, `beacon/commands/skill.py` |
| project profiles/orchestration | `beacon/utils/project_skills.py`, `beacon/commands/verify.py` |
| active context guidance | `beacon/utils/context_files.py`, docs and SKILL surfaces |

## Skill 面不是一回事

### 1. Implement adapters

面向“如何执行实现工作”。

### 2. Project skill registry / profiles

面向“某个项目真实如何验证和交付”。

### 3. Prompt / skill docs / context files

面向“人或 agent 该如何理解当前项目和阶段”。

把这三者混成一个概念，会导致架构理解失真。

## Project profile 的角色

profile 是 Beacon 对“目标项目真实工作流”的抽象。

它可以声明：

- 哪个 skill 用于 verify
- 哪个 skill 用于 delivery/debug
- required evidence
- required business cases
- orchestration graph

## 为什么这和 v1.1.10 有关

`v1.1.10` 做 QA precision，如果忽略项目自己的 verify/workflow reality，就只会优化“通用 QA”，而不是优化真实交付路径。

## 提示词/文档面

Beacon 本身还有一层非代码但架构相关的引导面：

- `SKILL.md`
- `docs/beacon/<version>/execution/*`
- `context_files.py` 生成的上下文块

这层不执行逻辑，但决定：

- 人/Agent 先看到什么
- 从哪个入口进入 lifecycle
- 读取哪一批 requirement materials

所以它同样属于架构的一部分。
