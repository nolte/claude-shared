# Project-Type Section Bundles

Read this file in step 4 (Derive the project-context bundle) of the skill's operation.

Each bundle lists the canonical section headings to compose for one detected project type. Bundles are starting points: the audience artefact may motivate further sections or trim listed sections that no audience needs. Never copy a bundle that does not match the detected project type.

All section headings stay in English regardless of the repo's documentation language (the GitHub release UI is English-only in practice).

---

## Claude Code plugin

**Detection.** `.claude-plugin/plugin.json` exists at the repo root; top-level `skills/` and / or `agents/` folder present.

**Sections to compose:**

- **Skills changed** — list `skills/<name>/` entries added, renamed, or removed since the previous release tag. Source: `git diff --stat <prev-tag>..<draft-sha> -- skills/`. Renames are detected via `git log --follow` on `skills/<old>/SKILL.md`.
- **Agents changed** — same shape for `agents/`.
- **Specs changed** — same shape for `spec/`. Subdivide by topic when the diff touches multiple topics (`spec/claude/`, `spec/project/`).
- **Breaking changes for plugin consumers** — only when the diff renames a slash command (frontmatter `name` change), removes a skill / agent, or bumps `.claude-plugin/plugin.json` `version` across a major boundary. List each breaking change with a one-line migration hint.
- **Required plugin re-install** — only when skill / agent artefacts moved or were renamed in a way that consumers cannot pick up via plugin auto-update. Default: omit unless explicitly required.

## Python application

**Detection.** `pyproject.toml` declares `[project.scripts]` (or equivalent application entry point); no library distribution metadata. Often a `Dockerfile` or runtime config is present.

**Sections to compose:**

- **Runtime requirements** — diff `pyproject.toml` `requires-python` and the `[project.dependencies]` block for explicit version bumps. Diff `Dockerfile` (`FROM`) or `compose.yaml` (`image:`) for container-base-image changes.
- **Migration notes for operators** — config changes, breaking environment-variable renames, breaking command-line flag renames, breaking default-value changes. Source: any commit touching the application's entry-point modules with a Conventional-Commits `feat!` / `fix!` / `BREAKING CHANGE:` annotation.
- **Hardware support** — only for hardware-touching applications (heuristic: `gphoto2`, `picamera2`, `pyserial`, `RPi.GPIO`, `smbus`, `pyudev` in dependencies, or operator confirms). List supported devices added / removed and firmware-version constraints changed.

## Python library

**Detection.** `pyproject.toml` declares a distributable package (typically `[project]` with `name`, no `[project.scripts]`, build backend such as `hatchling`, `setuptools`, or `poetry-core`).

**Sections to compose:**

- **API changes** — diff public modules and exported symbols. Source: walk `__init__.py`, `__all__`, `py.typed` markers; PRs touching public surface are usually labelled or have descriptive titles.
- **Compatibility breaks** — only when the major-version bumps; list each break with a migration hint.
- **Deprecations** — list `DeprecationWarning` introductions or removals scheduled for a future release.

## Node / TypeScript library or app

**Detection.** `package.json` exists. Library bias when `main` / `exports` is set; app bias when `bin` / `scripts.start` is set. When both are set, treat as a hybrid and ask the operator.

**Sections to compose** (library):

- **API changes** — diff `exports` field plus the source files it points to.
- **Compatibility breaks** — major-version bumps.
- **Runtime requirements** — diff `engines.node`, `packageManager`, peer dependencies.

**Sections to compose** (app):

- **Runtime requirements** — `engines.node`, container base image when present.
- **Migration notes for operators** — breaking config or environment changes.

## CLI tool

**Detection.** Declared CLI entry point in `pyproject.toml` (`[project.scripts]`), `package.json` (`bin`), or `Cargo.toml` (`[[bin]]`); the repo's primary deliverable is a command, not a library.

**Sections to compose:**

- **Command-line changes** — new commands, renamed commands, removed commands.
- **Flag deprecations** — flags marked deprecated in this release; include the removal target version when known.
- **Default-value changes** — flags whose default changed; mark each as a soft or hard break.

## Documentation-only repo

**Detection.** `mkdocs.yml`, `docusaurus.config.*`, or similar exists; no application source.

**Sections to compose:**

- **Restructured pages** — path moves under `docs/`. Source: `git log --follow` per moved file.
- **Removed pages** — pages dropped since the previous release.
- **New translations** — new language directories, new `mkdocs.yml` `i18n` languages, new translated source files.
