"""Truth L0 human-readable + humanizer checklist helpers (v1.6.7 / v2)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REASON_L0_MISSING = "truth_human_l0_missing"
REASON_L0_BUDGET = "truth_human_l0_budget_exceeded"
REASON_LANGUAGE = "truth_human_language_invalid"

L0_HEADINGS = ("## 人话", "## Plain language")
LANG_OK = frozenset({"zh", "en", "bilingual"})

# narrative fillers (scan L0 only)
FILLER_ZH = ("此外", "值得注意的是", "综上所述", "总而言之", "至关重要")
FILLER_EN = (
    "it is important to note",
    "furthermore",
    "in conclusion",
    "evolving landscape",
    "stands as a testament",
)


def _extract_frontmatter_language(text: str) -> Optional[str]:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    block = text[3:end]
    m = re.search(r"^language:\s*(\S+)", block, re.M)
    return m.group(1).strip().strip('"\'') if m else None


def extract_l0_sections(text: str) -> Dict[str, str]:
    """Return mapping heading -> body until next ## heading."""
    found: Dict[str, str] = {}
    for h in L0_HEADINGS:
        if h not in text:
            continue
        i = text.index(h) + len(h)
        rest = text[i:]
        m = re.search(r"\n## ", rest)
        body = rest[: m.start()] if m else rest
        found[h] = body.strip()
    return found


def count_cjk(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def l0_budget_ok(heading: str, body: str) -> Tuple[bool, str]:
    lines = [ln for ln in body.splitlines() if ln.strip()]
    if len(lines) > 40:
        return False, f"lines={len(lines)}>40"
    if heading == "## 人话":
        n = count_cjk(body)
        if n > 800:
            return False, f"cjk={n}>800"
    else:
        words = re.findall(r"[A-Za-z0-9']+", body)
        if len(words) > 500:
            return False, f"words={len(words)}>500"
    return True, "ok"


def four_question_cues(body: str, lang_hint: str) -> List[str]:
    """Soft cues — not full NLP."""
    missing: List[str] = []
    b = body.lower()
    if lang_hint == "zh" or "人话" in body or any("\u4e00" <= c <= "\u9fff" for c in body[:80]):
        for key, needles in (
            ("intent", ("意图", "要", "需要", "本湖", "规定")),
            ("can", ("能做", "可以", "支持")),
            ("cannot", ("不能", "禁止", "不做", "非目标")),
            ("done", ("怎样算", "算完", "完成", "done", "验收")),
        ):
            if not any(n.lower() in b or n in body for n in needles):
                missing.append(key)
    else:
        for key, needles in (
            ("intent", ("intent", "want", "need", "this lake", "must")),
            ("can", ("can:", "can ", "able", "supports")),
            ("cannot", ("cannot", "must not", "non-goal", "out of scope")),
            ("done", ("done when", "complete", "acceptance")),
        ):
            if not any(n in b for n in needles):
                missing.append(key)
    return missing


def scan_fillers(body: str) -> List[str]:
    hits: List[str] = []
    for w in FILLER_ZH:
        if w in body:
            hits.append(w)
    bl = body.lower()
    for w in FILLER_EN:
        if w in bl:
            hits.append(w)
    return hits


def check_truth_text(text: str, *, strict_four_q: bool = False) -> Dict[str, Any]:
    lang = _extract_frontmatter_language(text) or "zh"
    if lang not in LANG_OK:
        return {
            "ok": False,
            "reason_code": REASON_LANGUAGE,
            "language": lang,
            "l0": {},
        }
    l0 = extract_l0_sections(text)
    need_zh = lang in ("zh", "bilingual")
    need_en = lang in ("en", "bilingual")
    if need_zh and "## 人话" not in l0:
        return {"ok": False, "reason_code": REASON_L0_MISSING, "language": lang, "l0": l0, "missing": ["## 人话"]}
    if need_en and "## Plain language" not in l0:
        return {"ok": False, "reason_code": REASON_L0_MISSING, "language": lang, "l0": l0, "missing": ["## Plain language"]}
    if not l0:
        return {"ok": False, "reason_code": REASON_L0_MISSING, "language": lang, "l0": l0}

    for h, body in l0.items():
        ok, detail = l0_budget_ok(h, body)
        if not ok:
            return {
                "ok": False,
                "reason_code": REASON_L0_BUDGET,
                "language": lang,
                "l0": l0,
                "detail": detail,
                "heading": h,
            }
        fillers = scan_fillers(body)
        four = four_question_cues(body, "zh" if h == "## 人话" else "en")
        if strict_four_q and four:
            return {
                "ok": False,
                "reason_code": "truth_human_l0_four_q_incomplete",
                "language": lang,
                "missing_cues": four,
                "l0": l0,
            }
        # fillers are advisory in helper; gate can escalate later
        _ = fillers

    return {
        "ok": True,
        "reason_code": "",
        "language": lang,
        "l0_headings": list(l0.keys()),
        "blocked": False,
    }


def check_truth_file(path: Path, **kwargs: Any) -> Dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    result = check_truth_text(text, **kwargs)
    result["path"] = str(path)
    return result


def norms_paths(repo_root: Path) -> Dict[str, Path]:
    base = Path(repo_root) / "skills" / "beacon" / "references" / "truth-humanizer"
    return {
        "zh": base / "truth_prose.zh.md",
        "en": base / "truth_prose.en.md",
    }


def example_paths(repo_root: Path) -> Dict[str, Path]:
    base = Path(repo_root) / "skills" / "beacon" / "examples"
    return {
        "zh": base / "truth-human-readable.zh.md",
        "en": base / "truth-human-readable.en.md",
    }
