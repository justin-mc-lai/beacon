"""Safe PRD bootstrap utility for one-click requirement docs generation."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from beacon.utils.context_files import verify_context_files
from beacon.utils.runtime import now_iso, utc_compact_ts, write_json
from beacon.utils.versioning import resolve_runtime_version, resolve_target_version

PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\?\?\?"),
    re.compile(r"\[[^\]]*(Describe|What|待补充|占位)[^\]]*\]", flags=re.IGNORECASE),
)


def _slug(text: str) -> str:
    return "-".join([token for token in str(text or "").strip().lower().replace("_", " ").split(" ") if token]) or "feature"


def _lock_path(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "locks" / "prd-bootstrap.lock"


def _state_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "prd-bootstrap"


def _backup_dir(project_root: Path, run_id: str) -> Path:
    return _state_dir(project_root) / "backups" / run_id


class _BootstrapLock:
    def __init__(self, path: Path, *, run_id: str) -> None:
        self.path = path
        self.run_id = run_id
        self._acquired = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(f"lock already active: {self.path}") from exc
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"run_id={self.run_id}\n")
            handle.write(f"ts={now_iso()}\n")
        self._acquired = True

    def release(self) -> None:
        if self._acquired and self.path.exists():
            self.path.unlink(missing_ok=True)
        self._acquired = False

    def __enter__(self) -> "_BootstrapLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.release()


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".tmp-prd-bootstrap-", dir=str(path.parent))
    temp = Path(temp_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink(missing_ok=True)


def _placeholder_count(content: str) -> int:
    text = str(content or "")
    total = 0
    for pattern in PLACEHOLDER_PATTERNS:
        total += len(pattern.findall(text))
    return total


def _extract_ac_ids(content: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for match in re.finditer(r"\bAC-\d{3}\b", str(content or ""), flags=re.IGNORECASE):
        ac_id = str(match.group(0)).upper()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        out.append(ac_id)
    return out


def _ac_rows(feature: str, description: str) -> list[dict[str, str]]:
    title = str(feature or "").strip()
    desc = str(description or "").strip()
    return [
        {"id": "AC-001", "theme": "happy-path", "desc": f"用户可以完成「{title}」主流程，满足：{desc}"},
        {"id": "AC-002", "theme": "validation", "desc": "输入校验规则明确，非法输入会返回可读错误。"},
        {"id": "AC-003", "theme": "error-handling", "desc": "依赖失败时系统可恢复并提供下一步指引。"},
        {"id": "AC-004", "theme": "observability", "desc": "关键步骤具备可追踪日志与最小化诊断信息。"},
        {"id": "AC-005", "theme": "security", "desc": "仅授权用户可执行敏感操作，越权请求被拒绝。"},
    ]


def _render_user_story(feature: str, description: str, version: str, ac_rows: list[dict[str, str]]) -> str:
    table_rows = "\n".join(
        f"| {row['id']} | {row['theme']} | {row['desc']} |"
        for row in ac_rows
    )
    return (
        f"# User Story: {feature}\n\n"
        "## Story\n\n"
        "作为目标用户，我希望系统能够稳定地完成该需求主流程，以便快速完成业务动作。\n\n"
        f"### 需求描述\n\n{description}\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        f"{table_rows}\n\n"
        "## Metadata\n\n"
        f"- version: `{version}`\n"
        f"- feature: `{feature}`\n"
        "- status: `draft`\n"
        f"- generated_at: `{now_iso()}`\n"
    )


def _render_prd(feature: str, description: str, version: str, ac_rows: list[dict[str, str]]) -> str:
    fr_rows = "\n".join(
        f"| FR-{index:03d} | {row['id']} | {row['desc']} |"
        for index, row in enumerate(ac_rows, start=1)
    )
    ac_rows_text = "\n".join(
        f"| {row['id']} | {row['theme']} | {row['desc']} |"
        for row in ac_rows
    )
    return (
        f"# PRD: {feature}\n\n"
        "## 1. Overview\n\n"
        f"- 目标版本: `{version}`\n"
        f"- 需求描述: {description}\n\n"
        "## 2. Scope\n\n"
        f"- In scope: `{feature}` 的核心业务流程与必要风控校验。\n"
        "- Out of scope: 与该需求无关的跨域重构或新增平台能力。\n\n"
        "## 3. Functional Requirements\n\n"
        "| FR ID | Related AC | Requirement |\n"
        "| --- | --- | --- |\n"
        f"{fr_rows}\n\n"
        "## 4. Acceptance Traceability\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        f"{ac_rows_text}\n\n"
        "## 5. Risks\n\n"
        "- 需求理解偏差：通过 AC 与 TC 一一映射降低语义漂移。\n"
        "- 交付回归风险：通过测试用例覆盖主流程、异常路径与安全边界。\n\n"
        "## 6. Release Guard\n\n"
        "- 通过 `qa` 验证 AC 关闭状态后方可进入 release 评审。\n"
    )


def _render_test_cases(feature: str, version: str, ac_rows: list[dict[str, str]]) -> str:
    rows = []
    for index, row in enumerate(ac_rows, start=1):
        rows.append(
            (
                f"| TC-{index:03d} | {row['id']} | "
                f"{row['theme']} scenario | unit | {row['desc']} |"
            )
        )
    matrix = "\n".join(rows)
    return (
        f"# Test Cases: {feature}\n\n"
        "## Coverage Matrix\n\n"
        "| TC ID | AC ID | Scenario | Layer | Expected |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{matrix}\n\n"
        "## Execution Notes\n\n"
        f"- version: `{version}`\n"
        "- 每个 AC 至少对应一个 TC，且必须可执行可验证。\n"
    )


def _build_documents(feature: str, description: str, version: str) -> dict[str, str]:
    ac_rows = _ac_rows(feature, description)
    return {
        "prd": _render_prd(feature, description, version, ac_rows),
        "user_story": _render_user_story(feature, description, version, ac_rows),
        "test_case": _render_test_cases(feature, version, ac_rows),
    }


def _quality_report(documents: dict[str, str], *, max_placeholders: int) -> dict[str, Any]:
    per_doc = {
        name: _placeholder_count(content)
        for name, content in documents.items()
    }
    total = sum(per_doc.values())
    return {
        "max_placeholders": int(max_placeholders),
        "total_placeholders": int(total),
        "per_doc": per_doc,
        "ok": total <= int(max_placeholders),
    }


def _consistency_report(*, user_story: str, test_case: str) -> dict[str, Any]:
    story_ac = sorted(set(_extract_ac_ids(user_story)))
    test_ac = sorted(set(_extract_ac_ids(test_case)))
    missing_in_test = [ac for ac in story_ac if ac not in test_ac]
    return {
        "story_ac_ids": story_ac,
        "test_case_ac_ids": test_ac,
        "missing_in_test_case": missing_in_test,
        "ok": not missing_in_test,
    }


def _paths(project_root: Path, version: str, slug: str) -> dict[str, Path]:
    base = project_root / "docs" / "beacon" / version
    return {
        "prd": base / "prd" / f"{slug}.md",
        "user_story": base / "user-story" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
    }


def _prepare_overwrite_plan(targets: dict[str, Path], *, no_overwrite: bool) -> tuple[list[Path], list[Path]]:
    existing = [path for path in targets.values() if path.exists()]
    missing = [path for path in targets.values() if not path.exists()]
    if no_overwrite and existing:
        raise RuntimeError(
            "target docs already exist; default --no-overwrite blocks apply. "
            "Use --allow-overwrite after review."
        )
    return existing, missing


def _write_state(project_root: Path, run_id: str, payload: dict[str, Any]) -> Path:
    path = _state_dir(project_root) / f"{run_id}.json"
    write_json(path, payload)
    return path


def run_prd_bootstrap(
    project_root: Path,
    *,
    feature: str,
    description: str,
    version: str,
    apply: bool = False,
    dry_run: bool = False,
    no_overwrite: bool = True,
    strict_context_verify: bool = True,
    max_placeholders: int = 0,
) -> dict[str, Any]:
    if not str(feature or "").strip():
        raise ValueError("feature must not be empty")
    if not str(description or "").strip():
        raise ValueError("description must not be empty")
    if apply and dry_run:
        raise ValueError("--apply cannot be combined with --dry-run")

    resolved_version = resolve_target_version(project_root, version)
    run_id = f"prd-bootstrap-{utc_compact_ts()}"
    slug = _slug(feature)
    targets = _paths(project_root, resolved_version, slug)
    docs = _build_documents(feature, description, resolved_version)
    quality = _quality_report(docs, max_placeholders=max_placeholders)
    consistency = _consistency_report(user_story=docs["user_story"], test_case=docs["test_case"])
    should_apply = bool(apply) and not bool(dry_run)
    lock = _BootstrapLock(_lock_path(project_root), run_id=run_id)
    runtime_version = resolve_runtime_version(project_root, "auto")
    context_report = (
        verify_context_files(project_root, runtime_version=runtime_version, strict=True)
        if strict_context_verify
        else {"ok": True, "status": "pass", "checks": []}
    )

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "feature": feature,
        "feature_slug": slug,
        "description": description,
        "version": resolved_version,
        "generated_at": now_iso(),
        "mode": "apply" if should_apply else "dry-run",
        "dry_run": not should_apply,
        "no_overwrite": bool(no_overwrite),
        "strict_context_verify": bool(strict_context_verify),
        "targets": {name: str(path.relative_to(project_root)) for name, path in targets.items()},
        "quality": quality,
        "consistency": consistency,
        "context_verify": context_report,
        "status": "planned",
        "reason_code": "",
        "recommended_command": "",
        "write_actions": [],
        "rollback_plan": [],
    }

    if strict_context_verify and not bool(context_report.get("ok", False)):
        payload["status"] = "blocked"
        payload["reason_code"] = "context_verify_failed"
        payload["recommended_command"] = (
            f"beacon doctor setup-context --project-root {project_root} --sync-materials --version {resolved_version}"
        )
        state_path = _write_state(project_root, run_id, payload)
        payload["state_path"] = str(state_path.relative_to(project_root))
        return payload

    if not bool(quality.get("ok", False)):
        payload["status"] = "blocked"
        payload["reason_code"] = "quality_threshold_failed"
        payload["recommended_command"] = (
            f'beacon prd-bootstrap run "{feature}" --desc "{description}" --version {resolved_version} --dry-run'
        )
        state_path = _write_state(project_root, run_id, payload)
        payload["state_path"] = str(state_path.relative_to(project_root))
        return payload

    if not bool(consistency.get("ok", False)):
        payload["status"] = "blocked"
        payload["reason_code"] = "ac_testcase_mapping_incomplete"
        payload["recommended_command"] = (
            f'beacon prd-bootstrap run "{feature}" --desc "{description}" --version {resolved_version} --dry-run'
        )
        state_path = _write_state(project_root, run_id, payload)
        payload["state_path"] = str(state_path.relative_to(project_root))
        return payload

    if not should_apply:
        state_path = _write_state(project_root, run_id, payload)
        payload["state_path"] = str(state_path.relative_to(project_root))
        return payload

    backups_root = _backup_dir(project_root, run_id)
    backups_root.mkdir(parents=True, exist_ok=True)
    created_paths: list[Path] = []
    replaced_paths: list[tuple[Path, Path]] = []
    try:
        with lock:
            existing, _missing = _prepare_overwrite_plan(targets, no_overwrite=no_overwrite)
            if existing and no_overwrite:
                raise RuntimeError(
                    "target docs already exist; default --no-overwrite blocks apply. Use --allow-overwrite after review."
                )

            for name, path in targets.items():
                if path.exists():
                    backup_path = backups_root / f"{name}.bak"
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, backup_path)
                    replaced_paths.append((path, backup_path))
                else:
                    created_paths.append(path)
                _atomic_write_text(path, docs[name])
                payload["write_actions"].append(
                    {
                        "target": name,
                        "path": str(path.relative_to(project_root)),
                        "action": "overwritten" if path.exists() and any(item[0] == path for item in replaced_paths) else "created",
                        "backup_path": str((next((item[1] for item in replaced_paths if item[0] == path), Path(""))).relative_to(project_root))
                        if any(item[0] == path for item in replaced_paths)
                        else "",
                    }
                )

        rollback: list[dict[str, str]] = []
        for path in created_paths:
            rollback.append({"action": "delete", "path": str(path.relative_to(project_root))})
        for original, backup in replaced_paths:
            rollback.append(
                {
                    "action": "restore",
                    "path": str(original.relative_to(project_root)),
                    "backup_path": str(backup.relative_to(project_root)),
                }
            )
        payload["rollback_plan"] = rollback
        payload["status"] = "applied"
    except RuntimeError as exc:
        for path in reversed(created_paths):
            if path.exists():
                path.unlink(missing_ok=True)
        for original, backup in reversed(replaced_paths):
            if backup.exists():
                _atomic_write_text(original, backup.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        payload["reason_code"] = "write_blocked" if "no-overwrite" in str(exc) else "lock_active"
        payload["error"] = str(exc)
        payload["recommended_command"] = (
            f'beacon prd-bootstrap run "{feature}" --desc "{description}" --version {resolved_version} --apply --allow-overwrite'
            if "no-overwrite" in str(exc)
            else f"rm -f {_lock_path(project_root)}"
        )
    except Exception as exc:  # noqa: BLE001
        for path in reversed(created_paths):
            if path.exists():
                path.unlink(missing_ok=True)
        for original, backup in reversed(replaced_paths):
            if backup.exists():
                _atomic_write_text(original, backup.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        payload["reason_code"] = "write_failed"
        payload["error"] = str(exc)
        payload["recommended_command"] = (
            f'beacon prd-bootstrap run "{feature}" --desc "{description}" --version {resolved_version} --apply --dry-run'
        )

    state_path = _write_state(project_root, run_id, payload)
    payload["state_path"] = str(state_path.relative_to(project_root))
    payload["lock_path"] = str(_lock_path(project_root).relative_to(project_root))
    return payload
