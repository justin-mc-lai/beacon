#!/usr/bin/env python3
"""Sync SKILL.md command tables from beacon.prefixed.SUPPORTED_SUBCOMMANDS."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from beacon.prefixed import SUPPORTED_SUBCOMMANDS  # noqa: E402

START_MARKER = "<!-- AUTO-COMMANDS:START -->"
END_MARKER = "<!-- AUTO-COMMANDS:END -->"


def _build_table_block() -> str:
    lines: list[str] = [
        "### 可触发关键词（自动同步）",
        "",
        "| 关键词 | 对应子命令 |",
        "|--------|------------|",
    ]
    for command in SUPPORTED_SUBCOMMANDS:
        lines.append(f"| `beacon-{command}` | `{command}` |")
    lines.extend(
        [
            "",
            "### 完整子命令清单（自动同步）",
            "",
            "| 子命令 | 推荐触发 |",
            "|-------|----------|",
        ]
    )
    for command in SUPPORTED_SUBCOMMANDS:
        lines.append(f"| `{command}` | `beacon-{command}` |")
    return "\n".join(lines).rstrip()


def _sync_skill_text(text: str) -> str:
    if START_MARKER not in text or END_MARKER not in text:
        raise RuntimeError("AUTO-COMMANDS markers not found in SKILL.md")
    start_index = text.index(START_MARKER)
    end_index = text.index(END_MARKER) + len(END_MARKER)
    replacement = f"{START_MARKER}\n{_build_table_block()}\n{END_MARKER}"
    return text[:start_index] + replacement + text[end_index:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-file",
        default=str(ROOT / "SKILL.md"),
        help="Path to SKILL.md",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check whether SKILL.md is in sync",
    )
    args = parser.parse_args()

    skill_path = Path(args.skill_file)
    if not skill_path.exists():
        raise SystemExit(f"SKILL file not found: {skill_path}")

    current = skill_path.read_text(encoding="utf-8")
    updated = _sync_skill_text(current)
    if args.check:
        if updated != current:
            print("SKILL.md is out of sync. Run: python3 scripts/sync_skill_commands.py")
            return 1
        print("SKILL.md command tables are in sync.")
        return 0

    if updated != current:
        skill_path.write_text(updated, encoding="utf-8")
        print(f"Updated: {skill_path}")
    else:
        print("No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
