"""v2.0.0 Loom brand surface tests."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.loom_brand import (
    dual_install_names_ok,
    dual_matrix_checklist,
    docs_forbid_early_default,
    install_must_not_overwrite_beacon,
    legal_illegal_rows,
    naming_contract,
    public_entry_contract,
    state_roots,
)

ROOT = Path(__file__).resolve().parents[1]


def test_naming_contract() -> None:
    c = naming_contract()
    assert c["pip"] == "loom"
    assert c["cli"] == "loom"
    assert c["cli_rust_canonical"] == "beacon-v2"
    assert c["python_escape_cli"] == "loom-py"
    assert c["backend"] == "rust"
    assert c["public_skill"] == "loom-goal"
    assert c["default_replace_beacon"] is False


def test_dual_install_names() -> None:
    r = dual_install_names_ok()
    assert r["ok"] is True
    assert r["cli"] != r["beacon_cli"]


def test_no_replace_beacon() -> None:
    ok = install_must_not_overwrite_beacon(install_writes=["/usr/local/bin/loom"])
    assert ok["ok"] is True
    bad = install_must_not_overwrite_beacon(install_writes=["/usr/local/bin/beacon"])
    assert bad["ok"] is False
    assert bad["blocked"] is True


def test_loom_goal_facade() -> None:
    c = public_entry_contract()
    assert c["public_primary"] == "loom-goal"
    assert c["single_entry"] is True
    skill = ROOT / "skills/loom/loom-goal/SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert "loom-goal" in text
    assert "beacon-goal" in text


def test_beacon_preserved() -> None:
    assert (ROOT / "skills/beacon/beacon-goal/SKILL.md").exists()
    c = naming_contract()
    assert c["beacon_public_skill"] == "beacon-goal"


def test_state_isolation() -> None:
    r = state_roots(ROOT)
    assert r["isolated"] is True
    assert ".loom" in r["loom_project"]
    assert ".beacon" in r["beacon_project"]


def test_dual_matrix_doc() -> None:
    matrix = dual_matrix_checklist()
    assert len(matrix["rows"]) >= 4
    path = ROOT / "docs/beacon/v2.0.0/fixtures/parity-v167/dual-install-matrix.md"
    assert path.exists()
    assert "beacon" in path.read_text(encoding="utf-8").lower()


def test_examples() -> None:
    ex = ROOT / "skills/loom/examples/goal-one-shot-30s.md"
    assert ex.exists()
    text = ex.read_text(encoding="utf-8")
    assert "loom" in text.lower() and "beacon" in text.lower()


def test_no_early_default() -> None:
    paths = [
        ROOT / "skills/loom/loom-goal/SKILL.md",
        ROOT / "skills/loom/examples/goal-one-shot-30s.md",
        ROOT / "docs/beacon/v2.0.0/features/loom-brand-surface/truth.md",
    ]
    r = docs_forbid_early_default(paths)
    assert r["status"] == "pass", r["violations"]


def test_legal_illegal_rows() -> None:
    rows = legal_illegal_rows()
    assert rows["legal"]
    assert rows["illegal"]
    assert any("I-LOOM-BR-001" in (i.get("code") or "") for i in rows["illegal"])


def test_pyproject_no_loom_console_script() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'loom = "loom.main:app"' not in text
    assert 'loom-py = "loom.main:app"' in text
    assert 'beacon = "beacon.main:app"' in text


def test_install_loom_cli_script_exists() -> None:
    p = ROOT / "scripts/install-loom-cli.sh"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "beacon-v2" in text
    assert "production" in text.lower() or "unchanged" in text.lower() or "not modified" in text.lower()


def test_install_loom_skills_script_exists() -> None:
    p = ROOT / "scripts/install-loom-skills.sh"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "skills/loom" in text
