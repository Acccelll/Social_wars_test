#!/usr/bin/env bash
# Builds an isolated contract harness, not a modified original client.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${MXMLC:-}" ]]; then
  COMPILER="$MXMLC"
elif [[ -n "${FLEX_HOME:-}" ]]; then
  COMPILER="$FLEX_HOME/bin/mxmlc"
else
  COMPILER="$(command -v mxmlc || true)"
fi
if [[ -z "$COMPILER" ]]; then
  echo "mxmlc unavailable" >&2
  exit 2
fi
mkdir -p "$ROOT/dist"
"$COMPILER" \
  "-target-player=32.0" \
  "-debug=true" \
  "-omit-trace-statements=false" \
  "-static-link-runtime-shared-libraries=true" \
  "-source-path+=$ROOT/as3/contract_harness/src" \
  "-source-path+=$ROOT/as3/src" \
  "-output=$ROOT/dist/ContractProbe.swf" \
  "$ROOT/as3/contract_harness/src/ContractProbe.as"
test -s "$ROOT/dist/ContractProbe.swf"
echo "CONTRACT_COMPILATION_SUCCESS: $ROOT/dist/ContractProbe.swf"
