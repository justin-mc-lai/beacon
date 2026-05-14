#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
import time
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a Feishu post notification for Beacon automation jobs.")
    parser.add_argument("--webhook", required=True, help="Feishu bot webhook URL.")
    parser.add_argument("--secret", default="", help="Optional Feishu bot signing secret.")
    parser.add_argument("--title", required=True, help="Post title.")
    parser.add_argument("--summary-path", required=True, help="Path to a Beacon automation summary JSON file.")
    return parser.parse_args()


def load_summary(path: Path) -> dict:
    if not path.exists():
        return {
            "notification": {
                "title": "Beacon automation summary missing",
                "lines": [f"summary_path={path}", "summary_missing=true"],
            }
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def build_payload(*, title: str, summary: dict) -> dict:
    notification = summary.get("notification") if isinstance(summary.get("notification"), dict) else {}
    lines = notification.get("lines") if isinstance(notification.get("lines"), list) else []
    resolved_title = str(notification.get("title") or title).strip() or title
    reconciliation = summary.get("reconciliation") if isinstance(summary.get("reconciliation"), dict) else {}
    required_features = reconciliation.get("required_features") if isinstance(reconciliation.get("required_features"), list) else []
    reprojection_targets = reconciliation.get("reprojection_targets") if isinstance(reconciliation.get("reprojection_targets"), list) else []
    if required_features:
        lines = list(lines)
        lines.append("")
        lines.append("reconciliation_summary")
        lines.append(f"required_features={', '.join(str(item).strip() for item in required_features if str(item).strip())}")
        lines.append(f"reprojection_targets={', '.join(str(item).strip() for item in reprojection_targets if str(item).strip()) or '-'}")
    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": resolved_title,
                    "content": [[{"tag": "text", "text": line}] for line in lines],
                }
            }
        },
    }


def attach_signature(payload: dict, *, secret: str) -> None:
    if not secret:
        return
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    sign = base64.b64encode(
        hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    payload["timestamp"] = timestamp
    payload["sign"] = sign


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_path)
    summary = load_summary(summary_path)
    payload = build_payload(title=args.title, summary=summary)
    attach_signature(payload, secret=args.secret)
    request = urllib.request.Request(
        args.webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    result = json.loads(body) if body else {}
    status_code = result.get("StatusCode", result.get("code", 0))
    if status_code not in (0, "0", None):
        print(body, file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
