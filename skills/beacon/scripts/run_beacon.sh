#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

detect_beacon_host_runtime() {
  if [[ -n "${BEACON_HOST_RUNTIME:-}" ]]; then
    printf '%s' "${BEACON_HOST_RUNTIME}"
    return 0
  fi
  if [[ -d "${HOME}/.agents/skills/beacon" ]]; then
    printf 'codex'
    return 0
  fi
  if [[ -d "${HOME}/.claude/skills/beacon" ]]; then
    printf 'claude'
    return 0
  fi
  printf 'unknown'
}

HOST_RUNTIME="$(detect_beacon_host_runtime)"
if [[ "${HOST_RUNTIME}" != "unknown" ]]; then
  export BEACON_HOST_RUNTIME="${HOST_RUNTIME}"
fi

if [[ -z "${BEACON_HOST_PROTOTYPE_BRIDGE_CMD:-}" && "${HOST_RUNTIME}" != "unknown" ]]; then
  export BEACON_HOST_PROTOTYPE_BRIDGE_CMD="beacon prototype host-bridge"
fi
if [[ -z "${BEACON_HOST_PRD_BRIDGE_CMD:-}" && "${HOST_RUNTIME}" != "unknown" ]]; then
  export BEACON_HOST_PRD_BRIDGE_CMD="beacon prd host-bridge"
fi
if [[ -z "${BEACON_HOST_USER_STORY_BRIDGE_CMD:-}" && "${HOST_RUNTIME}" != "unknown" ]]; then
  export BEACON_HOST_USER_STORY_BRIDGE_CMD="beacon user-story host-bridge"
fi
if [[ -z "${BEACON_HOST_TEST_CASE_BRIDGE_CMD:-}" && "${HOST_RUNTIME}" != "unknown" ]]; then
  export BEACON_HOST_TEST_CASE_BRIDGE_CMD="beacon test-case host-bridge"
fi

cd "${ROOT_DIR}"
exec python3 -m beacon.main "$@"
