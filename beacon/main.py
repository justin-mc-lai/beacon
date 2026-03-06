"""Beacon CLI - Main entry point."""

from __future__ import annotations

import sys
from pathlib import Path


def _pin_beacon_import_path() -> None:
    """Ensure imports resolve from the same package root as this module."""
    package_dir = Path(__file__).resolve().parent
    package_root = str(package_dir.parent)
    sys.path = [package_root, *[p for p in sys.path if p != package_root]]

    pkg = sys.modules.get("beacon")
    if pkg is not None and hasattr(pkg, "__path__"):
        try:
            pkg.__path__ = [str(package_dir)]
        except Exception:  # noqa: BLE001
            pass


_pin_beacon_import_path()

from . import __version__
from .cli_factory import build_app

app = build_app(package_version=__version__)


if __name__ == "__main__":
    app()
