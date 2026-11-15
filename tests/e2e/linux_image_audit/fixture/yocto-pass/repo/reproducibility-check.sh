#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "build/tmp/deploy/images/qemux86-64/appliance-image-qemux86-64.rootfs.wic" "$first/"
./build.sh
diffoscope "$first/$(basename "build/tmp/deploy/images/qemux86-64/appliance-image-qemux86-64.rootfs.wic")" "build/tmp/deploy/images/qemux86-64/appliance-image-qemux86-64.rootfs.wic"
