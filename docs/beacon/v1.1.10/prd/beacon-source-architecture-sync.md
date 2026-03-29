# PRD: Beacon 源码架构人类友好文档与持续同步闭环（v1.1.10）

## 1. Background

Beacon 已经积累了较强的产品工作流、QA、release、project skill、technical archive 能力。

但当开发者真正进入源码层时，仍然存在一个明显问题：

> **产品层 requirement materials 已经很多，但源码层的人类友好架构投影还不够集中、稳定、版本化。**

当前仓里虽然已有多份架构/命令/内存/蓝图文档，但它们分布在多个历史版本中：

- `v1.0.3` 总体架构蓝图
- `v1.1.1` 功能架构目录地图
- `v1.1.5/v1.1.6/v1.1.7` command reference / memory architecture / lifecycle blueprint
- `v1.1.8/v1.1.9` architecture blueprint / closure blueprint / technical archive blueprint

这些材料有价值，但仍不够回答一个实际问题：

> 以当前 `v1.1.10` 为基线，Beacon 源码到底如何分层、如何流动、哪些文件负责什么、以后修改要同步什么？

## 2. First-principles problem

源码架构文档需要满足三个条件：

1. **面向人类理解**
   - 不是 API dump
   - 不是目录树罗列
2. **对当前实现负责**
   - 必须锚定当前源码入口与当前版本工件流
3. **能持续同步**
   - 后续变更时不是可选项，而是交付面的一部分

如果缺任一条件，就会退化为：

- 过时文档
- 无法指导接手
- 需求线与实现线断裂

## 3. Goals

1. 在 `docs/beacon/v1.1.10/source-architecture/` 下建立正式源码架构目录
2. 提供人类友好的源码架构阅读顺序与模块解释
3. 覆盖 memory、skill prompt/project skill、子命令、生命周期、工作流、QA、implement、release、feedback
4. 让源码架构文档成为后续开发必须同步更新的正式契约
5. 为该架构文档线提供同级 requirement materials 与 machine artifacts
6. 把该线纳入正式 materials/gate 闭环，而不是只靠回归测试

## 4. Non-goals

1. 不自动生成全量 API 参考文档
2. 不替代源码本身
3. 不要求把每个私有函数都逐行解释
4. 不承诺零偏差自动同步；本版先建立同步契约和目录标准

## 5. Product principles

1. **Human-first, source-anchored**
2. **Explain responsibility, not just filenames**
3. **Document flows, not only layers**
4. **Versioned architecture docs are part of delivery**
5. **Any structural code change should have a doc sync path**

## 6. Functional requirements

### FR-001 Source architecture directory must exist

Create:

```text
docs/beacon/v1.1.10/source-architecture/
```

### FR-002 Index and reading order must exist

The directory must contain an `index.md` that explains:

- what this directory is for
- who should read it
- recommended reading order

### FR-003 Overall architecture map must exist

Human-readable overall map should cover:

- `main.py`
- `cli_factory.py`
- `command_catalog.py`
- `commands/`
- `utils/`
- `adapters/`
- `docs/beacon/`
- `docs/beacon/<version>/.machine/`
- `.beacon/`

### FR-004 Command surface map must exist

Must explain:

- how commands are registered
- how core/support/labs/bridge surfaces differ
- how subcommands map to modules

### FR-005 Memory/runtime/state map must exist

Must explain:

- workflow memory
- story state
- revision state
- QA runtime/session
- `.beacon/state/`
- `.beacon/qa/`
- `.beacon/implement/`

### FR-006 Skill/prompt/project workflow map must exist

Must explain:

- skill adapters
- project skill registry
- profiles
- feature/profile binding
- verify orchestration
- prompt/skill guidance surfaces where relevant

### FR-007 Workflow/artifact flow map must exist

Must explain:

- `docs/beacon`
- `.machine`
- `.beacon`
- how artifacts move from requirement to implementation to QA to gate/release

### FR-008 QA/implement/release feedback loop map must exist

Must explain:

- browser session/auth persistence
- evidence packs
- release scorecard
- implement outputs
- technical archive
- requirement rewrite input
- architecture feedback

### FR-009 Sync contract must exist

Must explicitly say that future development affecting:

- structure
- state
- artifact flow
- command surface
- skill/project workflow

must update source architecture docs.

### FR-010 Parallel requirement materials must exist

This architecture-doc line must have:

- `user-story`
- `prd`
- `qa/test-cases`
- `release feedback`
- machine artifacts

### FR-011 Source-architecture line must enter formal audit

Formal materials/gate closure must know that this parallel line exists.

The shortest correct path is:

- detect source-architecture requirement line in materials audit
- fail or warn when it drifts or disappears

This is better than relying only on standalone tests, because the main gate should defend the main architecture contract.

## 7. Deliverables

### Requirement materials

- `user-story/beacon-source-architecture-sync.md`
- `prd/beacon-source-architecture-sync.md`
- `qa/test-cases/beacon-source-architecture-sync.md`
- `release/v1.1.10.md` update

### Source architecture directory

- `source-architecture/index.md`
- `source-architecture/overall-system-map.md`
- `source-architecture/command-surface-and-module-map.md`
- `source-architecture/lifecycle-memory-and-state.md`
- `source-architecture/skills-prompts-and-project-workflows.md`
- `source-architecture/workflow-and-artifact-flow.md`
- `source-architecture/qa-implement-release-feedback-loop.md`
- `source-architecture/sync-contract.md`

### Machine artifacts

- `.machine/user-story/beacon-source-architecture-sync.json`
- `.machine/qa/beacon-source-architecture-sync.ac-test-matrix.json`
- `.machine/qa/beacon-source-architecture-sync.story-scenario-map.json`
- `.machine/execution/beacon-source-architecture-sync.revision.json`

## 8. Success criteria

- 新接手 Beacon 源码的人可以只读 `source-architecture/` 先建立整体模型
- 开发者可以根据文档定位命令入口、状态流、artifact flow、skill/profile/orchestration 位置
- 架构文档线通过 versioned materials regression tests
- 后续代码结构变更具备明确 doc-sync 约束

## 9. Boundary matrix

| Boundary | Allowed | Not allowed |
| --- | --- | --- |
| Human readability | Explain responsibilities, flows, boundaries | Raw directory dump only |
| Version scope | v1.1.10 current-source projection | Rewriting every historical version |
| Source references | Link to current code entrypoints | Pretending docs replace code |
| Sync rule | Require docs update on structural changes | Treat docs as optional afterthought |

## 10. Final statement

`v1.1.10` should not only describe what Beacon does as a product.

It should also provide a stable, human-readable answer to:

```text
How Beacon is actually built today,
how its parts fit together,
and what must be updated when the system evolves.
```
