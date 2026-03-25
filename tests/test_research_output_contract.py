from __future__ import annotations

from pathlib import Path


def test_research_documents_should_live_under_docs_beacon_research(tmp_path: Path):
    root = tmp_path / "docs" / "beacon" / "v1.1.1" / "research"
    root.mkdir(parents=True, exist_ok=True)
    (root / "brainstorm-ai-agent-ux.md").write_text("# doc\n", encoding="utf-8")
    (root / "brainstorm-research-convergence-orchestration.md").write_text("# doc\n", encoding="utf-8")
    assert root.exists()
    docs = {p.name for p in root.glob("*.md")}
    assert "brainstorm-ai-agent-ux.md" in docs
    assert "brainstorm-research-convergence-orchestration.md" in docs
