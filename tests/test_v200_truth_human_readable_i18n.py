from pathlib import Path

from beacon.utils.truth_human_readable import check_truth_file, norms_paths

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/truth.md"
UP = ROOT / "docs/beacon/v1.6.7/features/beacon-truth-human-readable-i18n-v167/truth.md"


def test_self_l0():
    r = check_truth_file(TRUTH)
    assert r["ok"] is True, r


def test_parity_upstream_ac():
    up = UP.read_text(encoding="utf-8")
    assert "AC-HR-001" in up
    assert "UD-HR-001" in up


def test_shared_norms():
    n = norms_paths(ROOT)
    assert n["zh"].is_file() and n["en"].is_file()


def test_axis_has_lake():
    axis = ROOT / "docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/goalrun-main-axis.md"
    assert "beacon-v2-truth-human-readable-i18n" in axis.read_text(encoding="utf-8")


def test_reason_code_stable():
    from beacon.utils.truth_human_readable import REASON_L0_MISSING

    assert REASON_L0_MISSING == "truth_human_l0_missing"
