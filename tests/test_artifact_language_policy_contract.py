from __future__ import annotations

from pathlib import Path

from beacon.utils.artifact_language import (
    load_artifact_language_policy,
    render_artifact_language_policy_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def test_artifact_language_markdown_mirror_should_match_json_policy():
    policy = load_artifact_language_policy(ROOT)
    rendered = render_artifact_language_policy_markdown(policy, version="v1.3.0")
    # v1.3.0 is archived lineage; its mirror lives under docs/beacon/archive/.
    mirror_path = ROOT / "docs" / "beacon" / "archive" / "v1.3.0" / "execution" / "artifact-language-contract.md"
    assert mirror_path.read_text(encoding="utf-8") == rendered


def test_artifact_language_policy_should_freeze_human_vs_machine_defaults():
    policy = load_artifact_language_policy(ROOT)
    default_policy = policy["default_policy"]
    assert default_policy["human_primary_language"] == "zh-CN"
    assert default_policy["machine_primary_language"] == "en"
    assert policy["source_path"] == "beacon/artifact-language-policy.json"
    assert "Any new mirrored artifact type must define source JSON, Chinese mirror markdown, render function, and drift test." in policy["rules"]
    assert "source JSON artifact" in policy["sync_contract"]["enforcement"]
    assert "Chinese mirror markdown" in policy["sync_contract"]["enforcement"]
    assert "render function in source code" in policy["sync_contract"]["enforcement"]
