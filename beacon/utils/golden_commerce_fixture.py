"""Golden commerce checkout fixture authority (v1.6.7 P0 lake 2).

Canonical positive + negative fixtures under
docs/beacon/<version>/fixtures/golden-commerce-checkout/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.domain_fsm import evaluate_domain_fsm_authority, parse_domain_fsm_from_truth
from beacon.utils.versioning import normalize_version, resolve_target_version

FIXTURE_SLUG = "golden-commerce-checkout"
POSITIVE_DIR = "positive"
NEGATIVE_DIR = "negative-order-without-product"
SCHEMA_VERSION = "1.0"

REASON_POSITIVE_INCOMPLETE = "golden_positive_package_incomplete"
REASON_NEGATIVE_NOT_FAILING = "golden_negative_must_fail"
REASON_FSM_AGGREGATES_MISSING = "golden_fsm_aggregates_missing"
REASON_SKILL_POINTER_MISSING = "golden_skill_pointer_missing"


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def golden_fixture_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 7)


def golden_fixture_root(project_root: Path, *, version: str = "v1.6.7") -> Path:
    resolved = resolve_target_version(project_root, version) if (project_root / "docs" / "beacon").exists() else version
    # resolve_target_version needs project; fall back to raw version when used on partial trees
    try:
        resolved = resolve_target_version(Path(project_root), version)
    except Exception:  # noqa: BLE001
        resolved = normalize_version(version) or version
    root = Path(project_root) / "docs" / "beacon" / resolved / "fixtures" / FIXTURE_SLUG
    # v2 parity: prefer local mirror; else load v1.6.7 golden (UD-V2-GOLD-001)
    if not root.exists() and _semver_tuple(resolved) >= (2, 0, 0):
        upstream = Path(project_root) / "docs" / "beacon" / "v1.6.7" / "fixtures" / FIXTURE_SLUG
        if upstream.exists():
            return upstream
    return root


def parity_index_path(project_root: Path, *, version: str = "v2.0.0") -> Path:
    try:
        resolved = resolve_target_version(Path(project_root), version)
    except Exception:  # noqa: BLE001
        resolved = normalize_version(version) or version
    return Path(project_root) / "docs" / "beacon" / resolved / "fixtures" / "parity-v167" / "README.md"


def resolve_v2_parity_index(project_root: Path, *, version: str = "v2.0.0") -> dict:
    """AC-V2-GOLD-004: v2 fixtures/parity-v167 index must resolve loadable paths."""
    idx = parity_index_path(project_root, version=version)
    text = idx.read_text(encoding="utf-8") if idx.exists() else ""
    positive = Path(project_root) / "docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/positive"
    negative = Path(project_root) / "docs/beacon/v1.6.7/fixtures/golden-commerce-checkout/negative-order-without-product"
    findings = []
    if not idx.exists():
        findings.append({"reason_code": "parity_index_missing", "text": str(idx)})
    if "golden-commerce-checkout" not in text and idx.exists():
        findings.append({"reason_code": "parity_index_incomplete", "text": "missing golden commerce pointer"})
    if not positive.exists():
        findings.append({"reason_code": "parity_positive_missing", "text": str(positive)})
    if not negative.exists():
        findings.append({"reason_code": "parity_negative_missing", "text": str(negative)})
    return {
        "schema_version": SCHEMA_VERSION,
        "index_path": str(idx) if idx.exists() else "",
        "positive_path": str(positive) if positive.exists() else "",
        "negative_path": str(negative) if negative.exists() else "",
        "resolves": not findings,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "findings": findings,
    }


def positive_package_paths(root: Path) -> dict[str, Path]:
    base = root / POSITIVE_DIR
    return {
        "dir": base,
        "truth": base / "truth.md",
        "tests": base / "tests.md",
        "tasks": base / "tasks.md",
        "evidence": base / "evidence.md",
        "ui_state_matrix": base / "ui-state-matrix.md",
        "design": base / "DESIGN.md",
    }


def negative_package_paths(root: Path) -> dict[str, Path]:
    base = root / NEGATIVE_DIR
    return {
        "dir": base,
        "truth": base / "truth.md",
        "tests": base / "tests.md",
        "tasks": base / "tasks.md",
        "evidence": base / "evidence.md",
    }


def skill_example_paths(project_root: Path) -> list[Path]:
    return [
        Path(project_root) / "skills" / "beacon" / "examples" / "full-product-domain-freeze.md",
        Path(project_root) / "skills" / "beacon" / "examples" / "goal-one-shot-30s.md",
    ]


def _read(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def validate_positive_package(project_root: Path, *, version: str = "v1.6.7") -> dict[str, Any]:
    root = golden_fixture_root(project_root, version=version)
    paths = positive_package_paths(root)
    required_files = ("truth", "tests", "tasks", "evidence")
    missing = [name for name in required_files if not paths[name].exists()]
    truth = _read(paths["truth"])
    domain = evaluate_domain_fsm_authority(truth_markdown=truth, tests_markdown=_read(paths["tests"]), version=version)
    projection = parse_domain_fsm_from_truth(truth)
    aggregate_names = {str(item.get("name") or "").lower() for item in (projection.get("aggregates") or [])}
    has_product = any("product" in name for name in aggregate_names)
    has_order = any("order" in name for name in aggregate_names)
    findings: list[dict[str, str]] = []
    if missing:
        findings.append(
            {
                "kind": "positive_package_incomplete",
                "reason_code": REASON_POSITIVE_INCOMPLETE,
                "text": f"missing positive package files: {', '.join(missing)}",
            }
        )
    if not domain.get("required") or domain.get("blocked"):
        findings.append(
            {
                "kind": "positive_domain_fsm_invalid",
                "reason_code": REASON_POSITIVE_INCOMPLETE,
                "text": f"positive fixture domain authority blocked: {domain.get('reason_code') or domain.get('findings')}",
            }
        )
    if not (has_product and has_order):
        findings.append(
            {
                "kind": "fsm_aggregates_missing",
                "reason_code": REASON_FSM_AGGREGATES_MISSING,
                "text": f"expected Product+Order aggregates, got {sorted(aggregate_names)}",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_root": str(root),
        "paths": {k: str(v) for k, v in paths.items()},
        "missing_files": missing,
        "domain": domain,
        "aggregates": sorted(aggregate_names),
        "has_product_fsm": has_product,
        "has_order_fsm": has_order,
        "has_ui_state_matrix": paths["ui_state_matrix"].exists() or paths["design"].exists(),
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
    }


def validate_negative_package(project_root: Path, *, version: str = "v1.6.7") -> dict[str, Any]:
    root = golden_fixture_root(project_root, version=version)
    paths = negative_package_paths(root)
    truth = _read(paths["truth"])
    if not truth.strip():
        return {
            "schema_version": SCHEMA_VERSION,
            "blocked": True,
            "status": "blocked",
            "reason_code": REASON_POSITIVE_INCOMPLETE,
            "findings": [{"kind": "negative_missing", "reason_code": REASON_POSITIVE_INCOMPLETE, "text": "negative truth.md missing"}],
            "domain": {},
            "must_fail": True,
            "fails_closed": False,
        }
    domain = evaluate_domain_fsm_authority(
        truth_markdown=truth,
        tests_markdown=_read(paths["tests"]),
        version=version,
    )
    # Negative must fail domain freeze/clarity authority OR declare expected_gate
    frontmatter = domain.get("projection", {}).get("frontmatter") if isinstance(domain.get("projection"), dict) else {}
    expected_gate = str((frontmatter or {}).get("expected_gate") or "").lower()
    fails_closed = bool(domain.get("blocked")) or expected_gate in {
        "freeze_or_qa_fail",
        "domain_fsm",
        "entity_precedence",
        "qa_fail",
    }
    findings: list[dict[str, str]] = []
    if not fails_closed:
        findings.append(
            {
                "kind": "negative_not_failing",
                "reason_code": REASON_NEGATIVE_NOT_FAILING,
                "text": "negative fixture must block domain authority or declare expected_gate fail",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "paths": {k: str(v) for k, v in paths.items()},
        "domain": domain,
        "must_fail": True,
        "fails_closed": fails_closed,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
    }


def validate_skill_pointers(project_root: Path) -> dict[str, Any]:
    needle = f"fixtures/{FIXTURE_SLUG}"
    hits: list[str] = []
    missing: list[str] = []
    for path in skill_example_paths(project_root):
        text = _read(path)
        rel = str(path.relative_to(project_root)) if path.exists() else str(path)
        if needle in text or FIXTURE_SLUG in text:
            hits.append(rel)
        else:
            missing.append(rel)
    findings = []
    if not hits:
        findings.append(
            {
                "kind": "skill_pointer_missing",
                "reason_code": REASON_SKILL_POINTER_MISSING,
                "text": f"no skills/beacon/examples/* points to {FIXTURE_SLUG}",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "hits": hits,
        "missing": missing,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
    }


def build_golden_commerce_fixture_gate(project_root: Path, *, version: str = "v1.6.7") -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    if not golden_fixture_supported(version):
        return {
            "schema_version": SCHEMA_VERSION,
            "required": False,
            "blocked": False,
            "status": "not_supported",
            "reason_code": "",
        }
    positive = validate_positive_package(project_root, version=version)
    negative = validate_negative_package(project_root, version=version)
    skills = validate_skill_pointers(project_root)
    findings = list(positive.get("findings") or []) + list(negative.get("findings") or []) + list(skills.get("findings") or [])
    blocked = bool(findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_slug": FIXTURE_SLUG,
        "version": version,
        "required": True,
        "blocked": blocked,
        "status": "blocked" if blocked else "pass",
        "reason_code": findings[0]["reason_code"] if findings else "",
        "findings": findings,
        "positive": positive,
        "negative": negative,
        "skill_pointers": skills,
    }
