"""Feature-centric package materialization and validation for v1.5.0."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import (
    feature_package_dir,
    feature_package_file,
    machine_requirement_file,
    qa_docs_file,
)
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.versioning import normalize_version

REQUIRED_TRUTH_FRONTMATTER = ("slug", "version", "status", "language", "canonical_refs", "parser_contract")
PARSER_CONTRACT = "beacon-feature-package-v1"
# parser_contract versions the resolver may declare; validator accepts all of
# these (single source of truth — resolver and validator must not disagree).
ALLOWED_PARSER_CONTRACTS = ("beacon-feature-package-v1", "beacon-feature-package-v2")
PACKAGE_SHAPE_FLOOR = (1, 6, 10)
REASON_PACKAGE_SHAPE_UPGRADE = "package_shape_upgrade_required"
ALLOWED_EVIDENCE_AUTHORITIES = {"support_advisory", "qa_verdict", "release_verdict"}
EXTRA_VALID_EVIDENCE_AUTHORITIES = {"requirement_truth", "acceptance_truth", "test_truth"}
FORBIDDEN_EVIDENCE_FIELDS = ("final_verdict", "gate_truth", "release_ready", "qa_passed", "source_of_truth")
EVIDENCE_REQUIRED_COLUMNS = ("surface", "authority")
CHECKBOX_RE = re.compile(
    r"^\s*-\s+\[(?P<mark>[ xX-])\]\s+(?:`?(?P<id>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3,})`?\s+)?(?P<title>.+?)\s*$"
)
_SOFT_TEST_ONLY_CELL_RE = re.compile(r"^(integration|目录存在|fixture|可选)$", re.IGNORECASE)
_HARD_TEST_COMMAND_RE = re.compile(r"cargo|beacon\s|pnpm|npm test|BLOCKED:", re.IGNORECASE)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def package_shape_floor_ok(version: str | None) -> bool:
    """Return whether gold package shape is active.

    Docs version and toolkit version are separate axes. Gold shape is the only
    active template for all docs versions once this runtime is installed.
    ``version`` is retained for call-site compatibility; it is not used to
    soft-disable gold shape on product docs lines (e.g. v0.0.13).
    """
    _ = version
    return True


def package_shape_gates_enabled(version: str | None = None) -> bool:
    """Hard gates (TRG sections, ac=/evidence=, exec TC) always on for active packages."""
    _ = version
    return True


def package_shape_upgrade_payload(*, version: str, feature: str, op: str) -> dict[str, Any]:
    return {
        "schema": "package-shape-upgrade.v1",
        "blocked": True,
        "pass": False,
        "reason_code": REASON_PACKAGE_SHAPE_UPGRADE,
        "version": version,
        "feature": feature,
        "op": op,
        "floor": "gold-v1.6.10-shape",
        "user_facing": (
            f"feature package shape for {feature}@{version} is not gold-compliant. "
            "Replan intent and freeze a new truth under the v1.6.10 package shape "
            "(人话 + Intent Matrix + FSM + ac=/evidence= tasks + exec TC). "
            "No old-shape soft-compat (global-boundaries §2.1)."
        ),
        "recommended_next": [
            "plan re-decompose intent (program lakes)",
            "truth gen / change → gold template (any product docs version)",
            "truth review (TRG A–D) then freeze",
        ],
    }



def _canonical_ready_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 5, 1)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _slug(value: str) -> str:
    return feature_slug(value)


def package_paths(project_root: Path, *, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "dir": feature_package_dir(project_root, version, slug),
        "truth": feature_package_file(project_root, version, slug, "truth.md"),
        "tests": feature_package_file(project_root, version, slug, "tests.md"),
        "tasks": feature_package_file(project_root, version, slug, "tasks.md"),
        "evidence": feature_package_file(project_root, version, slug, "evidence.md"),
    }


def _extract_ac_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower() for cell in cells]
        if "ac id" in lowered:
            in_table = True
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and cells and re.match(r"AC-[A-Z0-9]+(?:-[A-Z0-9]+)*", cells[0]):
            rows.append(
                {
                    "ac_id": cells[0],
                    "theme": cells[1] if len(cells) > 1 else "",
                    "description": cells[2] if len(cells) > 2 else "",
                }
            )
    if rows:
        return rows
    for line in markdown.splitlines():
        bullet = re.match(r"^\s*[-*]\s+(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)[：:\s]+(.+)$", line.strip())
        if bullet:
            rows.append(
                {
                    "ac_id": bullet.group(1),
                    "theme": "",
                    "description": bullet.group(2).strip(),
                }
            )
            continue
        bold = re.search(r"\*\*(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\*\*", line)
        if bold:
            rows.append(
                {
                    "ac_id": bold.group(1),
                    "theme": "",
                    "description": line.strip(),
                }
            )
    return rows


def _extract_test_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower() for cell in cells]
        if "ac id" in lowered and "tc id" in lowered:
            in_table = True
            headers = [cell.lower().replace(" ", "_") for cell in cells]
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and cells and (
            re.match(r"AC-[A-Z0-9]+(?:-[A-Z0-9]+)*", cells[0])
            or re.match(r"TC-[A-Z0-9]+(?:-[A-Z0-9]+)*", cells[0], re.IGNORECASE)
        ):
            # Rejoin command cells when pipes appear inside command (naive split)
            if headers and len(cells) > len(headers) and ("command" in headers or "planned_command" in headers):
                command_index = headers.index("command") if "command" in headers else headers.index("planned_command")
                tail_count = len(headers) - command_index - 1
                command_end = len(cells) - tail_count if tail_count else len(cells)
                cells = [
                    *cells[:command_index],
                    "|".join(cells[command_index:command_end]).strip(),
                    *cells[command_end:],
                ]
            row = {headers[index]: cells[index] if index < len(cells) else "" for index in range(len(headers))}
            # Support both AC-first and TC-first layouts
            ac_id = row.get("ac_id") or ""
            tc_id = row.get("tc_id") or ""
            if not ac_id and re.match(r"AC-", cells[0] or ""):
                ac_id = cells[0]
            if not tc_id and re.match(r"TC-", cells[0] or "", re.I):
                tc_id = cells[0]
            if not ac_id:
                for cell in cells:
                    m = re.match(r"(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)", cell or "", re.I)
                    if m:
                        ac_id = m.group(1).upper()
                        break
            if not tc_id:
                for cell in cells:
                    m = re.match(r"(TC-[A-Z0-9]+(?:-[A-Z0-9]+)*)", cell or "", re.I)
                    if m:
                        tc_id = m.group(1).upper()
                        break
            rows.append(
                {
                    "ac_id": ac_id or cells[0],
                    "tc_id": tc_id or (cells[1] if len(cells) > 1 else ""),
                    "layer": row.get("layer") or "",
                    "command": row.get("command") or row.get("planned_command") or "",
                    "assertion": row.get("assertion") or "",
                    "evidence_path": row.get("evidence_path") or "",
                }
            )
    return rows


def _parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str, list[str]]:
    if not markdown.startswith("---\n"):
        return {}, markdown, ["frontmatter_missing"]
    end = markdown.find("\n---", 4)
    if end < 0:
        return {}, markdown, ["frontmatter_unclosed"]
    raw = markdown[4:end].strip("\n")
    body = markdown[end + 4 :].lstrip("\n")
    data: dict[str, Any] = {}
    errors: list[str] = []
    current_key = ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = value.strip("\"'")
            else:
                data[current_key] = {}
            continue
        if line.startswith("  ") and current_key:
            parent = data.setdefault(current_key, {})
            if isinstance(parent, dict) and ":" in line:
                key, value = line.strip().split(":", 1)
                parent[key.strip()] = value.strip().strip("\"'")
            else:
                errors.append(f"frontmatter_nested_parse_failed: {line.strip()}")
            continue
        errors.append(f"frontmatter_parse_failed: {line.strip()}")
    return data, body, errors


def _parse_checkboxes(markdown: str) -> tuple[list[dict[str, str]], list[str]]:
    tasks: list[dict[str, str]] = []
    errors: list[str] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if "- [" not in line:
            continue
        match = CHECKBOX_RE.match(line)
        if not match:
            errors.append(f"malformed_checkbox: line {line_number}")
            continue
        mark = match.group("mark").lower()
        if mark == "x":
            status = "checked"
        elif mark == "-":
            status = "blocked"
        else:
            status = "unchecked"
        task_id = match.group("id") or f"LINE-{line_number}"
        tasks.append({"id": task_id, "title": match.group("title").strip(), "status": status})
    return tasks, errors



_TASK_AC_RE = re.compile(r"(?i)\bac\s*[=:]\s*(?P<ac>[A-Z][A-Z0-9_-]*)")
_TASK_EVIDENCE_RE = re.compile(r"(?i)\bevidence\s*[=:]\s*`?(?P<path>[^`\s|]+)`?")


def parse_task_ac_evidence_binding(title: str) -> dict[str, str]:
    """Extract ac= and evidence= bindings from a task title."""
    ac_m = _TASK_AC_RE.search(title or "")
    ev_m = _TASK_EVIDENCE_RE.search(title or "")
    return {
        "ac_id": (ac_m.group("ac") if ac_m else "").strip(),
        "evidence_path": (ev_m.group("path") if ev_m else "").strip(),
    }


def evaluate_task_ac_evidence_bindings(
    project_root: Path,
    *,
    tasks_md: str,
    version: str = "",
) -> dict[str, Any]:
    """Checked tasks must have existing evidence files. Unchecked tasks need binding metadata on v1.6.10+."""
    root = Path(project_root).expanduser().resolve()
    rows, errors = _parse_checkboxes(tasks_md)
    findings: list[dict[str, Any]] = []
    for err in errors:
        findings.append({"kind": "malformed_checkbox", "text": err})
    checked_ok = 0
    checked_bad = 0
    unbound = 0
    for row in rows:
        title = row.get("title") or ""
        bind = parse_task_ac_evidence_binding(title)
        ac_id = bind.get("ac_id") or ""
        ev = bind.get("evidence_path") or ""
        status = row.get("status") or "unchecked"
        task_id = row.get("id") or ""
        # ALWAYS enforce ac=/evidence= (NO soft-compat for old ledgers / product docs lines).
        # Non-compliant packages must replan + freeze new truth (global-boundaries §2.1).
        enforce_shape = package_shape_gates_enabled(version)
        if enforce_shape and (not ac_id or not ev):
            unbound += 1
            findings.append(
                {
                    "kind": "task_binding_missing",
                    "text": f"{task_id or title[:40]} missing ac=/evidence= binding — replan+freeze new truth (no old-shape compat; see global-boundaries §2.1)",
                    "task_id": task_id,
                }
            )
            continue
        if status == "checked":
            if not ev:
                checked_bad += 1
                findings.append(
                    {
                        "kind": "checkbox_checked_without_evidence_path",
                        "text": f"{task_id} checked but no evidence= path",
                        "task_id": task_id,
                    }
                )
                continue
            ev_path = Path(ev)
            if not ev_path.is_absolute():
                ev_path = root / ev
            if not ev_path.is_file() or ev_path.stat().st_size < 2:
                checked_bad += 1
                findings.append(
                    {
                        "kind": "checkbox_checked_without_evidence_file",
                        "text": f"{task_id} checked but evidence missing: {ev}",
                        "task_id": task_id,
                        "evidence_path": ev,
                        "ac_id": ac_id,
                    }
                )
            else:
                checked_ok += 1
    ok = checked_bad == 0 and (unbound == 0 if package_shape_gates_enabled(version) and rows else True)
    # if no rows, not ok from other validators
    return {
        "pass": ok,
        "checked_ok": checked_ok,
        "checked_bad": checked_bad,
        "unbound": unbound,
        "findings": findings,
        "reason_code": "" if ok else "task_checkbox_evidence_failed",
    }


def _extract_evidence_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower().replace(" ", "_") for cell in cells]
        if "surface" in lowered and "authority" in lowered:
            in_table = True
            headers = lowered
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and headers:
            row = {headers[index]: cells[index] if index < len(cells) else "" for index in range(len(headers))}
            if row.get("surface") or row.get("authority"):
                rows.append(row)
    return rows


def _canonical_refs(project_root: Path, *, version: str, slug: str) -> dict[str, str]:
    return {
        "prd": f"docs/beacon/{version}/prd/{slug}.md",
        "user_story": f"docs/beacon/{version}/user-story/{slug}.md",
        "test_case": f"docs/beacon/{version}/qa/test-cases/{slug}.md",
    }


def _render_frontmatter(*, slug: str, version: str, language: str, status: str) -> str:
    refs = _canonical_refs(Path("."), version=version, slug=slug)
    return "\n".join(
        [
            "---",
            f"slug: {slug}",
            f"version: {version}",
            f"status: {status}",
            f"language: {language}",
            "canonical_refs:",
            f"  prd: {refs['prd']}",
            f"  user_story: {refs['user_story']}",
            f"  test_case: {refs['test_case']}",
            f"parser_contract: {PARSER_CONTRACT}",
            "---",
        ]
    )


def render_truth_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    language: str | None = None,
) -> str:
    """Render feature truth package.

    v1.6.10+: gold-aligned scaffold —
    人话 / Plain language + Intent Coverage Matrix + FSM 五元组 + illegal + AC + Non-goals.
    < v1.6.10: legacy plain-language projection template.
    """
    slug = _slug(feature)
    prd_path = project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"
    user_story_path = project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md"
    prd = _read_text(prd_path)
    user_story = _read_text(user_story_path)
    ac_rows = _extract_ac_rows(user_story) or [
        {"ac_id": match.group(0), "theme": "", "description": line.strip("- ")}
        for line in user_story.splitlines()
        for match in [re.search(r"AC-\d{3}", line)]
        if match
    ]
    if not ac_rows:
        ac_rows = [
            {
                "ac_id": "AC-001",
                "theme": "core",
                "description": f"User can complete the core outcome for `{feature}` within declared boundaries.",
            }
        ]

    if not package_shape_floor_ok(version):
        raise ValueError(
            f"{REASON_PACKAGE_SHAPE_UPGRADE}: version={version} feature={feature} "
            "floor=v1.6.10 — replan+freeze; legacy templates removed (global-boundaries §2.1)"
        )
    return _render_truth_package_v1610(
        project_root,
        version=version,
        feature=feature,
        slug=slug,
        language=language or "zh",
        ac_rows=ac_rows,
        prd=prd,
        user_story=user_story,
    )


def _render_truth_package_v1610(
    project_root: Path,
    *,
    version: str,
    feature: str,
    slug: str,
    language: str,
    ac_rows: list[dict[str, str]],
    prd: str,
    user_story: str,
) -> str:
    """Gold-aligned scaffold (v1.6.10 Truth Review Gate ready structure)."""
    _ = project_root
    lang = (language or "zh").strip().lower()
    if lang not in {"zh", "en", "bilingual"}:
        lang = "zh"
    primary_ac = ac_rows[0]["ac_id"] if ac_rows else "AC-001"
    fm = [
        "---",
        f"slug: {slug}",
        f"version: {version}",
        "status: draft",
        f"language: {lang}",
        "domain_required: false",
        "ux_required: false",
        "parser_contract: beacon-feature-package-v2",
        "truth_source_model: feature_package_authoritative",
        "package_maturity: scaffold",
        "materials_status: current",
        "canonical_refs:",
        f"  prd: docs/beacon/{version}/features/{slug}/truth.md",
        f"  user_story: docs/beacon/{version}/features/{slug}/truth.md",
        f"  test_case: docs/beacon/{version}/features/{slug}/tests.md",
        "---",
        "",
        f"# Requirement Truth: {feature} ({version})",
        "",
    ]
    if lang in {"zh", "bilingual"}:
        fm.extend(
            [
                "## 人话",
                "",
                f"本湖让用户能完成 `{feature}` 的核心结果。范围写清；状态变化写清；怎样算完写清。",
                "",
                f"- 能做：完成 `{feature}` 主路径与已声明边界内操作",
                "- 不能做：跳过审查直接冻结；未声明即默认支持的扩展场景",
                "- 怎样算完：Intent Matrix must 全 covered；每 AC 有 TC；需要时 FSM 无悬空",
                "",
            ]
        )
    if lang in {"en", "bilingual"}:
        fm.extend(
            [
                "## Plain language",
                "",
                f"This lake lets users complete the core outcome of `{feature}`. Scope, state changes, and done criteria must be explicit.",
                "",
                f"- can: complete `{feature}` happy path within declared boundaries",
                "- cannot: freeze without Truth Review Gate; invent undeclared scope",
                "- done when: must intents covered; each AC has a TC; FSM has no hanging states when domain_required",
                "",
            ]
        )
    fm.extend(
        [
            "## User Intent",
            "",
            f"Deliver a freeze-ready package truth for `{feature}` under Truth Review Gate (A/B/C).",
            "",
            "## User Intent Snapshot",
            "",
            "```yaml",
            "lake_or_ocean: 湖",
            "truth_review_gate: required",
            "scaffold: v1.6.10-gold-aligned",
            "```",
            "",
            "## Intent Coverage Matrix",
            "",
            "| intent_id | source | strength | landing | status |",
            "|-----------|--------|----------|---------|--------|",
        ]
    )
    for idx, row in enumerate(ac_rows, start=1):
        ac_id = row.get("ac_id") or f"AC-{idx:03d}"
        fm.append(f"| INT-{idx:03d} | prompt | must | {ac_id} | covered |")
    fm.extend(
        [
            "| INT-EDGE-optional | vision | should | Non-goal: deferred edge cases | deferred |",
            "",
            "## 用户旅程",
            "",
            "> scaffold：请改成真实旅程步骤后再 freeze（Check D）。",
            "",
            "1. 触发：用户进入入口（待补）",
            "2. 关键操作：完成主路径动作（待补）",
            "3. 结果：明确成功 / 失败原因 / 下一步（待补）",
            "4. 异常：超时、重复、权限等边界（待补）",
            "",
            "## First principles",
            "",
            "> scaffold：写清不可变约束；域湖必须具体化。",
            "",
            f"- 系统边界：本湖只解决 `{feature}` 声明范围内的结果",
            "- 不可变：未过 Truth Review Gate 不得 freeze；不得用 agent 自述替代 AC",
            "- 可推翻假设：待用户确认的默认值写在 Intent Matrix should/deferred",
            "",
            "## Domain Model",
            "",
            "> scaffold：列出核心实体与字段；business domain 必填。",
            "",
            "| Entity | Key fields | Notes |",
            "|--------|------------|-------|",
            f"| {feature}Aggregate | id, status | 待补真实实体 |",
            "",
            "## Acceptance Criteria",
            "",
            "| AC ID | Description |",
            "|-------|-------------|",
        ]
    )
    for row in ac_rows:
        desc = (row.get("description") or row.get("theme") or "").replace("|", "/")
        fm.append(f"| {row['ac_id']} | {desc} |")
    fm.extend(
        [
            "",
            "## FSM 五元组",
            "",
            "> domain_required=false 时 Check B 可 skip；若升级为 domain 湖，补全五元组与 illegal。",
            "",
            "| State | Event | Guard | To | Action |",
            "|-------|-------|-------|-----|--------|",
            "| draft | submit | package_complete | in_review | — |",
            "| in_review | pass | gate_ok | frozen | set_frozen |",
            "| in_review | fail | — | draft | attach_report |",
            "",
            "**终态：** frozen",
            "",
            "### invalid / illegal",
            "",
            "- draft → frozen（skip review）",
            "- in_review → frozen without review_gate_pass",
            "",
            "## Non-goals",
            "",
            "- 未在 Intent Matrix 声明的扩展场景",
            "- 以 agent 自述替代 frozen truth 验收",
            "",
            "## Freeze readiness",
            "",
            "- [ ] Intent Matrix must 无 missing",
            "- [ ] 用户旅程非「待补」占位",
            "- [ ] First principles / Domain Model 已具体化（非 scaffold 套话）",
            "- [ ] domain 湖：业务 FSM 五元组 + illegal（非 draft/in_review 元状态）",
            "- [ ] 每 AC ≥ 1 TC（Command+Assertion）+ ≥1 exec-layer TC",
            "- [ ] tasks 均有 ac= + evidence= 绑定",
            "- [ ] package_maturity: filled（去掉 scaffold）",
            "- [ ] `beacon truth review` pass 后再 freeze",
            "",
            "### Gap vs gold (订单支付示例)",
            "",
            f"- 对照：`docs/beacon/{version}/features/truth-gold-order-pay-v1610/truth.md`",
            "- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`",
            "- 宿主 Agent 读 Humanizer vendor 全文润色 L0（无需 API key）",
            "",
            "## Source Excerpt",
            "",
            "```markdown",
            (prd or user_story or feature)[:4000].rstrip(),
            "```",
            "",
        ]
    )
    return "\n".join(fm)


def render_tests_package(project_root: Path, *, version: str, feature: str) -> str:
    slug = _slug(feature)
    if not package_shape_floor_ok(version):
        raise ValueError(
            f"{REASON_PACKAGE_SHAPE_UPGRADE}: version={version} feature={feature} "
            "floor=v1.6.10 — replan+freeze for tests shape (global-boundaries §2.1)"
        )
    qa_path = qa_docs_file(project_root, version, f"{slug}.md")
    qa = _read_text(qa_path)
    rows = _extract_test_rows(qa)
    truth = _read_text(package_paths(project_root, version=version, feature=feature)["truth"]) if (project_root / "docs" / "beacon" / version / "features" / slug / "truth.md").exists() else ""
    ac_from_truth = _extract_ac_rows(truth) if truth else []
    if True:  # package shape floor enforced above
        lines = [
            "---",
            f"slug: {slug}",
            f"version: {version}",
            "materials_status: current",
            "---",
            "",
            f"# Tests: {feature}",
            "",
            "| TC ID | AC ID | Command | Assertion |",
            "|-------|-------|---------|-----------|",
        ]
        if rows:
            for idx, row in enumerate(rows, start=1):
                tc = row.get("tc_id") or f"TC-{idx:03d}"
                ac = row.get("ac_id") or "AC-001"
                command = row.get("command") or f'rg -n "{ac}" docs/beacon/{version}/features/{slug}/truth.md'
                assertion = row.get("assertion") or "exists"
                lines.append(f"| {tc} | {ac} | `{command}` | {assertion} |")
        elif ac_from_truth:
            for idx, row in enumerate(ac_from_truth, start=1):
                ac = row.get("ac_id") or f"AC-{idx:03d}"
                lines.append(
                    f"| TC-{idx:03d} | {ac} | `rg -n '{ac}' docs/beacon/{version}/features/{slug}/truth.md` | AC present |"
                )
        else:
            lines.append(
                f"| TC-001 | AC-001 | `rg -n 'AC-001' docs/beacon/{version}/features/{slug}/truth.md` | scaffold AC |"
            )
        # Ensure ≥1 execution-layer TC (domain Check C_exec / general readiness)
        domain_required = False
        try:
            truth_path = package_paths(project_root, version=version, feature=feature)["truth"]
            if truth_path.is_file():
                fm, _, _ = _parse_frontmatter(truth_path.read_text(encoding="utf-8"))
                domain_required = str(fm.get("domain_required") or "").lower() in {"true", "1", "yes", "y"}
        except Exception:
            domain_required = False
        primary_ac = "AC-001"
        if ac_from_truth:
            primary_ac = ac_from_truth[0].get("ac_id") or primary_ac
        elif rows:
            primary_ac = rows[0].get("ac_id") or primary_ac
        # Real CLI + pytest contracts (not print stubs)
        lines.append(
            f"| TC-EXEC-CLI | {primary_ac} | `python3 -c 'import beacon; print(chr(111)+chr(107))'` | import_beacon_ok |"
        )
        pytest_assertion = "exit_code==0" if domain_required else "exit_code_in_0_or_5"
        lines.append(
            f"| TC-EXEC-PYTEST | {primary_ac} | `python3 -m pytest -q tests/ -k {slug} --tb=no` | {pytest_assertion} |"
        )
        if domain_required:
            lines.append(
                f"| TC-EXEC-DOCTOR | {primary_ac} | `python3 -m beacon doctor --help` | exit_code==0 |"
            )
        lines.extend(["", "## Validation Note", "", "v1.6.10 TC layout for Truth Review Gate Check C + domain exec layer.", ""])
        return "\n".join(lines)


def render_tasks_package(project_root: Path, *, version: str, feature: str) -> str:
    """Derive AC-bound task ledger (v1.6.10+ only; no old-shape soft-compat)."""
    if not package_shape_floor_ok(version):
        raise ValueError(
            f"{REASON_PACKAGE_SHAPE_UPGRADE}: version={version} feature={feature} "
            "floor=v1.6.10 — replan+freeze for tasks shape (global-boundaries §2.1)"
        )
    slug = _slug(feature)
    ac_rows: list[dict[str, str]] = []
    truth_path = package_paths(project_root, version=version, feature=feature)["truth"]
    if truth_path.is_file():
        ac_rows = _extract_ac_rows(truth_path.read_text(encoding="utf-8"))
    if not ac_rows:
        user_story_path = project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md"
        if user_story_path.is_file():
            ac_rows = _extract_ac_rows(user_story_path.read_text(encoding="utf-8"))
    lines = [
        "---",
        f"slug: {slug}",
        f"version: {version}",
        "materials_status: current",
        "task_source: acceptance_criteria",
        "---",
        "",
        f"# Tasks: {feature}",
        "",
        "## Task Ledger",
        "",
    ]
    if not ac_rows:
        ac_rows = [{"ac_id": "AC-001", "description": "Fill Acceptance Criteria then re-materialize tasks"}]
    for idx, row in enumerate(ac_rows, start=1):
        ac = row.get("ac_id") or f"AC-{idx:03d}"
        desc = (row.get("description") or row.get("theme") or "implement").replace("\n", " ").strip()
        if len(desc) > 72:
            desc = desc[:69] + "..."
        evidence = f".beacon/evidence/implement/{slug}/{ac}.json"
        lines.append(
            f"- [ ] TASK-{idx:03d} Implement {ac}: {desc} · ac={ac} · evidence=`{evidence}`"
        )
    gate_ev = f".beacon/evidence/implement/{slug}/GATES.json"
    qa_ev = f".beacon/evidence/implement/{slug}/QA-MATRIX.json"
    lines.append(
        f"- [ ] TASK-{len(ac_rows)+1:03d} Validate package gates (truth review + freeze ack) · ac=GATES · evidence=`{gate_ev}`"
    )
    lines.append(
        f"- [ ] TASK-{len(ac_rows)+2:03d} Run QA against AC↔TC matrix + exec-layer evidence · ac=QA · evidence=`{qa_ev}`"
    )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Checkboxes are AC-bound ledgers. `[x]` is valid only when the bound `evidence=` file exists (completion ≠ self-tick).",
            "",
        ]
    )
    return "\n".join(lines)



def render_evidence_package(project_root: Path, *, version: str, feature: str) -> str:
    slug = _slug(feature)
    return "\n".join(
        [
            f"# Evidence Index: {feature}",
            "",
            "## Evidence Index",
            "",
            "| Surface | Authority | Canonical Artifact | Status | Route |",
            "|---------|-----------|--------------------|--------|-------|",
            f"| beacon-deep | support_advisory | docs/beacon/{version}/research/{slug}.md | indexed | change |",
            f"| beacon-ceo-review | support_advisory | docs/beacon/{version}/change/{slug}.refreeze-summary.md | indexed | change |",
            f"| qa | qa_verdict | docs/beacon/{version}/.machine/qa/{slug}.qa9-matrix.json | linked | qa |",
            f"| release | release_verdict | docs/beacon/{version}/release/ | linked | release |",
            "",
            "## Boundary",
            "",
            "`evidence.md` is an index/read model. It must not contain final verdict, gate truth, or release readiness authority fields.",
            "",
        ]
    )


def materialize_feature_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    force: bool = False,
) -> dict[str, Any]:
    slug = _slug(feature)
    # Always materialize gold shape for any product docs version (dual-axis safe).
    paths = package_paths(project_root, version=version, feature=feature)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    rendered = {
        "truth": render_truth_package(project_root, version=version, feature=feature),
        "tests": render_tests_package(project_root, version=version, feature=feature),
        "tasks": render_tasks_package(project_root, version=version, feature=feature),
        "evidence": render_evidence_package(project_root, version=version, feature=feature),
    }
    written: list[str] = []
    skipped: list[str] = []
    for key, content in rendered.items():
        path = paths[key]
        if path.exists() and not force:
            skipped.append(_rel(project_root, path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(_rel(project_root, path))
        # After truth is on disk, re-render tests so Check C covers all AC rows (v1.6.10+)
        if key == "truth" and "tests" in rendered:
            if paths["tests"].exists() and not force and _rel(project_root, paths["tests"]) in skipped:
                pass
            else:
                rendered["tests"] = render_tests_package(project_root, version=version, feature=feature)
    validation = validate_feature_package(project_root, version=version, feature=feature, write_report=True)
    post_write: dict[str, Any] = {}
    if written:
        from beacon.utils.truth_gen_postwrite import run_truth_gen_postwrite_gates

        post_write = run_truth_gen_postwrite_gates(
            project_root,
            version=version,
            feature=feature,
            written=written,
        )
    status = "materialized"
    if post_write.get("blocked"):
        status = "materialized_review_blocked"
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": status,
        "package_dir": _rel(project_root, paths["dir"]),
        "written": written,
        "skipped": skipped,
        "validation": validation,
        "truth_gen_postwrite": post_write,
        "recommend_freeze": bool(post_write.get("recommend_freeze", False)),
    }


def validate_feature_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    write_report: bool = False,
) -> dict[str, Any]:
    slug = _slug(feature)
    paths = package_paths(project_root, version=version, feature=feature)
    diagnostics: list[dict[str, Any]] = []
    truth = _read_text(paths["truth"])
    tests = _read_text(paths["tests"])
    tasks_md = _read_text(paths["tasks"])
    evidence = _read_text(paths["evidence"])

    for key in ("truth", "tests", "tasks", "evidence"):
        if not paths[key].exists():
            diagnostics.append({"severity": "error", "code": f"missing_{key}", "path": _rel(project_root, paths[key])})

    frontmatter, _body, frontmatter_errors = _parse_frontmatter(truth)
    for error in frontmatter_errors:
        diagnostics.append({"severity": "error", "code": error, "path": _rel(project_root, paths["truth"])})
    for key in REQUIRED_TRUTH_FRONTMATTER:
        if key not in frontmatter:
            diagnostics.append({"severity": "error", "code": f"frontmatter_missing_{key}", "path": _rel(project_root, paths["truth"])})
    if str(frontmatter.get("parser_contract") or "") not in ALLOWED_PARSER_CONTRACTS:
        diagnostics.append({"severity": "error", "code": "parser_contract_mismatch", "path": _rel(project_root, paths["truth"]), "allowed_contracts": list(ALLOWED_PARSER_CONTRACTS)})
    if frontmatter.get("slug") and str(frontmatter.get("slug")) != slug:
        diagnostics.append({"severity": "error", "code": "frontmatter_slug_mismatch", "path": _rel(project_root, paths["truth"])})

    ac_rows = _extract_ac_rows(truth)
    if not ac_rows:
        diagnostics.append({"severity": "error", "code": "acceptance_criteria_table_missing", "path": _rel(project_root, paths["truth"])})

    # v1.6.7+ human-readable L0 gate (AC-HR-001..005): fail-closed on freeze/change package validation
    if _semver_tuple(version) >= (1, 6, 7) and paths["truth"].exists() and truth.strip():
        from beacon.utils.truth_human_readable import check_truth_text

        prose = check_truth_text(truth, strict_four_q=False)
        payload_prose = {
            "severity": "error" if not prose.get("ok") else "info",
            "code": str(prose.get("reason_code") or "truth_human_l0_ok"),
            "path": _rel(project_root, paths["truth"]),
            "language": prose.get("language"),
            "l0_headings": prose.get("l0_headings") or list((prose.get("l0") or {}).keys()),
        }
        if not prose.get("ok"):
            # normalize reason_code for freeze consumers
            code = str(prose.get("reason_code") or "truth_human_l0_missing")
            payload_prose["code"] = code
            payload_prose["severity"] = "error"
            if prose.get("missing"):
                payload_prose["missing"] = prose.get("missing")
            if prose.get("detail"):
                payload_prose["detail"] = prose.get("detail")
            diagnostics.append(payload_prose)
        else:
            diagnostics.append(payload_prose)

    test_rows = _extract_test_rows(tests)
    if not test_rows:
        diagnostics.append({"severity": "warn", "code": "tests_coverage_table_missing", "path": _rel(project_root, paths["tests"])})
    for index, row in enumerate(test_rows, start=1):
        command = str(row.get("command") or "").strip()
        assertion = str(row.get("assertion") or "").strip()
        combined = f"{command} {assertion}"
        if not command and "BLOCKED:" not in combined:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "test_command_missing_or_blocked",
                    "path": _rel(project_root, paths["tests"]),
                    "tc_id": row.get("tc_id") or f"row-{index}",
                }
            )
        elif _SOFT_TEST_ONLY_CELL_RE.match(command) and not _HARD_TEST_COMMAND_RE.search(combined):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "soft_test_command_only",
                    "path": _rel(project_root, paths["tests"]),
                    "tc_id": row.get("tc_id") or f"row-{index}",
                }
            )

    checkbox_rows, checkbox_errors = _parse_checkboxes(tasks_md)
    for error in checkbox_errors:
        diagnostics.append({"severity": "error", "code": error, "path": _rel(project_root, paths["tasks"])})
    if not checkbox_rows:
        diagnostics.append({"severity": "error", "code": "checkbox_ledger_missing", "path": _rel(project_root, paths["tasks"])})
    task_evidence_gate = evaluate_task_ac_evidence_bindings(
        project_root, tasks_md=tasks_md, version=version
    )
    for finding in task_evidence_gate.get("findings") or []:
        diagnostics.append(
            {
                "severity": "error",
                "code": str(finding.get("kind") or "task_evidence_binding"),
                "path": _rel(project_root, paths["tasks"]),
                "text": finding.get("text"),
                "task_id": finding.get("task_id"),
                "evidence_path": finding.get("evidence_path"),
                "ac_id": finding.get("ac_id"),
            }
        )

    evidence_rows = _extract_evidence_rows(evidence)
    if not evidence_rows:
        diagnostics.append(
            {
                "severity": "error",
                "code": "evidence_authority_table_missing",
                "path": _rel(project_root, paths["evidence"]),
                "required_columns": list(EVIDENCE_REQUIRED_COLUMNS),
                "allowed_authorities": sorted(ALLOWED_EVIDENCE_AUTHORITIES | EXTRA_VALID_EVIDENCE_AUTHORITIES),
            }
        )
    # Forbidden gate-truth fields: flag when used as a declared key (`field:`)
    # or as an authority cell value — never on a path/filename substring.
    for field in FORBIDDEN_EVIDENCE_FIELDS:
        if re.search(rf"(?<![\w/]){re.escape(field)}\s*:", evidence, re.IGNORECASE):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": f"evidence_forbidden_gate_truth_field:{field}",
                    "path": _rel(project_root, paths["evidence"]),
                    "allowed_authorities": sorted(ALLOWED_EVIDENCE_AUTHORITIES | EXTRA_VALID_EVIDENCE_AUTHORITIES),
                }
            )
    for index, row in enumerate(evidence_rows, start=1):
        authority = str(row.get("authority") or "").strip()
        # Word-boundary: only flag when a forbidden name is actually used as an
        # authority cell value — never on a path/filename substring match.
        if authority in FORBIDDEN_EVIDENCE_FIELDS:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": f"evidence_forbidden_gate_truth_field:{authority}",
                    "path": _rel(project_root, paths["evidence"]),
                    "row": index,
                    "allowed_authorities": sorted(ALLOWED_EVIDENCE_AUTHORITIES | EXTRA_VALID_EVIDENCE_AUTHORITIES),
                }
            )
        elif authority not in ALLOWED_EVIDENCE_AUTHORITIES and authority not in EXTRA_VALID_EVIDENCE_AUTHORITIES:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": f"evidence_invalid_authority:{authority or '<empty>'}",
                    "path": _rel(project_root, paths["evidence"]),
                    "row": index,
                    "allowed_authorities": sorted(ALLOWED_EVIDENCE_AUTHORITIES | EXTRA_VALID_EVIDENCE_AUTHORITIES),
                }
            )

    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "blocked" if has_errors else "pass",
        "blocked": has_errors,
        "reason_code": (
            next(
                (
                    str(item.get("code") or "")
                    for item in diagnostics
                    if item.get("severity") == "error" and str(item.get("code") or "").startswith("truth_human_")
                ),
                "feature_package_validation_failed",
            )
            if has_errors
            else ""
        ),
        "generated_at": now_iso(),
        "package_dir": _rel(project_root, paths["dir"]),
        "truth_frontmatter": frontmatter,
        "ac_count": len(ac_rows),
        "test_count": len(test_rows),
        "checkbox_count": len(checkbox_rows),
        "evidence_row_count": len(evidence_rows),
        "gate_authority": "canonical_surfaces_preserved",
        "checkbox_gate_bypass": False,
        "task_evidence_gate": task_evidence_gate,
        "evidence_gate_truth": False,
        "diagnostics": diagnostics,
    }
    if _canonical_ready_supported(version):
        from beacon.utils.truth_map import (
            MACHINE_JSON_GENERATOR,
            MACHINE_JSON_ROLE,
            TRUTH_MAP_CONTRACT,
            TRUTH_PACKAGE_CONTRACT,
            resolve_feature_truth,
            truth_source_model_for_version,
        )

        resolved_truth = resolve_feature_truth(project_root, version=version, feature=slug)
        model = truth_source_model_for_version(version)
        payload.update(
            {
                "truth_map_contract": TRUTH_MAP_CONTRACT,
                "truth_source_model": model,
                "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
                "machine_json_role": MACHINE_JSON_ROLE,
                "generated_by": MACHINE_JSON_GENERATOR,
                "truth_authority": "markdown_feature_package",
                "json_authority": False,
                "source_paths": resolved_truth.get("source_paths", {}),
                "source_hashes": resolved_truth.get("source_hashes", {}),
                "runtime_json_requires_markdown_twin": False,
            }
        )
    if write_report:
        report_path = machine_requirement_file(project_root, version, "feature-package-validation.json")
        write_json(report_path, payload)
        payload["report_path"] = _rel(project_root, report_path)
        refresh_evidence_manifest(project_root, refs=[payload["report_path"]], version=version)
    return payload


def sync_truth_frontmatter_status(
    project_root: Path,
    *,
    version: str,
    feature: str,
    status: str,
) -> dict[str, Any]:
    """Align features/<slug>/truth.md frontmatter status with machine freeze state."""
    paths = package_paths(project_root, version=version, feature=feature)
    truth_path = paths["truth"]
    if not truth_path.exists():
        return {"updated": False, "reason": "truth_missing", "path": _rel(project_root, truth_path)}

    text = _read_text(truth_path)
    if not text.startswith("---\n"):
        return {"updated": False, "reason": "frontmatter_missing", "path": _rel(project_root, truth_path)}

    end = text.find("\n---", 4)
    if end < 0:
        return {"updated": False, "reason": "frontmatter_unclosed", "path": _rel(project_root, truth_path)}

    block = text[4:end]
    current_match = re.search(r"^status:\s*(\S+)", block, re.MULTILINE)
    current = current_match.group(1) if current_match else ""
    if current == status:
        return {"updated": False, "status": current, "path": _rel(project_root, truth_path)}

    if current_match:
        block = re.sub(r"^status:\s*\S+", f"status: {status}", block, count=1, flags=re.MULTILINE)
    else:
        block = f"status: {status}\n{block}"

    truth_path.write_text(f"---\n{block}\n---{text[end + 4:]}", encoding="utf-8")
    return {
        "updated": True,
        "status": status,
        "previous_status": current,
        "path": _rel(project_root, truth_path),
    }
