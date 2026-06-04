# Test Cases: Beacon v1.3.7 implement frozen-truth verification and canonical delivery baseline envelope

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | frozen `prd / user-story / test-case` 已存在，用户在 Codex / Claude 内以 `beacon-implement + version + prompt` 启动实现 | integration | 系统直接进入实现前核实流程，不要求用户重新手工准备 requirement 包。 |
| TC-002 | AC-002 | prompt 仅补充实现顺序、代码范围或 scope 内澄清 | unit | 系统将 prompt 判定为 `in_scope_implementation` 或 `clarification_within_scope`，允许继续。 |
| TC-003 | AC-003 | prompt 暗含新增用户故事、扩展 AC、扩展测试范围、改变需求边界 | integration | 系统判定为 `requirement_change`，阻断 implement，并返回 requirement change / refreeze 指引。 |
| TC-004 | AC-003 | prompt 与 frozen requirement truth 冲突 | integration | 系统判定为 `truth_conflict`，阻断 implement，不进入实现执行。 |
| TC-005 | AC-004 | `implement plan` 执行时生成 canonical delivery baseline envelope | integration | canonical envelope 先提交，再投影出 `architecture-blueprint`、deterministic contract、git workflow、implementation plan。 |
| TC-006 | AC-005 | 某个 projection 的 `baseline_id`、`source_hash` 或 service/branch/worktree 信息与 canonical envelope 不一致 | integration | gate 阻断，并返回明确 drift diagnostics。 |

## Execution Notes

- version: `v1.3.7`
- AC-001 到 AC-005 都必须有可执行测试覆盖。
- 必须同时验证 happy path、requirement change path、truth conflict path、projection drift path。
