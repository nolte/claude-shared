---
title: Release delivery
audience: [dogfooding-author, ci-operator]
content_mode: reference
track: developer-docs
last_updated: 2026-09-13
---

# Release delivery

What this repository ships, which stage secures each artifact class, what records its
provenance, and how to recover from a bad version. It's the per-project mapping
`spec/project/continuous-delivery/` §D asks for.

## Artifact classes

| Artifact class | Published as | Securing stage | Guarantee | Provenance record | Signed attestation |
| --- | --- | --- | --- | --- | --- |
| Plugin release (all five plugins, lockstep) | Git tag `vX.Y.Z` and its GitHub Release, installed from the marketplace | `release-publish.yml`: pre-publish verification, license verdict | policy-cleared; integrity through the immutable tag | The tag's commit SHA, and the `release-publish.yml` run that flipped the draft | None: a git tag carries no artifact bytes an attestation could bind, so this class has no verification path |
| Documentation site | The `gh-pages` branch served by GitHub Pages | `release-cd-deliver-docs.yml`, after `mkdocs build --strict` passed in the `docs` required check | built-from-source | The deploy commit on `gh-pages`, whose message names the source commit | None: GitHub Pages offers no verification path |

Release tags can't be deleted or moved: the repository ruleset `release-tags-immutable`
blocks deletion, update, and non-fast-forward changes to `refs/tags/v*`, so a version
reference always resolves to the same commit.

## Rollback

Recovery selects an earlier version; it never rebuilds an old commit.

- **Plugins:** a consumer pins the marketplace to the last good release tag and
  installs the plugins again from it:

    ```bash
    claude plugin marketplace add nolte/claude-shared@v0.1.10
    ```

- **Documentation site:** redeploy the site from the last good tag:

    ```bash
    gh workflow run release-cd-deliver-docs.yml --ref v0.1.10
    ```

- Record why the version was withdrawn in the next release's notes.
