# Example 02: Augment a Python library draft release with PyPI / changelog / migration sections

## Input prompt

"Shape the release notes for this library — operators need PyPI install lines and a migration note for the breaking change in `client.py`."

## Input files

- `pyproject.toml` — declares a distributable package (`[project]` with `name = "acme-sdk"`, `version = "2.0.0"`, classifiers including `Development Status :: 5 - Production/Stable`), no `[project.scripts]` block — signal 3 (Python library) matches; previous tagged version was `1.4.2`, so this is a major-version bump
- `src/acme_sdk/client.py` — public API surface; `git diff v1.4.2..origin/develop -- src/acme_sdk/` shows a renamed exported symbol (`AcmeClient.fetch` → `AcmeClient.get`), one new exported symbol (`AcmeClient.stream`), and a removed deprecated parameter on `__init__`
- `CHANGELOG.md` — already maintained per Keep-a-Changelog; the `## [Unreleased]` section lists the same three changes, suitable for cross-linking
- `docs/migrations/v2.md` — committed in the same window with a step-by-step `1.x → 2.x` migration recipe
- `AUDIENCES.md` — audience artefact pinning two primary audiences: "SDK consumers" (downstream applications pinning `acme-sdk` in their `pyproject.toml`) and "Integration maintainers" (DevOps owners of pipelines that depend on `acme-sdk`)
- `release-drafter.yml` and `.github/workflows/release-publish.yml` — present
- One open draft from `gh release list` — `tagName: v2.0.0`, `targetCommitish: develop`, ancestor of `origin/develop`; body so far carries `release-drafter`'s Conventional-Commits sections only
- `spec/project/release-skill-layer/en.md` — canonical spec
- `skills/release-notes-curate/references/project-bundles.md` — the Python-library bundle (Install, API changes, Breaking changes, Migration, Changelog pointer, Supported Python versions)

## Expected behaviour

1. Run preconditions, resolve the open draft (`v2.0.0`, single match, ancestor of `origin/develop`), detect project type via signal 3 (Python library — `pyproject.toml` declares a distributable package, no `[project.scripts]`).
2. Read `AUDIENCES.md`, pin SDK consumers and integration maintainers as the primary audiences; do not dispatch `audience-identify`.
3. Derive the Python-library bundle by walking `git log v1.4.2..<draft-target-sha>`: Install (PyPI install line `pip install acme-sdk==2.0.0` plus the `pyproject.toml` constraint snippet `acme-sdk = "^2.0.0"`), API changes (the new `AcmeClient.stream` symbol with its commit SHA / PR #), Breaking changes (the `fetch → get` rename and the removed `__init__` parameter, both attributed to commit SHAs), Migration (a one-line summary plus a link to `docs/migrations/v2.md` rather than copying the recipe verbatim), Changelog pointer (link to the `## [2.0.0]` section in `CHANGELOG.md` once the release lands), Supported Python versions (lifted from `pyproject.toml` classifiers / `requires-python`).
4. Self-validate: SDK consumers → Install + API changes + Breaking changes + Migration + Supported Python versions; integration maintainers → Install (pin syntax) + Breaking changes + Migration + Changelog pointer. Every primary audience maps to at least one section; no `## Open questions` needed.
5. Compose the augmentation block between the literal markers, with the `---` divider and the bundle sections in the order above. English-only.
6. Disclose to the operator in one block — detected project type with the matched signal, audience artefact path with the two primary audiences, the augmentation block as a literal Markdown preview, and the unified diff against the current draft body. Block until the operator confirms.
7. On confirmation, write the augmented body via `gh release edit v2.0.0 --notes-file <tempfile>` (the body crosses the 4 KiB threshold once the migration recipe link plus changelog pointer are included). Never call `gh release edit --draft=false`. Re-read via `gh release view v2.0.0 --json body` and verify exactly one start marker and one end marker remain. Report the augmented draft URL back to the operator.
