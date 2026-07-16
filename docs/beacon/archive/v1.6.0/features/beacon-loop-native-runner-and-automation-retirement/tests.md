# 测试：Beacon Loop Native Runner and Automation Retirement

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc001_automation_not_active_command_surface --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `automation` 不再作为 active command surface 暴露；如有 stub，只能阻断并提示 `beacon-loop goal`。 |
| AC-001 | TC-002 | negative | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc002_old_automation_queue_job_assets_retired --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 旧 automation queue/job/launchd 业务入口被删除或不再被 active tests/docs 引导。 |
| AC-002 | TC-003 | package | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc003_beacon_loop_package_builds --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `packages/beacon-loop` 能构建独立 `beacon-loop` CLI。 |
| AC-003 | TC-004 | contract | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc004_help_exposes_goal_not_lfg --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | help 只暴露 `goal`，不暴露 `lfg`。 |
| AC-003 | TC-005 | negative | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc005_lfg_alias_rejected --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `lfg` 不是可执行 alias、deprecated alias 或 compatibility route。 |
| AC-004 | TC-006 | integration | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc006_dry_run_includes_resolver_refs --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | run package 包含 `beacon truth-map resolve ... --json` 的 resolver refs。 |
| AC-005 | TC-007 | negative | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc007_resolver_blocked_fail_closed --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | feature package 缺失或 resolver blocked 时 fail closed，并推荐 `beacon-gen-change`。 |
| AC-006 | TC-008 | integration | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc008_dry_run_writes_runtime_package --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 创建完整 runtime package 文件集。 |
| AC-007 | TC-009 | negative | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc009_dirty_worktree_blocked --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 默认 dirty worktree 阻断。 |
| AC-008 | TC-010 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc010_success_failure_rollback_commit_repair --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | success commit；failure rollback；commit failure 保留 repair state。 |
| AC-009 | TC-011 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc011_resume_reuses_existing_run --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | resume 读取既有 metadata/notes/worktree，不新建无关 run。 |
| AC-010 | TC-012 | integration | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc012_import_evidence_bridge --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 调用 Beacon implementation evidence import。 |
| AC-011 | TC-013 | negative | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc013_no_qa_or_release_verdict_in_loop_payloads --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 不输出 QA pass、release ready 或 feature complete verdict。 |
| AC-012 | TC-014 | docs | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc014_active_surfaces_do_not_recommend_lfg --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | active 面不出现 `lfg` route。 |
| AC-013 | TC-015 | test-suite | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc015_focused_pytest_and_npm_tests_exist --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | automation retirement + beacon-loop 测试存在。 |
| AC-014 | TC-016 | contract | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc016_runtime_process_record_not_machine_projection --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime process record；不写 `.machine` requirement projection。 |
| AC-015 | TC-017 | CLI | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc017_doctor_and_diagnose --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | doctor 检查 prerequisites；diagnose 输出分桶。 |
| AC-016 | TC-019 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc019_multi_iteration_orchestrator --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 产生 iteration-001..003 artifacts；最终 `cap_reached` 或 stop-when。 |
| AC-017 | TC-018 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc018_resume_continues_next_iteration --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 下一轮 iteration 编号为 N+1，同一 run-id。 |
| AC-018 | TC-021 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc021_graceful_and_force_stop --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | graceful 等当前轮结束；force 立即 `force_stopped`。 |
| AC-019 | TC-022 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc022_consecutive_failures_and_noop --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 连续失败 abort；hard error 退避；no-op 计 failure。 |
| AC-020 | TC-020 | runner | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc020_iteration_prompt_includes_notes --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 第 N 轮 prompt 含 notes 累积内容。 |
| AC-021 | TC-023 | CLI | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc023_review_summary_fields --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | summary 含 elapsed/branch/iterations/tokens/commands。 |
| AC-022 | TC-024 | ledger | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc024_runs_query --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 返回 ledger 中 run 列表。 |
| AC-022 | TC-025 | ledger | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc025_runs_show --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 返回单 run 详情与 artifact refs。 |
| AC-023 | TC-026 | ledger | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc026_runs_diagnose --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 分桶 blocked/dirty/missing-backend 等。 |
| AC-024 | TC-027 | runtime | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc027_runtime_tracking_cycle --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime 状态与 run-id 关联并可查询。 |
| AC-025 | TC-028 | harness | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc028_analyze_and_learn_advisory_only --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 站外 index 产物生成；不修改 feature package。 |
| AC-026 | TC-029 | git | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc029_branch_mode_matrix --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | worktree/current-branch 合法；非法组合 fail closed。 |
| AC-027 | TC-030 | config | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc030_config_defaults_with_cli_override --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | config 默认值生效；CLI flag 覆盖 config。 |
| AC-028 | TC-031 | integration | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc031_codex_multi_iteration --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 非单次 fixture 路径下完成 ≥2 轮。 |
| AC-029 | TC-032 | contract | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc032_claude_and_acp_adapters --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 两 adapter 输出 required schema。 |
| AC-030 | TC-033 | e2e | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc033_scripted_closed_loop --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | goal -> import-evidence -> beacon qa run 可驱动；verdict 来自 Beacon。 |
| AC-008/011 | TC-034 | state | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc034_state_machine_excludes_beacon_terminal_closure --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `implementation_candidate` 不得直接 `terminal_closed`；iterating 不得跳 qa_pending。 |
| AC-009/016 | TC-035 | state | `python3 -m pytest -q tests/test_v160_beacon_loop_automation_retirement.py::test_v160_tc035_repair_resume_path --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | repair_required -> resume -> iterating 合法。 |

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
