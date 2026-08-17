from __future__ import annotations

from pathlib import Path

from beacon.utils.ceo_review_surface import run_ceo_review


VERSION = "v1.4.5"
FEATURE = "beacon-v1.4.5-guidance-first-docs-architecture-and-governed-external-capability-plane"
SUBFEATURES = [
    "beacon-v1.4.5-guidance-surface-family-and-cross-industry-positioning",
    "beacon-v1.4.5-docs-architecture-and-machine-truth-minimization",
    "beacon-v1.4.5-governed-external-skill-sources-and-learning-composition",
]


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_version_package_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/change/{VERSION}.md",
        "\n".join(
            [
                "# Change",
                "",
                "## Feature Packages",
                *(f"- `{feature}`" for feature in SUBFEATURES),
                "",
            ]
        ),
    )
    for feature in SUBFEATURES:
        _write(root, f"docs/beacon/{VERSION}/prd/{feature}.md", "# prd\n")
        _write(root, f"docs/beacon/{VERSION}/user-story/{feature}.md", "# story\n")
        _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{feature}.md", "# test\n")


def test_v145_ceo_review_binds_version_package_truth_refs(tmp_path: Path) -> None:
    _seed_version_package_docs(tmp_path)

    payload = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, focus="full")

    assert payload["status"] == "advisory"
    assert payload["decision"] == "hold"
    assert len(payload["truth_refs"]) == 9
    assert all(any(feature in ref for ref in payload["truth_refs"]) for feature in SUBFEATURES)
    assert "Bound version package features" in payload["operator_visible_summary"]
    assert "default downside axes" in payload["operator_visible_summary"]
