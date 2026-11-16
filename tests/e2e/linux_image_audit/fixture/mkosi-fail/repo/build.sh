#!/bin/sh
# Single build entry point for the edge-appliance image (CI runs the same command).
set -eu
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
export SOURCE_DATE_EPOCH
uvx --from 'git+https://github.com/systemd/mkosi@v26' mkosi build
go run github.com/anchore/syft/cmd/syft@v1.18.1 scan dir:mkosi.output/edge-appliance -o spdx-json=mkosi.output/edge-appliance.spdx.json
gh release upload "${RELEASE_TAG}" mkosi.output/edge-appliance.raw mkosi.output/edge-appliance.spdx.json
