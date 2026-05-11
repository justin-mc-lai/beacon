from __future__ import annotations

from pathlib import Path

from beacon.utils.ceo_review_surface import run_ceo_review


VERSION = "v1.4.3"
FEATURE = "beacon-v1.4.3-version-level-ceo-review-and-requirement-challenge-surface"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{FEATURE}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{FEATURE}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{FEATURE}.md", "# test\n")


def test_v143_ceo_review_surface_exists_and_is_support_only(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    payload = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, focus="full")

    assert payload["surface"] == "beacon-ceo-review"
    assert payload["status"] == "advisory"
    assert payload["next_route"]["target_surface"] == "beacon-implement"
    assert payload["artifacts"]["machine_path"].endswith("beacon-ceo-review-transaction.json")


def test_v143_ceo_review_scope_judgment_modes(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    expand = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="expand")
    hold = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="hold")
    reduce = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="reduce")
    reframe = run_ceo_review(tmp_path, version=VERSION, feature=FEATURE, decision="reframe")

    assert expand["decision"] == "expand"
    assert hold["decision"] == "hold"
    assert reduce["decision"] == "reduce"
    assert reframe["decision"] == "reframe"


def test_v143_ceo_review_version_level_challenge_scope(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    payload = run_ceo_review(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        focus="scope",
        decision="reduce",
        change_intent="narrow the scope before implementation",
    )

    assert payload["status"] == "accepted_for_writeback"
    assert payload["route_decision"]["route"] == "change/refreeze"
    assert len(payload["truth_refs"]) == 3


def test_v143_ceo_review_routes_back_to_truth_surfaces(tmp_path: Path) -> None:
    _seed_feature_docs(tmp_path)

    payload = run_ceo_review(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        focus="promise",
        decision="reframe",
    )

    assert payload["writeback_targets"] == [
        "beacon-change",
        "beacon-prd",
        "beacon-user-story",
        "beacon-test-case",
    ]
    assert "beacon change" in payload["next_route"]["command"]
