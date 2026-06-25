"""Tests for beacon-freeze-integrity-drift-repair-v163.

Covers 4 freeze-flow validator self-alignment fixes:
1. parser_contract single-source (v1 and v2 both accepted; unknown rejected)
2. forbidden-field word-boundary (path substring does not trigger)
3. pytest as hard marker (integration layer not auto-soft)
4. self-describing authority errors (allowed_authorities in diagnostics)
"""
from __future__ import annotations

import re
from pathlib import Path

from beacon.utils.feature_package import validate_feature_package
from beacon.utils import truth_integrity


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_TRUTH_TMPL = """\
---
slug: {slug}
version: v1.6.3
status: draft
language: zh
canonical_refs:
  prd: a
  user_story: a
  test_case: a
parser_contract: {contract}
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# t

## User Intent（一行）
x

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | a | a（Must） |
"""

_TESTS_TMPL = """\
---
slug: {slug}
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: {contract}
---

# t

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `python3 -m pytest tests/test_x.py::test_a -q` | pass |
"""

_TASKS_TMPL = """\
---
slug: {slug}
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: {contract}
---

# t

- [ ] TC-001 do something (BLOCKED:Phase-A)
"""

_EVIDENCE_TMPL = """\
---
slug: {slug}
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: {contract}
---

# t

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | a |
| tests.md | test_truth | a |
"""


def _build_pkg(
    root: Path,
    slug: str = "demo-freeze-fix",
    contract: str = "beacon-feature-package-v1",
    evidence_extra: str = "",
    tests_override: str | None = None,
) -> Path:
    version = "v1.6.3"
    pkg = root / "docs" / "beacon" / version / "features" / slug
    _write(pkg / "truth.md", _TRUTH_TMPL.format(slug=slug, contract=contract))
    _write(pkg / "tests.md", (tests_override or _TESTS_TMPL).format(slug=slug, contract=contract))
    _write(pkg / "tasks.md", _TASKS_TMPL.format(slug=slug, contract=contract))
    _write(pkg / "evidence.md", _EVIDENCE_TMPL.format(slug=slug, contract=contract) + evidence_extra)
    return root


def _codes(result: dict) -> list[str]:
    return [str(d.get("code", "")) for d in result.get("diagnostics", []) if d.get("severity") == "error"]


# ---- AC-001 parser_contract single source ----

def test_parser_contract_v2_accepted(tmp_path: Path) -> None:
    _build_pkg(tmp_path, contract="beacon-feature-package-v2")
    result = validate_feature_package(tmp_path, version="v1.6.3", feature="demo-freeze-fix")
    assert "parser_contract_mismatch" not in _codes(result)


def test_parser_contract_v1_still_accepted(tmp_path: Path) -> None:
    _build_pkg(tmp_path, contract="beacon-feature-package-v1")
    result = validate_feature_package(tmp_path, version="v1.6.3", feature="demo-freeze-fix")
    assert "parser_contract_mismatch" not in _codes(result)


def test_unknown_contract_still_mismatch(tmp_path: Path) -> None:
    _build_pkg(tmp_path, contract="beacon-feature-package-v9")
    result = validate_feature_package(tmp_path, version="v1.6.3", feature="demo-freeze-fix")
    assert "parser_contract_mismatch" in _codes(result)


# ---- AC-002 forbidden field word boundary ----

def test_forbidden_field_substring_not_banned(tmp_path: Path) -> None:
    """A path/test-filename containing the substring gate_truth must NOT trigger."""
    _build_pkg(
        tmp_path,
        evidence_extra="- junit: tests/test_v163_gate_truth_model_alignment.py\n",
    )
    result = validate_feature_package(tmp_path, version="v1.6.3", feature="demo-freeze-fix")
    codes = _codes(result)
    assert not any(c.startswith("evidence_forbidden_gate_truth_field") for c in codes)


def test_real_forbidden_authority_still_banned(tmp_path: Path) -> None:
    """An authority cell actually set to a forbidden name must still be reported."""
    forbidden_evidence = """\
---
slug: demo-freeze-fix
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: beacon-feature-package-v1
---

# t

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | source_of_truth | a |
"""
    root = tmp_path
    pkg = root / "docs" / "beacon" / "v1.6.3" / "features" / "demo-freeze-fix"
    _write(pkg / "truth.md", _TRUTH_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tests.md", _TESTS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tasks.md", _TASKS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "evidence.md", forbidden_evidence)
    result = validate_feature_package(root, version="v1.6.3", feature="demo-freeze-fix")
    codes = _codes(result)
    assert any("evidence_forbidden_gate_truth_field" in c or "evidence_invalid_authority" in c for c in codes), codes


# ---- AC-003 pytest hard marker ----

def test_integration_pytest_not_soft(tmp_path: Path) -> None:
    """truth_integrity must not flag an integration+pytest row as soft_test_assertion."""
    tests = """\
---
slug: demo-freeze-fix
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: beacon-feature-package-v1
---

# t

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | integration | `python3 -m pytest tests/test_x.py::test_a -q` | pass |
"""
    _build_pkg(tmp_path, tests_override=tests)
    findings = truth_integrity.scan_integrity_extension_lines(
        tmp_path, version="v1.6.3", feature="demo-freeze-fix"
    )
    soft = [f for f in findings if f.get("kind") == "soft_test_assertion"]
    assert soft == [], [f.get("text", "") for f in soft]


def test_hard_markers_regex_includes_pytest() -> None:
    assert truth_integrity._HARD_TEST_MARKERS_RE.search("python3 -m pytest tests/x.py")


def test_real_weak_assertion_still_blocked(tmp_path: Path) -> None:
    """An integration row with NO hard command must still be flagged."""
    tests = """\
---
slug: demo-freeze-fix
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: beacon-feature-package-v1
---

# t

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | integration | run-thing | pass |
"""
    _build_pkg(tmp_path, tests_override=tests)
    findings = truth_integrity.scan_integrity_extension_lines(
        tmp_path, version="v1.6.3", feature="demo-freeze-fix"
    )
    soft = [f for f in findings if f.get("kind") == "soft_test_assertion"]
    assert len(soft) >= 1


# ---- AC-004 self-describing errors ----

def test_authority_table_error_self_describing(tmp_path: Path) -> None:
    """Missing authority table must mention allowed authorities + required columns."""
    no_table_evidence = """\
---
slug: demo-freeze-fix
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: beacon-feature-package-v1
---

# t

no table here
"""
    root = tmp_path
    pkg = root / "docs" / "beacon" / "v1.6.3" / "features" / "demo-freeze-fix"
    _write(pkg / "truth.md", _TRUTH_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tests.md", _TESTS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tasks.md", _TASKS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "evidence.md", no_table_evidence)
    result = validate_feature_package(root, version="v1.6.3", feature="demo-freeze-fix")
    diag = next(
        (d for d in result.get("diagnostics", []) if d.get("code") == "evidence_authority_table_missing"),
        None,
    )
    assert diag is not None
    blob = str(diag).lower()
    assert "allowed_authorities" in blob or "authority" in blob
    assert "surface" in blob


def test_invalid_authority_error_self_describing(tmp_path: Path) -> None:
    """Invalid authority must list allowed values."""
    bad_auth_evidence = """\
---
slug: demo-freeze-fix
version: v1.6.3
status: draft
language: zh
truth_ref: a
parser_contract: beacon-feature-package-v1
---

# t

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | bogus_authority | a |
"""
    root = tmp_path
    pkg = root / "docs" / "beacon" / "v1.6.3" / "features" / "demo-freeze-fix"
    _write(pkg / "truth.md", _TRUTH_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tests.md", _TESTS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "tasks.md", _TASKS_TMPL.format(slug="demo-freeze-fix", contract="beacon-feature-package-v1"))
    _write(pkg / "evidence.md", bad_auth_evidence)
    result = validate_feature_package(root, version="v1.6.3", feature="demo-freeze-fix")
    diag = next(
        (d for d in result.get("diagnostics", []) if str(d.get("code", "")).startswith("evidence_invalid_authority")),
        None,
    )
    assert diag is not None
    blob = str(diag).lower()
    assert "allowed_authorities" in blob


# ---- AC-005 / AC-006 backward compat & no regression ----

def test_v1_package_backward_compat(tmp_path: Path) -> None:
    """A well-formed v1 contract package passes validation cleanly."""
    _build_pkg(tmp_path, contract="beacon-feature-package-v1")
    result = validate_feature_package(tmp_path, version="v1.6.3", feature="demo-freeze-fix")
    assert _codes(result) == []


def test_p03_package_no_regression() -> None:
    """The frozen P0-3 package must still pass validation after these fixes."""
    project_root = Path(__file__).resolve().parents[1]
    result = validate_feature_package(
        project_root,
        version="v1.6.3",
        feature="beacon-gate-truth-model-alignment-v163",
    )
    assert _codes(result) == []
