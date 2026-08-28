#!/usr/bin/env python3
"""Beacon package exports."""

__version__ = "1.6.17"
__toolkit_version__ = "v1.6.17"


def create_app():
    """Build canonical beacon CLI app."""
    from .cli_factory import build_app

    return build_app(package_version=__version__)


app = create_app()


if __name__ == "__main__":
    app()
