#!/bin/sh
# Single build entry point for the appliance bootc image (CI runs the same command).
# podman is pinned through the builder container image (podman 5.6).
set -eu
PODMAN="quay.io/podman/stable:v5.6.2"
IMAGE="ghcr.io/example/appliance:${RELEASE_TAG}"
SOURCE_DATE_EPOCH=0
mkdir -p dist
podman run --rm --privileged -v "$PWD:/src:Z" -w /src "$PODMAN" \
  podman build --source-date-epoch="$SOURCE_DATE_EPOCH" --rewrite-timestamp \
  -t "$IMAGE" -f Containerfile .
podman push "$IMAGE"
go run github.com/anchore/syft/cmd/syft@v1.18.1 scan "registry:$IMAGE" -o cyclonedx-json=dist/appliance.cdx.json
cosign sign --yes "$IMAGE"
cosign attest --yes --type cyclonedx --predicate dist/appliance.cdx.json "$IMAGE"
