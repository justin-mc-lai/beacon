# Test Cases: beacon-harness-program-plan-v161

## Overview

**Feature**: beacon-harness-program-plan-v161
**Test Type**: ALL
**Version**: v1.6.1
**Generated**: 2026-06-15 16:16
**Requested Mode**: auto
**Effective Mode**: markdown
**Fallback Reason**: N/A
**Memory Context**: N/A
**AC Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.ac-test-matrix.json
**QA9 Matrix JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.qa9-matrix.json
**Story Scenario Map JSON**: /Users/apple/Developer/Personal/products/beacon/docs/beacon/archive/v1.6.1/.machine/qa/beacon-harness-program-plan-v161.story-scenario-map.json
**Prototype Plan Present**: False
**Prototype Coverage Present**: False
**Prototype Navigation Contract**: False
**Prototype Interaction Contract**: False

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-PBP-001 | TC-PBP-001 | contract | `test -f docs/beacon/archive/v1.6.1/execution/program-plan-contract.md && rg -q 'feature-graph.json' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | exit 0；contract 定义 program 目录与 P0–P6 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-001.json` |
| AC-PBP-002 | TC-PBP-002 | contract | `rg -q 'beacon-harness-program-plan-v161' docs/beacon/archive/v1.6.1/SUMMARY.md` | exit 0；SUMMARY 声明 primary feature | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-002.json` |
| AC-PBP-003 | TC-PBP-003 | contract | `rg -q '## user_decision' docs/beacon/archive/v1.6.1/research/beacon-harness-program-plan-v161.md && rg -q '^promoted$' docs/beacon/archive/v1.6.1/research/beacon-harness-program-plan-v161.md && rg -q 'promotion_ref' docs/beacon/archive/v1.6.1/research/beacon-harness-program-plan-v161.md` | exit 0 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-003.json` |
| AC-PBP-004 | TC-PBP-004 | contract | `mkdir -p .beacon/qa-tmp && beacon program validate-graph --help >.beacon/qa-tmp/TC-PBP-004.txt 2>&1 && rg -q 'validate-graph' .beacon/qa-tmp/TC-PBP-004.txt` | exit 0 或 BLOCKED:Phase-B（CLI 未实现） | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-004.json` |
| AC-PBP-005 | TC-PBP-005 | contract | `mkdir -p .beacon/qa-tmp && beacon program guard-sea-single-lake --help >.beacon/qa-tmp/TC-PBP-005.txt 2>&1 && rg -q 'guard-sea' .beacon/qa-tmp/TC-PBP-005.txt` | exit 0 或 BLOCKED:Phase-B | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-005.json` |
| AC-PBP-006 | TC-PBP-006 | contract | `test -f docs/beacon/archive/v1.6.1/execution/program-plan-contract.md && rg -q 'truth-promotion' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | exit 0；contract 要求 per-lake 七轮证据 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-006.json` |
| AC-PBP-007 | TC-PBP-007 | contract | `mkdir -p .beacon/qa-tmp && beacon program freeze --help >.beacon/qa-tmp/TC-PBP-007.txt 2>&1 && rg -q 'program' .beacon/qa-tmp/TC-PBP-007.txt` | exit 0 或 BLOCKED:Phase-C | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-007.json` |
| AC-PBP-008 | TC-PBP-008 | unit | `mkdir -p .beacon/qa-tmp && beacon doctor verify-truth-integrity beacon-harness-program-plan-v161 --project-root . --version v1.6.1 --mode block --json >.beacon/qa-tmp/TC-PBP-008.json && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-PBP-008.json')); raise SystemExit(0 if d.get('result',{}).get('blocked') is False else 1)"` | exit 0 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-008.json` |
| AC-PBP-009 | TC-PBP-009 | contract | `mkdir -p .beacon/qa-tmp && beacon skill package verify-closure --feature beacon-harness-program-plan-v161 --project-root . --version v1.6.1 --json >.beacon/qa-tmp/TC-PBP-009.json && python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-PBP-009.json')); raise SystemExit(0 if d.get('closure_allowed') else 1)"` | closure_allowed=true | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-009.json` |
| AC-PBP-010 | TC-PBP-010 | contract | `rg -q 'must not write.*features/\*/truth' docs/beacon/archive/v1.6.1/execution/boundaries.md && rg -q 'HARD GATE' .cursor/skills/beacon-pln-brainstorm/SKILL.md` | planner 边界文档与 skill gate 存在 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-010.json` |
| AC-PBP-011 | TC-PBP-011 | contract | `rg -q 'full_parity' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | truth 声明 full_parity 默认 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-011.json` |
| AC-PBP-012 | TC-PBP-012 | contract | `rg -q 'program-parity-matrix' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | parity matrix 在 contract 中 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-012.json` |
| AC-PBP-013 | TC-PBP-013 | contract | `mkdir -p .beacon/qa-tmp && beacon change --help >.beacon/qa-tmp/TC-PBP-013.txt 2>&1 && rg -q 'change' .beacon/qa-tmp/TC-PBP-013.txt` | exit 0 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-013.json` |
| AC-PBP-014 | TC-PBP-014 | contract | `rg -q 'promotion_diff' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | change 路径要求 promotion_diff | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-014.json` |
| AC-PBP-015 | TC-PBP-015 | contract | `mkdir -p .beacon/qa-tmp && beacon change --help >.beacon/qa-tmp/TC-PBP-015.txt 2>&1 && rg -q 'refreeze-chain' .beacon/qa-tmp/TC-PBP-015.txt` | exit 0；change 暴露受治理 refreeze-chain | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-015.json` |
| AC-PBP-016 | TC-PBP-016 | contract | `mkdir -p .beacon/qa-tmp && node packages/beacon-run/dist/cli.mjs run --help >.beacon/qa-tmp/TC-PBP-016.txt 2>/dev/null && rg -i 'mode' .beacon/qa-tmp/TC-PBP-016.txt` | exit 0；help 暴露 mode（Phase E 补 program preset） | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-016.json` |
| AC-PBP-017 | TC-PBP-017 | contract | `test -f skills/beacon/beacon-pln-program/SKILL.md && rg -q 'beacon-pln-program' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | umbrella skill 存在且 truth 引用 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-017.json` |
| AC-PBP-018 | TC-PBP-018 | contract | `rg -q 'machine-readable' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | AC-PBP-018 maker-checker 写入 truth | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-018.json` |
| AC-PBP-019 | TC-PBP-019 | contract | `rg -q 'deferral-sovereignty' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md && rg -q 'accepted' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | exit 0；deferral 表均为 accepted | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-019.json` |
| AC-PBP-020 | TC-PBP-020 | contract | `rg 'plan -> truth -> generate -> evaluate -> release' docs/beacon/archive/v1.6.1/SUMMARY.md docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | 未新增主 lifecycle stage | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-020.json` |
| AC-PBP-021 | TC-PBP-021 | contract | `rg -q 'ProgramPlanState' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | State Model 在 truth | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-021.json` |
| AC-PBP-022 | TC-PBP-022 | unit | `python3 -m pytest tests/test_program_plan_state_contract.py tests/test_program_plan_cli.py -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | pytest 覆盖非法转移与 program CLI | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-022.json` |
| AC-PBP-023 | TC-PBP-023 | contract | `test -f skills/beacon/beacon-pln-program/SKILL.md && test -f skills/beacon/beacon-pln-program-auto/SKILL.md && test -f skills/beacon/beacon-pln-program-interactive/SKILL.md && rg -q 'HARD GATE' skills/beacon/beacon-pln-program/SKILL.md && rg -q 'delegation' skills/beacon/beacon-pln-program-auto/SKILL.md` | 三 skill 存在且 auto 声明委派 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-023.json` |
| AC-PBP-024 | TC-PBP-024 | contract | `mkdir -p .beacon/qa-tmp && beacon plan start --help >.beacon/qa-tmp/TC-PBP-024.txt 2>&1 && rg -q 'mode' .beacon/qa-tmp/TC-PBP-024.txt` | exit 0 或 BLOCKED:Phase-E | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-024.json` |
| AC-PBP-025 | TC-PBP-025 | contract | `rg -q 'plan_mode' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md && rg -q 'auto-detect' docs/beacon/archive/v1.6.1/execution/program-plan-contract.md` | contract 含分类规则 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-025.json` |
| AC-PBP-026 | TC-PBP-026 | contract | `rg -q 'Delegate' skills/beacon/beacon-pln-program/SKILL.md && rg -q 'Does not write features' skills/beacon/beacon-pln-program-auto/SKILL.md` | umbrella 委派 + 子 skill 边界 | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-026.json` |
| AC-PBP-027 | TC-PBP-027 | contract | `rg -q 'beacon plan start' docs/beacon/archive/v1.6.1/features/beacon-harness-program-plan-v161/truth.md` | 单一公共入口写入 truth | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-027.json` |
| AC-PBP-028 | TC-PBP-028 | contract | `rg -q 'beacon-pln-brainstorm' skills/beacon/beacon-pln-program-interactive/SKILL.md && rg -q 'beacon-pln-source' skills/beacon/beacon-pln-program-auto/SKILL.md` | interactive/auto 桥接既有 planner skill | `.beacon/evidence/test-results/beacon-harness-program-plan-v161/{run_id}/TC-PBP-028.json` |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-PBP-001 | Pending | from AC-PBP-001 |
| TC-PBP-002 | Pending | from AC-PBP-002 |
| TC-PBP-003 | Pending | from AC-PBP-003 |
| TC-PBP-004 | Pending | from AC-PBP-004 |
| TC-PBP-005 | Pending | from AC-PBP-005 |
| TC-PBP-006 | Pending | from AC-PBP-006 |
| TC-PBP-007 | Pending | from AC-PBP-007 |
| TC-PBP-008 | Pending | from AC-PBP-008 |
| TC-PBP-009 | Pending | from AC-PBP-009 |
| TC-PBP-010 | Pending | from AC-PBP-010 |
| TC-PBP-011 | Pending | from AC-PBP-011 |
| TC-PBP-012 | Pending | from AC-PBP-012 |
| TC-PBP-013 | Pending | from AC-PBP-013 |
| TC-PBP-014 | Pending | from AC-PBP-014 |
| TC-PBP-015 | Pending | from AC-PBP-015 |
| TC-PBP-016 | Pending | from AC-PBP-016 |
| TC-PBP-017 | Pending | from AC-PBP-017 |
| TC-PBP-018 | Pending | from AC-PBP-018 |
| TC-PBP-019 | Pending | from AC-PBP-019 |
| TC-PBP-020 | Pending | from AC-PBP-020 |
| TC-PBP-021 | Pending | from AC-PBP-021 |
| TC-PBP-022 | Pending | from AC-PBP-022 |
| TC-PBP-023 | Pending | from AC-PBP-023 |
| TC-PBP-024 | Pending | from AC-PBP-024 |
| TC-PBP-025 | Pending | from AC-PBP-025 |
| TC-PBP-026 | Pending | from AC-PBP-026 |
| TC-PBP-027 | Pending | from AC-PBP-027 |
| TC-PBP-028 | Pending | from AC-PBP-028 |
