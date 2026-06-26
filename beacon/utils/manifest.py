"""Manifest-based feature discovery and path resolution for v1.4.12+.

This module replaces glob-based feature discovery with a canonical manifest file
that serves as the single source of truth for feature lists and paths within a version.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.versioning import normalize_version, resolve_target_version
from beacon.utils.truth_map import feature_package_authoritative


MANIFEST_FILENAME = "version-features.json"
TRANSACTIONS_DIR = ".beacon"


class ManifestError(Exception):
    """Base manifest error."""


class ManifestMissingError(ManifestError):
    """Raised when a v1.4.12+ manifest does not exist."""

    def __init__(self, version: str) -> None:
        self.version = version
        super().__init__(f"Manifest missing for {version}; run 'beacon manifest sync' to create one")


class ManifestValidationError(ManifestError):
    """Raised when manifest validation fails."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _manifest_path(project_root: Path, version: str) -> Path:
    resolved = normalize_version(version) or version
    return project_root / "docs" / "beacon" / resolved / ".machine" / "manifest" / MANIFEST_FILENAME


def _version_root(project_root: Path, version: str) -> Path:
    from beacon.utils.artifact_paths import version_root

    return version_root(project_root, version)


def _slugify(feature: str) -> str:
    text = feature.strip().lower()
    out: list[str] = []
    for ch in text:
        if ch.isalnum() or ch == "-":
            out.append(ch)
        elif ch == " " or ch == "_":
            out.append("-")
    return "".join(out).strip("-") or text


def compute_feature_paths(project_root: Path, version: str, slug: str) -> dict[str, str]:
    """Compute all fixed paths for a feature based on version and slug."""
    base = _version_root(project_root, version)
    rel_base = f"docs/beacon/{version}"
    if feature_package_authoritative(version):
        # Package-authoritative (>=v1.5.2): truth lives in features/<slug>/.
        return {
            "prd": f"{rel_base}/features/{slug}/truth.md",
            "user_story": f"{rel_base}/features/{slug}/truth.md",
            "test_case": f"{rel_base}/features/{slug}/tests.md",
            "truth": f"{rel_base}/features/{slug}/truth.md",
            "tests": f"{rel_base}/features/{slug}/tests.md",
            "tasks": f"{rel_base}/features/{slug}/tasks.md",
            "evidence": f"{rel_base}/features/{slug}/evidence.md",
            "research": f"{rel_base}/research/{slug}.md",
            "source_architecture": f"{rel_base}/source-architecture/{slug}.md",
            "change": f"{rel_base}/change/{version}.md",
            "qa_matrix": f"{rel_base}/.machine/qa/{slug}.evidence-contract.json",
            "freeze_state": f"{rel_base}/.machine/requirement/{slug}.freeze-state.json",
        }
    return {
        "prd": f"{rel_base}/prd/{slug}.md",
        "user_story": f"{rel_base}/user-story/{slug}.md",
        "test_case": f"{rel_base}/qa/test-cases/{slug}.md",
        "research": f"{rel_base}/research/{slug}.md",
        "source_architecture": f"{rel_base}/source-architecture/{slug}.md",
        "change": f"{rel_base}/change/{version}.md",
        "qa_matrix": f"{rel_base}/.machine/qa/{slug}.evidence-contract.json",
        "freeze_state": f"{rel_base}/.machine/requirement/{slug}.freeze-state.json",
    }


def compute_version_level_paths(project_root: Path, version: str) -> dict[str, str]:
    """Compute version-level directory paths."""
    rel_base = f"docs/beacon/{version}"
    return {
        "research_dir": f"{rel_base}/research/",
        "execution_dir": f"{rel_base}/execution/",
        "release_dir": f"{rel_base}/release/",
        "change_dir": f"{rel_base}/change/",
        "design_dir": f"{rel_base}/design/",
    }


def _empty_manifest(version: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "version": version,
        "generated_at": _now_iso(),
        "features": [],
        "version_level_paths": {},
    }


def load_manifest(project_root: Path, version: str) -> dict[str, Any] | None:
    """Load manifest if it exists, return None otherwise."""
    path = _manifest_path(project_root, version)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data


def load_manifest_or_fail(project_root: Path, version: str) -> dict[str, Any]:
    """Load manifest for v1.4.12+, raise ManifestMissingError if not found."""
    resolved_version = resolve_target_version(project_root, version)
    data = load_manifest(project_root, resolved_version)
    if data is not None:
        return data
    raise ManifestMissingError(resolved_version)


def save_manifest(project_root: Path, version: str, manifest: dict[str, Any]) -> Path:
    """Save manifest to disk and write transaction record."""
    path = _manifest_path(project_root, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Write transaction record
    tx_dir = project_root / TRANSACTIONS_DIR / "transactions"
    tx_dir.mkdir(parents=True, exist_ok=True)
    tx_id = f"manifest-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tx_path = tx_dir / f"{tx_id}.json"
    tx_payload = {
        "schema_version": "1.0",
        "transaction_id": tx_id,
        "operation": "manifest_save",
        "version": version,
        "feature_count": len(manifest.get("features", [])),
        "generated_at": _now_iso(),
    }
    tx_path.write_text(json.dumps(tx_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return path


def add_feature(project_root: Path, version: str, feature: str, *, language: str = "en") -> dict[str, Any]:
    """Add a feature to the manifest, creating the manifest if needed."""
    resolved = resolve_target_version(project_root, version)
    manifest = load_manifest(project_root, resolved)
    if manifest is None:
        manifest = _empty_manifest(resolved)

    slug = _slugify(feature)
    # Check if feature already exists
    for existing in manifest.get("features", []):
        if existing.get("slug") == slug:
            return existing

    truth_paths = compute_feature_paths(project_root, resolved, slug)

    feature_entry = {
        "slug": slug,
        "status": "template",
        "language": language,
        "truth_paths": {
            "prd": truth_paths["prd"],
            "user_story": truth_paths["user_story"],
            "test_case": truth_paths["test_case"],
        },
        "evidence_paths": {
            "qa_matrix": truth_paths["qa_matrix"],
            "freeze_state": truth_paths["freeze_state"],
        },
    }

    if "version_level_paths" not in manifest or not manifest["version_level_paths"]:
        manifest["version_level_paths"] = compute_version_level_paths(project_root, resolved)

    manifest["features"].append(feature_entry)
    manifest["generated_at"] = _now_iso()
    save_manifest(project_root, resolved, manifest)

    return feature_entry


def remove_feature(project_root: Path, version: str, feature: str) -> bool:
    """Remove a feature from the manifest. Returns True if feature was found and removed."""
    resolved = resolve_target_version(project_root, version)
    manifest = load_manifest(project_root, resolved)
    if manifest is None:
        return False

    slug = _slugify(feature)
    original_count = len(manifest.get("features", []))
    manifest["features"] = [f for f in manifest.get("features", []) if f.get("slug") != slug]

    if len(manifest["features"]) == original_count:
        return False

    manifest["generated_at"] = _now_iso()
    save_manifest(project_root, resolved, manifest)
    return True


def list_features(project_root: Path, version: str) -> list[dict[str, Any]]:
    """List all features in the manifest."""
    manifest = load_manifest(project_root, version)
    if manifest is None:
        return []
    return manifest.get("features", [])


def sync_manifest(project_root: Path, version: str) -> dict[str, Any]:
    """Scan disk and rebuild manifest from existing files."""
    resolved = resolve_target_version(project_root, version)
    base = _version_root(project_root, resolved)
    manifest = _empty_manifest(resolved)
    manifest["version_level_paths"] = compute_version_level_paths(project_root, resolved)

    # Scan truth directories for feature slugs
    slugs: set[str] = set()
    for dirname in ("prd", "user-story", "qa/test-cases"):
        dir_path = base / dirname
        if dir_path.exists():
            for path in dir_path.glob("*.md"):
                if path.stem != "index" and path.is_file():
                    slugs.add(path.stem)

    # Package-authoritative (>=v1.5.2): also scan features/<slug>/ packages.
    if feature_package_authoritative(resolved):
        features_dir = base / "features"
        if features_dir.exists():
            for entry in features_dir.iterdir():
                if entry.is_dir() and (entry / "truth.md").exists():
                    slugs.add(entry.name)

    # Add discovered features
    for slug in sorted(slugs):
        truth_paths = compute_feature_paths(project_root, resolved, slug)
        # Determine language from existing file if possible
        language = "en"
        prd_file = base / "prd" / f"{slug}.md"
        if prd_file.exists():
            content = prd_file.read_text(encoding="utf-8")
            if "**Language**" in content:
                for line in content.split("\n"):
                    if line.strip().startswith("**Language**"):
                        lang_val = line.split("`")[1] if "`" in line else "en"
                        language = lang_val if lang_val in ("en", "zh") else "en"
                        break

        # Determine status: package-authoritative reads truth.md frontmatter;
        # legacy reads .machine/requirement/<slug>.freeze-state.json.
        status = "template"
        if feature_package_authoritative(resolved):
            truth_file = base / "features" / slug / "truth.md"
            if truth_file.exists():
                try:
                    fm_text = truth_file.read_text(encoding="utf-8")
                    if fm_text.lstrip().startswith("---"):
                        end = fm_text.find("---", 3)
                        if end > 0:
                            for line in fm_text[3:end].splitlines():
                                if line.strip().startswith("status:"):
                                    status = line.split(":", 1)[1].strip() or "template"
                                    break
                except OSError:
                    pass
        else:
            freeze_path = base / ".machine" / "requirement" / f"{slug}.freeze-state.json"
            if freeze_path.exists():
                try:
                    freeze_data = json.loads(freeze_path.read_text(encoding="utf-8"))
                    status = freeze_data.get("status", "template")
                except (json.JSONDecodeError, OSError):
                    pass

        feature_entry = {
            "slug": slug,
            "status": status,
            "language": language,
            "truth_paths": {
                "prd": truth_paths["prd"],
                "user_story": truth_paths["user_story"],
                "test_case": truth_paths["test_case"],
            },
            "evidence_paths": {
                "qa_matrix": truth_paths["qa_matrix"],
                "freeze_state": truth_paths["freeze_state"],
            },
        }
        manifest["features"].append(feature_entry)

    save_manifest(project_root, resolved, manifest)
    return manifest


def verify_manifest(project_root: Path, version: str, *, strict: bool = False) -> dict[str, Any]:
    """Verify manifest consistency with disk.
    
    Returns dict with:
        - status: "pass" or "fail"
        - missing_paths: list of paths in manifest but not on disk
        - extra_files: list of truth files on disk but not in manifest
        - feature_count: number of features in manifest
    """
    resolved = resolve_target_version(project_root, version)
    manifest = load_manifest(project_root, resolved)
    if manifest is None:
        return {
            "status": "fail",
            "missing_paths": [],
            "extra_files": [],
            "feature_count": 0,
            "reason_code": "manifest_missing",
        }

    missing_paths: list[str] = []
    manifest_slugs: set[str] = set()

    for feature in manifest.get("features", []):
        slug = feature.get("slug", "")
        manifest_slugs.add(slug)
        for key in ("prd", "user_story", "test_case"):
            rel_path = feature.get("truth_paths", {}).get(key, "")
            if rel_path:
                abs_path = project_root / rel_path
                if not abs_path.exists():
                    missing_paths.append(rel_path)

    # Check for truth files on disk not in manifest
    extra_files: list[str] = []
    base = _version_root(project_root, resolved)
    for dirname in ("prd", "user-story", "qa/test-cases"):
        dir_path = base / dirname
        if dir_path.exists():
            for path in dir_path.glob("*.md"):
                if path.stem != "index" and path.is_file() and path.stem not in manifest_slugs:
                    extra_files.append(str(path.relative_to(project_root)))

    status = "pass" if not missing_paths else "fail"
    if strict and extra_files:
        status = "fail"

    return {
        "status": status,
        "missing_paths": missing_paths,
        "extra_files": extra_files,
        "feature_count": len(manifest.get("features", [])),
        "reason_code": "manifest_path_missing" if missing_paths else ("manifest_extra_files" if extra_files and strict else None),
    }
