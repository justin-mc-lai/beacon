"""Compatibility governance registry for Beacon legacy surfaces."""

from .registry import (
    COMPATIBILITY_REGISTRY,
    REQUIRED_REGISTRY_FIELDS,
    command_aliases_from_registry,
    registry_by_id,
    required_registry_ids_from_baseline,
    validate_compatibility_registry,
)

__all__ = [
    "COMPATIBILITY_REGISTRY",
    "REQUIRED_REGISTRY_FIELDS",
    "command_aliases_from_registry",
    "registry_by_id",
    "required_registry_ids_from_baseline",
    "validate_compatibility_registry",
]
