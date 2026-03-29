# Test Cases: Beacon 源码架构人类友好文档与持续同步闭环（v1.1.10）

**Feature**: beacon-source-architecture-sync  
**Version**: v1.1.10

## 前置 Gate 结论

- Gate0 输入完整性：Pass
  已有并行 `user-story / prd / source-architecture/` 目标
- Gate1 文档范围：Pass
  覆盖命令、状态、memory、skill/project workflow、生命周期、QA、implement、release、feedback
- Gate2 同步契约：Pass
  已明确后续开发需同步更新 source-architecture 文档

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | directory | 检查 `docs/beacon/v1.1.10/source-architecture/` | 目录存在，作为正式源码架构子目录 |
| TC-002 | index | 读取 `source-architecture/index.md` | 有定位、受众和阅读顺序 |
| TC-003 | overall-map | 读取整体系统图 | 解释 `main.py / cli_factory.py / commands / utils / adapters / docs /.machine /.beacon` |
| TC-004 | command-map | 读取子命令与模块映射 | 能看懂命令如何注册、分层和落到源码模块 |
| TC-005 | state-map | 读取 memory/runtime/state 文档 | 能看懂 workflow memory、story/revision、QA session、`.beacon/state` |
| TC-006 | skills-map | 读取 skill/prompt/project workflow 文档 | 能看懂 skill adapters、project profiles、verify orchestration、prompt/skill surfaces |
| TC-007 | artifact-flow | 读取 workflow/artifact flow 文档 | 能看懂 `docs/beacon`、`.machine`、`.beacon` 之间的关系 |
| TC-008 | qa-loop | 读取 QA/implement/release feedback loop 文档 | 能看懂 browser session、evidence、implement、technical archive、architecture feedback 闭环 |
| TC-009 | sync-contract | 读取 `sync-contract.md` | 明确未来结构性变更必须同步更新架构文档 |
| TC-010 | human-friendly | 从新接手者视角审查文档 | 文档解释职责和配合关系，而不是只有文件罗列 |
| TC-011 | parallel-materials | 检查并行 `user-story / prd / qa/test-cases` | 该线有同级 requirement materials |
| TC-012 | machine-materials | 检查 `.machine` 工件 | 存在 story state、AC matrix、story-scenario-map、revision state |
| TC-013 | lifecycle-coverage | 审查文档主题 | 覆盖 lifecycle / workflow，而不只覆盖 CLI |
| TC-014 | skill-coverage | 审查 skill/workflow 内容 | 覆盖 memory、skill、子命令、生命周期、工作流、QA、implement、release |
| TC-015 | future-sync | 假设后续新增命令或状态流变化 | 文档明确这些变更必须同步更新 source-architecture 文档 |
| TC-016 | formal-audit | 审查 materials/gate 口径 | source-architecture 线应进入正式 audit/gate，而不只依赖独立测试 |

## 样板场景

### 场景 A：新开发者只读源码架构目录接手项目

- 不先读全部源码
- 先读 `source-architecture/index.md`
- 预期：能快速理解 Beacon 的主入口、分层、状态和工件流

### 场景 B：维护者新增一个 command 或状态面

- 例如新增子命令、运行态状态或新的 artifact path
- 预期：sync contract 明确要求同步更新对应 source-architecture 文档

### 场景 C：目标项目需要接入 profile / verify orchestration

- 开发者需要理解 project skill workflow
- 预期：源码架构文档可以解释 skill/profile/orchestration 在源码中的位置和关系

### 场景 D：源码架构线被主门禁检查

- 某次改动删掉或漂移了 `source-architecture/` 关键文档
- 预期：正式 materials/gate 能报告该问题，而不是只能等专门测试发现

## 执行语义

- `Pass`: source-architecture 目录与并行 requirement line 完整存在，内容覆盖全链路
- `Pass`: source-architecture 线进入正式 materials/gate 口径
- `Fail`: 只有零散旧版本架构文档，没有 v1.1.10 当前版源码架构目录
- `Blocked`: 架构文档与当前源码主入口、状态面或 artifact flow 存在关键冲突
