#!/usr/bin/env python3
"""Beacon package exports."""

__version__ = "1.1.1"
__toolkit_version__ = "v1.1.1"


def create_app():
    """Build canonical beacon CLI app."""
    from .cli_factory import build_app

    return build_app(package_version=__version__)


app = create_app()


if __name__ == "__main__":
    app()
