# User Story: Beacon 源码架构人类友好文档与持续同步闭环（v1.1.10）

**Feature**: beacon-source-architecture-sync  
**Version**: v1.1.10

**As a** Beacon 维护者 / 新接手开发者 / 使用 Beacon 做二次开发的 Agent 协作者  
**I want** 在 `docs/beacon/v1.1.10/` 下新增一组人类友好的源码架构拆解文档，并把它纳入正式 requirement materials 与后续开发同步契约  
**So that** 后续从 memory、skill prompts、子命令、生命周期、工作流、QA、implement、release 到架构回流的全链路都能被人类快速理解、校对、持续更新，而不是只能靠直接读源码。

## Story Slices

### US-001: Beacon 在 v1.1.10 下新增源码架构子目录
作为维护者，我希望 `docs/beacon/v1.1.10/source-architecture/` 成为人类主读的源码架构子目录，而不是把源码结构信息散落在多个旧版本设计文档里。

### US-002: Beacon 提供整体源码架构总览
作为新接手开发者，我希望快速看到 `main.py / cli_factory.py / commands / utils / adapters / docs /.machine /.beacon` 的整体分层图。

### US-003: Beacon 提供子命令与模块映射
作为 CLI 维护者，我希望能从子命令视角理解每个命令大致落在哪个源码模块与能力层。

### US-004: Beacon 提供 runtime state / memory / revision 结构说明
作为 workflow 维护者，我希望知道 `.beacon/`、story state、revision state、workflow memory、QA session 等状态面分别负责什么。

### US-005: Beacon 提供 skill / prompt / project profile / orchestration 结构说明
作为项目接入者，我希望知道 Beacon 如何与 skill adapters、project profiles、verify orchestration 和提示词面协作。

### US-006: Beacon 提供 lifecycle / workflow / artifact flow 拆解
作为需求交付维护者，我希望用一套人类友好的文档理解 `think → user-story → prd → test-case → implement → qa → gate → release → feedback` 如何映射到源码与工件。

### US-007: Beacon 提供 QA / browser / session / evidence / implement 回流链说明
作为 QA owner，我希望理解 browser session、evidence、release scorecard、implement technical archive、requirement rewrite input 的关系。

### US-008: Beacon 规定未来开发必须同步更新源码架构文档
作为架构负责人，我希望后续 `v1.1.10+` 相关开发都把源码架构文档更新当成正式交付项，而不是“以后再补”。

### US-009: Beacon 把架构文档纳入同级 requirement materials
作为版本负责人，我希望源码架构文档线有独立的 user-story / PRD / QA test cases / machine artifacts / release feedback，而不是只有目录说明。

### US-010: Beacon 让源码架构文档面向人类阅读，而不是机械罗列文件
作为新接手者，我希望文档回答“为什么这样分层、这些模块如何配合、改动时要同步什么”，而不是只给出文件清单。

### US-011: Beacon 把源码架构线纳入正式 materials audit / gate
作为架构负责人，我希望 source-architecture 线不只是“有测试”，而要进入正式的 materials/gate 闭环。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Source Architecture Dir | `docs/beacon/v1.1.10/source-architecture/` 正式存在并被纳入版本目录 |
| AC-002 | Reading Order | 该目录存在 `index.md` 并提供明确阅读顺序 |
| AC-003 | Overall Map | 存在整体源码架构总览，解释 `main.py / cli_factory.py / commands / utils / adapters / docs /.machine /.beacon` |
| AC-004 | Command Map | 存在子命令与模块映射文档，帮助人理解 CLI surface 与源码模块关系 |
| AC-005 | Memory State Map | 存在 memory / runtime / revision / story / QA session 等状态面说明 |
| AC-006 | Skill Prompt Map | 存在 skill adapters、project profile、verify orchestration、prompt/skill surfaces 的源码说明 |
| AC-007 | Workflow Artifact Map | 存在 lifecycle / workflow / docs / `.machine` / `.beacon` 工件流说明 |
| AC-008 | QA Implement Loop | 存在 QA / browser session / evidence / implement / technical archive / architecture feedback 回流说明 |
| AC-009 | Human Friendly Style | 文档面向人类阅读，解释职责、边界、配合关系和更新点，而不是单纯文件列表 |
| AC-010 | Sync And Gate Contract | 存在明确的同步契约，且 source-architecture 线进入正式 materials/gate 闭环 |
| AC-011 | Parallel Requirement Line | 该 feature 具有同级别 `user-story / prd / qa/test-cases / release feedback` |
| AC-012 | Machine Compatibility | 该 feature 也生成 `.machine/user-story`、`.machine/qa/*`、`.machine/execution/*.revision.json` 等标准机器工件 |
| AC-013 | Lifecycle Coverage | 文档覆盖 Beacon 生命周期与工作流，而不只覆盖 CLI 入口 |
| AC-014 | Skill Coverage | 文档覆盖 memory、skill prompts、project skills、子命令、workflow、QA、implement、release 等全链路 |
| AC-015 | Future Update Rule | 后续 `v1.1.10` 相关源码变更若影响结构、职责、工件流、状态流，必须同步更新源码架构文档 |

## Risks And Reminders

- 若只有源码没有人类友好架构文档，新接手成本仍然高，Agent 协作也更容易走偏
- 若架构文档只是静态一次性产物，不绑定后续更新规则，很快会过时
- 若不把 source-architecture 文档纳入同级 requirement materials，它会再次退化成“补充说明”
- 若 source-architecture 线不进入正式 audit/gate，它仍然只是“有测试兜底的附属文档”
- 若只写命令清单，不写状态流、artifact flow 与实现回流链，文档仍不足以指导迭代

## Execution Semantics

- `Pass`: 源码架构文档线完整存在，并与 v1.1.10 其它 requirement materials 同级治理
- `Pass`: 文档覆盖命令、状态、memory、skills、workflow、QA、implement、release、feedback 等全链路
- `Fail`: 只有零散说明，没有独立架构目录与并行 requirement line
- `Blocked`: 架构文档与源码实际入口、状态流或工件流存在关键冲突
