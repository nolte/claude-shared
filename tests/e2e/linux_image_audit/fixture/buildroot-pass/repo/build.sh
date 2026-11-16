#!/bin/sh
# Single build entry point for the gateway image (CI runs the same command).
set -eu
out=output
make -C buildroot O="../$out" BR2_EXTERNAL="$PWD" gateway_defconfig
make -C "$out"
make -C "$out" legal-info
go run github.com/anchore/syft/cmd/syft@v1.18.1 scan dir:"$out/target" -o spdx-json="$out/images/gateway.spdx.json"
gh release upload "${RELEASE_TAG}" "$out/images/rootfs.squashfs" "$out/images/gateway.spdx.json"
