#!/bin/sh
# Single build entry point for the appliance image (CI runs the same command).
set -eu
mkdir -p dist
nix build --impure .#nixosConfigurations.appliance.config.system.build.image -o result
nix run .#sbomnix -- ./result --spdx=dist/appliance.spdx.json
gh release upload "${RELEASE_TAG}" result/appliance.raw dist/appliance.spdx.json
