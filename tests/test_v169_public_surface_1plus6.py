"""Contract tests: Scheme A public surface 1+6 synonym table (v1.6.9 \\ v2.0.0)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "skills/beacon/references/public-surface-1plus6.md"
HARNESS_RS = ROOT / "packages/beacon-rs/beacon-core/src/harness.rs"
V169 = ROOT / "docs/beacon/v1.6.9/features/beacon-public-surface-1plus6-v169/truth.md"
V200 = ROOT / "docs/beacon/v2.0.0/features/loom-public-surface-1plus6-v200/truth.md"

# Stable public id -> Rust PUBLIC_ABILITIES id (Scheme A synonym table)
EXPECTED_MAP = {
    "plan": "loop",
    "truth": "truth",
    "design": "design",
    "implement": "implement",
    "qa": "qa-evidence",
    "release": "release",
}


def _public_abilities_from_rs(text: str) -> list[str]:
    m = re.search(r"PUBLIC_ABILITIES:\s*\[&str;\s*6\]\s*=\s*\[(.*?)\];", text, re.S)
    assert m, "PUBLIC_ABILITIES block not found"
    return re.findall(r'"([^"]+)"', m.group(1))


def test_ac_ps_001_table_exists_six_harness() -> None:
    assert TABLE.is_file()
    text = TABLE.read_text(encoding="utf-8")
    assert "Scheme A" in text or "goal" in text.lower()
    for hid in EXPECTED_MAP:
        assert hid in text, f"missing harness id {hid}"
    # goal transversal section
    assert "transversal" in text.lower() or "横切" in text or "Long-run facade" in text


def test_ac_ps_002_rust_map() -> None:
    abilities = _public_abilities_from_rs(HARNESS_RS.read_text(encoding="utf-8"))
    assert len(abilities) == 6
    assert abilities == list(EXPECTED_MAP.values())


def test_ac_ps_003_goal_not_in_public_abilities() -> None:
    abilities = _public_abilities_from_rs(HARNESS_RS.read_text(encoding="utf-8"))
    assert "goal" not in abilities
    table = TABLE.read_text(encoding="utf-8")
    assert "not counted" in table.lower() or "不计入" in table or "not a 7th" in table.lower() or "not counted in the six" in table.lower()


def test_ac_ps_004_dual_package_parity() -> None:
    assert V169.is_file() and V200.is_file()
    t169 = V169.read_text(encoding="utf-8")
    t200 = V200.read_text(encoding="utf-8")
    assert "public-surface-1plus6.md" in t169
    assert "public-surface-1plus6.md" in t200
    assert "status: frozen" in t169
    assert "status: frozen" in t200
    # brand columns differ
    assert "beacon-goal" in t169 or "beacon-goal" in TABLE.read_text(encoding="utf-8")
    assert "loom-goal" in t200 or "loom-goal" in TABLE.read_text(encoding="utf-8")


def test_ac_ps_005_denylist_not_public() -> None:
    text = HARNESS_RS.read_text(encoding="utf-8")
    abilities = set(_public_abilities_from_rs(text))
    for name in ("doctor", "router", "hooks", "gov", "status", "archive"):
        assert name not in abilities


def test_ac_ps_006_whitelist_documented() -> None:
    text = TABLE.read_text(encoding="utf-8")
    assert "host-visible" in text.lower() or "Host-visible" in text or "whitelist" in text.lower()
    assert "beacon-goal" in text and "loom-goal" in text
    for brand_prefix in ("beacon-", "loom-"):
        for hid in ("plan", "truth", "design", "implement", "qa", "release"):
            assert f"{brand_prefix}{hid}" in text


def test_ac_ps_007_exactly_six_in_code_and_table() -> None:
    abilities = _public_abilities_from_rs(HARNESS_RS.read_text(encoding="utf-8"))
    assert len(abilities) == 6
    # table should forbid seventh
    text = TABLE.read_text(encoding="utf-8")
    assert "Seventh" in text or "第七" in text or "seventh" in text.lower()


def test_ac_ps_008_install_and_governance_refs() -> None:
    assert (ROOT / "scripts/install-loom-cli.sh").is_file()
    assert (ROOT / "docs/beacon/v2.0.0/execution/loom-rust-cli-path-governance.md").is_file()
    gov = (ROOT / "docs/beacon/v2.0.0/execution/loom-rust-cli-path-governance.md").read_text(encoding="utf-8")
    assert "Rust" in gov and "beacon" in gov.lower()


def test_scheme_a_pipeline_in_table() -> None:
    text = TABLE.read_text(encoding="utf-8")
    assert "plan" in text and "truth" in text and "implement" in text
    assert "qa" in text and "release" in text
