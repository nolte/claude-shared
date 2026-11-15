#!/bin/sh
# Single build entry point for the edge-appliance image.
set -eu
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
export SOURCE_DATE_EPOCH
uvx --from 'git+https://github.com/systemd/mkosi@v26' mkosi -C images/edge-appliance build
