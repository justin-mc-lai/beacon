# 任务：Beacon Planner Review Intent Parity State Machine v1.6.0

## 任务台账

- [ ] TASK-001 新增 `skills/beacon/beacon-pln-review/SKILL.md`，并注入 v1.6.0 shared preamble 和 planner HARD GATE。
- [ ] TASK-002 为 `beacon-pln-review` 增加 `agents/openai.yaml` 或等价 metadata。
- [ ] TASK-003 增加 `references/reviewer-catalog.md`，定义 always-on 和 conditional reviewer。
- [ ] TASK-004 增加 `references/finding-schema.md`，定义 planner review finding schema 和 route rules。
- [ ] TASK-005 增加 `references/intent-parity-artifacts.md`，定义 intent snapshot、scope mode、source inventory、parity matrix、promotion diff 和 deferral ledger。
- [ ] TASK-006 增加 `references/state-machine-review.md`，定义状态机 reviewer 的触发条件、输出字段和 truth/tests 落点。
- [ ] TASK-007 增加 `references/skill-package-standard.md`，吸收 qi-dev/OpenAI/Anthropic skill-creator package 标准。
- [ ] TASK-008 更新 v1.6.0 skill projection / rename matrix，使 `beacon-pln-review` 成为 public planner skill。
- [ ] TASK-009 收敛 v1.6.0 public planner projection，只默认暴露 `beacon-pln-brainstorm`、`beacon-pln-source`、`beacon-pln-review`、`beacon-pln-friction`。
- [ ] TASK-010 将 founder/security/performance/doubt/context/simplify/adr/design/deep 降级为 internal reviewer/reference，避免作为默认 public route。
- [ ] TASK-011 更新 root `skills/beacon/SKILL.md` 和 metadata，反映收敛后的 planner public surface。
- [ ] TASK-012 更新 skill package verify 规则，检测 unexpected public planner skills。
- [ ] TASK-013 更新 skill eval benchmark cases，覆盖 intent parity、source parity、deferral ledger、state-machine reviewer 和 boundary negative。
- [ ] TASK-014 更新 tests，覆盖 materialize/verify/agent surface projection 和 reviewer references。
- [ ] TASK-015 运行 OpenAI/Anthropic quick validation 或 Beacon equivalent verify，证明 skill package anatomy 合格。
- [ ] TASK-016 运行 focused tests 和 formal QA handoff；生成 implementation evidence，但不自证 QA/release。

## 边界

任务台账不是 implementation completion。只有 implementation evidence、formal QA 和 release gate 通过后，才能进入 closure。
