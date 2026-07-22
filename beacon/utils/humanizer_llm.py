"""Optional LLM polish for Humanizer L0 (v1.6.10+).

Uses BEACON_LLM_* env (same as llm_loop) and oss-sync / vendored skill fulltext.
Falls back to rules when key missing or mode=rules.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any
from urllib import request


VENDOR_REL_ZH = Path("skills/beacon/references/truth-humanizer/vendor/Humanizer-zh/SKILL.md")
VENDOR_REL_EN = Path("skills/beacon/references/truth-humanizer/vendor/humanizer/SKILL.md")


def resolve_llm_mode(config: dict[str, Any] | None = None) -> str:
    """Return rules | llm | auto."""
    env = str(os.environ.get("BEACON_HUMANIZER_LLM_MODE") or os.environ.get("BEACON_LLM_MODE") or "").strip().lower()
    if env in {"real", "live", "api", "llm"}:
        return "llm"
    if env in {"rules", "rule", "offline", "0", "false", "off"}:
        return "rules"
    if env in {"auto"}:
        return "auto"
    cfg = config or {}
    mode = str(cfg.get("llm_mode") or cfg.get("mode") or "auto").strip().lower()
    if mode in {"real", "live", "api"}:
        return "llm"
    if mode in {"rules", "rule", "offline"}:
        return "rules"
    if mode == "llm":
        return "llm"
    return "auto"


def llm_available() -> bool:
    return bool(str(os.environ.get("BEACON_LLM_API_KEY") or "").strip())


def should_use_llm(config: dict[str, Any] | None = None) -> bool:
    mode = resolve_llm_mode(config)
    if mode == "rules":
        return False
    if mode == "llm":
        return llm_available()
    # auto
    return llm_available()


def vendor_humanizer_skills_into_beacon(
    project_root: Path,
    *,
    zh_source: Path | None = None,
    en_source: Path | None = None,
) -> dict[str, Any]:
    """Copy oss-sync Humanizer skills into beacon tree for offline/agent use."""
    root = Path(project_root).expanduser().resolve()
    written: list[str] = []
    skipped: list[str] = []
    mapping: list[tuple[Path | None, Path]] = [
        (zh_source, root / VENDOR_REL_ZH),
        (en_source, root / VENDOR_REL_EN),
    ]
    for src, dest in mapping:
        if src is None or not Path(src).is_file():
            skipped.append(str(dest.relative_to(root)) if dest.is_relative_to(root) else str(dest))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        try:
            written.append(str(dest.relative_to(root)))
        except Exception:  # noqa: BLE001
            written.append(str(dest))
    return {
        "schema": "humanizer-vendor.v1",
        "written": written,
        "skipped": skipped,
        "vendor_zh": str((root / VENDOR_REL_ZH)),
        "vendor_en": str((root / VENDOR_REL_EN)),
    }


def load_skill_text_prefer_vendor(
    project_root: Path,
    *,
    language: str,
    oss_skill_path: str = "",
    oss_skill_text: str = "",
) -> dict[str, Any]:
    """Prefer beacon-vendored skill, else oss-sync fulltext already loaded."""
    root = Path(project_root).expanduser().resolve()
    lang = (language or "zh").strip().lower()
    vendor = root / (VENDOR_REL_ZH if lang.startswith("zh") else VENDOR_REL_EN)
    if vendor.is_file():
        text = vendor.read_text(encoding="utf-8")
        return {"skill_path": str(vendor), "skill_text": text, "skill_chars": len(text), "source": "beacon_vendor"}
    if oss_skill_text:
        return {
            "skill_path": oss_skill_path,
            "skill_text": oss_skill_text,
            "skill_chars": len(oss_skill_text),
            "source": "oss_sync",
        }
    if oss_skill_path and Path(oss_skill_path).is_file():
        text = Path(oss_skill_path).read_text(encoding="utf-8")
        return {"skill_path": oss_skill_path, "skill_text": text, "skill_chars": len(text), "source": "oss_sync"}
    return {"skill_path": "", "skill_text": "", "skill_chars": 0, "source": "missing"}


def _chat_completion(*, system: str, user: str) -> dict[str, Any]:
    api_key = str(os.environ.get("BEACON_LLM_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("BEACON_LLM_API_KEY missing")
    api_base = str(os.environ.get("BEACON_LLM_API_BASE", "https://api.openai.com/v1")).strip().rstrip("/")
    model = str(os.environ.get("BEACON_LLM_MODEL", "gpt-4o-mini")).strip()
    timeout_s = float(str(os.environ.get("BEACON_LLM_TIMEOUT", "45")).strip() or "45")
    temperature = float(str(os.environ.get("BEACON_HUMANIZER_TEMPERATURE") or os.environ.get("BEACON_LLM_TEMPERATURE") or "0.2"))

    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    req = request.Request(
        url=f"{api_base}/chat/completions",
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with request.urlopen(req, timeout=timeout_s) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    content = ""
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first, dict) else {}
        if isinstance(message, dict):
            content = str(message.get("content") or "")
    return {
        "content": content.strip(),
        "model": model,
        "raw_usage": payload.get("usage") if isinstance(payload, dict) else {},
    }


def _strip_code_fence(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:markdown|md|text)?\n?", "", t)
        t = re.sub(r"\n?```$", "", t)
    return t.strip() + ("\n" if t.strip() else "")


def polish_l0_with_llm(
    l0_body: str,
    *,
    skill_text: str,
    language: str = "zh",
) -> dict[str, Any]:
    """Call chat completions with Humanizer skill fulltext as system guidance."""
    lang = "zh" if str(language).startswith("zh") else "en"
    skill_excerpt = (skill_text or "")[:12000]
    if lang == "zh":
        system = (
            "你是 Humanizer 编辑。严格按下方 skill 规范，只润色「人话/L0」段落：\n"
            "- 去掉 AI 套话与宣传腔\n"
            "- 保留业务事实与范围\n"
            "- 输出纯 Markdown 正文（不要标题 ## 人话，不要解释）\n"
            "- 尽量包含：能做 / 不能做 / 怎样算完\n"
            "- 禁止修改 AC ID、状态机、表格\n\n"
            f"## Skill fulltext\n{skill_excerpt}"
        )
        user = f"请润色以下 L0 正文：\n\n{l0_body}"
    else:
        system = (
            "You are a Humanizer editor. Follow the skill below. Polish ONLY the L0 plain-language section:\n"
            "- Remove AI slop\n"
            "- Keep facts and scope\n"
            "- Output pure markdown body (no ## heading, no commentary)\n"
            "- Prefer bullets: can / cannot / done when\n"
            "- Never invent AC IDs or FSM tables\n\n"
            f"## Skill fulltext\n{skill_excerpt}"
        )
        user = f"Polish this L0 body:\n\n{l0_body}"

    result = _chat_completion(system=system, user=user)
    polished = _strip_code_fence(result.get("content") or "")
    if len(polished.strip()) < 8:
        raise RuntimeError("llm_humanizer_empty_output")
    return {
        "ok": True,
        "polished": polished,
        "model": result.get("model"),
        "engine": "llm",
        "usage": result.get("raw_usage") or {},
    }
