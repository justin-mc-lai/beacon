"""Branch-governance contract projection and human-surface helpers."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from beacon.utils.git_alignment import git_output


BRANCH_GOVERNANCE_TOOL = "beacon-toolkit-branch-governance"
STANDARD_TEMPLATE = "standard-feature"
DUAL_VERSION_TEMPLATE = "previous-hotfix-forward-port"


def _string(value: Any) -> str:
    return str(value or "").strip()


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        text = _string(value)
        if text and text not in out:
            out.append(text)
    return out


def _evidence_map(values: Any) -> dict[str, str]:
    if isinstance(values, dict):
        return {
            _string(key): _string(value)
            for key, value in values.items()
            if _string(key)
        }
    evidence: dict[str, str] = {}
    if isinstance(values, list):
        for item in values:
            text = _string(item)
            if "=" not in text:
                continue
            key, raw_value = text.split("=", 1)
            key = _string(key)
            if key:
                evidence[key] = _string(raw_value)
    return evidence


def _hotfix_rule_matches(branch: str, rule: str) -> bool:
    normalized_branch = _string(branch)
    normalized_rule = _string(rule)
    if not normalized_branch or not normalized_rule:
        return False
    pattern = normalized_rule.replace("<ticket>", "*").replace("<version>", "*")
    return fnmatch.fnmatch(normalized_branch, pattern)


def _branch_governance_contract_from_sources(
    *,
    metadata_view: dict[str, Any] | None,
    git_workflow: dict[str, Any] | None,
    feature: str = "",
    version: str = "",
    project_root: Path | None = None,
) -> dict[str, Any]:
    metadata_view = metadata_view if isinstance(metadata_view, dict) else {}
    git_workflow = git_workflow if isinstance(git_workflow, dict) else {}
    version_contract = metadata_view.get("version_contract") if isinstance(metadata_view.get("version_contract"), dict) else {}
    selected_binding = metadata_view.get("selected_service_binding") if isinstance(metadata_view.get("selected_service_binding"), dict) else {}
    selected_service = _string(metadata_view.get("selected_service"))
    selected_branch = _string(metadata_view.get("selected_branch"))
    governance = version_contract.get("branch_governance") if isinstance(version_contract.get("branch_governance"), dict) else {}
    override = git_workflow.get("branch_governance_override") if isinstance(git_workflow.get("branch_governance_override"), dict) else {}
    template_name = (
        _string(override.get("template_name"))
        or _string(governance.get("template_name"))
        or _string(version_contract.get("branch_governance_template"))
        or STANDARD_TEMPLATE
    )
    template_source = "task_override" if override else ("project_metadata" if governance or version_contract.get("branch_governance_template") else "default")
    repo_root = _string(override.get("repo_root")) or _string(selected_binding.get("repo_root")) or _string(git_workflow.get("worktree_root")) or _string(project_root)
    target_branch = _string(git_workflow.get("expected_branch")) or selected_branch
    current_branch = git_output(Path(repo_root), "branch", "--show-current") if repo_root else ""
    current_worktree_path = _string(project_root) if project_root else repo_root
    worktree_path = (
        _string(override.get("worktree_path"))
        or _string(governance.get("worktree_path"))
        or _string(git_workflow.get("worktree_path"))
        or current_worktree_path
    )
    allow_worktree_when_feature_dirty = bool(
        override.get(
            "allow_worktree_when_feature_dirty",
            governance.get("allow_worktree_when_feature_dirty", version_contract.get("allow_worktree_when_feature_dirty", False)),
        )
    )
    merge_direction_policy = (
        _string_list(override.get("merge_direction_policy"))
        or _string_list(governance.get("merge_direction_policy"))
        or _string_list(version_contract.get("merge_direction_policy"))
    )
    forbidden_directions = (
        _string_list(override.get("forbidden_directions"))
        or _string_list(governance.get("forbidden_directions"))
        or _string_list(version_contract.get("forbidden_directions"))
    )
    evidence_contract = (
        _string_list(override.get("evidence_contract"))
        or _string_list(governance.get("evidence_contract"))
        or _string_list(version_contract.get("evidence_contract"))
    )
    evidence = (
        _evidence_map(override.get("evidence"))
        or _evidence_map(governance.get("evidence"))
        or _evidence_map(version_contract.get("evidence"))
    )
    if template_name == DUAL_VERSION_TEMPLATE:
        merge_direction_policy = merge_direction_policy or [
            "previous_baseline->hotfix",
            "hotfix->uat",
            "hotfix->next_feature",
        ]
        forbidden_directions = forbidden_directions or ["next_feature->first_production_fix"]
        evidence_contract = evidence_contract or [
            "source_commit",
            "forward_port_commit",
            "origin_uat_head",
            "pipeline_run_id",
        ]
    worktree_mode = (
        _string(override.get("worktree_mode"))
        or _string(governance.get("worktree_mode"))
        or ("dedicated-worktree" if bool(git_workflow.get("use_git_worktree")) or template_name == DUAL_VERSION_TEMPLATE else "branch-only")
    )
    return {
        "schema_version": "1.0",
        "tool_name": BRANCH_GOVERNANCE_TOOL,
        "feature": feature,
        "version": version,
        "template_name": template_name,
        "template_source": template_source,
        "service_key": selected_service,
        "repo_root": repo_root,
        "base_branch": _string(git_workflow.get("base_branch")) or selected_branch,
        "current_branch": current_branch,
        "target_branch": target_branch,
        "worktree_mode": worktree_mode,
        "worktree_path": worktree_path,
        "current_worktree_path": current_worktree_path,
        "previous_version_baseline_branch": (
            _string(override.get("previous_version_baseline_branch"))
            or _string(governance.get("previous_version_baseline_branch"))
            or _string(version_contract.get("previous_version_baseline_branch"))
        ),
        "next_version_feature_branch": (
            _string(override.get("next_version_feature_branch"))
            or _string(governance.get("next_version_feature_branch"))
            or _string(version_contract.get("next_version_feature_branch"))
        ),
        "hotfix_branch_naming_rule": (
            _string(override.get("hotfix_branch_naming_rule"))
            or _string(governance.get("hotfix_branch_naming_rule"))
            or _string(version_contract.get("hotfix_branch_naming_rule"))
        ),
        "allow_worktree_when_feature_dirty": allow_worktree_when_feature_dirty,
        "merge_direction_policy": merge_direction_policy,
        "forbidden_directions": forbidden_directions,
        "evidence_contract": evidence_contract,
        "evidence": evidence,
    }


def evaluate_branch_governance(contract: dict[str, Any]) -> dict[str, Any]:
    payload = dict(contract)
    template_name = _string(payload.get("template_name")) or STANDARD_TEMPLATE
    if template_name == DUAL_VERSION_TEMPLATE:
        payload["merge_direction_policy"] = _string_list(payload.get("merge_direction_policy")) or [
            "previous_baseline->hotfix",
            "hotfix->uat",
            "hotfix->next_feature",
        ]
        payload["forbidden_directions"] = _string_list(payload.get("forbidden_directions")) or [
            "next_feature->first_production_fix"
        ]
        payload["evidence_contract"] = _string_list(payload.get("evidence_contract")) or [
            "source_commit",
            "forward_port_commit",
            "origin_uat_head",
            "pipeline_run_id",
        ]
    target_branch = _string(payload.get("target_branch"))
    current_worktree_path = _string(payload.get("current_worktree_path"))
    worktree_path = _string(payload.get("worktree_path"))
    previous_baseline = _string(payload.get("previous_version_baseline_branch"))
    next_feature = _string(payload.get("next_version_feature_branch"))
    hotfix_rule = _string(payload.get("hotfix_branch_naming_rule"))
    evidence_contract = _string_list(payload.get("evidence_contract"))
    evidence = _evidence_map(payload.get("evidence"))
    blocked = False
    reason_codes: list[str] = []
    blocked_reason = ""
    recommended_action = ""
    missing_evidence = [field for field in evidence_contract if not _string(evidence.get(field))]

    if template_name == DUAL_VERSION_TEMPLATE:
        if not previous_baseline or not next_feature or not hotfix_rule:
            blocked = True
            reason_codes.append("branch_governance_template_incomplete")
            blocked_reason = "dual-version template is missing previous baseline, next feature, or hotfix naming rule"
            recommended_action = "fill the missing branch-governance template fields in project metadata"
        elif target_branch == next_feature:
            blocked = True
            reason_codes.append("branch_governance_forbidden_first_fix_lane")
            blocked_reason = "next-version feature branch cannot be the first production-fix lane"
            recommended_action = "switch implement target to a compliant hotfix branch first"
        elif target_branch and not _hotfix_rule_matches(target_branch, hotfix_rule):
            blocked = True
            reason_codes.append("branch_governance_hotfix_target_invalid")
            blocked_reason = "target branch does not satisfy the hotfix naming rule for the dual-version template"
            recommended_action = "create or switch to a compliant hotfix branch before implementation"

    if worktree_path and current_worktree_path and worktree_path != current_worktree_path and _string(payload.get("worktree_mode")) == "dedicated-worktree":
        blocked = True
        reason_codes.append("branch_governance_worktree_required")
        blocked_reason = blocked_reason or "governance requires a dedicated worktree lane before implementation"
        recommended_action = recommended_action or f"enter the governed worktree at {worktree_path}"

    if missing_evidence:
        blocked = True
        reason_codes.append("branch_governance_evidence_missing")
        blocked_reason = blocked_reason or ("required evidence is missing: " + ", ".join(missing_evidence))
        recommended_action = recommended_action or "record the missing workflow evidence before implementation"

    evidence_status = "pass" if not missing_evidence else "blocked"
    payload.update(
        {
            "status": "blocked" if blocked else "pass",
            "blocked": blocked,
            "reason_codes": reason_codes,
            "blocked_reason": blocked_reason,
            "recommended_action": recommended_action,
            "missing_evidence_fields": missing_evidence,
            "evidence_contract_status": evidence_status,
        }
    )
    return payload


def render_branch_governance_markdown(contract: dict[str, Any]) -> str:
    payload = evaluate_branch_governance(contract)
    template_name = _string(payload.get("template_name")) or STANDARD_TEMPLATE
    current_branch = _string(payload.get("current_branch"))
    target_branch = _string(payload.get("target_branch"))

    def mark(label: str, branch: str) -> str:
        return f"{label} [current]" if branch and branch == current_branch else label

    lines = [
        "## Branch Governance",
        "",
        f"- toolkit: `{BRANCH_GOVERNANCE_TOOL}`",
        f"- template_name: `{template_name}`",
        f"- template_source: `{payload.get('template_source', '')}`",
        f"- service_key: `{payload.get('service_key', '')}`",
        f"- repo_root: `{payload.get('repo_root', '')}`",
        f"- base_branch: `{payload.get('base_branch', '')}`",
        f"- current_branch: `{current_branch}`",
        f"- target_branch: `{target_branch}`",
        f"- worktree_mode: `{payload.get('worktree_mode', '')}`",
        f"- worktree_path: `{payload.get('worktree_path', '')}`",
        f"- evidence_contract_status: `{payload.get('evidence_contract_status', '')}`",
        f"- blocked_reason: `{payload.get('blocked_reason', '')}`",
        f"- recommended_action: `{payload.get('recommended_action', '')}`",
        "",
        "### Flow Diagram",
        "```text",
    ]
    if template_name == DUAL_VERSION_TEMPLATE:
        previous = _string(payload.get("previous_version_baseline_branch")) or "previous_version_baseline"
        hotfix = target_branch or _string(payload.get("hotfix_branch_naming_rule")) or "hotfix/<ticket>-<version>"
        uat = "uat"
        next_feature = _string(payload.get("next_version_feature_branch")) or "next_version_feature_branch"
        lines.extend(
            [
                f"{mark(previous, previous)}",
                f"    -> {mark(hotfix, hotfix)}",
                f"    -> {mark(uat, uat)}",
                "    -> forward-port",
                f"    -> {mark(next_feature, next_feature)}",
                "",
                f"{next_feature} -X-> first_production_fix",
            ]
        )
    else:
        base_branch = _string(payload.get("base_branch")) or "base_branch"
        lines.extend(
            [
                f"{mark(base_branch, base_branch)}",
                f"    -> {mark(target_branch or 'feature_branch', target_branch or 'feature_branch')}",
                "    -> uat",
            ]
        )
    lines.extend(
        [
            "```",
            "",
            "### Allowed Paths",
        ]
    )
    allowed = _string_list(payload.get("merge_direction_policy"))
    if allowed:
        lines.extend(f"- `{item}`" for item in allowed)
    else:
        lines.append("- `base_branch->feature_branch`")
    lines.extend(["", "### Forbidden Paths"])
    forbidden = _string_list(payload.get("forbidden_directions"))
    if forbidden:
        lines.extend(f"- `{item}`" for item in forbidden)
    else:
        lines.append("- none")
    lines.extend(["", "### Evidence Contract"])
    evidence_contract = _string_list(payload.get("evidence_contract"))
    if evidence_contract:
        lines.extend(f"- `{item}`" for item in evidence_contract)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def resolve_branch_governance_view(
    *,
    project_root: Path,
    version: str,
    feature: str = "",
    metadata_view: dict[str, Any] | None = None,
    git_workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = _branch_governance_contract_from_sources(
        metadata_view=metadata_view,
        git_workflow=git_workflow,
        feature=feature,
        version=version,
        project_root=project_root,
    )
    evaluated = evaluate_branch_governance(contract)
    return {
        **evaluated,
        "human_markdown": render_branch_governance_markdown(contract),
    }
