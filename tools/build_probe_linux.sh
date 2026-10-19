#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MXMLC="${MXMLC:-mxmlc}"
if ! command -v "$MXMLC" >/dev/null 2>&1; then
  echo "COMPILER_UNAVAILABLE: mxmlc is not available." >&2
  exit 2
fi
mkdir -p "$ROOT/dist"
"$MXMLC" "-source-path+=$ROOT/as3/src" "-output=$ROOT/dist/AS3Probe.swf" "$ROOT/as3/src/AS3Probe.as"
test -s "$ROOT/dist/AS3Probe.swf"
echo "COMPILATION_SUCCESS: $ROOT/dist/AS3Probe.swf"
