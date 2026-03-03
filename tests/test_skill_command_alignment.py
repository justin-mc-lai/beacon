from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from beacon.prefixed import SUPPORTED_SUBCOMMANDS


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"
START_MARKER = "<!-- AUTO-COMMANDS:START -->"
END_MARKER = "<!-- AUTO-COMMANDS:END -->"


def _auto_block(text: str) -> str:
    start = text.index(START_MARKER) + len(START_MARKER)
    end = text.index(END_MARKER)
    return text[start:end]


def test_skill_should_list_all_prefixed_commands_from_single_source():
    text = SKILL_PATH.read_text(encoding="utf-8")
    block = _auto_block(text)

    keyword_pairs = re.findall(r"\| `beacon-([^`]+)` \| `([^`]+)` \|", block)
    assert keyword_pairs
    assert [left for left, _ in keyword_pairs] == list(SUPPORTED_SUBCOMMANDS)
    assert [right for _, right in keyword_pairs] == list(SUPPORTED_SUBCOMMANDS)

    subcommand_pairs = re.findall(r"\| `([^`]+)` \| `beacon-([^`]+)` \|", block)
    assert subcommand_pairs
    assert [left for left, _ in subcommand_pairs] == list(SUPPORTED_SUBCOMMANDS)
    assert [right for _, right in subcommand_pairs] == list(SUPPORTED_SUBCOMMANDS)


def test_skill_should_keep_legacy_module_entrypoint_as_compatible_not_forbidden():
    text = SKILL_PATH.read_text(encoding="utf-8")
    assert "python3 -m beacon.think" in text
    assert "不要使用" not in text


def test_sync_script_check_should_pass():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_skill_commands.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
