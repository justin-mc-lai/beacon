# Tests: beacon-v1.5.0-parallel-plan-b-document-capability

## Coverage Matrix

| AC ID | TC ID | Layer | Assertion |
|-------|-------|-------|-----------|
| AC-001 | TC-001 | integration | 创建 `features/<slug>/truth.md`、`tests.md`、`tasks.md`、`evidence.md`，不删除 triptych。 |
| AC-002 | TC-002 | e2e | Freeze 仍使用 canonical PRD、user-story、test-case chain。 |
| AC-003 | TC-003 | unit | 旧命令存在并返回 help。 |
| AC-004 | TC-004 | integration | 文件包含 canonical artifact links 且无 final verdict field。 |
| AC-005 | TC-005 | integration | Rows 被标记为 `support_advisory`。 |
| AC-006 | TC-006 | e2e | QA/release verdicts 从现有 canonical outputs 读取。 |
| AC-007 | TC-007 | unit | Index 包含 `Surface`、`Authority`、`Canonical Artifact`、`Status`、`Route` columns。 |
| AC-008 | TC-008 | integration | Drift check 返回 blocked 或 warning，不 silent pass。 |
| AC-009 | TC-009 | unit | Canonical projection 与 transaction consistency 未削弱。 |
| AC-010 | TC-010 | e2e | 旧 skills 和 CLI 保持安装，无 retirement action。 |
| AC-011 | TC-011 | integration | YAML frontmatter 包含 required fields，且被报告为 parallel metadata。 |
| AC-012 | TC-012 | integration | CLI 报告 task ledger state，但不标记 implement/QA gate complete。 |
| AC-013 | TC-013 | unit | Validator 输出 deterministic diagnostics 并阻断或告警。 |
| AC-014 | TC-014 | e2e | Lifecycle state 在 CLI validation 通过前保持 draft。 |
| AC-015 | TC-015 | unit | Validator reject 或 flag 该字段。 |
| AC-016 | TC-016 | integration | Templates 包含 required fields 并通过 parser validation。 |

## Validation Note

This file is a parallel test read model. Canonical test truth remains in `qa/test-cases/` and `.machine/qa/` in v1.5.0.
