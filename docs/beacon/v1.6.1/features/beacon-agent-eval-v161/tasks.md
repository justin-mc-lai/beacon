# Tasks: beacon-agent-eval-v161

## Task Ledger

### Phase R0 — Research + truth freeze (R1)

- [x] TASK-AE-R01 创建 research promoted artifact。evidence: `docs/beacon/v1.6.1/research/beacon-agent-eval-v161.md`
- [x] TASK-AE-R02 TIG hygiene + verify-closure + freeze CLI R1。evidence: baseline `sha256:13809725…ebd2c`

### Phase R2 — Change: 全 skill live（用户确认）

- [x] TASK-AE-R03 `beacon change --reopen-now` R1→R2。reason: 全 skill live P0
- [x] TASK-AE-R04 truth/tests/tasks 写入 live skill matrix（§I）+ AC-AE-030..033
- [x] TASK-AE-R05 freeze R2 + TIG pass。evidence: baseline `sha256:72b97d62…482e`

### Phase A — Contract & catalog scaffold

- [x] TASK-AE-001 新增 `docs/beacon/v1.6.1/execution/agent-eval-contract.md`（normative CLI + scorecard schema）
- [x] TASK-AE-002 实现 `beacon eval` 顶层 typer 子树（catalog / run / scorecard / benchmark）
- [x] TASK-AE-003 实现 `materialize_agent_eval_catalog()` → `agent-eval-capability-catalog-v161.json`
- [x] TASK-AE-004 更新 v1.6.1 SUMMARY 索引本 feature

### Phase B — Run / replay / score synthesis

- [x] TASK-AE-005 新建 `beacon/utils/agent_eval_kit.py`（或扩展 `skill_eval_kit.py`）统一 case root
- [x] TASK-AE-006 实现 `beacon eval run --runner replay` traces + metrics.json
- [x] TASK-AE-007 实现 `beacon eval scorecard` 六维分 + composite + authority 字段
- [x] TASK-AE-008 实现 simulated 模式：`degraded` + `simulated_composite_score` + composite 封顶 85

### Phase C — Benchmark v1.6.1 case set

- [x] TASK-AE-009 扩展 benchmark 至 `--version v1.6.1`（继承 taxonomy-v160 条目 018–022 + TC-006..011/017）
- [x] TASK-AE-010 with_skill / baseline 双配置 grading + analysis.md
- [x] TASK-AE-011 fake-delivery / weak-assertion critique 写入 grading artifact

### Phase D — Live runner admission + full skill matrix

- [x] TASK-AE-012 定义 `agent-eval-runner-admission.json` schema + doctor 校验
- [x] TASK-AE-013 实现 live runner 启动与 trace 落盘（host adapter 抽象）
- [x] TASK-AE-014 无 admission 时 blocked + `agent_eval_live_runner_not_admitted`
- [x] TASK-AE-014a 实现 `materialize_agent_eval_live_skill_matrix()` → `agent-eval-live-skill-matrix-v161.json`（37 条，doctor strict 对齐）
- [x] TASK-AE-014b live regression-core 逐 skill 执行 + per_skill trace/blocked 输出（AC-AE-031/032）

### Phase E — FSM / skill / acceptance bridge

- [x] TASK-AE-015 实现 `AgentEvalState` + `beacon/utils/agent_eval_state.py`
- [x] TASK-AE-016 新增 `tests/test_agent_eval_state_contract.py`（非法转移 + recovery）
- [x] TASK-AE-017 物化 `beacon-eval-agent` host skill + agent surface verify
- [x] TASK-AE-018 Acceptance Kit trace-scorecard supplement 汇入 hook

### Phase F — QA closure

- [x] TASK-AE-019 `beacon test-case create` 同步 qa/test-cases + `.machine/qa` matrix
- [x] TASK-AE-020 `beacon truth-map rebuild-machine` + TIG block mode pass
- [x] TASK-AE-021 `beacon skill package verify-closure` pass
- [x] TASK-AE-022 `beacon qa run beacon-agent-eval-v161` 33/33 + acceptance-kit materialize
- [x] TASK-AE-023 Research artifact：`docs/beacon/v1.6.1/research/beacon-agent-eval-v161.md` + user_decision promoted
- [x] TASK-AE-024 Truth freeze R2（full_parity scope_mode 确认）

## Boundary

Checkboxes 仅为任务台账；implement / QA / release 完成须由既有 gate 验证，禁止 checkbox 自证 closure。

## Blocked TC 映射（实现前）

| TC 组 | 预期 BLOCKED 阶段 |
|-------|-------------------|
| TC-AE-001..003 | Phase-A |
| TC-AE-004..007 | Phase-B |
| TC-AE-008..009 | Phase-D |
| TC-AE-030..032 | Phase-D |
| TC-AE-010..012 | Phase-C |
| TC-AE-017..018 | Phase-E |
| TC-AE-027 | Phase-F |
