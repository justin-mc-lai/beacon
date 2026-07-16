# Tasks: beacon-global-workspace-git-admission-v162

## Task Ledger

### Phase R0 — Truth R2 + refreeze（方案 A）

- [x] TASK-WS-R01 truth/tests R2 方案 A（无 TTL、hook Should）。evidence: truth.md tests.md frozen R2
- [x] TASK-WS-R02 `beacon freeze` R2（TIG pass）。evidence: truth frontmatter status=frozen


### Phase R3 — Version-line operator closure

- [ ] TASK-WS-R03 truth/tests R3（upgrade-package 路由 + release stub）。evidence: truth.md tests.md
- [ ] TASK-WS-R04 `beacon change ... --refreeze-chain` R3。evidence: refreeze transaction complete
- [ ] TASK-WS-011 upgrade-package release stub + material gate routing。evidence: test_v162_version_line_package_closure.py
- [ ] TASK-WS-012 v1.6.2 verify-materials strict pass post upgrade-package。evidence: TC-VL-020

### Phase A — Governance + CLI

- [ ] TASK-WS-001 governance MD v1.6.2 block（dirty_only）。evidence: project-version-governance.md
- [ ] TASK-WS-002 实现 `beacon workspace admit` CLI + artifact schema。evidence: beacon/commands/workspace/
- [ ] TASK-WS-003 dirty invalidation 逻辑（无 TTL）。evidence: tests/test_v162_workspace_admit.py

### Phase B — Skill + CLI consumers

- [ ] TASK-WS-004 GIT_ADMISSION umbrella template + setup-agent-surface。evidence: skills/beacon/SKILL.md
- [ ] TASK-WS-005 implement/qa fail-closed wiring。evidence: implement + qa commands
- [ ] TASK-WS-006 check-branch alias + dev-run admit delegate。evidence: AC-010

### Phase C — Hook（Should）

- [ ] TASK-WS-007 Cursor/Claude admission hook（dirty/missing deny）。evidence: .cursor/hooks/
- [ ] TASK-WS-008 verify-agent-surface preamble fail / hook warn。evidence: agent_surface.py

### Phase D — QA closure

- [ ] TASK-WS-009 pytest suite + agent-eval fixture AC-011。evidence: tests/test_v162_*
- [ ] TASK-WS-010 `beacon qa run` + truth-map rebuild。evidence: qa verdict

## Boundary

Checkboxes 仅为任务台账；implement / QA / release 完成须由既有 gate 验证，禁止 checkbox 自证 closure。

## Blocked TC 映射（实现前）

| TC | 阻塞阶段 |
|----|----------|
| TC-WS-001..011 | BLOCKED:Phase-A/B |
| TC-WS-030..060 | BLOCKED:Phase-C |
| TC-WS-070..100 | BLOCKED:Phase-A/D |
