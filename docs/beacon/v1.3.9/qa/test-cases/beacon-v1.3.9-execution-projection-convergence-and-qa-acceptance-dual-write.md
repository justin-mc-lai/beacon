# Test Cases: Beacon v1.3.9 execution projection convergence and QA acceptance dual-write

**Feature**: `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`  
**Version**: `v1.3.9`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 读取 `v1.3.9` execution taxonomy contract | docs | artifact taxonomy 明确区分 canonical、required human、optional derived、deprecated template。 |
| TC-002 | AC-002 | QA 在 evidence-backed verdict 后完成一次 acceptance writeback | integration | 生成 machine-readable acceptance envelope，且包含 requirement refs、test-case refs、evidence refs、verdict 与 transaction metadata。 |
| TC-003 | AC-003 | 同一笔 QA acceptance transaction 被提交 | integration | machine sink 与 `docs/beacon/<version>/execution/qa-acceptance-<feature>.md` 在同一事务元数据下落盘。 |
| TC-004 | AC-004 | 对同一 feature 分别执行 `release check`、`release scorecard` 与 `gate check release` | integration | 三者消费同一 acceptance/readiness truth，reason codes 与 readiness judgement 无平级漂移。 |
| TC-005 | AC-005 | 读取保留的 execution human docs | docs | 文档包含 command usage、inputs、outputs、evidence refs 与 next step，而不是只剩模板壳。 |
| TC-006 | AC-006 | 执行 `help / status / doctor / archive` 的相关 delivery read-model 路径 | integration | 这些命令优先返回解释型结果，不会默认制造新的模板 execution 文档。 |
| TC-007 | AC-007 | 检查 `docs/beacon/v1.3.9/execution/` 的迁移策略输出 | docs | 明确标记旧文件属于保留、合并、按需生成或废弃。 |
| TC-008 | AC-008 | 新的 qa/release/gate/support 收敛链路落盘 | integration | transaction lineage、writeback、canonical projection 与 host-native orchestration 复用既有 Beacon 能力，而不是新建平行 truth pipeline。 |
| TC-009 | AC-009 | 在 host/LLM compile 不可用或 contract 校验失败条件下执行 `prototype plan/create --mode auto` | integration | 系统显式返回 downgrade/block 信号，不会静默产出被判定为正常通过的固定模板结果。 |
| TC-010 | AC-010 | QA 在 evidence-backed verdict 后执行 acceptance writeback | integration | 同一 transaction 共享 `source_hash / projection_seq / transaction_id / committed_at / sink_checksums`，并覆盖 machine sink、human sink、runtime projection sink。 |
| TC-011 | AC-011 | 在 acceptance/prototype transaction 出现 sink 缺失、failed transaction 或 metadata drift 时执行 `status / doctor / gate / release` | integration | 四个消费者给出一致的 fail/block 结论，不会出现单面 pass。 |
| TC-012 | AC-012 | 构造一个 PRD/change/release 面承诺了 operator-visible surface、但 implement/review/evidence 面没有 shipped trace 的 feature | integration | `implement` downstream read-model、`gate check release` 与 `release check/scorecard` 会给出一致的 promised-vs-shipped blocking drift verdict。 |
| TC-013 | AC-013 | 执行 `beacon prd create` 或等价 PRD 生成路径，并观察仅能产出 generic placeholder 的场景 | integration | 系统不会把 generic placeholder 当作 requirement-ready 成功结果；返回的是 requirement-aware scaffold，或显式 downgrade/fail。 |

## Execution Notes

- `TC-002` 到 `TC-004` 需要真实或隔离项目验证，不能只靠静态文档断言。
- `TC-005` 到 `TC-007` 负责验证 execution human 面是否真正减模板化。
- `TC-009` 用于证明 `prototype` 已不再把模板 fallback 伪装成正常 requirement compile。
- `TC-010` 与 `TC-011` 用于证明 acceptance/prototype transaction 已真正进入跨 sink anti-drift 阻断链。
- `TC-012` 用于证明“主摩擦”已经被 requirement truth 正式吸收为 blocking gate，而不是继续停留在 friction 报告里。
- `TC-013` 用于证明“单独 PRD 摩擦场景”被单独建模，而不是继续混在 generic requirement compile 成功路径里。
- 所有测试都必须能回链到同一组 requirement refs 与 transaction metadata。
