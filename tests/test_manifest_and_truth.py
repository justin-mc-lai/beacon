"""Tests for manifest and truth template/format modules (v1.4.12)."""

import json
import tempfile
from pathlib import Path

import pytest

from beacon.utils.manifest import (
    add_feature,
    compute_feature_paths,
    load_manifest,
    load_manifest_or_fail,
    ManifestMissingError,
    remove_feature,
    sync_manifest,
    verify_manifest,
)
from beacon.utils.truth_format import (
    detect_content_language,
    validate_prd_format,
    validate_test_case_format,
    validate_user_story_format,
)
from beacon.utils.truth_template import (
    PRD_MANDATORY,
    USER_STORY_MANDATORY,
    TEST_CASE_MANDATORY,
    render_prd_template,
    render_test_case_template,
    render_user_story_template,
)


# --- Manifest Tests ---

class TestManifestCore:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp)
        version = "v1.4.12"
        base = self.root / "docs" / "beacon" / version
        (base / "prd").mkdir(parents=True, exist_ok=True)
        (base / "user-story").mkdir(parents=True, exist_ok=True)
        (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
        (base / ".machine" / "manifest").mkdir(parents=True, exist_ok=True)
        (base / ".machine" / "requirement").mkdir(parents=True, exist_ok=True)
        (base / "research").mkdir(parents=True, exist_ok=True)
        (base / "source-architecture").mkdir(parents=True, exist_ok=True)

    def test_add_feature(self):
        entry = add_feature(self.root, "v1.4.12", "test-feature", language="en")
        assert entry["slug"] == "test-feature"
        assert entry["status"] == "template"
        assert entry["language"] == "en"
        assert "prd" in entry["truth_paths"]

    def test_add_feature_duplicate(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        entry2 = add_feature(self.root, "v1.4.12", "test-feature", language="zh")
        assert entry2["language"] == "en"  # Already exists, returns existing

    def test_remove_feature(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        assert remove_feature(self.root, "v1.4.12", "test-feature")
        assert not remove_feature(self.root, "v1.4.12", "test-feature")  # Already removed

    def test_load_manifest(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        manifest = load_manifest(self.root, "v1.4.12")
        assert manifest is not None
        assert len(manifest["features"]) == 1
        assert manifest["features"][0]["slug"] == "test-feature"

    def test_load_manifest_missing(self):
        assert load_manifest(self.root, "v1.4.13") is None

    def test_load_manifest_or_fail(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        manifest = load_manifest_or_fail(self.root, "v1.4.12")
        assert manifest is not None

    def test_load_manifest_or_fail_raises(self):
        with pytest.raises(ManifestMissingError):
            load_manifest_or_fail(self.root, "v1.4.13")

    def test_verify_manifest_pass(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        # Create package-auth truth files on disk
        pkg = self.root / "docs" / "beacon" / "v1.4.12" / "features" / "test-feature"
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "truth.md").write_text("# TRUTH", encoding="utf-8")
        (pkg / "tests.md").write_text("# TESTS", encoding="utf-8")
        (pkg / "tasks.md").write_text("# TASKS", encoding="utf-8")
        (pkg / "evidence.md").write_text("# EVIDENCE", encoding="utf-8")
        result = verify_manifest(self.root, "v1.4.12")
        assert result["status"] == "pass"

    def test_verify_manifest_missing_paths(self):
        add_feature(self.root, "v1.4.12", "test-feature", language="en")
        # Don't create truth files -> missing paths
        result = verify_manifest(self.root, "v1.4.12")
        assert result["status"] == "fail"
        assert len(result["missing_paths"]) > 0

    def test_sync_manifest(self):
        base = self.root / "docs" / "beacon" / "v1.4.12"
        (base / "prd" / "synced-feature.md").write_text("# PRD", encoding="utf-8")
        (base / "user-story" / "synced-feature.md").write_text("# US", encoding="utf-8")
        (base / "qa" / "test-cases" / "synced-feature.md").write_text("# TC", encoding="utf-8")
        manifest = sync_manifest(self.root, "v1.4.12")
        assert len(manifest["features"]) == 1
        assert manifest["features"][0]["slug"] == "synced-feature"

    def test_compute_feature_paths(self):
        paths = compute_feature_paths(self.root, "v1.4.12", "my-feature")
        assert "features/my-feature/truth.md" in paths["prd"]
        assert "v1.4.12" in paths["prd"]


# --- Truth Template Tests ---

class TestTruthTemplate:
    def test_prd_template_has_mandatory_sections(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12", lang="en")
        for section in PRD_MANDATORY:
            assert f"## {section}" in content, f"Missing section: {section}"

    def test_user_story_template_has_mandatory_sections(self):
        content = render_user_story_template(feature_slug="test", version="v1.4.12", lang="en")
        for section in USER_STORY_MANDATORY:
            assert f"## {section}" in content, f"Missing section: {section}"

    def test_test_case_template_has_mandatory_sections(self):
        content = render_test_case_template(feature_slug="test", version="v1.4.12", lang="en")
        for section in TEST_CASE_MANDATORY:
            assert f"## {section}" in content, f"Missing section: {section}"

    def test_prd_has_mermaid(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12", lang="en")
        assert "```mermaid" in content

    def test_us_has_mermaid(self):
        content = render_user_story_template(feature_slug="test", version="v1.4.12", lang="en")
        assert "```mermaid" in content

    def test_tc_has_mermaid(self):
        content = render_test_case_template(feature_slug="test", version="v1.4.12", lang="en")
        assert "```mermaid" in content

    def test_lang_zh(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12", lang="zh")
        assert "**Language**: `zh`" in content

    def test_lang_en(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12", lang="en")
        assert "**Language**: `en`" in content

    def test_no_numbering(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12", lang="en")
        assert "## 1." not in content
        assert "### 1.1" not in content


# --- Truth Format Validation Tests ---

class TestTruthFormat:
    def test_valid_prd_passes(self):
        content = render_prd_template(feature_slug="test-feature", version="v1.4.12")
        result = validate_prd_format(content, strict=True)
        assert result["status"] == "pass"
        assert result["mandatory_ok"] is True
        assert result["no_numbering"] is True

    def test_numbering_rejected(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12")
        content = content.replace("## Problem", "## 1. Problem")
        result = validate_prd_format(content, strict=True)
        assert result["status"] == "fail"
        assert any("numbering_prefix_not_allowed" in i for i in result["issues"])

    def test_missing_outline_rejected(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12")
        content = content.replace("## Outline", "## Removed")
        result = validate_prd_format(content, strict=True)
        assert result["status"] == "fail"
        assert any("missing_mandatory_section: Outline" in i for i in result["issues"])

    def test_missing_mermaid_rejected(self):
        content = render_prd_template(feature_slug="test", version="v1.4.12")
        content = content.replace("```mermaid", "```text")
        result = validate_prd_format(content, strict=True)
        assert result["status"] == "fail"
        assert any("missing_mermaid_block" in i for i in result["issues"])

    def test_detect_en(self):
        assert detect_content_language("Hello world this is a test") == "en"

    def test_detect_zh(self):
        assert detect_content_language("这是一个测试内容，用于检测语言") == "zh"

    def test_detect_zh_with_beacon_technical_structure(self):
        content = """
# Test Cases: Example

**Language**: `zh`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
|-------|-------|-------|-----------------|-----------|---------------|
| AC-001 | TC-001 | integration | `beacon validate-feature-package <feature>` | 创建 `features/<slug>/truth.md`，并保持 canonical triptych 不变。 | `docs/beacon/v1.5.0/features/<slug>/` |

## Explicit Non Coverage

- deep、CEO review、QA verdict、release readiness authority 不能迁移到 `evidence.md`。
- checkbox-only 不能完成 implement、QA 或 release gates。
"""
        assert detect_content_language(content) == "zh"
