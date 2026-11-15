#!/bin/sh
# Single build entry point for the kiosk image (CI runs the same command).
set -eu
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
# The archive snapshot is pinned to the same moment as SOURCE_DATE_EPOCH.
SNAPSHOT="$(date -u -d "@${SOURCE_DATE_EPOCH}" +%Y%m%dT%H%M%SZ)"
MIRROR="http://snapshot.debian.org/archive/debian/${SNAPSHOT}/"
export SOURCE_DATE_EPOCH
mkdir -p dist
mmdebstrap --variant=minbase --include="$(paste -sd, packages.list)" \
  --aptopt='Acquire::Check-Valid-Until "false"' \
  --customize-hook='copy-in overlay/usr /' \
  --customize-hook='chroot "$1" systemctl enable appliance-health.service' \
  --customize-hook='truncate -s 0 "$1/etc/machine-id"' \
  --customize-hook='rm -f "$1/var/lib/systemd/random-seed" "$1"/etc/ssh/ssh_host_*' \
  bookworm dist/kiosk-rootfs.tar "$MIRROR"
go run github.com/anchore/syft/cmd/syft@v1.18.1 scan file:dist/kiosk-rootfs.tar -o spdx-json=dist/kiosk-rootfs.spdx.json
gh release upload "${RELEASE_TAG}" dist/kiosk-rootfs.tar dist/kiosk-rootfs.spdx.json
