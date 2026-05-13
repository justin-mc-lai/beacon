#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/status"
BEACON_BIN="${ROOT_DIR}/beacon-cli"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --queue)
      QUEUE_PATH="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --beacon-bin)
      BEACON_BIN="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date '+%Y%m%dT%H%M%S')"
OUT_FILE="${OUTPUT_DIR}/status-${TIMESTAMP}.txt"

{
  echo "job=beacon-status-job"
  echo "timestamp=${TIMESTAMP}"
  echo "project_root=${PROJECT_ROOT}"
  echo "queue=${QUEUE_PATH}"
  echo "beacon_bin=${BEACON_BIN}"
  echo
  "${BEACON_BIN}" status --project-root "${PROJECT_ROOT}" --version "${VERSION}" show-status
} | tee "${OUT_FILE}"

echo "wrote ${OUT_FILE}"
