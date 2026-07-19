"""AC-169 skill-score-corpus.v1 formal score surface."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.loom_skill_score import (
    REASON_CORPUS_MISSING,
    load_skill_score_corpus,
    score_with_corpus,
)

ROOT = Path(__file__).resolve().parents[1]


def test_tc_w5_001_corpus_fields() -> None:
    loaded = load_skill_score_corpus(ROOT)
    assert loaded["ok"] is True
    corpus = loaded["corpus"]
    assert corpus["schema"] == "skill-score-corpus.v1"
    assert "baseline" in corpus
    assert len(corpus.get("public_skills") or []) >= 6
    payload = score_with_corpus(ROOT, require_corpus=True)
    assert payload.get("ok") is True
    assert payload.get("auto_edit_skill_md") is False
    assert payload.get("corpus_schema") == "skill-score-corpus.v1"


def test_tc_w5_002_missing_corpus_fail_closed(tmp_path: Path) -> None:
    payload = score_with_corpus(
        tmp_path,
        require_corpus=True,
        corpus_path=str(tmp_path / "nope.json"),
    )
    assert payload.get("blocked") is True
    assert payload.get("reason_code") == REASON_CORPUS_MISSING


def test_tc_w5_no_auto_edit_flag() -> None:
    payload = score_with_corpus(ROOT, skill="loom-goal", require_corpus=True)
    assert payload.get("auto_edit_skill_md") is False
