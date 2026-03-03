"""Backward-compatible module entry for `python -m beacon.think`.

Historically some integrations invoked:

    python3 -m beacon.think start "<topic>" --project <path>

Beacon's canonical entrypoint is `beacon.main`. This file keeps old
`python -m beacon.think ...` calls working by exposing the dedicated think
subcommand app directly.
"""

from __future__ import annotations

from .commands.think import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
