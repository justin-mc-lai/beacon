"""Post-write gates after gen-truth / materialize (v1.6.10+).

HARD:
1. resolve_humanizer_profile — require oss-sync fulltext when require_on_truth_write
2. run truth review (A/B/C + D fill-depth + domain exec) — fail ⇒ do not recommend freeze
3. After A/B/C pass: apply Humanizer L0 writeback (preserve_machine_fields)
4. Scaffold packages stay draft — next step is truth-review fill, not freeze
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.humanizer_config import apply_humanizer_l0_to_path, resolve_humanizer_profile
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_review_gate import run_truth_review_gate, truth_review_gate_supported
from beacon.utils.versioning import normalize_version, resolve_target_version


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def run_truth_gen_postwrite_gates(
    project_root: Path,
    *,
    version: str,
    feature: str,
    written: list[str] | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """Run humanizer resolve + truth review + optional L0 apply after package write."""
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = feature_slug(feature)

    lang = language
    if not lang:
        truth_path = root / "docs" / "beacon" / resolved / "features" / slug / "truth.md"
        if truth_path.is_file():
            head = truth_path.read_text(encoding="utf-8")[:400]
            if "language: en" in head:
                lang = "en"
            elif "language: bilingual" in head:
                lang = "zh"
            else:
                lang = "zh"
        else:
            lang = "zh"

    humanizer = resolve_humanizer_profile(root, language=lang)
    review = run_truth_review_gate(
        root,
        version=resolved,
        feature=slug,
        write_report=True,
    )
    review_pass = bool(review.get("pass") or review.get("review_gate_pass"))
    abc_pass = bool(review.get("abc_pass"))
    if not abc_pass:
        # older reports may lack abc_pass — derive from checks
        checks = review.get("checks") if isinstance(review.get("checks"), dict) else {}
        a = checks.get("A_intent_coverage") or {}
        b = checks.get("B_fsm_audit") or {}
        c = checks.get("C_testability") or {}
        if checks:
            abc_pass = all(bool(x.get("pass")) for x in (a, b, c))
        else:
            abc_pass = review_pass

    humanizer_apply: dict[str, Any] = {"applied": False, "skipped": True, "reason": "abc_not_pass"}
    if abc_pass and bool(humanizer.get("ok")):
        humanizer_apply = apply_humanizer_l0_to_path(
            root,
            version=resolved,
            feature=slug,
            profile=humanizer,
            language=lang,
        )
        # Re-run review after L0 writeback so report matches disk
        review = run_truth_review_gate(
            root,
            version=resolved,
            feature=slug,
            write_report=True,
        )
        review_pass = bool(review.get("pass") or review.get("review_gate_pass"))
        abc_pass = bool(review.get("abc_pass", abc_pass))

    humanizer_ok = bool(humanizer.get("ok"))
    humanizer_blocked = bool(humanizer.get("blocked"))
    blocked = (not review_pass) or humanizer_blocked
    # Freeze only when full review (incl D fill + exec) passes
    recommend_freeze = review_pass and humanizer_ok and not humanizer_blocked

    reason_codes: list[str] = []
    if not review_pass:
        reason_codes.append(str(review.get("reason_code") or "truth_review_gate_failed"))
    if humanizer_blocked:
        reason_codes.append(str(humanizer.get("reason_code") or "humanizer_skill_path_missing"))

    next_steps: list[str]
    if recommend_freeze:
        next_steps = ["beacon freeze"]
    elif not review_pass and str(review.get("reason_code") or "") in {
        "truth_scaffold_not_filled",
        "domain_exec_tc_missing",
    }:
        next_steps = [
            "fill Matrix/FSM/用户旅程 (set package_maturity=filled)",
            "add domain exec-layer TC if business domain",
            "beacon truth review",
            "do not freeze until review_gate_pass",
        ]
    else:
        next_steps = ["fix truth per findings", "beacon truth review", "do not freeze until review_gate_pass"]

    return {
        "schema": "truth-gen-postwrite.v1",
        "version": resolved,
        "feature": slug,
        "written": list(written or []),
        "humanizer": {
            "ok": humanizer_ok,
            "blocked": humanizer_blocked,
            "language": humanizer.get("language"),
            "skill_path": humanizer.get("skill_path"),
            "skill_exists": humanizer.get("skill_exists"),
            "skill_chars": humanizer.get("skill_chars"),
            "reason_code": humanizer.get("reason_code") or "",
            "require_on_truth_write": humanizer.get("require_on_truth_write"),
            "fulltext_loaded": bool(humanizer.get("skill_exists") and int(humanizer.get("skill_chars") or 0) > 0),
            "apply": humanizer_apply,
        },
        "truth_review_gate": {
            "pass": review_pass,
            "review_gate_pass": review_pass,
            "abc_pass": abc_pass,
            "reason_code": review.get("reason_code") or "",
            "report_path": review.get("report_path") or (review.get("paths") or {}).get("report"),
            "findings": (review.get("findings") or [])[:20],
            "checks": review.get("checks") or {},
        },
        "blocked": blocked,
        "recommend_freeze": recommend_freeze,
        "reason_codes": reason_codes,
        "workflow": {
            "scaffold_is_draft_only": True,
            "required_before_freeze": [
                "truth-review fill (Matrix/FSM/旅程)",
                "package_maturity=filled",
                "review_gate_pass",
            ],
            "mode_id": "truth-review",
        },
        "next_steps": next_steps,
    }
