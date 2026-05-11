"""Safe PRD bootstrap utility for one-click requirement docs generation."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from beacon.utils.change_surface import build_change_command
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _extract_title(content: str) -> str:
    for line in str(content or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _extract_first_match(content: str, pattern: str) -> str:
    match = re.search(pattern, str(content or ""), flags=re.IGNORECASE | re.MULTILINE)
    return str(match.group(1)).strip() if match else ""


def _strip_backticks(value: str) -> str:
    return str(value or "").strip().strip("`").strip()


def _extract_doc_metadata(content: str) -> dict[str, str]:
    text = str(content or "")
    return {
        "title": _extract_title(text),
        "feature": _strip_backticks(_extract_first_match(text, r"^\s*[-*]\s*feature:\s*(.+?)\s*$")),
        "version": _strip_backticks(_extract_first_match(text, r"^\s*[-*]\s*version:\s*(.+?)\s*$")),
        "status": _strip_backticks(_extract_first_match(text, r"^\s*[-*]\s*status:\s*(.+?)\s*$")),
    }


def _has_any_section(content: str, candidates: list[str]) -> bool:
    lowered = str(content or "").lower()
    return any(candidate.lower() in lowered for candidate in candidates)


def _derive_status(existing: str, *, reverse_derived: bool) -> str:
    normalized = str(existing or "").strip().lower()
    if normalized:
        if "bootstrap-generated" in normalized:
            return existing
        if reverse_derived:
            return "bootstrap-generated / review-required / derived-from-downstream / not-yet-frozen"
        if "draft" in normalized:
            return "bootstrap-generated / review-required / not-yet-frozen"
    if reverse_derived:
        return "bootstrap-generated / review-required / derived-from-downstream / not-yet-frozen"
    return "bootstrap-generated / review-required / not-yet-frozen"


def _minimal_prd_from_downstream(
    feature: str,
    version: str,
    description: str,
    *,
    story_text: str,
    test_case_text: str,
    reverse_derived: bool,
) -> str:
    ac_ids = _extract_ac_ids(story_text or test_case_text)
    ac_rows = [
        {"id": ac_id, "theme": "derived", "desc": f"Derived acceptance anchor for {ac_id}."}
        for ac_id in ac_ids
    ] or _ac_rows(feature, description)
    status = _derive_status("", reverse_derived=reverse_derived)
    fr_rows = "\n".join(
        f"| FR-{index:03d} | {row['id']} | {row['desc']} |"
        for index, row in enumerate(ac_rows, start=1)
    )
    ac_rows_text = "\n".join(
        f"| {row['id']} | {row['theme']} | {row['desc']} |"
        for row in ac_rows
    )
    gaps = []
    if not story_text.strip():
        gaps.append("- 缺少原生 user-story，当前 PRD 由 test-case / intent 反推。")
    if not test_case_text.strip():
        gaps.append("- 缺少 test-case 证据，当前 PRD 仍需补验收覆盖。")
    if not gaps:
        gaps.append("- 当前 PRD 为 reverse-derived shell，仍需 truth review 后才能冻结。")
    return (
        f"# PRD: {feature}\n\n"
        "## 1. Overview\n\n"
        f"- version: `{version}`\n"
        f"- feature: `{feature}`\n"
        f"- status: `{status}`\n"
        f"- 需求描述: {description}\n\n"
        "## 2. Scope\n\n"
        f"- In scope: `{feature}` 的最小闭环补齐与 truth review。\n"
        "- Out of scope: 未被当前 evidence 支撑的扩展能力。\n\n"
        "## 3. Functional Requirements\n\n"
        "| FR ID | Related AC | Requirement |\n"
        "| --- | --- | --- |\n"
        f"{fr_rows}\n\n"
        "## 4. Acceptance Traceability\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        f"{ac_rows_text}\n\n"
        "## 5. Gaps\n\n"
        + "\n".join(gaps)
        + "\n\n## 6. Review Route\n\n- 当前 PRD 为 reverse-derived truth shell，必须进入 truth review / refreeze。\n"
    )


def _minimal_story_from_truth(
    feature: str,
    version: str,
    description: str,
    *,
    prd_text: str,
    test_case_text: str,
    reverse_derived: bool,
) -> str:
    ac_ids = _extract_ac_ids(test_case_text or prd_text)
    rows = [
        {"id": ac_id, "theme": "derived", "desc": f"Derived acceptance criterion for {ac_id}."}
        for ac_id in ac_ids
    ] or _ac_rows(feature, description)
    table_rows = "\n".join(f"| {row['id']} | {row['theme']} | {row['desc']} |" for row in rows)
    status = _derive_status("", reverse_derived=reverse_derived)
    notes = []
    if reverse_derived:
        notes.append("- 当前 story 含 downstream-derived 内容，必须进入 truth review。")
    if not prd_text.strip():
        notes.append("- 缺少原生 PRD truth。")
    return (
        f"# User Story: {feature}\n\n"
        "## Story\n\n"
        "作为目标用户，我希望系统能够形成可验证的需求闭环，以便进入正式实现。\n\n"
        f"### 需求描述\n\n{description}\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        f"{table_rows}\n\n"
        "## Metadata\n\n"
        f"- version: `{version}`\n"
        f"- feature: `{feature}`\n"
        f"- status: `{status}`\n"
        f"- generated_at: `{now_iso()}`\n"
        + ("\n".join(notes) + "\n" if notes else "")
    )


def _minimal_test_case_from_truth(
    feature: str,
    version: str,
    description: str,
    *,
    prd_text: str,
    story_text: str,
) -> str:
    ac_ids = _extract_ac_ids(story_text or prd_text)
    rows = []
    if ac_ids:
        for index, ac_id in enumerate(ac_ids, start=1):
            rows.append(f"| TC-{index:03d} | {ac_id} | derived scenario | unit | Derived coverage for {ac_id}. |")
    else:
        for index, row in enumerate(_ac_rows(feature, description), start=1):
            rows.append(f"| TC-{index:03d} | {row['id']} | {row['theme']} scenario | unit | {row['desc']} |")
    matrix = "\n".join(rows)
    return (
        f"# Test Cases: {feature}\n\n"
        "## Coverage Matrix\n\n"
        "| TC ID | AC ID | Scenario | Layer | Expected |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{matrix}\n\n"
        "## Execution Notes\n\n"
        f"- version: `{version}`\n"
        "- status: `bootstrap-generated / review-required / not-yet-frozen`\n"
        "- 每个 AC 至少对应一个 TC，若 AC 由 reverse-derived truth 提供，则必须先 truth review。\n"
    )


def _existing_package(project_root: Path, version: str, slug: str) -> dict[str, Any]:
    targets = _paths(project_root, version, slug)
    docs = {name: _read_text(path) for name, path in targets.items()}
    exists = {name: bool(text.strip()) for name, text in docs.items()}
    metadata = {name: _extract_doc_metadata(text) for name, text in docs.items()}
    return {"targets": targets, "docs": docs, "exists": exists, "metadata": metadata}


def _detect_package_state(package: dict[str, Any]) -> str:
    exists = package["exists"]
    present = tuple(name for name in ("prd", "user_story", "test_case") if exists.get(name))
    if not present:
        return "empty"
    if present == ("prd",):
        return "prd_only"
    if present == ("user_story",):
        return "user_story_only"
    if present == ("test_case",):
        return "test_case_only"
    if present == ("prd", "user_story"):
        return "prd_user_story"
    if present == ("prd", "test_case"):
        return "prd_test_case"
    if present == ("user_story", "test_case"):
        return "user_story_test_case"
    if present == ("prd", "user_story", "test_case"):
        story_ac = sorted(set(_extract_ac_ids(package["docs"]["user_story"])))
        test_ac = sorted(set(_extract_ac_ids(package["docs"]["test_case"])))
        if story_ac and test_ac and story_ac == test_ac:
            return "full_consistent"
        return "full_inconsistent"
    return "empty"


def _gap_entry(*, gap_id: str, theme: str, question: str, blocks: list[str]) -> dict[str, Any]:
    return {"gap_id": gap_id, "theme": theme, "question": question, "blocks": blocks}


def _build_orchestrated_documents(
    project_root: Path,
    *,
    feature: str,
    description: str,
    version: str,
) -> dict[str, Any]:
    slug = _slug(feature)
    package = _existing_package(project_root, version, slug)
    package_state = _detect_package_state(package)
    docs = dict(package["docs"])
    metadata = dict(package["metadata"])
    generated_layers: list[str] = []
    missing_layers = [name for name in ("prd", "user_story", "test_case") if not package["exists"].get(name)]
    reverse_derived_layers: list[dict[str, Any]] = []
    derived_layers: list[dict[str, Any]] = []
    drift_digest: list[dict[str, Any]] = []
    supplement_tasks: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    if package_state == "empty":
        docs = _build_documents(feature, description, version)
        metadata = {name: _extract_doc_metadata(content) for name, content in docs.items()}
        generated_layers = ["prd", "user_story", "test_case"]
        gaps.append(_gap_entry(gap_id="GAP-001", theme="missing-context", question="当前仅基于意图生成 draft package，仍需补充边界与异常。", blocks=["freeze_ready", "implementation_pending"]))
    elif package_state == "prd_only":
        docs["user_story"] = _minimal_story_from_truth(feature, version, description, prd_text=docs["prd"], test_case_text="", reverse_derived=False)
        docs["test_case"] = _minimal_test_case_from_truth(feature, version, description, prd_text=docs["prd"], story_text=docs["user_story"])
        metadata["user_story"] = _extract_doc_metadata(docs["user_story"])
        metadata["test_case"] = _extract_doc_metadata(docs["test_case"])
        generated_layers.extend(["user_story", "test_case"])
        derived_layers.extend(
            [
                {"layer": "user_story", "derived_from": ["prd"]},
                {"layer": "test_case", "derived_from": ["prd", "user_story"]},
            ]
        )
    elif package_state == "user_story_only":
        docs["prd"] = _minimal_prd_from_downstream(feature, version, description, story_text=docs["user_story"], test_case_text="", reverse_derived=True)
        docs["test_case"] = _minimal_test_case_from_truth(feature, version, description, prd_text=docs["prd"], story_text=docs["user_story"])
        metadata["prd"] = _extract_doc_metadata(docs["prd"])
        metadata["test_case"] = _extract_doc_metadata(docs["test_case"])
        generated_layers.extend(["prd", "test_case"])
        reverse_derived_layers.append({"layer": "prd", "derived_from": ["user_story"], "risk": "derived_from_downstream"})
        derived_layers.append({"layer": "test_case", "derived_from": ["prd", "user_story"]})
        gaps.append(_gap_entry(gap_id="GAP-001", theme="reverse-derived-prd", question="PRD 由 user-story 反推，仍需 truth review。", blocks=["implementation_pending"]))
    elif package_state == "test_case_only":
        docs["user_story"] = _minimal_story_from_truth(feature, version, description, prd_text="", test_case_text=docs["test_case"], reverse_derived=True)
        docs["prd"] = _minimal_prd_from_downstream(feature, version, description, story_text=docs["user_story"], test_case_text=docs["test_case"], reverse_derived=True)
        metadata["user_story"] = _extract_doc_metadata(docs["user_story"])
        metadata["prd"] = _extract_doc_metadata(docs["prd"])
        generated_layers.extend(["user_story", "prd"])
        reverse_derived_layers.extend(
            [
                {"layer": "user_story", "derived_from": ["test_case"], "risk": "derived_from_downstream"},
                {"layer": "prd", "derived_from": ["user_story", "test_case"], "risk": "derived_from_downstream"},
            ]
        )
        gaps.append(_gap_entry(gap_id="GAP-001", theme="reverse-derived-upstream", question="当前上游 truth 主要从 test-case 反推，必须先 review/refreeze。", blocks=["freeze_ready", "implementation_pending"]))
    elif package_state == "prd_user_story":
        docs["test_case"] = _minimal_test_case_from_truth(feature, version, description, prd_text=docs["prd"], story_text=docs["user_story"])
        metadata["test_case"] = _extract_doc_metadata(docs["test_case"])
        generated_layers.append("test_case")
        derived_layers.append({"layer": "test_case", "derived_from": ["prd", "user_story"]})
    elif package_state == "prd_test_case":
        docs["user_story"] = _minimal_story_from_truth(feature, version, description, prd_text=docs["prd"], test_case_text=docs["test_case"], reverse_derived=True)
        metadata["user_story"] = _extract_doc_metadata(docs["user_story"])
        generated_layers.append("user_story")
        reverse_derived_layers.append({"layer": "user_story", "derived_from": ["prd", "test_case"], "risk": "derived_from_downstream"})
        gaps.append(_gap_entry(gap_id="GAP-001", theme="reverse-derived-story", question="user-story 由 PRD + test-case 补推，仍需 truth review。", blocks=["implementation_pending"]))
    elif package_state == "user_story_test_case":
        docs["prd"] = _minimal_prd_from_downstream(feature, version, description, story_text=docs["user_story"], test_case_text=docs["test_case"], reverse_derived=True)
        metadata["prd"] = _extract_doc_metadata(docs["prd"])
        generated_layers.append("prd")
        reverse_derived_layers.append({"layer": "prd", "derived_from": ["user_story", "test_case"], "risk": "derived_from_downstream"})
        gaps.append(_gap_entry(gap_id="GAP-001", theme="reverse-derived-prd", question="PRD 由下游 truth 反推，仍需 truth review。", blocks=["implementation_pending"]))
    elif package_state == "full_inconsistent":
        story_ac = sorted(set(_extract_ac_ids(docs["user_story"])))
        test_ac = sorted(set(_extract_ac_ids(docs["test_case"])))
        drift_digest.append(
            {
                "drift_id": "DRIFT-001",
                "theme": "ac_traceability_mismatch",
                "affected_layers": ["user_story", "test_case"],
                "story_ac_ids": story_ac,
                "test_case_ac_ids": test_ac,
                "recommended_route": "review/refreeze before implementation",
            }
        )
    # full_consistent falls through with existing docs unchanged

    consistency = _consistency_report(user_story=docs["user_story"], test_case=docs["test_case"]) if docs.get("user_story") and docs.get("test_case") else {"ok": True, "story_ac_ids": [], "test_case_ac_ids": [], "missing_in_test_case": []}
    quality = _quality_report(docs, max_placeholders=0)
    closure_analysis = _closure_analysis(docs, metadata)

    if reverse_derived_layers:
        supplement_tasks.append(
            {
                "task_id": "SUP-001",
                "target_doc": reverse_derived_layers[0]["layer"],
                "action": "truth-review",
                "reason": "reverse-derived upstream truth requires review",
            }
        )
    if package_state == "empty":
        closure_verdict = "draft_generated"
        readiness_verdict = "supplement_required"
    elif drift_digest:
        closure_verdict = "drift_repair_required"
        readiness_verdict = "drift_repair_required"
    elif reverse_derived_layers:
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"
    elif not closure_analysis.get("ok", False):
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"
    elif not consistency.get("ok", False):
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"
    elif package_state in {"prd_only", "prd_user_story", "full_consistent"}:
        closure_verdict = "freeze_ready"
        readiness_verdict = "implementation_pending"
    else:
        closure_verdict = "freeze_ready"
        readiness_verdict = "implementation_pending"

    if package_state == "empty" and not quality.get("ok", False):
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"

    return {
        "slug": slug,
        "targets": package["targets"],
        "docs": docs,
        "package_state": package_state,
        "missing_layers": missing_layers,
        "generated_layers": generated_layers,
        "derived_layers": derived_layers,
        "reverse_derived_layers": reverse_derived_layers,
        "drift_digest": drift_digest,
        "quality": quality,
        "consistency": consistency,
        "closure_analysis": closure_analysis,
        "closure_verdict": closure_verdict,
        "readiness_verdict": readiness_verdict,
        "supplement_tasks": supplement_tasks,
        "gap_digest": gaps,
    }


def inspect_requirement_closure(
    project_root: Path,
    *,
    feature: str,
    version: str,
) -> dict[str, Any]:
    slug = _slug(feature)
    package = _existing_package(project_root, version, slug)
    package_state = _detect_package_state(package)
    docs = dict(package["docs"])
    metadata = dict(package["metadata"])
    drift_digest: list[dict[str, Any]] = []

    if package_state == "full_inconsistent":
        story_ac = sorted(set(_extract_ac_ids(docs["user_story"])))
        test_ac = sorted(set(_extract_ac_ids(docs["test_case"])))
        drift_digest.append(
            {
                "drift_id": "DRIFT-001",
                "theme": "ac_traceability_mismatch",
                "affected_layers": ["user_story", "test_case"],
                "story_ac_ids": story_ac,
                "test_case_ac_ids": test_ac,
                "recommended_route": "review/refreeze before implementation",
            }
        )

    consistency = (
        _consistency_report(user_story=docs["user_story"], test_case=docs["test_case"])
        if docs.get("user_story") and docs.get("test_case")
        else {"ok": True, "story_ac_ids": [], "test_case_ac_ids": [], "missing_in_test_case": []}
    )
    quality = _quality_report(docs, max_placeholders=0)
    closure_analysis = _closure_analysis(docs, metadata)
    missing_layers = [name for name in ("prd", "user_story", "test_case") if not package["exists"].get(name)]

    if package_state == "full_inconsistent" or drift_digest:
        closure_verdict = "drift_repair_required"
        readiness_verdict = "drift_repair_required"
    elif missing_layers:
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"
    elif not closure_analysis.get("ok", False) or not consistency.get("ok", False) or not quality.get("ok", False):
        closure_verdict = "supplement_required"
        readiness_verdict = "supplement_required"
    else:
        closure_verdict = "freeze_ready"
        readiness_verdict = "implementation_pending"

    return {
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "package_state": package_state,
        "missing_layers": missing_layers,
        "drift_digest": drift_digest,
        "quality": quality,
        "consistency": consistency,
        "closure_analysis": closure_analysis,
        "closure_verdict": closure_verdict,
        "readiness_verdict": readiness_verdict,
        "source_of_truth_root": f"docs/beacon/{version}",
        "targets": {name: str(path.relative_to(project_root)) for name, path in package["targets"].items()},
    }


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


def _closure_analysis(documents: dict[str, str], metadata: dict[str, dict[str, str]]) -> dict[str, Any]:
    prd_text = documents.get("prd", "")
    story_text = documents.get("user_story", "")
    test_case_text = documents.get("test_case", "")
    story_ac = sorted(set(_extract_ac_ids(story_text)))
    test_ac = sorted(set(_extract_ac_ids(test_case_text)))
    checks = {
        "goal_defined": bool(metadata.get("prd", {}).get("title")) and _has_any_section(prd_text, ["## 1. overview", "## overview"]),
        "main_flow_defined": _has_any_section(story_text, ["## story", "## user story"]),
        "scope_defined": _has_any_section(prd_text, ["## 2. scope", "## scope"]),
        "acceptance_coverage_sufficient": bool(story_ac) and bool(test_ac) and set(story_ac).issubset(set(test_ac)),
        "blocking_unknowns": _placeholder_count(prd_text) + _placeholder_count(story_text) + _placeholder_count(test_case_text) > 0,
    }
    missing_evidence = [name for name, ok in checks.items() if name != "blocking_unknowns" and not ok]
    blocking_items = ["blocking_unknowns"] if checks["blocking_unknowns"] else []
    return {
        "ok": not missing_evidence and not blocking_items,
        "checks": checks,
        "missing_evidence": missing_evidence,
        "blocking_items": blocking_items,
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
    orchestration = _build_orchestrated_documents(
        project_root,
        feature=feature,
        description=description,
        version=resolved_version,
    )
    slug = orchestration["slug"]
    targets = orchestration["targets"]
    docs = orchestration["docs"]
    quality = _quality_report(docs, max_placeholders=max_placeholders)
    consistency = orchestration["consistency"]
    should_apply = bool(apply) and not bool(dry_run)
    lock = _BootstrapLock(_lock_path(project_root), run_id=run_id)
    runtime_version = resolve_runtime_version(project_root, resolved_version)
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
        "package_state": orchestration["package_state"],
        "missing_layers": orchestration["missing_layers"],
        "generated_layers": orchestration["generated_layers"],
        "derived_layers": orchestration["derived_layers"],
        "reverse_derived_layers": orchestration["reverse_derived_layers"],
        "drift_digest": orchestration["drift_digest"],
        "closure_verdict": orchestration["closure_verdict"],
        "readiness_verdict": orchestration["readiness_verdict"],
        "closure_analysis": orchestration["closure_analysis"],
        "supplement_tasks": orchestration["supplement_tasks"],
        "gap_digest": orchestration["gap_digest"],
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

    if orchestration["drift_digest"]:
        payload["status"] = "blocked"
        payload["reason_code"] = "truth_drift_detected"
        payload["recommended_command"] = build_change_command(
            feature=feature,
            project_root=project_root,
            version=resolved_version,
            reason="truth-drift-detected",
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

    if payload["closure_verdict"] == "supplement_required":
        payload["reason_code"] = payload.get("reason_code") or "supplement_required"
        payload["recommended_command"] = (
            f'beacon prd-bootstrap run "{feature}" --desc "{description}" --version {resolved_version} --dry-run'
        )

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
