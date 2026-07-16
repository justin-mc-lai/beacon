# 测试：Beacon Planner Review Compound Parity v1.6.0

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `beacon validate-feature-package beacon-pln-review-compound-parity-v160 --project . --version v1.6.0 --json` | feature package 为 package-authoritative truth，frontmatter 状态为 frozen，并声明 `full_parity`。 |
| AC-002 | TC-002 | contract | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_compound_review_contract_reference_exists --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `beacon-pln-review` references 包含 Compound parity output contract 字段。 |
| AC-003 | TC-003 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_reviewer_catalog_covers_compound_and_beacon_reviewers --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | always-on 和 conditional reviewer catalog 覆盖 correctness、testing、maintainability、standards、intent、route、source parity、diff scope、security、performance、API、reliability、browser ops、release ops、adversarial 和 state machine。 |
| AC-004 | TC-004 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_full_parity_prompt_requires_source_inventory_and_parity_matrix --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 完整复刻、同等能力、做全、不要 MVP 或 source refs 触发 `full_parity`、source capability inventory、parity matrix、coverage mapping 和 deferral ledger。 |
| AC-005 | TC-005 | negative | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_unapproved_mvp_downgrade_is_blocked --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | full parity 被降级为 MVP/patch/defer 且无 user decision 时，产生 P0/P1 finding 并阻断 implement/freeze route。 |
| AC-006 | TC-006 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_finding_schema_contains_synthesis_and_routing_fields --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | findings 包含 severity、confidence、authority、dedup、merged_from、conflict_group、owner、autofix_class、requires_verification 和 recommended_route。 |
| AC-007 | TC-007 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_synthesis_dedups_conflicts_and_selects_conservative_route --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | synthesis 合并重复 finding，保留冲突，提升最高 severity，并输出单一 recommended route。 |
| AC-008 | TC-008 | negative | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_planner_autofix_classification_does_not_execute_repairs --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | planner 只分类 `safe_auto/gated_auto/manual/advisory/release`，不改 truth 或代码；safe_auto 路由到 generator。 |
| AC-009 | TC-009 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_diff_scope_review_records_worktree_surfaces --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | diff scope 包含 base、changed、untracked、generated/projection、deleted、high-risk files 和 scope confidence；scope 不明时 degraded。 |
| AC-010 | TC-010 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_release_ops_review_routes_install_and_projection_gaps --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | release ops review 检查 global/local skill、stale copies、post-release hooks、canary/smoke install、rollback 和 version alignment。 |
| AC-011 | TC-011 | unit | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_qa_evidence_hygiene_flags_junit_assertion_and_placeholder_gaps --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | QA evidence hygiene 对 JUnit、assertion_count、fake runner、placeholder evidence、browser admission、compatibility pair evidence 和 benchmark metadata/grading/analysis 产生 finding。 |
| AC-012 | TC-012 | contract | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_compound_parity_state_machine_contract_is_materialized --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 状态机覆盖 scope、source parity、reviewer selection、lane execution、finding synthesis、route recommendation、blocked transitions 和 terminal states。 |
| AC-013 | TC-013 | negative | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py::test_planner_review_artifact_has_no_truth_or_verdict_authority --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | review artifact 标记非 truth、非 QA verdict、非 release verdict，并禁止 planner 写 truth、代码、`.machine` 或执行修复。 |
| AC-014 | TC-014 | behavior | `beacon skill eval-kit benchmark --version v1.6.0 --json` | benchmark 覆盖 Compound parity、source parity、防 MVP 缩水、finding synthesis、autofix boundary、diff scope、release ops 和 QA evidence hygiene。 |
| AC-015 | TC-015 | regression | `python3 -m pytest -q tests/test_v160_pln_review_compound_parity.py tests/test_v160_pln_review_multi_agent.py tests/test_v160_skill_harness_taxonomy.py --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | review contract references、artifact schema、synthesis rules、benchmark grading、multi-agent runtime 和 skill projection 回归通过。 |
| AC-016 | TC-016 | integration | `beacon skill package verify --project-root . --version v1.6.0 --json` | 不新增 host-visible reviewer 子 skill；新增能力作为 `beacon-pln-review` internal reviewer/reference/runtime contract 投影。 |

## 验证说明

本测试包定义 acceptance coverage。Benchmark 和 planner runtime artifact 只能支持 formal QA，不能替代 `beacon-eval-qa` 或 release verdict。

