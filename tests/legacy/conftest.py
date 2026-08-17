"""Legacy-archive collection guard.

Files under tests/legacy/ are historical-line tests (v1.0-v1.5) archived by
AC-004 of beacon-test-modernization-v1612. They are excluded from the default
suite via `norecursedirs` in pyproject.toml; this conftest additionally applies
the `legacy` marker so `-m 'not legacy'` behaves correctly on explicit runs.
"""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.legacy)
