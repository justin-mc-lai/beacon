# 测试：Beacon Planner Review Runtime Multi-Agent v1.6.0

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `beacon validate-feature-package beacon-pln-review-runtime-multi-agent-v160 --project . --version v1.6.0 --json` | feature package 为 package-authoritative truth，且 truth 声明 `full_parity`。 |
| AC-002 | TC-002 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_runtime_artifact_contains_required_multi_agent_fields` | runtime artifact 包含 review id、execution mode、host runtime、fallback reason、selected reviewers、reviewer lanes、findings、synthesis 和 evidence paths。 |
| AC-003 | TC-003 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_always_on_reviewers_produce_lanes` | always-on reviewers 每次都生成独立 lane。 |
| AC-004 | TC-004 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_conditional_reviewers_are_selected_from_prompt_signals` | conditional reviewer 按 source、deferral、security、performance、design、brownfield、evidence、simplification、founder、doubt、ADR、context 信号选择。 |
| AC-005 | TC-005 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_each_lane_has_finding_or_no_findings_status` | 每个 lane 有独立 finding 或 `no_findings`，不得只有综合段落。 |
| AC-006 | TC-006 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_synthesis_merges_dedups_and_preserves_conflicts` | 合成器输出 `merged_from`、conflict group、最高 severity 和单一 recommended route。 |
| AC-007 | TC-007 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_fallback_transparency_blocks_fake_parallel_claims` | 无 subagent runtime 时输出 `single_process_multi_reviewer` 和 fallback reason，不声称 parallel subagent。 |
| AC-008 | TC-008 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_planner_boundary_flags_forbid_truth_code_machine_and_verdict_writes` | artifact 明确禁止 truth/code/.machine/QA/release 写入。 |
| AC-009 | TC-009 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_runtime_evidence_has_no_truth_or_verdict_authority` | runtime evidence 非 truth、非 formal QA verdict、非 release verdict。 |
| AC-010 | TC-010 | unit | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_review_state_machine_contract_is_materialized` | 状态机覆盖 request、context、selection、lane execution、synthesis、route、terminal 和 blocked transitions。 |
| AC-011 | TC-011 | contract | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_skill_reference_documents_multi_agent_runtime_contract` | `beacon-pln-review` references 说明 multi-agent model、fallback 和 planner-only 边界。 |
| AC-012 | TC-012 | behavior | `beacon skill eval-kit benchmark --version v1.6.0 --json` | benchmark 覆盖 multi-agent lane selection、independent findings、synthesis、fallback transparency 和 planner boundary。 |
| AC-013 | TC-013 | regression | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py tests/test_v160_skill_harness_taxonomy.py` | runtime artifact、benchmark grading、skill package projection 和既有 harness taxonomy 回归通过。 |
| AC-014 | TC-014 | integration | `beacon skill package verify --project-root . --version v1.6.0 --json` | 不新增 host-visible reviewer 子 skill，skill package 仍只有收敛后的 public planner surface。 |
| AC-015 | TC-015 | evidence | `python3 -m pytest -q tests/test_v160_pln_review_multi_agent.py::test_implementation_evidence_marker_is_imported_without_reopening` | implementation evidence marker 已存在且记录 changed files、测试命令、benchmark artifact 和 QA 后续路由；QA 只读验证，不重新执行 import 或 reopen implementation。 |

## 验证说明

Benchmark/runtime evidence 只支持 formal QA，不替代 `beacon-eval-qa` 或 release verdict。
