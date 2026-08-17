#!/usr/bin/env python3
"""Map Beacon gate reason_code to immediate remediation actions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REASON_ACTIONS = {
    "qa9_matrix_missing": "先运行: beacon test-case create \"<feature>\" --version v1.0.2",
    "qa9_matrix_schema_invalid": "修复 *.qa9-matrix.json schema（qa_types/qa_requirements/entries）",
    "qa9_required_type_missing": "补齐 --require-qa-types 指定的 QA 类型",
    "qa9_command_missing_auto_case": "为 automation=auto/hybrid 的 TC 补 command",
    "qa9_ac_traceability_broken": "为每个 TC 补 ac_id 并保证 AC->TC 映射",
    "qa9_automation_rate_below_target": "提高 auto 用例覆盖或下调阈值并评审",
    "qa_llm_plan_missing": "补 llm_plan 节点（mode/model/project_scan）",
    "qa_llm_project_scan_missing": "补 llm_plan.project_scan（language/framework/frontend/risk）",
    "assertion_count_zero_pass": "确保测试报告包含断言计数并 > 0",
    "junit_missing_or_invalid": "为通过层输出有效 junit.xml（testsuite/testsuites）",
    "evidence_replay_detected": "启用 --require-fresh-evidence 并确保 evidence_path 含 run_id",
    "execution_fingerprint_missing": "通过层补 execution_fingerprint",
    "execution_fingerprint_mismatch": "清理复用证据，重跑生成唯一指纹",
    "report_result_mismatch": "对齐 auto-test 汇总状态与层状态",
    "compatibility_axis_incomplete": "补 compatibility_matrix 的 browsers/devices/required_pairs",
    "compatibility_execution_missing": "执行 compatibility 层并回填 required_pairs evidence",
    "contract_spec_missing": "补 contract 条目并关联 openapi/pact 规范",
    "contract_verification_missing": "执行并通过 contract 层",
    "integration_env_missing": "补集成环境前置（依赖服务/数据/凭据）",
    "integration_execution_missing": "执行 integration 层并产出证据",
    "test_execution_missing": "先运行: beacon auto-test create qa9 ...",
    "manual_waiver_unapproved": "补 waiver 审批人与有效期（expires_at 未过期）",
}


def _load_payload(path: str) -> dict:
    if path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    start = raw.find("{")
    if start < 0:
        raise ValueError("未找到 JSON 对象")
    payload = json.loads(raw[start:])
    if not isinstance(payload, dict):
        raise ValueError("JSON 顶层必须是对象")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "gate_json",
        nargs="?",
        default="-",
        help="Gate JSON 文件路径，默认从 stdin 读取（传 '-'）。",
    )
    args = parser.parse_args()

    payload = _load_payload(args.gate_json)
    issues = payload.get("issues")
    if not isinstance(issues, list) or not issues:
        print("✅ 未发现 issues")
        return 0

    print("# reason_code 修复建议")
    seen: set[str] = set()
    for item in issues:
        if not isinstance(item, dict):
            continue
        reason = str(item.get("reason_code") or "").strip()
        if not reason or reason in seen:
            continue
        seen.add(reason)
        action = REASON_ACTIONS.get(reason, "参考 docs/beacon/v1.0.2/execution/v1.0.2-reason-code-action-cheatsheet.md")
        print(f"- {reason}: {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

