"""Utilities for static prototype generation and governance."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

from beacon import __toolkit_version__
from beacon.utils.versioning import resolve_target_version

BOOTSTRAP_VERSION = "5.3.3"
BOOTSTRAP_ICONS_VERSION = "1.11.3"
ALPINE_VERSION = "3.14.1"
DEFAULT_UI_KIT = "bootstrap-5.3.x"
DEFAULT_GENERATOR_VERSION = f"prototype:{__toolkit_version__}"


def slugify_feature(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_files(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = prototype_dir(project_root, version, feature)
    return {
        "root": root,
        "index_html": root / "index.html",
        "manifest": root / "manifest.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
    }


def source_doc_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = slugify_feature(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "user-story": base / "user-story" / f"{slug}.md",
        "prd": base / "prd" / f"{slug}.md",
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:  # noqa: BLE001
        pass
    return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_source_documents(project_root: Path, version: str, feature: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for doc_type, path in source_doc_paths(project_root, version, feature).items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "type": doc_type,
                "path": path,
                "relative_path": str(path.relative_to(project_root)),
                "text": text,
                "fingerprint": sha256_text(text),
            }
        )
    return docs


def _doc_preview(text: str, *, max_lines: int = 6) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[:max_lines]


def _build_section_cards(source_docs: list[dict[str, Any]]) -> tuple[str, str]:
    cards: list[str] = []
    nav_links: list[str] = []
    for doc in source_docs:
        label = "User Story" if doc["type"] == "user-story" else "PRD"
        anchor = "user-story" if doc["type"] == "user-story" else "prd"
        nav_links.append(
            f'<a class="nav-link text-body-secondary" href="#{anchor}">{html.escape(label)}</a>'
        )
        preview_lines = _doc_preview(str(doc["text"]))
        preview_html = "".join(
            f"<li class=\"small text-body-secondary mb-2\">{html.escape(line[:180])}</li>"
            for line in preview_lines
        ) or '<li class="small text-body-secondary">No preview available.</li>'
        cards.append(
            f"""
            <section id="{anchor}" class="col-12 col-lg-6">
              <div class="card prototype-card h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <span class="badge text-bg-light border border-secondary-subtle">{html.escape(label)}</span>
                      <h2 class="h4 mt-3 mb-1">{html.escape(label)} Signals</h2>
                    </div>
                    <button class="btn btn-sm btn-outline-secondary" aria-label="Open {html.escape(label)} preview modal" data-bs-toggle="modal" data-bs-target="#sourcePreviewModal">
                      <i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>
                    </button>
                  </div>
                  <ul class="list-unstyled mb-0">{preview_html}</ul>
                </div>
              </div>
            </section>
            """
        )
    return "".join(cards), "".join(nav_links)


def render_bootstrap_prototype_html(feature: str, version: str, source_docs: list[dict[str, Any]]) -> str:
    title = html.escape(feature)
    cards_html, nav_links = _build_section_cards(source_docs)
    source_summary = "".join(
        f'<li><code>{html.escape(doc["relative_path"])}</code></li>' for doc in source_docs
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} · Beacon Prototype</title>
    <link rel="preconnect" href="https://cdn.jsdelivr.net">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@{BOOTSTRAP_ICONS_VERSION}/font/bootstrap-icons.min.css" rel="stylesheet">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@{ALPINE_VERSION}/dist/cdn.min.js"></script>
    <style>
      :root {{
        --beacon-bg: #0b1020;
        --beacon-surface: rgba(17, 24, 39, 0.85);
        --beacon-surface-soft: rgba(255, 255, 255, 0.82);
        --beacon-primary: #3b82f6;
        --beacon-accent: #22c55e;
        --beacon-border: rgba(148, 163, 184, 0.28);
        --beacon-shadow: 0 32px 80px rgba(15, 23, 42, 0.22);
        --beacon-radius: 24px;
      }}
      html {{ scroll-behavior: smooth; }}
      body {{
        background:
          radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 32%),
          radial-gradient(circle at top right, rgba(34,197,94,0.12), transparent 24%),
          linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        color: #0f172a;
      }}
      .prototype-shell {{
        min-height: 100vh;
      }}
      .prototype-nav {{
        backdrop-filter: blur(16px);
        background: rgba(255,255,255,0.75);
        border-bottom: 1px solid rgba(148,163,184,0.18);
      }}
      .prototype-hero {{
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
        color: #fff;
        border-radius: calc(var(--beacon-radius) + 4px);
        box-shadow: var(--beacon-shadow);
        overflow: hidden;
        position: relative;
      }}
      .prototype-hero::after {{
        content: "";
        position: absolute;
        inset: auto -20% -35% auto;
        width: 340px;
        height: 340px;
        background: radial-gradient(circle, rgba(59,130,246,0.36), transparent 72%);
        pointer-events: none;
      }}
      .prototype-card {{
        border: 1px solid var(--beacon-border);
        border-radius: var(--beacon-radius);
        background: rgba(255,255,255,0.82);
        box-shadow: 0 18px 50px rgba(15,23,42,0.08);
        backdrop-filter: blur(14px);
      }}
      .prototype-token {{
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .45rem .75rem;
        border-radius: 999px;
        background: rgba(59,130,246,0.1);
        color: #1d4ed8;
        font-size: .85rem;
        font-weight: 600;
      }}
      .prototype-status {{
        border-radius: 999px;
        padding: .4rem .7rem;
        font-size: .8rem;
        font-weight: 700;
        letter-spacing: .02em;
      }}
      .prototype-status--draft {{
        background: rgba(234,179,8,0.12);
        color: #854d0e;
      }}
      .prototype-sidebar {{
        position: sticky;
        top: 5rem;
      }}
      .prototype-preview-panel {{
        border: 1px dashed rgba(59,130,246,0.3);
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,250,252,0.84));
      }}
      .prototype-preview-surface {{
        min-height: 320px;
        border-radius: 18px;
        background: linear-gradient(180deg, #fff, #f8fafc);
        border: 1px solid rgba(226,232,240,0.9);
      }}
      .prototype-list li + li {{
        margin-top: .65rem;
      }}
      .btn-primary {{
        box-shadow: 0 14px 30px rgba(59,130,246,0.28);
      }}
      :focus-visible {{
        outline: 3px solid rgba(59,130,246,0.45);
        outline-offset: 2px;
      }}
      @media (prefers-reduced-motion: reduce) {{
        html {{ scroll-behavior: auto; }}
        *, *::before, *::after {{
          animation: none !important;
          transition: none !important;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="prototype-shell" x-data="{{ tab: 'overview', ready: true }}">
      <nav class="navbar navbar-expand-lg prototype-nav sticky-top">
        <div class="container py-2">
          <a class="navbar-brand fw-semibold" href="#top">Beacon Prototype</a>
          <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#prototypeDrawer" aria-controls="prototypeDrawer" aria-label="Open navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse">
            <div class="navbar-nav ms-auto">{nav_links}<a class="nav-link text-body-secondary" href="#prototype-preview">Preview</a></div>
          </div>
        </div>
      </nav>

      <div class="offcanvas offcanvas-end" tabindex="-1" id="prototypeDrawer" aria-labelledby="prototypeDrawerLabel">
        <div class="offcanvas-header">
          <h2 class="offcanvas-title h5 mb-0" id="prototypeDrawerLabel">Navigate</h2>
          <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close navigation"></button>
        </div>
        <div class="offcanvas-body d-flex flex-column gap-2">
          <a class="btn btn-outline-primary text-start" href="#overview">Overview</a>
          <a class="btn btn-outline-primary text-start" href="#prototype-preview">Preview</a>
          <a class="btn btn-outline-primary text-start" href="#user-story">User Story</a>
          <a class="btn btn-outline-primary text-start" href="#prd">PRD</a>
        </div>
      </div>

      <main class="container py-4 py-lg-5" id="top">
        <section class="prototype-hero p-4 p-lg-5 mb-4 mb-lg-5">
          <div class="row g-4 align-items-center">
            <div class="col-lg-8">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="prototype-token"><i class="bi bi-layout-text-window-reverse"></i> Static Single Page</span>
                <span class="prototype-token"><i class="bi bi-bootstrap-fill"></i> Bootstrap {BOOTSTRAP_VERSION}</span>
                <span class="prototype-token"><i class="bi bi-stars"></i> Beacon Theme</span>
              </div>
              <h1 class="display-6 fw-bold mb-3">{title}</h1>
              <p class="lead text-white-50 mb-4">Reference Prototype generated from Beacon requirement materials. This artifact is intended for visual alignment, review, and delivery governance.</p>
              <div class="d-flex flex-wrap gap-3">
                <a class="btn btn-primary btn-lg" href="#prototype-preview">Review Preview</a>
                <button class="btn btn-outline-light btn-lg" data-bs-toggle="modal" data-bs-target="#sourcePreviewModal">View Sources</button>
              </div>
            </div>
            <div class="col-lg-4">
              <div class="prototype-card p-4 text-dark">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <strong>Governance</strong>
                  <span class="prototype-status prototype-status--draft">DRAFT</span>
                </div>
                <ul class="list-unstyled small text-body-secondary mb-0 prototype-list">
                  <li>Version: <strong class="text-dark">{html.escape(version)}</strong></li>
                  <li>UI kit: <strong class="text-dark">{DEFAULT_UI_KIT}</strong></li>
                  <li>Generator: <strong class="text-dark">{html.escape(DEFAULT_GENERATOR_VERSION)}</strong></li>
                  <li>Sources:</li>
                  <ul>{source_summary}</ul>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <div class="row g-4">
          <aside class="col-lg-3">
            <div class="prototype-card prototype-sidebar p-3">
              <div class="nav nav-pills flex-column gap-2">
                <button class="btn btn-outline-primary text-start" @click="tab='overview'">Overview</button>
                <button class="btn btn-outline-primary text-start" @click="tab='flow'">Flow</button>
                <button class="btn btn-outline-primary text-start" @click="tab='states'">States</button>
                <button class="btn btn-outline-primary text-start" data-bs-toggle="toast" data-bs-target="#prototypeToast" aria-label="Show toast sample">Toast Sample</button>
              </div>
            </div>
          </aside>
          <div class="col-lg-9">
            <section id="overview" class="row g-4 mb-4">{cards_html}</section>

            <section id="prototype-preview" class="prototype-card p-4 p-lg-5">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
                <div>
                  <h2 class="h3 mb-2">Prototype Preview Surface</h2>
                  <p class="text-body-secondary mb-0">A single-page reference shell with tabs, modal, drawer, form states, alerts, and CTA zones.</p>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#prototypeModal">Launch Modal</button>
                  <button class="btn btn-outline-primary" data-bs-toggle="offcanvas" data-bs-target="#prototypeDrawer">Open Drawer</button>
                </div>
              </div>

              <div class="prototype-preview-panel p-3 p-lg-4">
                <div class="prototype-preview-surface p-4">
                  <ul class="nav nav-tabs mb-4">
                    <li class="nav-item"><button class="nav-link" :class="{{'active': tab==='overview'}}" @click="tab='overview'">Overview</button></li>
                    <li class="nav-item"><button class="nav-link" :class="{{'active': tab==='flow'}}" @click="tab='flow'">Flow</button></li>
                    <li class="nav-item"><button class="nav-link" :class="{{'active': tab==='states'}}" @click="tab='states'">States</button></li>
                  </ul>

                  <div x-show="tab==='overview'" class="row g-3">
                    <div class="col-md-7">
                      <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body">
                          <h3 class="h5">Primary Review Card</h3>
                          <p class="text-body-secondary">Use this area to summarize the core user outcome, constraints, and review notes.</p>
                          <div class="alert alert-primary" role="status">Prototype generated from requirement materials; freeze before gate.</div>
                          <div class="d-flex gap-2">
                            <button class="btn btn-primary">Primary CTA</button>
                            <button class="btn btn-outline-secondary">Secondary CTA</button>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-5">
                      <form class="card h-100 border-0 shadow-sm">
                        <div class="card-body">
                          <h3 class="h6 text-uppercase text-body-secondary">Quick Form</h3>
                          <label for="prototypeInput" class="form-label">Feature Signal</label>
                          <input id="prototypeInput" class="form-control mb-3" name="feature-signal" autocomplete="off" placeholder="Type a signal">
                          <label for="prototypeSelect" class="form-label">State</label>
                          <select id="prototypeSelect" class="form-select mb-3" name="feature-state">
                            <option>Draft</option>
                            <option>Frozen</option>
                            <option>Stale</option>
                          </select>
                          <button type="button" class="btn btn-success w-100">Save Prototype Note</button>
                        </div>
                      </form>
                    </div>
                  </div>

                  <div x-show="tab==='flow'" class="row g-3">
                    <div class="col-md-4"><div class="card border-0 shadow-sm h-100"><div class="card-body"><div class="text-uppercase small text-body-secondary mb-2">Step 1</div><h3 class="h5">Read Main Chain</h3><p class="text-body-secondary mb-0">Pull feature context from User Story and PRD.</p></div></div></div>
                    <div class="col-md-4"><div class="card border-0 shadow-sm h-100"><div class="card-body"><div class="text-uppercase small text-body-secondary mb-2">Step 2</div><h3 class="h5">Generate View</h3><p class="text-body-secondary mb-0">Compose Bootstrap layout with Beacon theme styling.</p></div></div></div>
                    <div class="col-md-4"><div class="card border-0 shadow-sm h-100"><div class="card-body"><div class="text-uppercase small text-body-secondary mb-2">Step 3</div><h3 class="h5">Freeze + Verify</h3><p class="text-body-secondary mb-0">Record source fingerprints and gate on stale/missing state.</p></div></div></div>
                  </div>

                  <div x-show="tab==='states'" class="row g-3">
                    <div class="col-md-3"><div class="alert alert-light border">Empty State</div></div>
                    <div class="col-md-3"><div class="alert alert-warning">Draft State</div></div>
                    <div class="col-md-3"><div class="alert alert-success">Frozen State</div></div>
                    <div class="col-md-3"><div class="alert alert-danger">Stale State</div></div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      <div class="toast-container position-fixed bottom-0 end-0 p-3">
        <div id="prototypeToast" class="toast" role="status" aria-live="polite" aria-atomic="true">
          <div class="toast-header">
            <strong class="me-auto">Beacon Prototype</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close toast"></button>
          </div>
          <div class="toast-body">Remember to freeze the prototype before delivery gate checks.</div>
        </div>
      </div>

      <div class="modal fade" id="prototypeModal" tabindex="-1" aria-labelledby="prototypeModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header">
              <h2 class="modal-title fs-5" id="prototypeModalLabel">Prototype Modal</h2>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close modal"></button>
            </div>
            <div class="modal-body">
              This modal demonstrates the default Bootstrap interaction surface expected in Beacon prototypes.
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary">Confirm</button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal fade" id="sourcePreviewModal" tabindex="-1" aria-labelledby="sourcePreviewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
          <div class="modal-content border-0 shadow-lg">
            <div class="modal-header">
              <h2 class="modal-title fs-5" id="sourcePreviewModalLabel">Source Materials</h2>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close source preview"></button>
            </div>
            <div class="modal-body">
              <p class="text-body-secondary">Prototype derived from the following materials:</p>
              <ul>{source_summary}</ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""


def write_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(
            f"No source documents found for '{feature}'. Expected at least one of: "
            + ", ".join(str(path) for path in source_doc_paths(project_root, version, feature).values())
        )

    files["root"].mkdir(parents=True, exist_ok=True)
    html_text = render_bootstrap_prototype_html(feature, version, source_docs)
    files["index_html"].write_text(html_text, encoding="utf-8")

    source_payload = {
        "feature": feature,
        "version": version,
        "derived_from": [doc["type"] for doc in source_docs],
        "source_refs": [doc["relative_path"] for doc in source_docs],
        "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
        "sections": [
            {
                "id": "overview",
                "title": "Overview",
                "derived_from": [doc["type"] for doc in source_docs],
            },
            {"id": "flow", "title": "Flow", "derived_from": [doc["type"] for doc in source_docs]},
            {"id": "states", "title": "States", "derived_from": [doc["type"] for doc in source_docs]},
        ],
    }
    manifest_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "ui_kit": DEFAULT_UI_KIT,
        "generator_version": DEFAULT_GENERATOR_VERSION,
        "prototype_type": "static-single-page",
        "artifacts": {
            "index_html": str(files["index_html"].relative_to(project_root)),
            "manifest": str(files["manifest"].relative_to(project_root)),
            "source_map": str(files["source_map"].relative_to(project_root)),
            "freeze": str(files["freeze"].relative_to(project_root)),
        },
        "source_refs": source_payload["source_refs"],
        "status": "draft",
    }
    freeze_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "version": version,
        "status": "draft",
        "frozen_at": None,
        "ui_kit": DEFAULT_UI_KIT,
        "generator_version": DEFAULT_GENERATOR_VERSION,
        "source_fingerprints": source_payload["source_fingerprints"],
        "artifact_fingerprints": {
            "index_html": sha256_file(files["index_html"]),
        },
    }
    _write_json(files["source_map"], source_payload)
    _write_json(files["manifest"], manifest_payload)
    _write_json(files["freeze"], freeze_payload)
    return {
        "feature": feature,
        "version": version,
        "root": files["root"],
        "files": files,
        "source_docs": source_docs,
    }


def freeze_prototype(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["index_html"].exists():
        raise FileNotFoundError(f"Prototype HTML not found: {files['index_html']}")
    source_docs = load_source_documents(project_root, version, feature)
    if not source_docs:
        raise FileNotFoundError(f"No source documents found for '{feature}'")
    payload = _read_json(files["freeze"])
    payload.update(
        {
            "schema_version": "1.0",
            "feature": feature,
            "version": version,
            "status": "frozen",
            "frozen_at": __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "ui_kit": DEFAULT_UI_KIT,
            "generator_version": DEFAULT_GENERATOR_VERSION,
            "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
            "artifact_fingerprints": {
                "index_html": sha256_file(files["index_html"]),
            },
        }
    )
    _write_json(files["freeze"], payload)
    manifest = _read_json(files["manifest"])
    manifest["status"] = "frozen"
    _write_json(files["manifest"], manifest)
    return payload


def evaluate_prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    exists = files["index_html"].exists()
    freeze_payload = _read_json(files["freeze"])
    manifest_payload = _read_json(files["manifest"])
    source_docs = load_source_documents(project_root, version, feature)
    current_source_hashes = {doc["type"]: doc["fingerprint"] for doc in source_docs}
    frozen_source_hashes = freeze_payload.get("source_fingerprints", {}) if isinstance(freeze_payload, dict) else {}
    status = "missing"
    stale = False
    if exists:
        status = str(freeze_payload.get("status", "draft") or "draft")
        if status == "frozen" and current_source_hashes and frozen_source_hashes:
            stale = current_source_hashes != frozen_source_hashes
            if stale:
                status = "stale"
        elif status not in {"draft", "frozen", "stale"}:
            status = "draft"
    return {
        "feature": feature,
        "version": version,
        "exists": exists,
        "status": status,
        "stale": stale,
        "ui_kit": str(manifest_payload.get("ui_kit", DEFAULT_UI_KIT) or DEFAULT_UI_KIT),
        "root": files["root"],
        "files": files,
        "source_refs": [doc["relative_path"] for doc in source_docs],
        "current_source_fingerprints": current_source_hashes,
        "frozen_source_fingerprints": frozen_source_hashes,
    }


def resolve_prototype_requirement(
    project_root: Path,
    *,
    version: str | None = None,
    feature: str | None = None,
    state: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    if isinstance(state, dict):
        enabled = bool(state.get("prototype_enabled"))
        run_feature = str(state.get("feature", "") or "") or feature
        if enabled and run_feature:
            return True, run_feature
    resolved_version = resolve_target_version(project_root, version or "auto")
    prototype_root = project_root / "docs" / "beacon" / resolved_version / "prototype"
    if feature and (prototype_root / slugify_feature(feature)).exists():
        return True, feature
    return False, feature
