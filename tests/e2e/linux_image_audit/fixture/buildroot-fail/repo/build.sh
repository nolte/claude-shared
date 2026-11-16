#!/bin/sh
# Single build entry point for the gateway image (CI runs the same command).
set -eu
out=output
make -C buildroot O="../$out" BR2_EXTERNAL="$PWD" gateway_defconfig
make -C "$out"
make -C "$out" legal-info
tar -C "$out" -czf "$out/images/gateway-legal-info.tar.gz" legal-info
gh release upload "${RELEASE_TAG}" "$out/images/rootfs.squashfs" "$out/images/gateway-legal-info.tar.gz"
