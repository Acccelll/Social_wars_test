#!/usr/bin/env bash
# Install Apache Flex 4.16.1 and Adobe Flash 32.0 playerglobal.swc
# for CI or a local Linux development machine.
# Downloads ONLY to a temporary/local directory; never commits SDK binaries.
set -euo pipefail

VERSION="4.16.1"
SDK_URL="https://dlcdn.apache.org/flex/4.16.1/binaries/apache-flex-sdk-4.16.1-bin.tar.gz"
PLAYERGLOBAL_URL="https://fpdownload.macromedia.com/get/flashplayer/updaters/32/playerglobal32_0.swc"
DEST="${FLEX_SDK_DEST:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/social-wars-flex-sdk}"
STAGING="${DEST}.download"
mkdir -p "$DEST" "$STAGING"
archive="$STAGING/flex-sdk.tar.gz"

if [[ ! -f "$DEST/bin/mxmlc" ]]; then
  echo "Downloading Apache Flex ${VERSION} from apache.org..."
  curl --fail --location --retry 3 --connect-timeout 15 "$SDK_URL" --output "$archive"
  curl --fail --location --retry 3 --connect-timeout 15 "${SDK_URL}.md5" --output "$archive.md5"
  expected="$(sed -n 's/^\([[:xdigit:]]\{32\}\).*/\1/p' "$archive.md5" | head -n 1)"
  actual="$(md5sum "$archive" | cut -d ' ' -f 1)"
  if [[ -z "$expected" || "${expected,,}" != "${actual,,}" ]]; then
    echo "Apache-provided checksum validation failed" >&2
    exit 10
  fi
  echo "Archive checksum verified against Apache's published MD5."
  mkdir -p "$STAGING/unpacked"
  tar -xzf "$archive" -C "$STAGING/unpacked"
  if [[ -f "$STAGING/unpacked/bin/mxmlc" ]]; then
    root="$STAGING/unpacked"
  else
    root="$(find "$STAGING/unpacked" -mindepth 1 -maxdepth 6 -path '*/bin/mxmlc' -print -quit)"
    if [[ -z "$root" ]]; then
      echo "Flex SDK extraction does not contain bin/mxmlc" >&2
      exit 11
    fi
    root="${root%/bin/mxmlc}"
  fi
  # Keep the extracted tree intact and use its absolute location.
  if [[ "$root" != "$DEST" ]]; then
    cp -a "$root/." "$DEST/"
  fi
fi

player="$DEST/frameworks/libs/player/32.0/playerglobal.swc"
mkdir -p "$(dirname "$player")"
if [[ ! -s "$player" ]]; then
  echo "Downloading Adobe playerglobal.swc, Flash 32.0..."
  curl --fail --location --retry 3 --connect-timeout 15 "$PLAYERGLOBAL_URL" --output "$player"
fi
if ! unzip -t "$player" >/dev/null; then
  echo "Invalid playerglobal.swc (must be a readable SWC/ZIP)" >&2
  exit 12
fi
if [[ ! -f "$DEST/bin/mxmlc" ]]; then
  echo "mxmlc missing" >&2
  exit 13
fi

echo "Flex SDK ready: $DEST"
echo "PLAYERGLOBAL_HOME=$DEST/frameworks/libs/player"
if [[ -n "${GITHUB_ENV:-}" ]]; then
  {
    echo "FLEX_HOME=$DEST"
    echo "MXMLC=$DEST/bin/mxmlc"
    echo "PLAYERGLOBAL_HOME=$DEST/frameworks/libs/player"
  } >> "$GITHUB_ENV"
fi
