"""Implementation evidence classification helpers."""

from __future__ import annotations

from typing import Any


STATIC_SHELL_TOKENS = {
    "coming_soon",
    "coming soon",
    "preview_only",
    "preview-only",
    "static_shell",
    "static shell",
    "unready",
    "disabled",
    "no-op",
    "noop",
    "recovery_navigate_only",
}

SOURCE_ASSERTION_TOKENS = {
    "source_grep_only",
    "source-grep-only",
    "readfilesync",
    ".tocontain",
    "toContain",
    "grep",
    "route name",
    "exported constant",
}

NON_BEHAVIOR_TOKENS = {
    "dry_run",
    "dry-run",
    "simulated_runner",
    "simulated runner",
    "skipped",
    "no_assertion",
    "no-assertion",
    "no_artifact",
    "no-artifact",
}

BEHAVIOR_PROOF_TOKENS = {
    "browser_trace",
    "browser trace",
    "screenshot",
    "dom_interaction",
    "dom interaction",
    "state_transition",
    "state transition",
    "canvas",
    "pixel",
    "playwright",
    "e2e",
    "runtime_behavior",
    "runtime behaviour",
    "user_behavior",
    "user behaviour",
}


def _flatten_text(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for key, nested in value.items():
            out.append(str(key))
            out.extend(_flatten_text(nested))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(_flatten_text(item))
        return out
    if value is None:
        return []
    return [str(value)]


def _contains_any(text: str, tokens: set[str]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def classify_behavior_evidence(evidence: Any) -> dict[str, Any]:
    """Classify whether an evidence candidate can satisfy behavior acceptance."""
    text_values = _flatten_text(evidence)
    combined = "\n".join(text_values)
    if not combined.strip():
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "classification": "no_candidate",
        }

    if _contains_any(combined, STATIC_SHELL_TOKENS):
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "static_shell_implementation_evidence",
            "classification": "non_behavior_evidence",
        }

    has_source_assertion = _contains_any(combined, SOURCE_ASSERTION_TOKENS)
    has_behavior_proof = _contains_any(combined, BEHAVIOR_PROOF_TOKENS)
    if has_source_assertion and not has_behavior_proof:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "static_source_assertion_only",
            "classification": "non_behavior_evidence",
        }

    if _contains_any(combined, NON_BEHAVIOR_TOKENS):
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "non_behavior_implementation_evidence",
            "classification": "non_behavior_evidence",
        }

    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "classification": "behavior_evidence_candidate",
    }


def implementation_evidence_gate(result_payload: dict[str, Any]) -> dict[str, Any]:
    """Validate implementation result evidence before delivery writeback."""
    if not isinstance(result_payload, dict):
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": "implementation_evidence_invalid",
            "classification": "invalid_payload",
        }

    candidates: list[Any] = []
    for key in (
        "implementation_evidence",
        "acceptance_evidence",
        "behavior_evidence",
        "qa_evidence",
        "evidence",
        "verification",
    ):
        value = result_payload.get(key)
        if value not in (None, "", [], {}):
            candidates.append(value)
    if not candidates:
        return {
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "reason_code": "",
            "classification": "no_candidate",
            "checked_candidates": 0,
        }

    results = [classify_behavior_evidence(candidate) for candidate in candidates]
    for result in results:
        if result.get("blocked"):
            return {
                **result,
                "checked_candidates": len(candidates),
                "candidate_results": results,
            }
    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "classification": "behavior_evidence_candidate",
        "checked_candidates": len(candidates),
        "candidate_results": results,
    }
