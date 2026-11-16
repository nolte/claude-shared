#!/bin/sh
# CI job: build the image twice from the same commit and compare the OCI archives.
set -eu
first="$(mktemp -d)"
./build.sh
podman save --format oci-archive -o "$first/appliance.oci.tar" "ghcr.io/example/appliance:${RELEASE_TAG}"
./build.sh
podman save --format oci-archive -o dist/appliance.oci.tar "ghcr.io/example/appliance:${RELEASE_TAG}"
diffoscope "$first/appliance.oci.tar" dist/appliance.oci.tar
