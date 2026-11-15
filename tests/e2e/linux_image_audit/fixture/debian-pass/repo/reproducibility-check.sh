#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "dist/kiosk-rootfs.tar" "$first/"
./build.sh
diffoscope "$first/$(basename "dist/kiosk-rootfs.tar")" "dist/kiosk-rootfs.tar"
