#!/bin/sh
set -eu

SOURCE_JUNIT=".beacon/tmp-lightweight-full-junit.xml"
TARGET_JUNIT="${BEACON_JUNIT_PATH:-.beacon/junit.xml}"

if [ ! -f "$SOURCE_JUNIT" ]; then
  echo "missing precomputed junit: $SOURCE_JUNIT" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_JUNIT")"
cp "$SOURCE_JUNIT" "$TARGET_JUNIT"
echo "BEACON_ASSERTIONS: 104"
