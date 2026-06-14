# Example 01: Permissive Python project, clean pass

## Input prompt

"Mach bitte einen Lizenzcheck, bevor ich das Release schneide."

## Input files (optional)

- `LICENSE` — MIT (the outbound license / compatibility anchor)
- `pyproject.toml` + `uv.lock` — Python dependencies; the pinned transitive graph
- `Taskfile.yml` — declares a `license:sbom` target (CycloneDX SBOM with resolved licenses)
- `REUSE.toml` + `LICENSES/MIT.txt` — REUSE 3.3 configuration

## Expected behaviour

1. Read the root `LICENSE`, record the outbound SPDX identifier as `MIT`, and set it as the compatibility anchor. Detect the trigger as a pre-release license gate.
2. Generate the SBOM yourself first (a skill may install and write): run `task license:sbom`, producing `sbom.cdx.json` with resolved licenses including the full transitive set.
3. Dispatch `license-check-scanner` (Agent), passing the repo root, the generated `sbom.cdx.json` path, and the outbound license `MIT`. The agent reads the SBOM, maps every component to a canonical SPDX identifier, classifies each into a category, and returns the inventory plus the REUSE state (compliant) and AI-provenance hints (none).
4. Apply the policy gate: every component resolves to a permissive category (MIT, BSD-2/3-Clause, Apache-2.0, ISC, …) on the SPDX-anchored allowlist, and each is compatible with the MIT anchor — so all are `allow`. No `review` or `deny` findings.
5. Verify own-code and attribution: `LICENSE` is a valid MIT identifier, REUSE is compliant; the plugin/product ships no third-party code, so record that no third-party NOTICE is obligated.
6. Persist the artifact to `.audits/license-check/license-YYYY-MM-DD.md` recording date, trigger, scope, tools and versions, the pinned SPDX List version, every component's SPDX id / category / tier, the Git revision, and link to the prior artifact. Report the verdict `pass` (no `deny`, every component `allow`), with the surrounding prose in German per the user-language policy while the artifact keeps English headings.
