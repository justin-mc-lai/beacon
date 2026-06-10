# 测试：Beacon Loop Native Runner and Automation Retirement

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `beacon --help` / command catalog tests | `automation` 不再作为 active command surface 暴露；如有 stub，只能阻断并提示 `beacon-loop goal`。 |
| AC-001 | TC-002 | negative | `rg "beacon-automation-queue|beacon-hourly-qa|repair-window" beacon automation tests` | 旧 automation queue/job/launchd 业务入口被删除或不再被 active tests/docs 引导。 |
| AC-002 | TC-003 | package | `cd packages/beacon-loop && npm run build` | `packages/beacon-loop` 能构建独立 `beacon-loop` CLI。 |
| AC-003 | TC-004 | contract | `beacon-loop --help` | help 只暴露 `goal`，不暴露 `lfg`。 |
| AC-003 | TC-005 | negative | `beacon-loop lfg "x"` | `lfg` 不是可执行 alias、deprecated alias 或 compatibility route。 |
| AC-004 | TC-006 | integration | `beacon-loop goal "<goal>" --dry-run --json` | run package 包含 `beacon truth-map resolve ... --json` 的 resolver refs。 |
| AC-005 | TC-007 | negative | `beacon-loop goal "<missing-feature>" --json` | feature package 缺失或 resolver blocked 时 fail closed，并推荐 `beacon-gen-change`。 |
| AC-006 | TC-008 | integration | `beacon-loop goal "<goal>" --dry-run --json` | 创建完整 runtime package 文件集。 |
| AC-007 | TC-009 | negative | dirty worktree fixture | 默认 dirty worktree 阻断。 |
| AC-008 | TC-010 | runner | mocked agent success/failure/commit-failure tests | success commit；failure rollback；commit failure 保留 repair state。 |
| AC-009 | TC-011 | runner | `beacon-loop resume <run-id> --json` | resume 读取既有 metadata/notes/worktree，不新建无关 run。 |
| AC-010 | TC-012 | integration | `beacon-loop import-evidence <run-id> --json` | 调用 Beacon implementation evidence import。 |
| AC-011 | TC-013 | negative | inspect `beacon-loop` result payloads | 不输出 QA pass、release ready 或 feature complete verdict。 |
| AC-012 | TC-014 | docs | `rg "beacon-loop lfg|\\blfg\\b" docs beacon packages tests` | active 面不出现 `lfg` route。 |
| AC-013 | TC-015 | test-suite | focused pytest/npm tests | automation retirement + beacon-loop 测试存在。 |
| AC-014 | TC-016 | contract | inspect run artifacts | runtime process record；不写 `.machine` requirement projection。 |
| AC-015 | TC-017 | CLI | `beacon-loop doctor --json` / `beacon-loop doctor --diagnose --json` | doctor 检查 prerequisites；diagnose 输出分桶。 |
| AC-016 | TC-019 | runner | multi-iteration fixture `--max-iterations 3` | 产生 iteration-001..003 artifacts；最终 `cap_reached` 或 stop-when。 |
| AC-017 | TC-018 | runner | resume after partial run | 下一轮 iteration 编号为 N+1，同一 run-id。 |
| AC-018 | TC-021 | runner | stop graceful vs `--force` | graceful 等当前轮结束；force 立即 `force_stopped`。 |
| AC-019 | TC-022 | runner | consecutive failure + backoff fixtures | 连续失败 abort；hard error 退避；no-op 计 failure。 |
| AC-020 | TC-020 | runner | inspect iteration prompt build | 第 N 轮 prompt 含 notes 累积内容。 |
| AC-021 | TC-023 | CLI | `beacon-loop review <run-id>` after multi-run | summary 含 elapsed/branch/iterations/tokens/commands。 |
| AC-022 | TC-024 | ledger | `beacon-loop runs query --json` | 返回 ledger 中 run 列表。 |
| AC-022 | TC-025 | ledger | `beacon-loop runs show <run-id> --json` | 返回单 run 详情与 artifact refs。 |
| AC-023 | TC-026 | ledger | `beacon-loop runs diagnose --json` | 分桶 blocked/dirty/missing-backend 等。 |
| AC-024 | TC-027 | runtime | runtime-set/list/remove cycle | runtime 状态与 run-id 关联并可查询。 |
| AC-025 | TC-028 | harness | `beacon-loop analyze/learn <run-id> --json` | 站外 index 产物生成；不修改 feature package。 |
| AC-026 | TC-029 | git | branch mode matrix | worktree/current-branch 合法；非法组合 fail closed。 |
| AC-027 | TC-030 | config | config file load + CLI override | config 默认值生效；CLI flag 覆盖 config。 |
| AC-028 | TC-031 | integration | codex multi-iteration (opt-in live or recorded) | 非单次 fixture 路径下完成 ≥2 轮。 |
| AC-029 | TC-032 | contract | claude + acp adapter contract tests | 两 adapter 输出 required schema。 |
| AC-030 | TC-033 | e2e | scripted closed loop | goal -> import-evidence -> beacon qa run 可驱动；verdict 来自 Beacon。 |
| AC-008/011 | TC-034 | state | illegal transition tests | `implementation_candidate` 不得直接 `terminal_closed`；iterating 不得跳 qa_pending。 |
| AC-009/016 | TC-035 | state | resume + repair paths | repair_required -> resume -> iterating 合法。 |

## State Machine Coverage

| Transition class | TC IDs |
|------------------|--------|
| allowed | TC-010, TC-018, TC-019, TC-021, TC-035 |
| illegal | TC-034 |
| terminal (Beacon-only) | TC-013, TC-033 |
| recovery | TC-011, TC-035 |

## 验证说明

本测试包只定义 acceptance coverage。`beacon-loop` 的 runtime artifacts 不能替代 `features/<slug>/{truth,tests,tasks,evidence}.md`，也不能替代 Beacon QA/release verdict。

TC-031 允许 opt-in live agent tier；默认 CI 使用 recorded/fixture tier，但不得用单次 dry-run 冒充多轮 orchestrator 覆盖。
