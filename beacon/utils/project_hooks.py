"""Project-level lifecycle hook contracts and runtime evidence."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import generate_run_id, now_iso, write_json
from beacon.utils.skill_config import SkillConfigError, _Parser

ALLOWED_HOOK_CODES = {
    "post_implement_pre_qa",
    "qa_diagnostics",
    "post_qa_pre_release",
    "post_release",
}

ALLOWED_TRIGGER_POLICIES = {
    "dry_run_only",
    "manual_confirmed",
    "auto_allowed",
}

ALLOWED_FAILURE_ROUTES = {
    "implement",
    "qa",
    "release",
    "change",
    "blocked",
}

AUTHORITY_BOUNDARY_KEYWORDS = {
    "prd truth",
    "user-story truth",
    "test-case truth",
    "qa verdict",
    "release verdict",
    "gate verdict",
    "freeze state",
    "requirement truth",
}


def hooks_root(project_root: Path) -> Path:
    return project_root / "docs" / "beacon" / "hooks"


def hook_path(project_root: Path, hook_id: str) -> Path:
    return hooks_root(project_root) / f"{hook_id}.md"


def hook_state_dir(project_root: Path, hook_id: str) -> Path:
    return project_root / ".beacon" / "state" / "hooks" / hook_id


def hook_latest_read_model_path(project_root: Path, hook_id: str) -> Path:
    return project_root / "docs" / "beacon" / ".machine" / "hooks" / f"{hook_id}.latest.json"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    if not text.startswith("---\n"):
        return {}, text, ["frontmatter_missing"]
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text, ["frontmatter_unclosed"]
    raw = text[4:end].strip("\n")
    body = text[text.find("\n", end + 1) + 1 :]
    try:
        data = _Parser(raw.splitlines()).parse()
    except SkillConfigError:
        return {}, body, ["frontmatter_parse_failed"]
    return data, body, []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def load_hook_contract(project_root: Path, hook_id: str) -> dict[str, Any]:
    path = hook_path(project_root, hook_id)
    if not path.exists():
        return {
            "hook_id": hook_id,
            "path": str(path.relative_to(project_root)),
            "exists": False,
            "frontmatter": {},
            "body": "",
            "parse_errors": ["hook_file_missing"],
        }
    text = path.read_text(encoding="utf-8")
    frontmatter, body, parse_errors = _parse_frontmatter(text)
    return {
        "hook_id": str(frontmatter.get("hook_id") or hook_id),
        "path": str(path.relative_to(project_root)),
        "exists": True,
        "frontmatter": frontmatter,
        "body": body,
        "parse_errors": parse_errors,
    }


def list_hook_contracts(project_root: Path) -> list[dict[str, Any]]:
    root = hooks_root(project_root)
    if not root.exists():
        return []
    hooks: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.md")):
        hooks.append(load_hook_contract(project_root, path.stem))
    return hooks


def _body_has_required_sections(body: str) -> list[str]:
    lower = body.lower()
    missing: list[str] = []
    for section in ("purpose", "admission", "evidence", "failure"):
        if f"## {section}" not in lower and f"### {section}" not in lower:
            missing.append(section)
    return missing


def _authority_boundary_issues(body: str, frontmatter: dict[str, Any]) -> list[str]:
    text = f"{body}\n{frontmatter.get('authority', '')}\n{frontmatter.get('authority_boundary', '')}".lower()
    issues: list[str] = []
    for keyword in AUTHORITY_BOUNDARY_KEYWORDS:
        if re.search(rf"\b(can|may|will|writes?|rewrites?|sets?|passes?)\b[^.\n]*{re.escape(keyword)}", text):
            issues.append("hook_authority_bypass")
            break
    return issues


def validate_hook_contract(project_root: Path, hook_id: str, *, feature: str = "", hook_code: str = "") -> dict[str, Any]:
    contract = load_hook_contract(project_root, hook_id)
    frontmatter = contract["frontmatter"]
    diagnostics: list[dict[str, str]] = []

    for reason in contract["parse_errors"]:
        diagnostics.append({"reason_code": reason, "message": reason})

    path_hook_id = Path(contract["path"]).stem
    declared_hook_id = str(frontmatter.get("hook_id") or "").strip()
    if declared_hook_id != path_hook_id:
        diagnostics.append({"reason_code": "hook_id_mismatch", "message": "hook_id must match file name"})

    declared_code = str(frontmatter.get("hook_code") or "").strip()
    if declared_code not in ALLOWED_HOOK_CODES:
        diagnostics.append({"reason_code": "unknown_hook_code", "message": "hook_code is not allowed"})
    if hook_code and declared_code != hook_code:
        diagnostics.append({"reason_code": "hook_code_mismatch", "message": "hook_code does not match requested boundary"})

    if frontmatter.get("enabled") is not True:
        diagnostics.append({"reason_code": "hook_disabled", "message": "hook is disabled or missing enabled: true"})

    trigger_policy = str(frontmatter.get("trigger_policy") or "").strip()
    if trigger_policy not in ALLOWED_TRIGGER_POLICIES:
        diagnostics.append({"reason_code": "invalid_trigger_policy", "message": "trigger_policy is not allowed"})

    failure_route = str(frontmatter.get("failure_route") or "").strip()
    if failure_route not in ALLOWED_FAILURE_ROUTES:
        diagnostics.append({"reason_code": "invalid_failure_route", "message": "failure_route is not allowed"})

    skill = str(frontmatter.get("skill") or "").strip()
    command_template = str(frontmatter.get("command_template") or "").strip()
    if not skill and not command_template:
        diagnostics.append({"reason_code": "hook_invocation_missing", "message": "skill or command_template is required"})

    produces_evidence = _string_list(frontmatter.get("produces_evidence"))
    if not produces_evidence:
        diagnostics.append({"reason_code": "required_evidence_missing", "message": "produces_evidence is required"})

    feature_pattern = str(frontmatter.get("feature_pattern") or "").strip()
    if feature and feature_pattern and feature_pattern not in {"*", feature} and feature_pattern not in feature:
        diagnostics.append({"reason_code": "feature_selector_mismatch", "message": "hook does not apply to this feature"})

    for section in _body_has_required_sections(str(contract.get("body") or "")):
        diagnostics.append({"reason_code": f"section_missing_{section}", "message": f"missing body section: {section}"})

    for reason in _authority_boundary_issues(str(contract.get("body") or ""), frontmatter):
        diagnostics.append({"reason_code": reason, "message": "hook cannot claim lifecycle truth authority"})

    status = "pass" if not diagnostics else "blocked"
    return {
        "schema_version": "1.0",
        "hook_id": hook_id,
        "hook_code": declared_code,
        "feature": feature,
        "path": contract["path"],
        "status": status,
        "blocked": bool(diagnostics),
        "reason_codes": [item["reason_code"] for item in diagnostics],
        "diagnostics": diagnostics,
        "contract": {
            "hook_id": declared_hook_id,
            "hook_code": declared_code,
            "enabled": bool(frontmatter.get("enabled")),
            "trigger_policy": trigger_policy,
            "skill": skill,
            "command_template": command_template,
            "produces_evidence": produces_evidence,
            "failure_route": failure_route,
        },
    }


def plan_hook(project_root: Path, hook_id: str, *, version: str = "", feature: str = "", hook_code: str = "") -> dict[str, Any]:
    admission = validate_hook_contract(project_root, hook_id, feature=feature, hook_code=hook_code)
    return {
        "schema_version": "1.0",
        "action": "plan",
        "hook_id": hook_id,
        "version": version,
        "feature": feature,
        "status": "planned" if not admission["blocked"] else "blocked",
        "blocked": bool(admission["blocked"]),
        "admission": admission,
        "evidence_policy": "runtime_evidence_only",
        "truth_authority": False,
        "evidence_paths": {
            "runtime_root": str(hook_state_dir(project_root, hook_id).relative_to(project_root)),
            "latest_read_model": str(hook_latest_read_model_path(project_root, hook_id).relative_to(project_root)),
        },
    }


def run_hook(
    project_root: Path,
    hook_id: str,
    *,
    version: str = "",
    feature: str = "",
    hook_code: str = "",
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    plan = plan_hook(project_root, hook_id, version=version, feature=feature, hook_code=hook_code)
    run_id = generate_run_id(project_root)
    payload = {
        "schema_version": "1.0",
        "action": "run",
        "run_id": run_id,
        "hook_id": hook_id,
        "version": version,
        "feature": feature,
        "dry_run": dry_run,
        "confirmed": confirm,
        "status": "planned" if dry_run else "passed",
        "blocked": False,
        "reason_code": "",
        "plan": plan,
        "side_effect_executed": False,
        "runtime_evidence_only": True,
        "truth_authority": False,
        "written_at": now_iso(),
    }
    if plan["blocked"]:
        payload.update({"status": "blocked", "blocked": True, "reason_code": "hook_admission_blocked"})
    else:
        trigger_policy = str(plan["admission"]["contract"]["trigger_policy"])
        if dry_run:
            payload["status"] = "planned"
        elif trigger_policy == "dry_run_only":
            payload.update({"status": "blocked", "blocked": True, "reason_code": "hook_dry_run_only"})
        elif trigger_policy == "manual_confirmed" and not confirm:
            payload.update({"status": "blocked", "blocked": True, "reason_code": "manual_confirmation_required"})
        elif not confirm:
            payload.update({"status": "blocked", "blocked": True, "reason_code": "hidden_auto_run_not_allowed"})
        else:
            payload["side_effect_executed"] = True

    runtime_path = hook_state_dir(project_root, hook_id) / f"{run_id}.json"
    latest_path = hook_latest_read_model_path(project_root, hook_id)
    payload["evidence_paths"] = {
        "runtime": str(runtime_path.relative_to(project_root)),
        "latest_read_model": str(latest_path.relative_to(project_root)),
    }
    write_json(runtime_path, payload)
    write_json(latest_path, payload)
    return payload


def disable_hook(project_root: Path, hook_id: str) -> dict[str, Any]:
    path = hook_path(project_root, hook_id)
    if not path.exists():
        return {"schema_version": "1.0", "hook_id": hook_id, "status": "blocked", "reason_code": "hook_file_missing"}
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?m)^enabled:\s*(true|false)\s*$", text):
        updated = re.sub(r"(?m)^enabled:\s*(true|false)\s*$", "enabled: false", text, count=1)
    elif text.startswith("---\n"):
        updated = text.replace("---\n", "---\nenabled: false\n", 1)
    else:
        updated = f"---\nhook_id: {hook_id}\nenabled: false\n---\n\n{text}"
    path.write_text(updated, encoding="utf-8")
    return {"schema_version": "1.0", "hook_id": hook_id, "status": "disabled", "path": str(path.relative_to(project_root))}


def hook_status(project_root: Path, hook_id: str, *, feature: str = "") -> dict[str, Any]:
    admission = validate_hook_contract(project_root, hook_id, feature=feature)
    latest_path = hook_latest_read_model_path(project_root, hook_id)
    latest = {}
    if latest_path.exists():
        from beacon.utils.runtime import read_json

        latest = read_json(latest_path, {})
    return {
        "schema_version": "1.0",
        "hook_id": hook_id,
        "feature": feature,
        "status": "ready" if not admission["blocked"] else "blocked",
        "blocked": bool(admission["blocked"]),
        "admission": admission,
        "latest_run": latest if isinstance(latest, dict) else {},
        "truth_authority": False,
    }
