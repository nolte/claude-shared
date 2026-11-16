#!/bin/sh
# Single build entry point for the appliance OSTree commit (CI runs the same command).
set -eu
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
export SOURCE_DATE_EPOCH
ostree --repo=repo init --mode=archive
rpm-ostree compose tree --unified-core --repo=repo appliance.yaml
ostree --repo=repo checkout --user-mode appliance/x86_64/stable tree
mkdir -p dist
tar -C repo -cf dist/appliance-ostree-repo.tar .
go run github.com/anchore/syft/cmd/syft@v1.18.1 scan dir:tree -o spdx-json=dist/appliance.spdx.json
gh release upload "${RELEASE_TAG}" dist/appliance-ostree-repo.tar dist/appliance.spdx.json
