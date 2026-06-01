#!/usr/bin/env python3
"""Beacon package exports."""

__version__ = "1.4.13"
__toolkit_version__ = "v1.4.13"


def create_app():
    """Build canonical beacon CLI app."""
    from .cli_factory import build_app

    return build_app(package_version=__version__)


app = create_app()


if __name__ == "__main__":
    app()
