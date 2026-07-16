# Beacon v1.5.0

## 当前冻结范围

- `beacon-v1.5.0-parallel-plan-b-document-capability`

## 版本定位

v1.5.0 上线新的 feature-centric 整体文档能力，并与现有 Beacon truth triptych 并行存在。它不退役现有 `prd`、`user-story`、`qa/test-cases`、`execution` 或 `.machine` 表面。

## 权威材料

- PRD: `docs/beacon/archive/v1.5.0/prd/beacon-v1.5.0-parallel-plan-b-document-capability.md`
- User Story: `docs/beacon/archive/v1.5.0/user-story/beacon-v1.5.0-parallel-plan-b-document-capability.md`
- Test Cases: `docs/beacon/archive/v1.5.0/qa/test-cases/beacon-v1.5.0-parallel-plan-b-document-capability.md`
- Research: `docs/beacon/archive/v1.5.0/research/beacon-v1.5.0-parallel-plan-b-document-capability.md`

## 执行边界

- 新增 `features/<slug>/{truth,tests,tasks,evidence}.md` 并行文档包。
- `truth.md` frontmatter 是并行 metadata，不替代 `.machine`。
- `tasks.md` checkbox 是任务台账，不绕过 implement / QA gate。
- `evidence.md` 是索引/read model，不承载 gate truth。
- CLI 负责确定性解析和校验 frontmatter、AC 表、checkbox、evidence authority labels。
- LLM 可以写 MD 内容和 checklist，但状态推进必须经 CLI validation。
