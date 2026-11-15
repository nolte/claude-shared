#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "output/images/rootfs.squashfs" "$first/"
./build.sh
diffoscope "$first/$(basename "output/images/rootfs.squashfs")" "output/images/rootfs.squashfs"
