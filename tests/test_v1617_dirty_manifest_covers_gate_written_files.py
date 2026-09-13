"""Regression for issue #29: the clean-exit gate blocked on Beacon's own output.

`verify_clean_workspace()` classifies every dirty path through ``DIRTY_MANIFEST``
and fails with ``workspace_dirty_unclassified`` when nothing matches it. Paths
that `beacon qa run` / `beacon change` rewrite on every run had no role, so a
feature could not exit cleanly *because* the gate had just produced its verdict
files -- 11 such paths showed up in a real project whose QA run had otherwise
passed 44/44 with empty ``reason_codes``.

Classification follows what the operator should actually do: commit a tracked
verdict, ignore rolling local state. The rolling half is pinned against
``gitignore_policy`` so the two lists cannot drift apart silently again.
"""

from __future__ import annotations

from beacon.utils.gitignore_policy import STANDARD_BEACON_GITIGNORE_LINES
from beacon.utils.workspace_clean import (
    DIRTY_MANIFEST,
    GATE_FORMAL_PATTERNS,
    GATE_ROLLING_PATTERNS,
    artifact_role_for_path,
)

GATE_WRITTEN = [
    ".beacon/flaky-history.json",
    ".beacon/raw-command-log.jsonl",
    ".beacon/qa/features/workbench-desktop-shell/status.json",
    ".beacon/qa/features/workbench-desktop-shell/scorecard.json",
    ".beacon/qa/features/workbench-desktop-shell/matrix.qa9.json",
    ".beacon/evidence/design-md-lint/latest.json",
    ".beacon/evidence/design-md-lint/workbench-desktop-shell.json",
    "docs/beacon/v0.0.5/change/workbench-desktop-shell.refreeze-summary.md",
    "docs/beacon/v0.0.5/change/v0.0.5.md",
]


def test_gate_written_files_are_never_unclassified() -> None:
    assert [p for p in GATE_WRITTEN if artifact_role_for_path(p) == "unclassified"] == []


def test_tracked_gate_verdicts_ask_for_a_commit() -> None:
    for path in (
        ".beacon/qa/features/f/status.json",
        ".beacon/qa/features/f/scorecard.json",
        ".beacon/evidence/design-md-lint/latest.json",
    ):
        assert artifact_role_for_path(path) == "formal_evidence", path
    assert "commit" in DIRTY_MANIFEST["formal_evidence"]["allowed_actions"]


def test_change_records_are_committable_canonical_truth() -> None:
    assert artifact_role_for_path("docs/beacon/v0.0.5/change/f.refreeze-summary.md") == "canonical_truth"
    assert DIRTY_MANIFEST["canonical_truth"]["allowed_actions"] == ["commit"]


def test_rolling_state_stays_runtime_private_and_ignorable() -> None:
    for pattern in GATE_ROLLING_PATTERNS:
        probe = pattern.replace("*", "sample")
        assert artifact_role_for_path(probe) == "runtime_private", pattern
        declared = set(STANDARD_BEACON_GITIGNORE_LINES)
        assert pattern in declared or pattern.replace("/*", "/**") in declared, (
            f"{pattern} is classified as ignorable runtime state but the gitignore "
            f"policy does not declare it -- the two lists drifted (#29)"
        )


def test_gate_formal_patterns_classify_as_committable() -> None:
    for pattern in GATE_FORMAL_PATTERNS:
        probe = pattern.replace("*", "sample")
        assert artifact_role_for_path(probe) in {"formal_evidence", "canonical_truth"}, pattern


def test_user_code_still_blocks() -> None:
    for path in ("src/app.py", "apps/workbench/app/page.tsx", "docs/notes.md"):
        assert artifact_role_for_path(path) == "unclassified", path


def test_secrets_still_block() -> None:
    assert artifact_role_for_path(".env") == "forbidden"
