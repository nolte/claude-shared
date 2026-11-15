#!/bin/sh
# CI job: build twice from the same commit and compare the outputs with diffoscope.
set -eu
first="$(mktemp -d)"
./build.sh
cp -a "dist/appliance-ostree-repo.tar" "$first/"
./build.sh
diffoscope "$first/$(basename "dist/appliance-ostree-repo.tar")" "dist/appliance-ostree-repo.tar"
