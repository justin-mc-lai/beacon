from __future__ import annotations

from pathlib import Path


def test_research_documents_should_live_under_docs_beacon_research():
    root = Path("/Users/apple/Developer/Personal/my_skill/beacon/docs/beacon/v1.1.1/research")
    assert root.exists()
    docs = {p.name for p in root.glob("*.md")}
    assert "brainstorm-ai-agent-ux.md" in docs
    assert "brainstorm-research-convergence-orchestration.md" in docs
