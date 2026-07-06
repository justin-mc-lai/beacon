"""Version-scoped workspace git admission (v1.6.2+)."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.git_alignment import ensure_expected_worktree_lane, git_output
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug

SCHEMA_VERSION = "workspace-admission-v1"

GIT_ADMISSION_PREAMBLE = """## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch
5. When admission is soft-skipped (`require_workspace_admission=false`), still verify `current_branch == resolved target_branch` before repo writes (R5 UD-024)
"""

TIER_A_SKILLS = frozenset(
    {
        "beacon-gen-implement",
        "beacon-gen-change",
        "beacon-gen-truth",
        "beacon-eval-qa",
        "beacon-eval-release",
        "beacon-gov-branch",
    }
)

TIER_B_SKILLS = frozenset(
    {
        "beacon-gov-router",
        "beacon-gov-debug",
        "beacon-gov-doctor",
        "beacon-pln-brainstorm",
        "beacon-pln-source",
        "beacon-pln-review",
        "beacon-pln-friction",
    }
)

GIT_ADMISSION_SKILLS = TIER_A_SKILLS | TIER_B_SKILLS


def _semver_tuple(value: str) -> tuple[int, int, int]:
    text = str(value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    numbers: list[int] = []
    for part in text.split(".")[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits or "0"))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def _normalized_path(value: Any, *, project_root: Path) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = (project_root / path).resolve()
    else:
        path = path.resolve()
    return str(path)


def resolve_workspace_project_root(project_root: Path) -> Path:
    """Normalize any linked worktree checkout to the primary repo root."""
    from beacon.utils.git_alignment import git_output, git_repo_exists

    root = project_root.expanduser().resolve()
    if not git_repo_exists(root):
        return root
    git_dir_raw = git_output(root, "rev-parse", "--git-dir")
    if not git_dir_raw:
        return root
    git_dir = Path(git_dir_raw)
    if not git_dir.is_absolute():
        git_dir = (root / git_dir).resolve()
    parts = git_dir.parts
    if "worktrees" in parts:
        idx = parts.index("worktrees")
        if idx >= 2 and parts[idx - 1] == ".git":
            return Path(*parts[: idx - 1]).resolve()
    toplevel = git_output(root, "rev-parse", "--show-toplevel")
    return Path(toplevel).resolve() if toplevel else root


def artifact_path(project_root: Path, *, version: str, feature: str) -> Path:
    slug = feature_slug(feature)
    return (
        project_root.expanduser().resolve()
        / ".beacon/state/workspace-admission"
        / version
        / f"{slug}.json"
    )


def load_admission_contract(project_root: Path, *, version: str) -> dict[str, Any]:
    from beacon.utils.project_metadata import resolve_project_metadata_view

    root = project_root.expanduser().resolve()
    view = resolve_project_metadata_view(root, version=version)
    version_contract = view.get("version_contract") if isinstance(view.get("version_contract"), dict) else {}
    branch_governance = view.get("branch_governance") if isinstance(view.get("branch_governance"), dict) else {}
    per_service = (
        version_contract.get("per_service_canonical_branch")
        if isinstance(version_contract.get("per_service_canonical_branch"), dict)
        else {}
    )
    selected_service = str(view.get("selected_service") or "").strip()
    canonical_branch = str(per_service.get(selected_service) or view.get("selected_branch") or "").strip()
    pattern = str(
        version_contract.get("next_version_feature_branch")
        or branch_governance.get("next_version_feature_branch")
        or ""
    ).strip()
    previous_baseline = str(
        version_contract.get("previous_version_baseline_branch")
        or branch_governance.get("previous_version_baseline_branch")
        or ""
    ).strip()
    worktree_mode_raw = str(
        version_contract.get("worktree_mode") or branch_governance.get("worktree_mode") or ""
    ).strip()
    worktree_mode = "dedicated-worktree" if worktree_mode_raw.lower() in {"dedicated", "dedicated-worktree"} else worktree_mode_raw
    worktree_base = str(
        version_contract.get("worktree_path") or branch_governance.get("worktree_path") or ""
    ).strip()
    require_raw = version_contract.get("require_workspace_admission")
    if require_raw is None:
        require_raw = branch_governance.get("require_workspace_admission")
    if require_raw is None:
        require = _semver_tuple(version) >= (1, 6, 2) and worktree_mode == "dedicated-worktree"
    else:
        require = bool(require_raw) if not isinstance(require_raw, str) else require_raw.lower() in {"1", "true", "yes", "on"}
    invalidation = str(
        version_contract.get("admission_invalidation")
        or branch_governance.get("admission_invalidation")
        or "dirty_only"
    ).strip() or "dirty_only"
    return {
        "version": version,
        "require_workspace_admission": require,
        "admission_invalidation": invalidation,
        "canonical_branch": canonical_branch,
        "feature_branch_pattern": pattern,
        "previous_version_baseline_branch": previous_baseline,
        "worktree_mode": worktree_mode,
        "worktree_base": worktree_base,
    }


def resolve_feature_branch(contract: dict[str, Any], *, feature: str, version: str) -> str:
    slug = feature_slug(feature)
    pattern = str(contract.get("feature_branch_pattern") or "").strip()
    if pattern:
        return pattern.replace("<feature-slug>", slug).replace("{feature-slug}", slug)
    canonical = str(contract.get("canonical_branch") or "").strip()
    if canonical:
        return f"{canonical}/{slug}"
    return f"beacon/{version}/{slug}"


def resolve_worktree_path(project_root: Path, contract: dict[str, Any], *, feature: str) -> str:
    slug = feature_slug(feature)
    base = str(contract.get("worktree_base") or "").strip() or f".beacon/worktrees/{contract.get('version', '')}"
    base_path = Path(base)
    if base_path.name == slug:
        return _normalized_path(base, project_root=project_root)
    return _normalized_path(base_path / slug, project_root=project_root)


def write_admission_artifact(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_admission_artifact(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def validate_workspace_admission(
    project_root: Path,
    *,
    version: str,
    feature: str,
    cwd: Path | str | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = resolve_workspace_project_root(project_root)
    contract = contract if isinstance(contract, dict) else load_admission_contract(root, version=version)
    slug = feature_slug(feature)
    artifact_file = artifact_path(root, version=version, feature=feature)
    artifact = read_admission_artifact(artifact_file)
    reason_codes: list[str] = []
    if not contract.get("require_workspace_admission"):
        from beacon.utils.execution_branch_contract import resolve_workspace_branch_targets

        branch_targets = resolve_workspace_branch_targets(
            root, version=version, feature=feature, admission_contract={**contract, "version": version}
        )
        expected_branch = str(branch_targets.get("feature_branch") or "").strip()
        check_root = Path(cwd).expanduser().resolve() if cwd is not None else root
        current_branch = git_output(check_root, "branch", "--show-current")
        if expected_branch and current_branch and current_branch != expected_branch:
            return {
                "valid": False,
                "status": "blocked",
                "skipped": False,
                "reason_code": "branch_alignment_required",
                "reason_codes": ["branch_alignment_required"],
                "artifact_path": str(artifact_file.relative_to(root)) if artifact_file.is_file() else "",
                "expected_branch": expected_branch,
                "current_branch": current_branch,
                "branch_resolution": branch_targets,
            }
        return {
            "valid": True,
            "status": "pass",
            "skipped": True,
            "reason_codes": [],
            "artifact_path": str(artifact_file.relative_to(root)) if artifact_file.is_file() else "",
            "branch_resolution": branch_targets,
        }
    if not artifact:
        reason_codes.append("workspace_admission_missing")
        return {
            "valid": False,
            "status": "blocked",
            "reason_code": "workspace_admission_missing",
            "reason_codes": reason_codes,
            "artifact_path": str(artifact_file.relative_to(root)),
        }
    worktree_path = _normalized_path(artifact.get("worktree_path"), project_root=root)
    branch = str(artifact.get("branch") or "").strip()
    recorded_head = str(artifact.get("git_head") or "").strip()
    worktree_root = Path(worktree_path) if worktree_path else None
    if not worktree_root or not worktree_root.exists():
        reason_codes.append("workspace_admission_worktree_missing")
    else:
        current_branch = git_output(worktree_root, "branch", "--show-current")
        current_head = git_output(worktree_root, "rev-parse", "HEAD")
        if branch and current_branch and branch != current_branch:
            reason_codes.append("workspace_admission_dirty_branch")
        if recorded_head and current_head and recorded_head != current_head:
            reason_codes.append("workspace_admission_dirty_head")
    if cwd is not None:
        cwd_path = Path(cwd).expanduser().resolve()
        if worktree_path:
            try:
                cwd_path.relative_to(Path(worktree_path))
            except ValueError:
                reason_codes.append("workspace_admission_cwd_mismatch")
    valid = not reason_codes
    return {
        "valid": valid,
        "status": "pass" if valid else "blocked",
        "reason_code": reason_codes[0] if reason_codes else "",
        "reason_codes": reason_codes,
        "artifact_path": str(artifact_file.relative_to(root)),
        "artifact": artifact,
        "worktree_path": worktree_path,
        "admission_invalidation": str(contract.get("admission_invalidation") or "dirty_only"),
    }


def _merge_main_into_feature_branch(lane_root: Path, base_branch: str = "main") -> dict[str, Any]:
    """Merge main into the feature branch before implementation (R4 §4.2, AC-017).

    Ensures implementation bases on main-frozen truth, not a stale dev copy.
    Returns {status: merged|conflict|up_to_date, base_branch, stdout/stderr}.
    """
    base = str(base_branch or "main").strip() or "main"
    try:
        result = subprocess.run(
            ["git", "merge", base, "--no-edit", "--ff"],
            cwd=str(lane_root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": "conflict", "base_branch": base, "stderr": str(exc)}
    stdout = str(result.stdout or "").strip()
    stderr = str(result.stderr or "").strip()
    if result.returncode == 0:
        already = "Already up to date" in stdout
        return {
            "status": "up_to_date" if already else "merged",
            "base_branch": base,
            "stdout": stdout,
            "stderr": stderr,
        }
    # conflict — abort to leave the lane clean
    subprocess.run(["git", "merge", "--abort"], cwd=str(lane_root), capture_output=True, timeout=15, check=False)
    return {"status": "conflict", "base_branch": base, "stdout": stdout, "stderr": stderr}


def run_workspace_admit(
    project_root: Path,
    *,
    version: str,
    feature: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    from beacon.utils.execution_branch_contract import resolve_workspace_branch_targets

    root = resolve_workspace_project_root(project_root)
    contract = load_admission_contract(root, version=version)
    slug = feature_slug(feature)
    branch_targets = resolve_workspace_branch_targets(
        root, version=version, feature=feature, admission_contract={**contract, "version": version}
    )
    feature_branch = str(branch_targets.get("feature_branch") or "").strip()
    worktree_path = str(branch_targets.get("worktree_path") or "").strip()
    base_branch = str(contract.get("previous_version_baseline_branch") or contract.get("canonical_branch") or "main").strip()
    artifact_file = artifact_path(root, version=version, feature=feature)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "status": "pass",
        "version": version,
        "feature": feature,
        "feature_slug": slug,
        "branch": feature_branch,
        "worktree_path": worktree_path,
        "cwd": worktree_path,
        "artifact_path": str(artifact_file.relative_to(root)),
        "base_branch": base_branch,
        "reason_codes": [],
        "admission_contract": {
            "require_workspace_admission": contract.get("require_workspace_admission"),
            "admission_invalidation": contract.get("admission_invalidation"),
            "worktree_mode": contract.get("worktree_mode"),
        },
        "branch_resolution": branch_targets,
    }
    if not contract.get("require_workspace_admission"):
        payload["skipped"] = True
        payload["summary"] = "workspace admission not required for this version contract"
        return payload
    if dry_run:
        payload["dry_run"] = True
        payload["summary"] = "dry-run: would ensure worktree lane and write admission artifact"
        return payload
    worktree_attempt = ensure_expected_worktree_lane(
        root,
        feature_branch,
        worktree_path=worktree_path,
        base_branch=base_branch,
    )
    payload["worktree_attempt"] = worktree_attempt
    if worktree_attempt.get("status") not in {"created", "switched"}:
        payload["status"] = "blocked"
        payload["reason_codes"] = ["workspace_admission_worktree_failed"]
        payload["reason_code"] = "workspace_admission_worktree_failed"
        payload["summary"] = "failed to create or switch governed worktree lane"
        return payload
    lane_root = Path(str(worktree_attempt.get("worktree_path") or worktree_path)).resolve()
    # R4 §4.2 / AC-017: merge main into the feature branch so implementation
    # bases on main-frozen truth, not a stale dev-branch copy.
    merge_main = _merge_main_into_feature_branch(lane_root, base_branch=base_branch)
    payload["merge_main"] = merge_main
    if merge_main.get("status") == "conflict":
        payload["status"] = "blocked"
        payload["reason_codes"] = payload.get("reason_codes", []) + ["merge_main_conflict"]
        payload["reason_code"] = "merge_main_conflict"
        payload["summary"] = f"merge {base_branch} into {feature_branch} conflicted; resolve before implementing"
        return payload
    git_head = git_output(lane_root, "rev-parse", "HEAD")
    current_branch = git_output(lane_root, "branch", "--show-current") or feature_branch
    artifact_payload = {
        "schema_version": SCHEMA_VERSION,
        "version": version,
        "feature_slug": slug,
        "project_root": str(root),
        "branch": current_branch,
        "worktree_path": str(lane_root),
        "base_branch": base_branch,
        "issued_at": now_iso(),
        "git_head": git_head,
        "status": "pass",
    }
    write_admission_artifact(artifact_file, artifact_payload)
    payload.update(
        {
            "branch": current_branch,
            "worktree_path": str(lane_root),
            "cwd": str(lane_root),
            "git_head": git_head,
            "artifact": artifact_payload,
            "summary": "workspace admission issued",
        }
    )
    return payload


def build_workspace_admission_branch_preflight(
    project_root: Path,
    *,
    version: str,
    feature: str,
    run_id: str,
    cwd: Path | str | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """When workspace admission is required and valid, satisfy implement branch preflight."""
    root = resolve_workspace_project_root(project_root)
    contract = contract if isinstance(contract, dict) else load_admission_contract(root, version=version)
    if not contract.get("require_workspace_admission"):
        return None
    validation = validate_workspace_admission(
        root,
        version=version,
        feature=feature,
        cwd=cwd,
        contract=contract,
    )
    slug = feature_slug(feature)
    base: dict[str, Any] = {
        "run_id": run_id,
        "feature": feature,
        "feature_slug": slug,
        "generated_at": now_iso(),
        "workspace_admission_branch_guard": True,
        "artifact_path": str(validation.get("artifact_path") or ""),
        "admission_invalidation": str(validation.get("admission_invalidation") or "dirty_only"),
    }
    if validation.get("valid"):
        artifact = validation.get("artifact") if isinstance(validation.get("artifact"), dict) else {}
        branch = str(artifact.get("branch") or "").strip()
        worktree_path = str(validation.get("worktree_path") or artifact.get("worktree_path") or "").strip()
        return {
            **base,
            "schema_version": "1.0",
            "status": "pass",
            "blocked": False,
            "summary": "branch preflight satisfied via valid workspace admission artifact",
            "reason_codes": [],
            "expected_branch": branch,
            "current_branch": branch,
            "worktree_path": worktree_path,
        }
    reason_codes = list(validation.get("reason_codes") or [])
    reason_code = str(validation.get("reason_code") or (reason_codes[0] if reason_codes else "workspace_admission_invalid"))
    return {
        **base,
        "schema_version": "1.0",
        "status": "blocked",
        "blocked": True,
        "summary": "branch preflight blocked because workspace admission artifact is invalid",
        "reason_code": reason_code,
        "reason_codes": reason_codes,
        "expected_branch": "",
        "current_branch": "",
        "worktree_path": str(validation.get("worktree_path") or ""),
    }


def gate_workspace_admission_or_block(
    project_root: Path,
    *,
    version: str,
    feature: str,
    cwd: Path | str | None = None,
) -> dict[str, Any] | None:
    contract = load_admission_contract(project_root, version=version)
    validation = validate_workspace_admission(
        project_root,
        version=version,
        feature=feature,
        cwd=cwd,
        contract=contract,
    )
    if validation.get("valid"):
        return None
    slug = feature_slug(feature)
    root = project_root.expanduser().resolve()
    return {
        "schema_version": "1.0",
        "status": "blocked",
        "reason_code": str(validation.get("reason_code") or "workspace_admission_required"),
        "reason_codes": list(validation.get("reason_codes") or []),
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "workspace_admission": validation,
        "recommended_command": (
            f"beacon workspace admit --project-root {root} --version {version} --feature {slug} --json"
        ),
    }


def inject_git_admission_into_skill_text(skill_id: str, text: str) -> str:
    if skill_id not in GIT_ADMISSION_SKILLS:
        return text
    if "GIT_ADMISSION" in text and "workspace admit" in text:
        return text
    marker = "## Beacon v1.6.0 共享 Preamble"
    if marker in text:
        idx = text.find(marker)
        end = text.find("\n## ", idx + len(marker))
        insert_at = end if end != -1 else len(text)
        return text[:insert_at].rstrip() + "\n\n" + GIT_ADMISSION_PREAMBLE + "\n" + text[insert_at:].lstrip("\n")
    return text.rstrip() + "\n\n" + GIT_ADMISSION_PREAMBLE + "\n"


def _versions_requiring_admission(project_root: Path) -> list[str]:
    from beacon.utils.project_governance import load_governance_payload

    root = project_root.expanduser().resolve()
    payload = load_governance_payload(root)
    versions: list[str] = []
    scoped = payload.get("version_scoped_metadata") if isinstance(payload.get("version_scoped_metadata"), dict) else {}
    for version in scoped:
        contract = load_admission_contract(root, version=str(version))
        if contract.get("require_workspace_admission"):
            versions.append(str(version))
    if versions:
        return sorted(set(versions), key=_semver_tuple)
    from beacon.utils.versioning import resolve_target_version

    fallback_version = resolve_target_version(root, "auto")
    fallback_contract = load_admission_contract(root, version=fallback_version)
    if fallback_contract.get("require_workspace_admission"):
        return [fallback_version]
    return []


def hook_should_deny_write(
    project_root: Path,
    *,
    target_path: Path | str,
    cwd: Path | str | None = None,
) -> tuple[bool, str]:
    root = project_root.expanduser().resolve()
    target = Path(target_path).expanduser()
    if not target.is_absolute():
        target = (Path(cwd or root) / target).resolve()
    try:
        rel = target.relative_to(root)
    except ValueError:
        return False, ""
    rel_text = rel.as_posix()
    if rel_text.startswith(".beacon/state/workspace-admission/"):
        return False, ""

    required_versions = _versions_requiring_admission(root)
    if not required_versions:
        return False, ""

    for version in required_versions:
        contract = load_admission_contract(root, version=version)
        admission_root = root / ".beacon/state/workspace-admission" / version
        if not admission_root.is_dir():
            return True, "workspace_admission_missing"
        for artifact_file in sorted(admission_root.glob("*.json")):
            artifact = read_admission_artifact(artifact_file)
            if not artifact:
                continue
            feature = str(artifact.get("feature_slug") or artifact_file.stem)
            validation = validate_workspace_admission(
                root,
                version=version,
                feature=feature,
                cwd=cwd or root,
                contract=contract,
            )
            worktree_path = str(validation.get("worktree_path") or artifact.get("worktree_path") or "")
            if not worktree_path:
                continue
            try:
                target.relative_to(Path(worktree_path))
            except ValueError:
                continue
            if validation.get("valid"):
                return False, ""
            return True, str(validation.get("reason_code") or "workspace_admission_invalid")
        return True, "workspace_admission_missing"
    return False, ""
