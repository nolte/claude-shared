#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "result/appliance.raw" "$first/"
./build.sh
diffoscope "$first/$(basename "result/appliance.raw")" "result/appliance.raw"
