#!/usr/bin/env python3
"""Generate a lightweight QA9 operations dashboard from local Beacon artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def _safe_load(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Project root path")
    parser.add_argument("--output", default=".beacon/qa9-dashboard.md", help="Markdown output path")
    parser.add_argument("--json-output", default=".beacon/qa9-dashboard.json", help="JSON output path")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    auto_status = _safe_load(root / ".beacon" / "auto-test-status.json") or {}
    gate_report = _safe_load(root / ".beacon" / "gate-report.json") or {}
    flaky_history = _safe_load(root / ".beacon" / "flaky-history.json") or []
    if not isinstance(flaky_history, list):
        flaky_history = []

    qa9_summary = {}
    qa9 = auto_status.get("qa9")
    if isinstance(qa9, dict) and isinstance(qa9.get("summary"), dict):
        qa9_summary = qa9.get("summary", {})

    issues = gate_report.get("issues")
    if not isinstance(issues, list):
        issues = []
    reason_counter = Counter(str(item.get("reason_code") or "").strip() for item in issues if isinstance(item, dict))
    reason_counter.pop("", None)

    latest_flaky = flaky_history[-20:]
    flaky_rate_avg = 0.0
    if latest_flaky:
        rates = []
        for item in latest_flaky:
            if not isinstance(item, dict):
                continue
            flaky = item.get("flaky")
            if isinstance(flaky, dict):
                rates.append(float(flaky.get("flaky_rate", 0.0) or 0.0))
        if rates:
            flaky_rate_avg = sum(rates) / len(rates)

    dashboard_json = {
        "generated_at": datetime.now().isoformat(),
        "qa9_summary": qa9_summary,
        "gate_status": gate_report.get("status", "Unknown"),
        "blocked_count": gate_report.get("blocked_count", 0),
        "top_reason_codes": reason_counter.most_common(10),
        "flaky_rate_avg_last_20": round(flaky_rate_avg, 4),
        "runs_analyzed": len(latest_flaky),
    }

    markdown_lines = [
        "# QA9 Dashboard",
        "",
        f"- 生成时间: {dashboard_json['generated_at']}",
        f"- Gate 状态: {dashboard_json['gate_status']}",
        f"- Blocked 数: {dashboard_json['blocked_count']}",
        f"- 最近 20 次平均 Flaky: {dashboard_json['flaky_rate_avg_last_20']}",
        "",
        "## QA9 汇总",
        "",
        f"- 总用例: {qa9_summary.get('cases_total', 0)}",
        f"- 通过: {qa9_summary.get('passed', 0)}",
        f"- 失败: {qa9_summary.get('failed', 0)}",
        f"- 阻断: {qa9_summary.get('blocked', 0)}",
        f"- 自动化覆盖率: {qa9_summary.get('automation_rate', 0)}",
        "",
        "## Top Reason Codes",
        "",
    ]
    if reason_counter:
        for code, count in reason_counter.most_common(10):
            markdown_lines.append(f"- {code}: {count}")
    else:
        markdown_lines.append("- 无")

    output_md = root / args.output
    output_json = root / args.json_output
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps(dashboard_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ QA9 dashboard generated: {output_md}")
    print(f"✓ QA9 dashboard json: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

