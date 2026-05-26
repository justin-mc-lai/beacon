"""Authority role helpers for Beacon artifact wording and audits."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ArtifactRole = Literal[
    "truth",
    "projection",
    "evidence",
    "runtime_state",
    "compat_mirror",
    "historical_fixture",
]

ARTIFACT_ROLES: tuple[ArtifactRole, ...] = (
    "truth",
    "projection",
    "evidence",
    "runtime_state",
    "compat_mirror",
    "historical_fixture",
)


@dataclass(frozen=True)
class AuthorityRoots:
    truth_root: str
    projection_root: str
    runtime_evidence_root: str


def authority_roots(version: str) -> AuthorityRoots:
    normalized = str(version or "<version>").strip() or "<version>"
    truth_root = f"docs/beacon/{normalized}"
    return AuthorityRoots(
        truth_root=truth_root,
        projection_root=f"{truth_root}/.machine",
        runtime_evidence_root=".beacon",
    )


def classify_artifact_role(path: str | Path) -> ArtifactRole:
    text = str(path).replace("\\", "/").strip()
    parts = [part for part in text.split("/") if part]
    lowered = text.lower()

    if "/tests/" in f"/{lowered}/" or lowered.startswith("tests/"):
        if "legacy" in lowered or "historical" in lowered:
            return "historical_fixture"
    if "/.beacon/prd/" in f"/{lowered}/" or lowered.startswith(".beacon/prd/"):
        return "compat_mirror"
    if lowered.startswith(".beacon/") or "/.beacon/" in f"/{lowered}/":
        return "runtime_state" if "/state/" in f"/{lowered}/" else "evidence"
    if ".machine" in parts:
        return "projection"
    if "/docs/product/" in f"/{lowered}/" or lowered.startswith("docs/product/"):
        return "compat_mirror"
    if "/docs/beacon/" in f"/{lowered}/" or lowered.startswith("docs/beacon/"):
        return "truth"
    return "evidence"


def role_description(role: ArtifactRole) -> str:
    descriptions = {
        "truth": "Human-reviewed requirement truth.",
        "projection": "Deterministic machine projection or read model derived from truth.",
        "evidence": "Evidence artifact used by QA, release, or diagnostics.",
        "runtime_state": "Runtime state owned by the local Beacon execution environment.",
        "compat_mirror": "Compatibility mirror retained for older readers or migration.",
        "historical_fixture": "Historical fixture retained for regression or migration tests.",
    }
    return descriptions[role]
