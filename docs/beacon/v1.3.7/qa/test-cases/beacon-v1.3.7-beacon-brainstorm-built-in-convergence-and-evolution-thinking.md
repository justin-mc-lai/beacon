# Test Cases: Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 用户在 Beacon 人类面中使用 `beacon-brainstorm` | integration | `beacon-brainstorm` 作为 Beacon 内建、host-visible、非主流程子 skill 存在。 |
| TC-002 | AC-002 | `beacon-brainstorm` 接收 version 与 prompt，并读取 `docs/beacon/<version>/` 材料继续头暴 | integration | 输出明确引用 version docs，而不是脱离正式材料发散。 |
| TC-003 | AC-003 | 用户分别触发 requirement convergence、frozen-truth delta、evolution exploration、redundancy pruning | integration | skill 能在四类模式下给出对应分析与收敛结果。 |
| TC-004 | AC-004 | skill 针对同一问题进行追问与收敛 | unit | 输出显式体现第一性原理拆解、苏格拉底式追问、奥卡姆式冗余剔除。 |
| TC-005 | AC-005 | skill 生成最终建议与文档产物 | integration | skill 只输出思考、收敛与建议，不直接改写 requirement truth、不直接执行 implement，并生成单一 Markdown 文件。 |

## Execution Notes

- version: `v1.3.7`
- AC-001 到 AC-005 都必须有可执行测试覆盖。
- 必须同时验证 version grounding、四类模式、三类思维协议、边界约束与产物输出。
