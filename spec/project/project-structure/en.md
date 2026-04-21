# Repository Project Structure

Status: draft

## Context
Projects in this ecosystem share a recognizable shape on disk: a Python (or multi-language) codebase with MkDocs documentation, Taskfile-driven automation, pre-commit and Renovate hygiene, a `spec/` folder for requirements, and Claude Code integration via `CLAUDE.md` and `.claude/`. Reference implementations are [`nolte/kamerplanter`](https://github.com/nolte/kamerplanter) (multi-component repository with backend, frontend, knowledge service, and HA integration) and [`nolte/kamerplanter-ha`](https://github.com/nolte/kamerplanter-ha) (single-purpose Home Assistant custom integration). New repositories should follow the same structural conventions so that tooling expectations, CI wiring, onboarding, and AI-assisted workflows work the same way across the portfolio.

## Goals
- Every new git repository has a predictable top-level layout that humans and AI agents can navigate without per-project discovery
- Common tooling (pre-commit, Renovate, MkDocs, Taskfile) is wired in consistently and in the same locations
- Claude Code integration (`CLAUDE.md`, `.claude/`) is present from day one
- The shape scales from a single-purpose repository to a multi-component monorepo without reorganization
- Local developer commands and CI invocations run through the same entry points

## Non-Goals
- Programming language choice (Python, TypeScript, Go, etc.)
- Specific CI platform features or the contents of individual workflow jobs
- Domain or business logic
- Release, versioning, and publishing processes (separate spec)
- Branching / Git-flow conventions (separate spec)

## Requirements

### Top-level files
- **MUST** include a `README.md` at the repository root with project intro, feature overview, quickstart, and pointers to full documentation
- **MUST** include a `.gitignore`
- **MUST** include a `CLAUDE.md` that documents AI-assisted development conventions, architecture hints, and command entry points for the repository
- **MUST** include a `renovate.json5` (preferred) or `renovate.json` configuring automated dependency updates
- **MUST** include a `.pre-commit-config.yaml` pinning linters and formatters relevant to the stack
- **SHOULD** include a `LICENSE` file at the root when the repository is published or intended for redistribution

### Claude Code integration
- **MUST** include a `.claude/` directory containing project-level Claude Code configuration (any combination of `agents/`, `skills/`, `commands/`, and `settings*.json` as needed)
- **MUST** keep `CLAUDE.md` and `.claude/` in sync with what the repository actually uses; stale references are treated as bugs

### CI and automation
- **MUST** include a `.github/` directory with workflows under `.github/workflows/`
- **MUST** include a `Taskfile.yml` (or `Taskfile.yaml`) at the repository root exposing reproducible commands for at least test, lint, and documentation targets
- **SHOULD** invoke lint, test, and docs commands from CI through Taskfile targets so local and CI behavior stay identical
- **SHOULD** produce CI status badges in `README.md` for the primary workflows

### Documentation
- **MUST** include a `docs/` directory as the MkDocs source
- **MUST** include an `mkdocs.yml` at the repository root
- **SHOULD** publish the documentation site via a CI workflow (for example GitHub Pages)
- **MAY** split `docs/` by language (`docs/en/`, `docs/de/`, …) when multilingual documentation is required

### Specifications
- **MUST** include a `spec/` directory at the repository root for requirements, NFRs, style guides, and domain knowledge
- **SHOULD** organize `spec/` by topic subfolder (for example `req/`, `nfr/`, `ui-nfr/`, `style-guides/`, `knowledge/`) once more than a handful of specs exist
- **MAY** reuse the multilingual spec skill convention (`<slug>/<lang>.md`) when the project needs translated specifications

### Tests
- **MUST** include a `tests/` directory at the repository root
- **SHOULD** mirror the shape of the source tree inside `tests/`
- **MAY** place end-to-end tests in a dedicated subfolder such as `tests/e2e/`

### Source layout
- **MUST** place primary source code under one of these conventional layouts:
  - `src/` for a single-component library or service
  - `src/<component>/` per subproject in a multi-component repository (for example `src/backend/`, `src/frontend/`, `src/knowledge-service/`)
  - `custom_components/<name>/` for a Home Assistant custom integration
- **MUST NOT** keep primary source files loose at the repository root; only tooling configs, metadata, and small scripts may live there
- **MAY** include a `scripts/` and/or `tools/` folder for repository-local automation helpers

### Home Assistant integrations (optional)
- **MAY** include a `hacs.json` at the repository root when the repository ships an HA custom integration
- **MUST** place integration code in `custom_components/<domain>/` using the integration's lowercase ASCII HA domain as the folder name when `hacs.json` is present
- **MAY** include an `info.md` for HACS-rendered repository metadata

### Containerization and orchestration (optional)
- **MAY** include `docker-compose.yml` (and variants such as `docker-compose.e2e.yml`, `docker-compose.release.yml`) for local stack bring-up
- **MAY** include a `docker/` folder holding per-service Dockerfiles and build contexts
- **MAY** include `helm/` and `skaffold.yaml` for Kubernetes-based development loops
- **MUST** provide a `.env.example` documenting every required environment variable when the stack is configured through env files
- **MUST NOT** track a real `.env` in version control; `.env` **MUST** be listed in `.gitignore`

### Branding and assets (optional)
- **MAY** include a `brand/` folder for source brand assets (logos, banners) that are referenced by docs or README

## Acceptance Criteria
- [ ] `README.md`, `.gitignore`, `CLAUDE.md`, `renovate.json5` (or `renovate.json`), and `.pre-commit-config.yaml` exist at the repository root
- [ ] `.claude/` exists and contains at least one of `agents/`, `skills/`, `commands/`, or a `settings*.json` file
- [ ] `.github/workflows/` contains at least one workflow file
- [ ] `Taskfile.yml` or `Taskfile.yaml` is present and `task --list` enumerates test, lint, and docs targets
- [ ] `docs/` and `mkdocs.yml` exist, and `mkdocs build` completes without errors
- [ ] `spec/` exists at the repository root
- [ ] `tests/` exists and contains at least one test
- [ ] Primary source lives under `src/`, `src/<component>/`, or `custom_components/<name>/` — not loose at the root
- [ ] If `.env.example` is present, a literal `.env` entry appears in `.gitignore`
- [ ] If `hacs.json` is present, `custom_components/<domain>/` exists and matches the HA integration domain
- [ ] CI status badges for the primary workflows appear near the top of `README.md`

## Open Questions
- Should `LICENSE` be elevated to **MUST** for all public repositories in the portfolio?
- Should the spec prescribe a minimum `.github/` shape (issue templates, PR template, `CODEOWNERS`)?
- Is `renovate.json5` the canonical default, or should `renovate.json` stay equally acceptable?
- Should release artifacts (changelogs, release workflows, versioning policy) be referenced from here or left entirely to a separate release-process spec?
- Should multilingual documentation (`docs/<lang>/`) be a **SHOULD** once a second language appears, or stay **MAY**?
- Is there a canonical minimum Taskfile target set beyond test/lint/docs (for example `setup`, `ci`, `release`)?
