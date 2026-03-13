from __future__ import annotations

from pathlib import Path


def test_research_governance_doc_should_declare_source_boundary():
    path = Path("/Users/apple/Developer/Personal/my_skill/beacon/docs/beacon/v1.1.1/research/brainstorm-research-convergence-orchestration.md")
    text = path.read_text(encoding="utf-8")
    assert "source_of_truth=false" in text
    assert "divergent" in text
    assert "triaged" in text
    assert "converged" in text
