#!/usr/bin/env bash
# Install the Vale binary pinned in .vale-version into DEST_DIR (#768).
#
# The release asset is downloaded to a file, verified against the committed
# SHA-256 with `sha256sum -c`, and only then unpacked, so an asset replaced
# under the same tag never runs (spec/project/github-actions-best-practices/
# §A, spec/project/continuous-integration/ §C). Both workflows and
# `task install:vale` call this script, so CI and local installs share it.
#
# Usage: scripts/install_vale.sh DEST_DIR
set -euo pipefail

dest="${1:?usage: install_vale.sh DEST_DIR}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pin_file="$repo/.vale-version"

# Read the two keys with fixed patterns instead of sourcing the file, so the
# pin file can never inject shell or environment state.
version="$(sed -n 's/^VALE_VERSION=\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)$/\1/p' "$pin_file")"
checksum_line="$(sed -n 's/^VALE_SHA256=\([0-9a-f]\{64\}  vale_[0-9.]*_Linux_64-bit\.tar\.gz\)$/\1/p' "$pin_file")"
if [ -z "$version" ] || [ -z "$checksum_line" ]; then
  echo "install_vale.sh: $pin_file needs one VALE_VERSION=<x.y.z> and one VALE_SHA256=<sha256>  vale_<x.y.z>_Linux_64-bit.tar.gz line" >&2
  exit 1
fi
asset="vale_${version}_Linux_64-bit.tar.gz"
if [ "${checksum_line#*  }" != "$asset" ]; then
  echo "install_vale.sh: VALE_SHA256 is for '${checksum_line#*  }', not '$asset'." >&2
  echo "Copy the Linux_64-bit line of vale_${version}_checksums.txt from the v${version} release into $pin_file." >&2
  exit 1
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
curl -fsSL --retry 3 --retry-all-errors -o "$work/$asset" \
  "https://github.com/vale-cli/vale/releases/download/v${version}/${asset}"
(cd "$work" && printf '%s\n' "$checksum_line" | sha256sum -c -)
tar -xzf "$work/$asset" -C "$work" vale
mkdir -p "$dest"
# Run the verified binary before it replaces anything in DEST: on another OS or
# architecture it fails here and leaves an existing vale untouched.
"$work/vale" --version
install -m 0755 "$work/vale" "$dest/vale"
