# Test Cases: beacon-agent-eval-v161

## Overview

**Feature**: beacon-agent-eval-v161
**Test Type**: ALL
**Version**: v1.6.1
**Generated**: 2026-06-15 19:22
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-agent-eval-v161.ac-test-matrix.json
**QA9 Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-agent-eval-v161.qa9-matrix.json
**Story Scenario Map JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-agent-eval-v161.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-AE-001 | TC-AE-001 | contract | `mkdir -p .beacon/qa-tmp && beacon eval --help >.beacon/qa-tmp/TC-AE-001.txt 2>&1 && rg -q 'catalog' .beacon/qa-tmp/TC-AE-001.txt && rg -q 'scorecard' .beacon/qa-tmp/TC-AE-001.txt && python3 -m pytest tests/test_v161_agent_eval.py::test_agent_eval_help_lists_subcommands -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | exit 0 或 BLOCKED:Phase-A | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-001.json` |
| AC-AE-002 | TC-AE-002 | contract | `mkdir -p .beacon/qa-tmp && beacon eval catalog --project-root . --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-002.json 2>&1 && test -f docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json` | catalog JSON 存在 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-002.json` |
| AC-AE-003 | TC-AE-003 | contract | `python3 -c "import json; c=json.load(open('docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json')); h=set(x.get('harness') for x in c.get('entries',[])); assert {'pln','gen','eval','gov'}.issubset(h)"` | 四类 harness 在 catalog | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-003.json` |
| AC-AE-004 | TC-AE-004 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval run --project-root . --split regression-core --runner replay --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-004.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-004.json')); assert d.get('traces_path') or d.get('status')=='blocked'" && python3 -m pytest tests/test_v161_agent_eval.py::test_agent_eval_catalog_materialize -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | traces 或明确 blocked | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-004.json` |
| AC-AE-005 | TC-AE-005 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval scorecard --project-root . --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-005.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-005.json')); dims=d.get('dimensions',{}); assert len(dims)>=6 and 'composite_score' in d"` | 六维 + composite | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-005.json` |
| AC-AE-006 | TC-AE-006 | contract | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval scorecard --project-root . --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-006.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-006.json')); a=d.get('authority',d); assert d.get('runtime_evidence_only') is True and d.get('formal_verdict_authority') is False"` | authority 字段正确 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-006.json` |
| AC-AE-007 | TC-AE-007 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval scorecard --project-root . --version v1.6.1 --runner simulated --json >.beacon/qa-tmp/TC-AE-007.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-007.json')); assert d.get('degraded') is True and 'simulated_composite_score' in d"` | simulated 降级标记 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-007.json` |
| AC-AE-008 | TC-AE-008 | negative | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval run --project-root . --runner live --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-008.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-008.json')); assert d.get('status')=='blocked' and d.get('reason_code')=='agent_eval_live_runner_not_admitted'"` | 无 admission 时 blocked | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-008.json` |
| AC-AE-009 | TC-AE-009 | integration | `test -f docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-runner-admission.json && mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval run --project-root . --runner live --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-009.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-009.json')); assert d.get('status') in ('pass','running','completed')"` | admission 存在时可启动 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-009.json` |
| AC-AE-010 | TC-AE-010 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval benchmark --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-010.json 2>&1 && python3 -c "import json,glob; d=json.load(open('.beacon/qa-tmp/TC-AE-010.json')); root=d.get('root',''); assert all(glob.glob(root+'/**/'+x, recursive=True) or x in str(d) for x in ['eval_metadata','grading','benchmark','analysis'])"` | 四类 artifact 目录 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-010.json` |
| AC-AE-011 | TC-AE-011 | contract | `python3 -c "import json,glob; import pathlib; b=pathlib.Path('.beacon/state/agent-eval/benchmarks'); bs=sorted(b.glob('*'))[-1] if b.exists() else None; g=list(bs.glob('grading/*.json')) if bs else []; assert len(g)>=2"` | grading 含多配置 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-011.json` |
| AC-AE-012 | TC-AE-012 | contract | `python3 -c "import json,pathlib; b=pathlib.Path('.beacon/state/agent-eval/benchmarks'); bs=sorted(b.glob('*'))[-1] if b.exists() else None; found=any('critique' in str(v) for p in (bs.glob('grading/*.json') if bs else []) for v in json.load(open(p)).values()); assert found"` | grading 含 critique | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-012.json` |
| AC-AE-013 | TC-AE-013 | contract | ``test -f .beacon/state/agent-eval/benchmarks/*/analysis/analysis.md` | Provider/consumer contract assertions pass | `rg -q 'formal.*QA' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md`` |
| AC-AE-014 | TC-AE-014 | contract | `rg -q 'TC-006' beacon/utils/skill_eval_kit.py && rg -q 'TC-017' beacon/utils/skill_eval_kit.py && rg -q 'v1.6.1' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md` | v1.6.1 继承 v1.6.0 行为轴 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-014.json` |
| AC-AE-015 | TC-AE-015 | contract | ``rg -q 'hard-gate' .beacon/state/skill-eval/cases.json 2>/dev/null` | Provider/consumer contract assertions pass | `rg -q 'boundary' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md`` |
| AC-AE-016 | TC-AE-016 | contract | `test -f skills/beacon/beacon-eval-agent/SKILL.md && rg -q 'HARD GATE' skills/beacon/beacon-eval-agent/SKILL.md && rg -q 'release verdict' skills/beacon/beacon-eval-agent/SKILL.md` | eval-agent skill + gate | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-016.json` |
| AC-AE-017 | TC-AE-017 | unit | `rg -q 'AgentEvalState' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && python3 -m pytest tests/test_agent_eval_state_contract.py -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | FSM 单测 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-017.json` |
| AC-AE-018 | TC-AE-018 | unit | `python3 -m pytest tests/test_agent_eval_state_contract.py -q -k recovery --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | recovery 路径单测 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-018.json` |
| AC-AE-019 | TC-AE-019 | contract | `python3 -c "import json; c=json.load(open('docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json')); ids=[x.get('id','') for x in c.get('entries',[])]; assert any('plan start' in i or 'plan.start' in i for i in ids)"` | catalog 含 plan start | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-019.json` |
| AC-AE-020 | TC-AE-020 | contract | `rg -q 'trace-scorecard' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q 'acceptance-kit' beacon/utils/acceptance_kit.py` | acceptance kit 桥接声明 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-020.json` |
| AC-AE-021 | TC-AE-021 | contract | `rg -q 'anti-fake-delivery' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q 'fake_delivery' beacon/utils/skill_eval_kit.py` | anti-fake-delivery | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-021.json` |
| AC-AE-022 | TC-AE-022 | contract | `rg -q 'Agent Eval' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q '验收标准' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md` | 中文 truth | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-022.json` |
| AC-AE-023 | TC-AE-023 | contract | `rg -q 'beacon-agent-eval-v161' docs/beacon/archive/v1.6.1/SUMMARY.md` | SUMMARY 索引 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-023.json` |
| AC-AE-024 | TC-AE-024 | contract | `rg -q 'skill.eval' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q 'skill_eval' beacon/utils/skill_eval_kit.py` | skill eval kit 桥接 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-024.json` |
| AC-AE-025 | TC-AE-025 | contract | `python3 -c "import json; c=json.load(open('docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json')); ids=' '.join(x.get('id','') for x in c.get('entries',[])); assert 'verify-agent-surface' in ids"` | doctor surface 在 catalog | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-025.json` |
| AC-AE-026 | TC-AE-026 | contract | `rg -q 'route_stability' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q '15%' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md` | 权重在 truth | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-026.json` |
| AC-AE-027 | TC-AE-027 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval run --split regression-core --runner replay --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-027-run.json 2>&1 && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval scorecard --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-027-sc.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-027-sc.json')); assert d.get('composite_score',0)>=70 or d.get('status')=='blocked'"` | regression pass 时 composite≥70 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-027.json` |
| AC-AE-028 | TC-AE-028 | contract | `rg -q 'full_parity' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md && rg -q 'Deferral Ledger' docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md` | scope_mode + deferral 表 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-028.json` |
| AC-AE-029 | TC-AE-029 | contract | `rg -q '## user_decision' docs/beacon/archive/v1.6.1/research/beacon-agent-eval-v161.md && rg -q '^promoted$' docs/beacon/archive/v1.6.1/research/beacon-agent-eval-v161.md && rg -q 'promotion_ref' docs/beacon/archive/v1.6.1/research/beacon-agent-eval-v161.md` | exit 0 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-029.json` |
| AC-AE-030 | TC-AE-030 | contract | ``python3 -c "import json; from beacon.utils.agent_surface import v160_skill_package_projection; m=json.load(open('docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-live-skill-matrix-v161.json')); ids={x['skill_id'] for x in m.get('entries',[])}; exp={p.id for p in v160_skill_package_projection()}` | {'beacon-eval-agent'}; assert ids==exp"` | `matrix 37 条与 projection 一致` |
| AC-AE-031 | TC-AE-031 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval run --project-root . --split regression-core --runner live --version v1.6.1 --json >.beacon/qa-tmp/TC-AE-031.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-031.json')); per=d.get('per_skill',[]); assert len(per)>=37"` | 每条 skill 有 trace 或 blocked | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-031.json` |
| AC-AE-032 | TC-AE-032 | integration | `mkdir -p .beacon/qa-tmp && BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 beacon eval scorecard --project-root . --version v1.6.1 --runner live --json >.beacon/qa-tmp/TC-AE-032.json 2>&1 && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-AE-032.json')); t=d.get('live_skill_total',0); assert t>=37; p=d.get('live_skill_pass',0); assert p==t or d.get('live_coverage_blocked') is True"` | 100% live pass 或全量 blocked 报告 | `.beacon/evidence/test-results/beacon-agent-eval-v161/{run_id}/TC-AE-032.json` |
| AC-AE-033 | TC-AE-033 | contract | ``python3 -c "import re; t=open('docs/beacon/archive/v1.6.1/features/beacon-agent-eval-v161/truth.md').read(); pb=re.search(r'## Phased Backlog.*?(?=\\n## )', t, re.S); section=pb.group(0) if pb else ''; assert '全 skill live' in t and 'change_reason' in t and '` | PB-AE-001 | `' not in section"`` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-AE-001 | Pending | from AC-AE-001 |
| TC-AE-002 | Pending | from AC-AE-002 |
| TC-AE-003 | Pending | from AC-AE-003 |
| TC-AE-004 | Pending | from AC-AE-004 |
| TC-AE-005 | Pending | from AC-AE-005 |
| TC-AE-006 | Pending | from AC-AE-006 |
| TC-AE-007 | Pending | from AC-AE-007 |
| TC-AE-008 | Pending | from AC-AE-008 |
| TC-AE-009 | Pending | from AC-AE-009 |
| TC-AE-010 | Pending | from AC-AE-010 |
| TC-AE-011 | Pending | from AC-AE-011 |
| TC-AE-012 | Pending | from AC-AE-012 |
| TC-AE-013 | Pending | from AC-AE-013 |
| TC-AE-014 | Pending | from AC-AE-014 |
| TC-AE-015 | Pending | from AC-AE-015 |
| TC-AE-016 | Pending | from AC-AE-016 |
| TC-AE-017 | Pending | from AC-AE-017 |
| TC-AE-018 | Pending | from AC-AE-018 |
| TC-AE-019 | Pending | from AC-AE-019 |
| TC-AE-020 | Pending | from AC-AE-020 |
| TC-AE-021 | Pending | from AC-AE-021 |
| TC-AE-022 | Pending | from AC-AE-022 |
| TC-AE-023 | Pending | from AC-AE-023 |
| TC-AE-024 | Pending | from AC-AE-024 |
| TC-AE-025 | Pending | from AC-AE-025 |
| TC-AE-026 | Pending | from AC-AE-026 |
| TC-AE-027 | Pending | from AC-AE-027 |
| TC-AE-028 | Pending | from AC-AE-028 |
| TC-AE-029 | Pending | from AC-AE-029 |
| TC-AE-030 | Pending | from AC-AE-030 |
| TC-AE-031 | Pending | from AC-AE-031 |
| TC-AE-032 | Pending | from AC-AE-032 |
| TC-AE-033 | Pending | from AC-AE-033 |
