#!/usr/bin/env bash
# Build ONLY the small AS3Probe SWF; this is not the full Social Wars client.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${MXMLC:-}" ]]; then
  COMPILER="$MXMLC"
elif [[ -n "${FLEX_HOME:-}" ]]; then
  COMPILER="$FLEX_HOME/bin/mxmlc"
else
  COMPILER="$(command -v mxmlc || true)"
fi

if [[ -z "$COMPILER" || ! -f "$COMPILER" ]] && ! command -v "$COMPILER" >/dev/null 2>&1; then
  echo "COMPILER_UNAVAILABLE: install Flex 4.16.1 or run tools/bootstrap_flex_linux.sh" >&2
  exit 2
fi
mkdir -p "$ROOT/dist"
echo "Compiling AS3Probe with: $COMPILER"
"$COMPILER" \
  "-target-player=32.0" \
  "-debug=true" \
  "-omit-trace-statements=false" \
  "-static-link-runtime-shared-libraries=true" \
  "-source-path+=$ROOT/as3/src" \
  "-output=$ROOT/dist/AS3Probe.swf" \
  "$ROOT/as3/src/AS3Probe.as"
test -s "$ROOT/dist/AS3Probe.swf"
echo "COMPILATION_SUCCESS: $ROOT/dist/AS3Probe.swf"
