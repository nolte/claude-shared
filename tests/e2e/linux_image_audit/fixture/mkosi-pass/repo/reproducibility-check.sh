#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "mkosi.output/edge-appliance.raw" "$first/"
./build.sh
diffoscope "$first/$(basename "mkosi.output/edge-appliance.raw")" "mkosi.output/edge-appliance.raw"
