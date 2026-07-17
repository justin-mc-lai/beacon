"""Curated commercial DESIGN templates for unattended visual alignment.

Seeded from awesome-design-md style catalogs (inspired-by, Beacon-owned).
Not a ship authority — only baseline seed before fine-tune.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Curated first-wave commercial templates (prefer alignment over uniqueness).
COMPANY_DESIGN_TEMPLATES: dict[str, dict[str, Any]] = {
    "vercel": {
        "label": "Vercel-inspired console",
        "inspired_by": "vercel",
        "default_surface": "pc-console",
        "default_preset": "operator-console",
        "keywords": ["vercel", "developer", "deploy", "console", "edge", "next", "开发者控制台"],
        "colors": {
            "primary": "#171717",
            "on-primary": "#ffffff",
            "secondary": "#666666",
            "neutral": "#fafafa",
            "canvas": "#ffffff",
            "border": "#eaeaea",
            "link": "#0070f3",
            "danger": "#ee0000",
            "success": "#0070f3",
            "warning": "#f5a623",
        },
    },
    "stripe": {
        "label": "Stripe-inspired trust commerce",
        "inspired_by": "stripe",
        "default_surface": "web",
        "default_preset": "restrained-product",
        "keywords": ["stripe", "payment", "billing", "checkout", "支付", "结算", "金融"],
        "colors": {
            "primary": "#635bff",
            "on-primary": "#ffffff",
            "secondary": "#425466",
            "neutral": "#f6f9fc",
            "canvas": "#ffffff",
            "border": "#e3e8ee",
            "danger": "#df1b41",
            "success": "#0cce6b",
            "warning": "#ffb020",
            "ink": "#0a2540",
        },
    },
    "linear": {
        "label": "Linear-inspired workbench",
        "inspired_by": "linear.app",
        "default_surface": "pc-console",
        "default_preset": "operator-console",
        "keywords": ["linear", "issue", "sprint", "workbench", "工单", "迭代"],
        "colors": {
            "primary": "#5e6ad2",
            "on-primary": "#ffffff",
            "secondary": "#8a8f98",
            "neutral": "#0f1011",
            "canvas": "#16171a",
            "border": "#23252a",
            "danger": "#eb5757",
            "success": "#4cb782",
            "warning": "#f2c94c",
            "ink": "#f7f8f8",
        },
    },
    "notion": {
        "label": "Notion-inspired knowledge surface",
        "inspired_by": "notion",
        "default_surface": "web",
        "default_preset": "editorial-calm",
        "keywords": ["notion", "docs", "wiki", "notes", "知识库", "文档"],
        "colors": {
            "primary": "#2383e2",
            "on-primary": "#ffffff",
            "secondary": "#787774",
            "neutral": "#ffffff",
            "canvas": "#ffffff",
            "border": "#e3e2e0",
            "danger": "#eb5757",
            "success": "#0f7b6c",
            "warning": "#d9730d",
            "ink": "#37352f",
        },
    },
    "figma": {
        "label": "Figma-inspired creative chrome",
        "inspired_by": "figma",
        "default_surface": "client",
        "default_preset": "restrained-product",
        "keywords": ["figma", "design tool", "canvas", "创意", "设计工具"],
        "colors": {
            "primary": "#0d99ff",
            "on-primary": "#ffffff",
            "secondary": "#8c8c8c",
            "neutral": "#2c2c2c",
            "canvas": "#1e1e1e",
            "border": "#444444",
            "danger": "#f24822",
            "success": "#0dcf57",
            "warning": "#ffcd29",
            "ink": "#ffffff",
        },
    },
    "apple": {
        "label": "Apple-inspired restrained product",
        "inspired_by": "apple",
        "default_surface": "web",
        "default_preset": "restrained-product",
        "keywords": ["apple", "consumer", "premium", "克制", "消费级", "gallery"],
        "colors": {
            "primary": "#0071e3",
            "on-primary": "#ffffff",
            "secondary": "#6e6e73",
            "neutral": "#f5f5f7",
            "canvas": "#ffffff",
            "border": "#d2d2d7",
            "danger": "#ff3b30",
            "success": "#34c759",
            "warning": "#ff9f0a",
            "ink": "#1d1d1f",
        },
    },
    "shopify": {
        "label": "Shopify-inspired merchant admin",
        "inspired_by": "shopify",
        "default_surface": "pc-console",
        "default_preset": "operator-console",
        "keywords": ["shopify", "merchant", "commerce", "电商", "商家", "店铺后台"],
        "colors": {
            "primary": "#008060",
            "on-primary": "#ffffff",
            "secondary": "#6d7175",
            "neutral": "#f6f6f7",
            "canvas": "#ffffff",
            "border": "#c9cccf",
            "danger": "#d72c0d",
            "success": "#008060",
            "warning": "#b98900",
            "ink": "#202223",
        },
    },
    "airbnb": {
        "label": "Airbnb-inspired consumer market",
        "inspired_by": "airbnb",
        "default_surface": "web",
        "default_preset": "restrained-product",
        "keywords": ["airbnb", "marketplace", "booking", "预订", "消费市场", "住宿"],
        "colors": {
            "primary": "#ff385c",
            "on-primary": "#ffffff",
            "secondary": "#717171",
            "neutral": "#f7f7f7",
            "canvas": "#ffffff",
            "border": "#dddddd",
            "danger": "#c13515",
            "success": "#008a05",
            "warning": "#e07912",
            "ink": "#222222",
        },
    },
    "slack": {
        "label": "Slack-inspired collab client",
        "inspired_by": "slack",
        "default_surface": "client",
        "default_preset": "restrained-product",
        "keywords": ["slack", "chat", "collab", "协作", "IM", "消息客户端"],
        "colors": {
            "primary": "#611f69",
            "on-primary": "#ffffff",
            "secondary": "#616061",
            "neutral": "#f8f8f8",
            "canvas": "#ffffff",
            "border": "#dddddd",
            "danger": "#e01e5a",
            "success": "#2eb67d",
            "warning": "#ecb22e",
            "ink": "#1d1c1d",
        },
    },
    "ibm": {
        "label": "IBM-inspired enterprise console",
        "inspired_by": "ibm",
        "default_surface": "pc-console",
        "default_preset": "operator-console",
        "keywords": ["ibm", "enterprise", "carbon", "企业", "政企", "中台"],
        "colors": {
            "primary": "#0f62fe",
            "on-primary": "#ffffff",
            "secondary": "#525252",
            "neutral": "#f4f4f4",
            "canvas": "#ffffff",
            "border": "#e0e0e0",
            "danger": "#da1e28",
            "success": "#198038",
            "warning": "#f1c21b",
            "ink": "#161616",
        },
    },
}


def list_company_templates() -> dict[str, dict[str, Any]]:
    return {
        key: {
            "label": meta["label"],
            "inspired_by": meta["inspired_by"],
            "default_surface": meta["default_surface"],
            "default_preset": meta["default_preset"],
            "keywords": list(meta["keywords"]),
        }
        for key, meta in COMPANY_DESIGN_TEMPLATES.items()
    }


def auto_select_company_template(*texts: str, surface: str | None = None) -> dict[str, Any]:
    blob = "\n".join(str(t or "") for t in texts).lower()
    scores = {k: 0 for k in COMPANY_DESIGN_TEMPLATES}
    hits: dict[str, list[str]] = {k: [] for k in COMPANY_DESIGN_TEMPLATES}
    for key, meta in COMPANY_DESIGN_TEMPLATES.items():
        for kw in meta["keywords"]:
            if kw.lower() in blob:
                scores[key] += 1
                hits[key].append(kw)
        if surface and meta.get("default_surface") == surface:
            scores[key] += 0.5  # soft bias
    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] <= 0:
        # surface-based commercial default
        surface_defaults = {
            "pc-console": "vercel",
            "web": "apple",
            "h5": "airbnb",
            "client": "linear",
        }
        selected = surface_defaults.get(str(surface or "web"), "apple")
        reason = f"no company keyword; surface default → {selected}"
    else:
        selected = best[0]
        reason = f"keyword hits: {', '.join(hits[selected][:8]) or 'score'}"
    meta = COMPANY_DESIGN_TEMPLATES[selected]
    return {
        "company_template": selected,
        "label": meta["label"],
        "inspired_by": meta["inspired_by"],
        "default_surface": meta["default_surface"],
        "default_preset": meta["default_preset"],
        "colors": dict(meta["colors"]),
        "reason": reason,
        "scores": scores,
        "hits": hits.get(selected) or [],
        "catalog_size": len(COMPANY_DESIGN_TEMPLATES),
    }


def resolve_company_template_paths() -> list[str]:
    """Optional local awesome-design-md paths for copy seed (not required at runtime)."""
    home = Path.home()
    roots = [
        home / "Developer/Personal/oss-sync/design/skills/awesome-design-md/design-md",
        Path("/Users/apple/Developer/Personal/oss-sync/design/skills/awesome-design-md/design-md"),
    ]
    found: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for key, meta in COMPANY_DESIGN_TEMPLATES.items():
            inspired = str(meta.get("inspired_by") or key)
            candidate = root / inspired / "DESIGN.md"
            if candidate.exists():
                found.append(str(candidate))
    return found
