# Repository Project Structure

Status: draft

## Context
Projects in this ecosystem share a recognizable shape on disk: a Python (or multi-language) codebase with MkDocs documentation, Taskfile-driven automation, pre-commit and Renovate hygiene, a `spec/` folder for requirements, and Claude Code integration via `CLAUDE.md` and `.claude/`. Reference implementations are [`nolte/kamerplanter`](https://github.com/nolte/kamerplanter) (multi-component repository with backend, frontend, knowledge service, and HA integration) and [`nolte/kamerplanter-ha`](https://github.com/nolte/kamerplanter-ha) (single-purpose Home Assistant custom integration). New repositories should follow the same structural conventions so that tooling expectations, CI wiring, onboarding, and AI-assisted workflows work the same way across the portfolio.

## Goals
- Every new git repository has a predictable top-level layout that humans and AI agents can navigate without per-project discovery
- Common tooling (pre-commit, Renovate, MkDocs, Taskfile) is wired in consistently and in the same locations
- Dependency hygiene is automated portfolio-wide: every repository runs Renovate against the shared `nolte/gh-plumbing` preset so security and version updates land as PRs without per-repository configuration drift, and Renovate is therefore an essential part of every project rather than an optional add-on
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
- **MUST** include a `README.md` at the repository root with project intro, feature overview, quickstart, and pointers to full documentation; the internal structure of that file (required sections, ordering, badges, cross-repository links) is governed by the `readme-structure` spec
- **MUST** include a `.gitignore`
- **MUST** include a `CLAUDE.md` that documents AI-assisted development conventions, architecture hints, and command entry points for the repository
- **MUST** include a `renovate.json5` (preferred) or `renovate.json` that `extends` the portfolio-wide preset `github>nolte/gh-plumbing//renovate-configs/common#<tag>`, pinned to a release tag (for example `#v1.1.12`), so Renovate configuration stays aligned across the portfolio; per-repository overrides **SHOULD** stay narrow (typically package-grouping or automerge rules)
- **MUST** have the Renovate GitHub App (<https://github.com/apps/renovate>) installed on the repository so that the `renovate.json5` configuration above actually drives dependency updates; without the app, the config file is inert and no PRs or Dependency-Dashboard issues are produced. The same Probot-style installation pattern applies as for `settings` / `boring-cyborg` / `stale`, and the install action is human-only
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

### Release and documentation workflows
The `nolte/gh-plumbing` portfolio ships reusable workflows for release management and documentation delivery. The `branching-model` spec lists the release-management workflows in full and makes three of them mandatory. This spec additionally surfaces the documentation and packaging companions so that a project-structure audit catches them even when the branching-model spec is read in isolation.

- **MUST** include the release-management workflows mandated by the `branching-model` spec: `.github/workflows/release-drafter.yml`, `.github/workflows/release-cd-refresh-master.yml`, and `.github/workflows/automerge.yaml`, each wired to the corresponding reusable workflow under `nolte/gh-plumbing/.github/workflows/`
- **SHOULD** include `.github/workflows/release-cd-deliver-docs.yml`: triggered on `release: [published]` and invoking `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml`: whenever `mkdocs.yml` is present, so documentation is republished on every release
- **MAY** include a repository-specific packaging workflow (for example a `release.yml` that patches `manifest.json`, builds a ZIP, and uploads it via `gh release upload`) triggered on `release: [published]` when the repository ships a delivery artifact such as an HACS integration
- **SHOULD** pin every reusable-workflow reference to a tag (for example `@v1.1.12`) rather than a moving branch, so release-pipeline behavior stays reproducible

### GitHub repository configuration
- **MUST** manage GitHub repository settings—topics, description, homepage, branch protection, labels, collaborators, and merge-button options—as code via `.github/settings.yml`, consumed by the [Probot Settings app](https://probot.github.io/apps/settings/)
- **MUST** inherit the portfolio-wide defaults via `_extends: nolte/gh-plumbing:.github/commons-settings.yml` (the short form `gh-plumbing:.github/commons-settings.yml` is equivalent within the `nolte` organization) and keep per-repository content limited to repo-specific fields such as `name`, `description`, `homepage`, and `topics`
- **MUST NOT** maintain repository settings manually through the GitHub UI once `.github/settings.yml` is present; any UI edit is drift and has to be reconciled back into the file
- **MUST** keep every label `description` in `.github/settings.yml` (and in any `commons-settings.yml` it inherits from) at **100 characters or fewer** (counted as UTF-16 code units, matching JavaScript `String.length` and GitHub's API enforcement). GitHub's labels API rejects longer descriptions with HTTP 422 `description is too long (maximum is 100 characters)`, at which point the Probot Settings App silently skips that one label and the rest of the sync run completes without surfacing the failure. Observed on 2026-05-01 in `nolte/gh-plumbing`: a 117-character description on the `release` label kept it from being created in the live repo while the other 19 labels of the same sync run landed successfully
- **MUST** include a `.github/release-drafter.yml` extending `nolte/gh-plumbing:.github/commons-release-drafter.yml` to feed the release-notes drafter (the accompanying workflow is specified by the branching-model spec)
- **SHOULD** include a `.github/boring-cyborg.yml` extending `nolte/gh-plumbing:.github/commons-boring-cyborg.yml` for newcomer onboarding, automatic labeling, and reviewer assignment via the [Boring Cyborg app](https://probot.github.io/apps/boring-cyborg/)
- **SHOULD** include a `.github/stale.yml` extending `nolte/gh-plumbing:.github/commons-stale.yml` to manage inactive issues and pull requests via the [Stale app](https://probot.github.io/apps/stale/)
- **MAY** override individual keys from the inherited `commons-*.yml` files when a repository's needs diverge from the portfolio defaults; keep such overrides narrow and explain them alongside the change

### Documentation
- **MUST** include a `docs/` directory as the MkDocs source
- **MUST** include an `mkdocs.yml` at the repository root
- **SHOULD** publish the documentation site via a CI workflow (for example GitHub Pages)
- **MAY** split `docs/` by language (`docs/en/`, `docs/de/`, …) when multilingual documentation is required

### Specifications
- **MUST** include a `spec/` directory at the repository root for requirements, NFRs, style guides, and domain knowledge
- **SHOULD** organize `spec/` by topic subfolder (for example `req/`, `nfr/`, `ui-nfr/`, `style-guides/`, `knowledge/`) once more than a handful of specs exist
- **MAY** reuse the multilingual spec skill convention (`<slug>/<lang>.md`) when the project needs translated specifications

### Project planning artefacts (optional)
The portfolio tracks roadmap, sprint, feature, and release-artefact records as version-controlled markdown under a top-level `project/` directory when the repository runs the Claude-driven planning suite (`roadmap-init`, `sprint-plan`, `feature-decompose`, and the `sprint-execute` / `sprint-review` skills that read those artefacts). The internal shape of each artefact is governed by its own spec (`roadmap`, `sprint`, `feature`, `release-artifact`); this spec only declares the directory layout that hosts them, so a project-structure audit recognises the planning surface even when those skills haven't yet run.

- **MAY** include a top-level `project/` directory holding the planning artefacts; absence is permitted for repositories that don't run the planning suite
- **MUST**, when `project/` is present, organise files as `project/roadmap.md` (the queue), `project/goals.md` (vision plus outcomes), `project/sprints/<NNNN>-<slug>.md` (one file per sprint), `project/features/<slug>.md` (one file per feature), and (when out-of-band releases occur) `project/release-artifacts/out-of-band/<NNNN>-<slug>.md` plus a regenerated `project/release-artifacts/out-of-band/INDEX.md`; the per-file shape is governed by the `roadmap`, `sprint`, `feature`, and `release-artifact` specs respectively
- **MUST NOT** nest the `project/` tree under `docs/` or any other subdirectory; the planning surface is a top-level orientation point, parallel to `spec/` and `tests/`
- **MUST NOT** redefine here any rule declared by the `roadmap`, `sprint`, `feature`, or `release-artifact` specs; this section is layout-only

### Tests
- **MUST** include a `tests/` directory at the repository root
- **SHOULD** mirror the shape of the source tree inside `tests/`
- **MAY** place end-to-end tests in a dedicated subfolder such as `tests/e2e/`

### Source layout
- **MUST** place primary source code under one of these conventional layouts:
  - `src/` for a single-component library or service
  - `src/<component>/` per subproject in a multi-component repository (for example `src/backend/`, `src/frontend/`, `src/knowledge-service/`)
  - `custom_components/<name>/` for a Home Assistant custom integration
  - `.claude-plugin/` together with `skills/<name>/` (and optionally `agents/<name>.md`) for a Claude Code plugin repository, where prompt and skill content is the primary deliverable and no runtime source exists
  - `playbooks/`, `roles/`, and an inventory tree (`inventory/` for a single environment, or `inventories/<env>/` per environment per `spec/ansible/playbook-development/`) plus optional `group_vars/` and `host_vars/`, alongside `ansible.cfg` and `requirements.yml` at the repository root for an Ansible bootstrap or provisioning repository, where configuration and automation code is the primary deliverable and no runtime source exists; Ansible's standard conventions can't be wrapped under a `src/` shell without breaking `ansible-playbook`'s default role and inventory discovery
- **MUST NOT** keep primary source files loose at the repository root; only tooling configs, metadata, and small scripts may live there; the Ansible variant above is a deliberate exception to this rule
- **MAY** include a `scripts/` and/or `tools/` folder for repository-local automation helpers

### Python development (optional)
- **MUST** install and run all Python project dependencies inside a project-local Python virtual environment, regardless of whether that environment is created via `python -m venv`, `uv venv`, `virtualenv`, or an equivalent tool; system-wide or user-global installation of project dependencies isn't permitted
- **MUST** keep the local virtual-environment directory (typically `.venv/`) out of version control by listing it in `.gitignore`
- **MUST** include a `pyproject.toml` (at the repository root for a single-component repository, or under each `src/<component>/` for a multi-component repository) declaring `[build-system]`, project metadata (`name`, `version`, `license`, `authors`, `classifiers`, `urls`), and Python tooling configuration (`[tool.ruff]`, `[tool.pytest.ini_options]`, and similar); `pyproject.toml` carries distribution metadata and tooling configuration, while runtime dependencies remain in `requirements.txt` (see below) so the two files don't overlap
- **MUST** track direct runtime dependencies in a `requirements.txt`, located at the repository root for a single-component repository or under `src/<component>/requirements.txt` per component in a multi-component repository; the runtime install set is sourced from `requirements.txt`, not from a `[project.dependencies]` block in `pyproject.toml`
- **SHOULD** track development- and test-only dependencies separately in a `requirements-dev.txt` (or `src/<component>/requirements-dev.txt`) so that production installs don't pull in tooling
- **SHOULD** wire Taskfile targets (for example `task install`, `task test`, `task lint`) so they create or use the project-local virtual environment and install via `pip install -r requirements.txt` (and `requirements-dev.txt` where applicable), so local and CI execution share one entry point

### Requirements file format (optional, applies when `requirements*.txt` exist)
These rules apply to every `requirements.txt` and `requirements-dev.txt` written under this spec, and exist so that scaffolding and drift checks can validate the file structure—not just its presence.

- **MUST** list every dependency on its own line with an explicit version specifier (for example `pkg>=1.2`, `pkg==1.2.3`, or `pkg~=1.2`); bare package names without a specifier aren't permitted because they let transitive resolution drift silently across installs
- **MUST NOT** chain `requirements-dev.txt` to `requirements.txt` via a `-r requirements.txt` (or equivalent `--requirement`) directive; the Taskfile pattern in the section above installs both files independently, so the chain is redundant, hides the dev-only contract, and silently follows a stale runtime list when one accidentally lands
- **MAY** use `#` comment lines for headers, rationale, or upstream-tracking pointers; a comment-only `requirements.txt` is permitted as a temporary placeholder when no runtime dependency has been published yet (for example, an SDK still pre-release), but the placeholder **MUST** be replaced with real entries as soon as the first runtime dependency lands

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
- [ ] `renovate.json5` (or `renovate.json`) extends `github>nolte/gh-plumbing//renovate-configs/common#<tag>` pinned to a release tag, not a moving branch
- [ ] The Renovate GitHub App (slug `renovate`) is installed on the repository, verifiable via the App's repository selection, the presence of an open or closed Dependency-Dashboard issue, the presence of `app/renovate-bot`-authored PRs, or the Mend Renovate dashboard at `https://developer.mend.io/github/<owner>/<repo>`
- [ ] `.claude/` exists and contains at least one of `agents/`, `skills/`, `commands/`, or a `settings*.json` file
- [ ] `.github/workflows/` contains at least one workflow file
- [ ] `.github/workflows/` contains `release-drafter.yml`, `release-cd-refresh-master.yml`, and `automerge.yaml`, each wired to the matching `nolte/gh-plumbing` reusable workflow
- [ ] If `mkdocs.yml` is present, `.github/workflows/release-cd-deliver-docs.yml` exists and triggers on `release: [published]`
- [ ] Every `uses: nolte/gh-plumbing/.github/workflows/...` reference in `.github/workflows/` is pinned to a release tag, not a moving branch
- [ ] `.github/settings.yml` is present and extends `nolte/gh-plumbing:.github/commons-settings.yml` (or the equivalent short form)
- [ ] Every label `description` field in `.github/settings.yml` and the inherited `commons-settings.yml` is 100 characters or fewer
- [ ] `.github/release-drafter.yml` is present and extends `nolte/gh-plumbing:.github/commons-release-drafter.yml`
- [ ] `.github/boring-cyborg.yml` and `.github/stale.yml` are present and extend their respective `nolte/gh-plumbing` commons files
- [ ] `Taskfile.yml` or `Taskfile.yaml` is present and `task --list` enumerates test, lint, and docs targets
- [ ] `docs/` and `mkdocs.yml` exist, and `mkdocs build` completes without errors
- [ ] `spec/` exists at the repository root
- [ ] `tests/` exists and contains at least one test
- [ ] Primary source lives under `src/`, `src/<component>/`, `custom_components/<name>/`, `.claude-plugin/` + `skills/<name>/`, **or** the repository is an Ansible bootstrap / provisioning repository with `playbooks/`, `roles/`, and an inventory tree (`inventory/` or `inventories/<env>/`) at the root; not loose at the root
- [ ] If the repository contains Python source code (`*.py` files, `custom_components/<name>/`, or `pyproject.toml`), a `requirements.txt` is present at the repository root or under each `src/<component>/` that ships Python code
- [ ] If the repository contains Python source code, a `pyproject.toml` exists at the repository root (single-component) or under each `src/<component>/` (multi-component) and declares `[build-system]`, project metadata, and any Python tooling configuration in use
- [ ] If the repository contains Python source code, `.gitignore` excludes the local virtual-environment directory (for example `.venv/`)
- [ ] If `requirements.txt` or `requirements-dev.txt` is present, every non-comment, non-blank line carries a version specifier (no bare package names)
- [ ] If `requirements-dev.txt` is present, it doesn't contain a `-r requirements.txt` (or `--requirement`) directive
- [ ] If `.env.example` is present, a literal `.env` entry appears in `.gitignore`
- [ ] If `hacs.json` is present, `custom_components/<domain>/` exists and matches the HA integration domain
- [ ] If `project/` is present, planning artefacts live under the layout `project/roadmap.md`, `project/goals.md`, `project/sprints/<NNNN>-<slug>.md`, `project/features/<slug>.md`, or `project/release-artifacts/out-of-band/<NNNN>-<slug>.md` (with `project/release-artifacts/out-of-band/INDEX.md` when at least one out-of-band entry exists); nested or alternative locations fail validation
- [ ] CI status badges for the primary workflows appear near the top of `README.md`

## Open Questions
- Should `LICENSE` be elevated to **MUST** for all public repositories in the portfolio?
- Should the spec additionally prescribe issue templates, pull-request templates, and `CODEOWNERS` for `.github/`? Probot configuration (settings, release-drafter, boring-cyborg, stale) is now covered; the community-health files remain open.
- Is `renovate.json5` the canonical default, or should `renovate.json` stay equally acceptable?
- Should release artifacts (changelogs, release workflows, versioning policy) be referenced from here or left entirely to a separate release-process spec?
- Should multilingual documentation (`docs/<lang>/`) be a **SHOULD** once a second language appears, or stay **MAY**?
- Is there a canonical minimum Taskfile target set beyond test/lint/docs (for example `setup`, `ci`, `release`)?
- Should `tests/` be softened from **MUST** to **SHOULD** for Claude Code plugin repositories that ship only prompt/skill content and carry no runtime code?
