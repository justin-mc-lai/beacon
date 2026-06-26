"""Truth Integrity Gate (TIG) — unified freeze/refreeze integrity authority for v1.6.0+."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

from beacon.utils.agent_surface import verify_v160_no_fake_delivery
from beacon.utils.feature_package import package_paths, validate_feature_package, _parse_frontmatter, _read_text
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version

TIG_SCHEMA_VERSION = "1.0"

Mode = Literal["block", "audit"]

_DEFAULT_REPAIR_ROUTE = "beacon-gen-truth"

_FAKE_DELIVERY_LINE_PATTERNS: dict[str, re.Pattern[str]] = {
    "placeholder_implementation": re.compile(
        r"placeholder[- ]implementation|占位实现|假实现", re.IGNORECASE
    ),
    "placeholder_acceptance": re.compile(
        r"placeholder[- ]acceptance|占位验收|placeholder ac|stub-only closure|contract test 占位",
        re.IGNORECASE,
    ),
    "docs_only_closure": re.compile(
        r"(?<!非)(?<!不)docs[- ]only[- ]completion|(?<!非)(?<!不)docs[- ]only(?!\s*闭环)|只写文档|文档完成",
        re.IGNORECASE,
    ),
    "fake_runner_evidence": re.compile(
        r"fake[- ]runner[- ]evidence|fake[- ]runner|假 runner|假运行器", re.IGNORECASE
    ),
    "zero_assertions": re.compile(
        r"zero[- ]assertions|0 assertions|0 个断言|零断言", re.IGNORECASE
    ),
    "placeholder_evidence": re.compile(
        r"placeholder[- ]evidence|占位证据|假证据", re.IGNORECASE
    ),
    "soft_test_only": re.compile(
        r"soft[- ]test[- ]only|软占位|仅 integration 验证", re.IGNORECASE
    ),
    "pending_deferral": re.compile(
        r"user_decision:\s*pending|\|\s*pending\s*\|", re.IGNORECASE
    ),
    "implementation_claim_without_evidence": re.compile(
        r"implementation claim without evidence|无证据声称完成", re.IGNORECASE
    ),
}

_PLACEHOLDER_AC_RE = re.compile(
    r"占位|placeholder|stub-only|tbd closure|假装 closure|假装闭环", re.IGNORECASE
)
_ILLEGAL_CLOSURE_RE = re.compile(
    r"仅 contract|subprocess 替身|零断言即可|contract-only closure", re.IGNORECASE
)
_SOFT_TEST_CELL_RE = re.compile(r"^(integration|目录存在|fixture|可选)$", re.IGNORECASE)
_HARD_TEST_MARKERS_RE = re.compile(
    r"cargo|beacon\s|pnpm|npm test|pytest|BLOCKED:", re.IGNORECASE
)
_OCEAN_MARKERS_RE = re.compile(
    r"scope_mode\s*[:=]\s*[`\"']?ocean[`\"']?|scope:\s*ocean", re.IGNORECASE
)
_ALIGNMENT_SURFACE_RE = re.compile(
    r"alignment surface|phased backlog|对齐面|alignment surface（", re.IGNORECASE
)
_USER_INTENT_RE = re.compile(r"user intent|用户意图", re.IGNORECASE)
_DEFERRAL_PENDING_RE = re.compile(
    r"\|\s*pending\s*\||user_decision:\s*pending|状态\s*pending", re.IGNORECASE
)

# --- TIG-DC: Determinism Check patterns (Phase A) ---

_DC_PLACEHOLDER_PATTERNS: dict[str, re.Pattern[str]] = {
    "english_tbd": re.compile(r"\bTBD\b"),
    "english_todo": re.compile(r"\bTODO\b"),
    "english_tbc": re.compile(r"\bTBC\b"),
    "english_pending": re.compile(r"\bpending\b", re.IGNORECASE),
    "chinese_daiding": re.compile("待定"),
    "chinese_daiqueren": re.compile("待确认"),
    "chinese_xujinyibuqueren": re.compile("需进一步确认"),
    "chinese_shiqingkuangerding": re.compile("视情况而定"),
    "chinese_houxubuchong": re.compile("后续补充"),
    "chinese_dai_x_queren": re.compile(r"待.+确认"),
}

_DC_HOLLOW_TEMPLATE_PATTERNS: dict[str, re.Pattern[str]] = {
    "hollow_good": re.compile("具有良好的"),
    "hollow_all": re.compile("支持所有"),
    "hollow_full_compat": re.compile("兼容全部"),
    "hollow_actual": re.compile("根据实际情况"),
    "hollow_per_spec": re.compile(r"按照.+规范"),
}

_DC_DOMAIN_VOCAB_SKIP_RE = re.compile(
    r"^(slug|canonical_refs|prd|user_story|test_case|version|language|parser_contract"
    r"|truth_source_model|truth_map_contract|status|parent_feature)\s*:"
    r"|docs/beacon/"
    r"|go-todo-"
    r"|/todos"
    r"|TODO\s*(CRUD|api|model|item|handler|service|route|controller|repo|store|list|entity|struct|type|interface)"
    r"|创建的\s*TODO",
    re.IGNORECASE,
)


def _rel(project_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root.resolve()))
    except ValueError:
        return str(path)


def _finding(
    *,
    kind: str,
    file: Path,
    line: int,
    text: str,
    reason_code: str = "",
    repair_route: str = _DEFAULT_REPAIR_ROUTE,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "file": str(file),
        "line": line,
        "text": text.strip(),
        "reason_code": reason_code or kind,
        "repair_route": repair_route,
    }


def _with_repair_route(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routed: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        routed.append(
            {
                **item,
                "repair_route": str(item.get("repair_route") or _DEFAULT_REPAIR_ROUTE),
            }
        )
    return routed


def build_closure_payload_from_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, str]:
    paths = package_paths(project_root, version=version, feature=feature)
    payload: dict[str, str] = {}
    for key in ("truth", "tests", "tasks", "evidence"):
        path = paths[key]
        payload[key] = path.read_text(encoding="utf-8") if path.exists() else ""
    return payload


def scan_fake_delivery_lines(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> list[dict[str, Any]]:
    paths = package_paths(project_root, version=version, feature=feature)
    findings: list[dict[str, Any]] = []
    for key in ("truth", "tests", "tasks", "evidence"):
        path = paths[key]
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for code, pattern in _FAKE_DELIVERY_LINE_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        _finding(
                            kind=code,
                            file=path,
                            line=line_number,
                            text=line,
                            reason_code="fake_delivery_closure_blocked",
                            repair_route="beacon-gen-truth",
                        )
                    )
    return findings


def scan_determinism_lines(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> list[dict[str, Any]]:
    """TIG-DC: scan for placeholder words and hollow template sentences in feature package files."""
    paths = package_paths(project_root, version=version, feature=feature)
    findings: list[dict[str, Any]] = []

    for key in ("truth", "tests", "tasks", "evidence"):
        path = paths[key]
        if not path.exists():
            continue
        text = _read_text(path)
        lines = text.splitlines()
        in_frontmatter = False
        frontmatter_done = False
        in_code_fence = False

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Skip YAML frontmatter
            if not frontmatter_done:
                if line_number == 1 and stripped == "---":
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    if stripped == "---":
                        in_frontmatter = False
                        frontmatter_done = True
                    continue
                frontmatter_done = True

            # Skip code fences
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            # Skip domain vocabulary lines (slugs, paths, data model names)
            if _DC_DOMAIN_VOCAB_SKIP_RE.search(stripped):
                continue

            # Skip heading lines
            if stripped.startswith("#"):
                continue

            # Placeholder word detection (block severity)
            for code, pattern in _DC_PLACEHOLDER_PATTERNS.items():
                if pattern.search(stripped):
                    findings.append(
                        _finding(
                            kind=f"dc_placeholder_{code}",
                            file=path,
                            line=line_number,
                            text=line,
                            reason_code="TRUTH_DETERMINISM_PLACEHOLDER",
                            repair_route="beacon-gen-truth",
                        )
                    )

            # Hollow template detection (warn severity)
            for code, pattern in _DC_HOLLOW_TEMPLATE_PATTERNS.items():
                if pattern.search(stripped):
                    findings.append(
                        _finding(
                            kind=f"dc_hollow_{code}",
                            file=path,
                            line=line_number,
                            text=line,
                            reason_code="TRUTH_DETERMINISM_HOLLOW_TEMPLATE",
                            repair_route="beacon-gen-truth",
                        )
                    )

    return findings


def scan_integrity_extension_lines(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> list[dict[str, Any]]:
    paths = package_paths(project_root, version=version, feature=feature)
    truth_path = paths["truth"]
    tests_path = paths["tests"]
    findings: list[dict[str, Any]] = []

    truth_text = _read_text(truth_path) if truth_path.exists() else ""
    tests_text = _read_text(tests_path) if tests_path.exists() else ""

    if truth_path.exists():
        for line_number, line in enumerate(truth_text.splitlines(), start=1):
            if _PLACEHOLDER_AC_RE.search(line) and re.search(r"AC-\d{3}", line, re.IGNORECASE):
                findings.append(
                    _finding(
                        kind="placeholder_ac_language",
                        file=truth_path,
                        line=line_number,
                        text=line,
                        repair_route="beacon-gen-truth",
                    )
                )
            if _ILLEGAL_CLOSURE_RE.search(line):
                findings.append(
                    _finding(
                        kind="illegal_closure_path",
                        file=truth_path,
                        line=line_number,
                        text=line,
                        repair_route="beacon-gen-truth",
                    )
                )
            if _DEFERRAL_PENDING_RE.search(line):
                findings.append(
                    _finding(
                        kind="deferral_pending",
                        file=truth_path,
                        line=line_number,
                        text=line,
                        repair_route="beacon-gen-change",
                    )
                )

    if tests_path.exists():
        for line_number, line in enumerate(tests_text.splitlines(), start=1):
            if "|" not in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            for cell in cells:
                if _SOFT_TEST_CELL_RE.match(cell.strip()) and not _HARD_TEST_MARKERS_RE.search(line):
                    findings.append(
                        _finding(
                            kind="soft_test_assertion",
                            file=tests_path,
                            line=line_number,
                            text=line,
                            repair_route="beacon-gen-truth",
                        )
                    )
                    break

    if _OCEAN_MARKERS_RE.search(truth_text):
        if not _ALIGNMENT_SURFACE_RE.search(truth_text):
            findings.append(
                _finding(
                    kind="alignment_surface_missing",
                    file=truth_path,
                    line=1,
                    text="ocean-scope feature missing Alignment Surface or Phased Backlog section",
                    repair_route="beacon-gen-truth",
                )
            )
        if not _USER_INTENT_RE.search(truth_text):
            findings.append(
                _finding(
                    kind="user_intent_missing",
                    file=truth_path,
                    line=1,
                    text="ocean-scope feature missing User Intent section",
                    repair_route="beacon-gen-truth",
                )
            )

    return findings


def _truth_frontmatter_status(project_root: Path, version: str, feature: str) -> str:
    paths = package_paths(project_root, version=version, feature=feature)
    truth_path = paths["truth"]
    if not truth_path.exists():
        return ""
    frontmatter, _, _ = _parse_frontmatter(_read_text(truth_path))
    return str(frontmatter.get("status") or "").strip().lower()


def _validation_findings(
    project_root: Path,
    validation: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    diagnostics = validation.get("diagnostics") if isinstance(validation.get("diagnostics"), list) else []
    for diagnostic in diagnostics:
        if not isinstance(diagnostic, dict):
            continue
        severity = str(diagnostic.get("severity") or "error")
        if severity not in {"error", "warn"}:
            continue
        rel_path = str(diagnostic.get("path") or "")
        file_path = project_root / rel_path if rel_path else project_root
        findings.append(
            _finding(
                kind="feature_package_validation",
                file=file_path,
                line=1,
                text=str(diagnostic.get("code") or "validation_failed"),
                reason_code="feature_package_validation_failed",
                repair_route="beacon-gen-truth",
            )
        )
    return findings


def build_truth_integrity_gate(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    mode: Mode = "block",
) -> dict[str, Any]:
    """Build unified truth integrity gate payload for freeze/refreeze/doctor."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)

    clarity_gate = build_requirement_clarity_gate_payload(
        project_root, version=resolved_version, feature=feature
    )
    findings: list[dict[str, Any]] = _with_repair_route(
        list(clarity_gate.get("findings", [])) if isinstance(clarity_gate.get("findings"), list) else []
    )

    paths = package_paths(project_root, version=resolved_version, feature=feature)
    for key in ("truth", "tests", "tasks", "evidence"):
        if not paths[key].exists():
            findings.append(
                _finding(
                    kind="missing_package_file",
                    file=paths[key],
                    line=1,
                    text=f"missing_{key}",
                    reason_code="feature_package_incomplete",
                )
            )

    findings.extend(scan_integrity_extension_lines(project_root, version=resolved_version, feature=feature))
    findings.extend(scan_fake_delivery_lines(project_root, version=resolved_version, feature=feature))

    # TIG-DC: Determinism Check (placeholder + hollow template)
    dc_findings = scan_determinism_lines(project_root, version=resolved_version, feature=feature)
    findings.extend(dc_findings)
    dc_placeholder_count = sum(1 for f in dc_findings if f.get("reason_code") == "TRUTH_DETERMINISM_PLACEHOLDER")
    dc_hollow_count = sum(1 for f in dc_findings if f.get("reason_code") == "TRUTH_DETERMINISM_HOLLOW_TEMPLATE")

    closure_payload = build_closure_payload_from_package(
        project_root, version=resolved_version, feature=feature
    )
    fake_delivery = verify_v160_no_fake_delivery(closure_payload)

    validation = validate_feature_package(
        project_root,
        version=resolved_version,
        feature=feature,
        write_report=mode == "block",
    )
    findings.extend(_validation_findings(project_root, validation))

    truth_status = _truth_frontmatter_status(project_root, resolved_version, feature)
    integrity_findings = [f for f in findings if f.get("kind") != "inline_marker" or True]
    # TIG-DC: hollow template findings are warn-only, not blocking
    blocking_findings = [
        f for f in integrity_findings
        if f.get("reason_code") != "TRUTH_DETERMINISM_HOLLOW_TEMPLATE"
    ]
    has_blocking = bool(blocking_findings) or not fake_delivery.get("closure_allowed", True)
    if str(validation.get("status") or "").lower() == "blocked":
        has_blocking = True

    if mode == "audit" and truth_status == "frozen":
        status = "audit_only" if has_blocking else "pass"
        blocked = False
        reason_code = ""
        if has_blocking:
            reason_code = "truth_integrity_audit_findings"
    elif has_blocking:
        status = "blocked"
        blocked = True
        reason_code = str(clarity_gate.get("reason_code") or "")
        if not fake_delivery.get("closure_allowed", True):
            reason_code = str(fake_delivery.get("reason_code") or "fake_delivery_closure_blocked")
        if str(validation.get("status") or "").lower() == "blocked":
            reason_code = "feature_package_validation_failed"
        if not reason_code:
            reason_code = "truth_integrity_blocked"
    else:
        status = "pass"
        blocked = False
        reason_code = ""

    return {
        "schema_version": TIG_SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "mode": mode,
        "truth_status": truth_status,
        "status": status,
        "blocked": blocked,
        "reason_code": reason_code,
        "findings": findings,
        "finding_count": len(findings),
        "requirement_clarity": clarity_gate,
        "fake_delivery": fake_delivery,
        "feature_package_validation": validation,
        "determinism_check": {
            "placeholder_count": dc_placeholder_count,
            "hollow_template_count": dc_hollow_count,
        },
        "closure_contract": {
            "closure_allowed": fake_delivery.get("closure_allowed", not blocked),
            "detected": fake_delivery.get("detected", []),
        },
        "recommended_action": (
            "resolve_truth_integrity_findings_before_freeze"
            if blocked
            else ("review_audit_findings" if status == "audit_only" else "")
        ),
    }


def verify_closure_via_tig(
    project_root: Path,
    *,
    version: str,
    feature: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Align verify-closure with TIG fake_delivery slice."""
    if payload is None:
        payload = build_closure_payload_from_package(project_root, version=version, feature=feature)
    fake_delivery = verify_v160_no_fake_delivery(payload)
    line_findings = scan_fake_delivery_lines(project_root, version=version, feature=feature)
    if line_findings and fake_delivery.get("closure_allowed", True):
        detected = list(fake_delivery.get("detected", []))
        for item in line_findings:
            kind = str(item.get("kind") or "")
            if kind and kind not in detected:
                detected.append(kind)
        fake_delivery = {
            **fake_delivery,
            "status": "fail",
            "ok": False,
            "closure_allowed": False,
            "detected": detected,
            "reason_code": "fake_delivery_closure_blocked",
            "line_findings": line_findings,
        }
    else:
        fake_delivery = {**fake_delivery, "line_findings": line_findings}
    return fake_delivery
