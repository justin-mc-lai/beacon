"""v1.1.0 memory upsert/revision contracts."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.memory import append_memory_entry, load_memory_entries


def test_debug_feedback_memory_should_support_upsert_and_revision(tmp_path: Path):
    first = append_memory_entry(
        project_root=tmp_path,
        mem_type="insight",
        text="[feedback:run-a] low-confidence",
        source_session_id="run-a",
        source="feedback.apply.debug",
        reason_codes=["low-confidence"],
        upsert=True,
    )
    second = append_memory_entry(
        project_root=tmp_path,
        mem_type="insight",
        text="[feedback:run-a] low-confidence",
        source_session_id="run-a",
        source="feedback.apply.debug",
        reason_codes=["low-confidence"],
        upsert=True,
    )
    assert first.get("memory_id") == second.get("memory_id")

    revised = append_memory_entry(
        project_root=tmp_path,
        mem_type="insight",
        text="[feedback:run-a] router_false_positive",
        source_session_id="run-a",
        source="feedback.apply.debug",
        reason_codes=["router_false_positive"],
        revision_of=str(first.get("memory_id", "")),
        upsert=False,
    )
    assert revised.get("revision_of") == first.get("memory_id")

    rows = load_memory_entries(tmp_path)
    old_row = next(item for item in rows if item.get("memory_id") == first.get("memory_id"))
    assert old_row.get("status") == "superseded"
    assert old_row.get("superseded_by") == revised.get("memory_id")
