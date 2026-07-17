"""Delivery-surface design packs for Beacon unattended UI decisions.

Surfaces are copy-ready defaults for:
- pc-console  (PC 中台 / operator workbench)
- web         (public / product web)
- h5          (mobile H5)
- client      (desktop/native client shell)

Aligned with:
- google-labs-code/design.md (YAML front matter tokens + prose sections)
- awesome-design-md (reference-only brand pattern absorption)
- Beacon open-source UI agent map (vibe-to-ui / ui-ux-pro-max / impeccable)
"""

from __future__ import annotations

import re
from typing import Any

# Delivery surfaces (Beacon-owned). Auto-select from requirement truth keywords.
SURFACE_PACKS: dict[str, dict[str, Any]] = {
    "pc-console": {
        "label": "PC 中台 / Operator Console",
        "preset": "operator-console",
        "density": "compact",
        "touch_min": "32px",  # pointer-first; keep 44px for critical destructive
        "nav": "left-rail + top utility",
        "primary_pattern": "table + filter + detail drawer",
        "keywords": [
            "中台", "后台", "admin", "console", "operator", "workbench", "dashboard",
            "管理端", "运营", "crm", "erp", "b-side", "to-b", "internal tool",
            "pc 中台", "pc中台",
        ],
        "google_tokens": {
            "name": "Beacon PC Console",
            "description": "Dense operator workbench: left rail, filterable tables, detail drawers, explicit blocked/error recovery.",
            "colors": {
                "primary": "#171717",
                "on-primary": "#ffffff",
                "secondary": "#525252",
                "neutral": "#fafafa",
                "canvas": "#ffffff",
                "border": "#e5e5e5",
                "muted": "#737373",
                "danger": "#ee0000",
                "success": "#0a7",
                "warning": "#f5a623",
                "link": "#0070f3",
            },
            "typography": {
                "h1": {"fontFamily": "Geist, Inter, system-ui, sans-serif", "fontSize": "24px", "fontWeight": 600, "lineHeight": 1.25},
                "h2": {"fontFamily": "Geist, Inter, system-ui, sans-serif", "fontSize": "18px", "fontWeight": 600, "lineHeight": 1.3},
                "body-md": {"fontFamily": "Geist, Inter, system-ui, sans-serif", "fontSize": "14px", "fontWeight": 400, "lineHeight": 1.5},
                "label": {"fontFamily": "ui-monospace, SFMono-Regular, Menlo, monospace", "fontSize": "12px", "fontWeight": 500, "lineHeight": 1.3},
            },
            "rounded": {"sm": "4px", "md": "6px", "lg": "8px"},
            "spacing": {"sm": "8px", "md": "12px", "lg": "16px", "xl": "24px"},
            "components": {
                "button-primary": {"backgroundColor": "{colors.primary}", "textColor": "{colors.on-primary}", "rounded": "{rounded.md}"},
                "button-secondary": {"backgroundColor": "{colors.canvas}", "textColor": "{colors.primary}", "border": "{colors.border}"},
                "table-header": {"backgroundColor": "{colors.neutral}", "textColor": "{colors.secondary}"},
                "input": {"border": "{colors.border}", "rounded": "{rounded.sm}", "minHeight": "32px"},
            },
        },
        "do": [
            "Left rail for primary IA; overflow tools in secondary menus",
            "Tables are first-class; filters sticky; row actions explicit",
            "Blocked/error rows show recovery, not only red text",
            "Dense but readable; monospaced labels for IDs/timestamps",
        ],
        "dont": [
            "Marketing hero or mesh gradients on operator pages",
            "Card-in-card nesting for form sections",
            "Hide destructive actions without confirm",
            "Use mobile bottom-tab IA on desktop console",
        ],
    },
    "web": {
        "label": "Web Product / Marketing-capable",
        "preset": "restrained-product",
        "density": "comfortable",
        "touch_min": "44px",
        "nav": "top nav + content column",
        "primary_pattern": "content first + primary CTA",
        "keywords": [
            "web", "官网", "landing", "marketing", "saas", "to-c", "product site",
            "portal", "网站", "浏览器", "responsive web",
        ],
        "google_tokens": {
            "name": "Beacon Web Product",
            "description": "Restrained product web: quiet neutrals, one accent, content hierarchy before chrome.",
            "colors": {
                "primary": "#0071e3",
                "on-primary": "#ffffff",
                "secondary": "#6e6e73",
                "neutral": "#f5f5f7",
                "canvas": "#ffffff",
                "ink": "#1d1d1f",
                "border": "#d2d2d7",
                "danger": "#ff3b30",
                "success": "#34c759",
                "warning": "#ff9f0a",
            },
            "typography": {
                "h1": {"fontFamily": "SF Pro Display, system-ui, -apple-system, sans-serif", "fontSize": "40px", "fontWeight": 600, "lineHeight": 1.1, "letterSpacing": "-0.02em"},
                "h2": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "24px", "fontWeight": 600, "lineHeight": 1.25},
                "body-md": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "16px", "fontWeight": 400, "lineHeight": 1.5},
                "label": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "13px", "fontWeight": 500, "lineHeight": 1.3},
            },
            "rounded": {"sm": "6px", "md": "8px", "lg": "12px"},
            "spacing": {"sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"},
            "components": {
                "button-primary": {"backgroundColor": "{colors.primary}", "textColor": "{colors.on-primary}", "rounded": "{rounded.md}", "minHeight": "44px"},
                "button-secondary": {"backgroundColor": "transparent", "textColor": "{colors.ink}", "border": "{colors.border}"},
                "card": {"backgroundColor": "{colors.canvas}", "border": "{colors.border}", "rounded": "{rounded.md}"},
            },
        },
        "do": [
            "One primary CTA per viewport",
            "Quiet neutrals + single accent",
            "Product imagery or content first; chrome recedes",
            "Explicit empty/loading/error/success",
        ],
        "dont": [
            "Purple-to-blue AI gradients",
            "Multiple competing primaries",
            "Glassmorphism decoration",
            "Dense admin tables as the default public IA",
        ],
    },
    "h5": {
        "label": "H5 / Mobile Web",
        "preset": "restrained-product",
        "density": "comfortable",
        "touch_min": "44px",
        "nav": "bottom tab or top back stack",
        "primary_pattern": "single-column + sticky primary action",
        "keywords": [
            "h5", "mobile", "移动端", "小程序", "wechat", "ios", "android webview",
            "touch", "手机", "m-site", "responsive mobile",
        ],
        "google_tokens": {
            "name": "Beacon H5 Mobile",
            "description": "Thumb-first mobile web: single column, sticky CTA, large targets, bottom or stack navigation.",
            "colors": {
                "primary": "#0071e3",
                "on-primary": "#ffffff",
                "secondary": "#6e6e73",
                "neutral": "#f5f5f7",
                "canvas": "#ffffff",
                "ink": "#1d1d1f",
                "border": "#e5e5ea",
                "danger": "#ff3b30",
                "success": "#34c759",
                "warning": "#ff9f0a",
            },
            "typography": {
                "h1": {"fontFamily": "system-ui, -apple-system, sans-serif", "fontSize": "22px", "fontWeight": 600, "lineHeight": 1.25},
                "body-md": {"fontFamily": "system-ui, -apple-system, sans-serif", "fontSize": "16px", "fontWeight": 400, "lineHeight": 1.5},
                "label": {"fontFamily": "system-ui, -apple-system, sans-serif", "fontSize": "12px", "fontWeight": 500, "lineHeight": 1.3},
            },
            "rounded": {"sm": "8px", "md": "12px", "lg": "16px"},
            "spacing": {"sm": "8px", "md": "12px", "lg": "16px", "xl": "20px"},
            "components": {
                "button-primary": {"backgroundColor": "{colors.primary}", "textColor": "{colors.on-primary}", "rounded": "{rounded.lg}", "minHeight": "44px"},
                "list-row": {"minHeight": "48px", "border": "{colors.border}"},
                "tab-bar": {"backgroundColor": "{colors.canvas}", "border": "{colors.border}", "minHeight": "49px"},
            },
        },
        "do": [
            "Single column; sticky primary action in thumb zone",
            "44px+ targets; avoid hover-only affordances",
            "Bottom tab or clear back stack",
            "Forms one primary field group per screen",
        ],
        "dont": [
            "Desktop multi-column tables as default",
            "Tiny icon-only hit targets",
            "Hover tooltips as sole instruction",
            "Fixed left rail navigation",
        ],
    },
    "client": {
        "label": "Desktop / Native Client",
        "preset": "restrained-product",
        "density": "comfortable",
        "touch_min": "32px",
        "nav": "app chrome + content pane (+ optional sidebar)",
        "primary_pattern": "shell + document/work surface",
        "keywords": [
            "client", "desktop", "electron", "tauri", "native", "extension",
            "客户端", "桌面端", "mac app", "windows app", "chrome extension", "plugin",
        ],
        "google_tokens": {
            "name": "Beacon Desktop Client",
            "description": "Native-feeling app shell: titlebar/chrome restraint, content pane focus, keyboard-first shortcuts.",
            "colors": {
                "primary": "#0071e3",
                "on-primary": "#ffffff",
                "secondary": "#6e6e73",
                "neutral": "#f5f5f7",
                "canvas": "#ffffff",
                "ink": "#1d1d1f",
                "border": "#d2d2d7",
                "chrome": "#ececec",
                "danger": "#ff3b30",
                "success": "#34c759",
            },
            "typography": {
                "h1": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "20px", "fontWeight": 600, "lineHeight": 1.25},
                "body-md": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "13px", "fontWeight": 400, "lineHeight": 1.45},
                "label": {"fontFamily": "SF Pro Text, system-ui, -apple-system, sans-serif", "fontSize": "11px", "fontWeight": 500, "lineHeight": 1.3},
            },
            "rounded": {"sm": "4px", "md": "6px", "lg": "8px"},
            "spacing": {"sm": "6px", "md": "10px", "lg": "14px", "xl": "20px"},
            "components": {
                "button-primary": {"backgroundColor": "{colors.primary}", "textColor": "{colors.on-primary}", "rounded": "{rounded.sm}", "minHeight": "28px"},
                "toolbar": {"backgroundColor": "{colors.chrome}", "border": "{colors.border}", "minHeight": "40px"},
                "sidebar": {"backgroundColor": "{colors.neutral}", "border": "{colors.border}", "width": "240px"},
            },
        },
        "do": [
            "Respect OS window chrome; content pane is primary",
            "Keyboard shortcuts for frequent actions",
            "Sidebar optional; never steal focus from document",
            "Extension UIs stay compact and state-honest",
        ],
        "dont": [
            "Web marketing layout inside native shell",
            "Ignore platform safe areas / traffic lights",
            "Modal spam for routine actions",
            "H5 bottom-tab pattern on desktop client",
        ],
    },
}

_SURFACE_ALIASES = {
    "pc": "pc-console",
    "console": "pc-console",
    "admin": "pc-console",
    "mid": "pc-console",
    "中台": "pc-console",
    "web": "web",
    "www": "web",
    "h5": "h5",
    "mobile": "h5",
    "m": "h5",
    "client": "client",
    "desktop": "client",
    "native": "client",
    "extension": "client",
}


def list_surfaces() -> dict[str, dict[str, Any]]:
    return {
        key: {
            "label": pack["label"],
            "preset": pack["preset"],
            "density": pack["density"],
            "nav": pack["nav"],
            "primary_pattern": pack["primary_pattern"],
            "keywords": list(pack["keywords"]),
        }
        for key, pack in SURFACE_PACKS.items()
    }


def resolve_surface(surface: str | None) -> str:
    key = str(surface or "auto").strip().lower().replace("_", "-")
    if key in {"", "auto"}:
        return "auto"
    return _SURFACE_ALIASES.get(key, key if key in SURFACE_PACKS else "web")


def auto_select_surface_from_text(*texts: str) -> dict[str, Any]:
    """Pick delivery surface from requirement/design truth text (unattended)."""
    blob = "\n".join(str(t or "") for t in texts).lower()
    scores: dict[str, int] = {k: 0 for k in SURFACE_PACKS}
    hits: dict[str, list[str]] = {k: [] for k in SURFACE_PACKS}
    for key, pack in SURFACE_PACKS.items():
        for kw in pack["keywords"]:
            if kw.lower() in blob:
                scores[key] += 1
                hits[key].append(kw)
    # defaults: if nothing matched, prefer web product; if admin+web both, prefer higher score
    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] <= 0:
        selected = "web"
        reason = "no surface keywords; default web product"
    else:
        selected = best[0]
        # tie-break priority for operator work when equal
        tied = [k for k, v in scores.items() if v == best[1]]
        if len(tied) > 1:
            priority = ["pc-console", "client", "h5", "web"]
            selected = next(p for p in priority if p in tied)
        reason = f"keyword hits: {', '.join(hits[selected][:8])}"
    pack = SURFACE_PACKS[selected]
    return {
        "surface": selected,
        "label": pack["label"],
        "preset": pack["preset"],
        "reason": reason,
        "scores": scores,
        "hits": hits[selected],
    }


def google_yaml_frontmatter(surface: str, *, product_name: str = "") -> str:
    """Emit google-labs-code/design.md compatible YAML front matter."""
    key = resolve_surface(surface)
    if key == "auto" or key not in SURFACE_PACKS:
        key = "web"
    pack = SURFACE_PACKS[key]
    tokens = pack["google_tokens"]
    name = str(product_name or tokens.get("name") or pack["label"]).strip()
    lines = ["---", "version: alpha", f"name: {name}"]
    desc = str(tokens.get("description") or "").strip()
    if desc:
        # YAML plain string; escape quotes lightly
        safe = desc.replace('"', "'")
        lines.append(f'description: "{safe}"')
    lines.append("colors:")
    for ck, cv in (tokens.get("colors") or {}).items():
        lines.append(f'  {ck}: "{cv}"')
    lines.append("typography:")
    for tk, tv in (tokens.get("typography") or {}).items():
        lines.append(f"  {tk}:")
        if isinstance(tv, dict):
            for pk, pv in tv.items():
                if isinstance(pv, str):
                    lines.append(f'    {pk}: "{pv}"' if any(c in pv for c in " ,") else f"    {pk}: {pv}")
                else:
                    lines.append(f"    {pk}: {pv}")
        else:
            lines.append(f"    value: {tv}")
    lines.append("rounded:")
    for rk, rv in (tokens.get("rounded") or {}).items():
        lines.append(f"  {rk}: {rv}")
    lines.append("spacing:")
    for sk, sv in (tokens.get("spacing") or {}).items():
        lines.append(f"  {sk}: {sv}")
    lines.append("components:")
    for ck, cv in (tokens.get("components") or {}).items():
        lines.append(f"  {ck}:")
        if isinstance(cv, dict):
            for pk, pv in cv.items():
                lines.append(f'    {pk}: "{pv}"')
    lines.append("---")
    return "\n".join(lines)


def surface_copy_elements(surface: str) -> dict[str, Any]:
    """Copy-ready design elements for a delivery surface."""
    key = resolve_surface(surface)
    if key == "auto" or key not in SURFACE_PACKS:
        key = "web"
    pack = SURFACE_PACKS[key]
    tokens = pack["google_tokens"]["colors"]
    return {
        "surface": key,
        "label": pack["label"],
        "css_variables": {
            "--bg": tokens.get("neutral") or tokens.get("canvas"),
            "--fg": tokens.get("ink") or tokens.get("primary"),
            "--card": tokens.get("canvas") or "#ffffff",
            "--border": tokens.get("border") or tokens.get("hairline") or "#e5e5e5",
            "--muted": tokens.get("muted") or tokens.get("secondary"),
            "--primary": tokens.get("primary") or tokens.get("link"),
            "--primary-fg": tokens.get("on-primary") or "#ffffff",
            "--danger": tokens.get("danger") or "#ff3b30",
            "--success": tokens.get("success") or "#34c759",
            "--warning": tokens.get("warning") or "#ff9f0a",
            "--radius": pack["google_tokens"]["rounded"].get("md", "8px"),
            "--touch-min": pack["touch_min"],
            "--density": pack["density"],
        },
        "nav": pack["nav"],
        "primary_pattern": pack["primary_pattern"],
        "do": list(pack["do"]),
        "dont": list(pack["dont"]),
        "components": pack["google_tokens"].get("components") or {},
    }


def scan_truth_for_ux(truth_markdown: str) -> dict[str, Any]:
    """Detect whether requirement truth claims visual delivery."""
    text = str(truth_markdown or "")
    lowered = text.lower()
    signals = []
    if re.search(r"ux_required\s*:\s*true", text, re.I):
        signals.append("ux_required:true")
    if re.search(r"design_required\s*:\s*true", text, re.I):
        signals.append("design_required:true")
    for token in (
        "ui-state-matrix",
        "visual",
        "界面",
        "视觉",
        "ui/ux",
        "design.md",
        "页面",
        "前端",
        "sidebar",
        "fullscreen",
        "badge",
        "layout",
    ):
        if token in lowered:
            signals.append(token)
    return {
        "visual_delivery_claimed": bool(signals),
        "signals": signals[:20],
    }
