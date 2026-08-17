from __future__ import annotations

from pathlib import Path


def test_research_governance_doc_should_declare_source_boundary(tmp_path: Path):
    path = tmp_path / "docs" / "beacon" / "v1.1.1" / "research" / "brainstorm-research-convergence-orchestration.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("source_of_truth=false\ndivergent\ntriaged\nconverged\n", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    assert "source_of_truth=false" in text
    assert "divergent" in text
    assert "triaged" in text
    assert "converged" in text
