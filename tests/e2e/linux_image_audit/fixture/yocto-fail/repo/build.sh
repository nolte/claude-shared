#!/bin/sh
# Single build entry point for the appliance image (CI runs the same command).
set -eu
pip install --require-hashes -r requirements-kas.txt
kas build kas.yml
deploy=build/tmp/deploy/images/qemux86-64
gh release upload "${RELEASE_TAG}" "$deploy/appliance-image-qemux86-64.rootfs.wic" \
  "$deploy/appliance-image-qemux86-64.rootfs.spdx.json"
