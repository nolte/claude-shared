---
name: project-structure-apply
description: Audit a repository against spec/project/project-structure/<canonical_language>.md and scaffold or patch any missing artefacts—README, Claude.md, .gitignore, .pre-commit-config.yaml, Renovate config, Taskfile, MkDocs setup, .claude/ directory, and the full .github/ layout (workflows, settings.yml, release-drafter.yml, boring-cyborg.yml, stale.yml) with the portfolio-wide Probot extends pointers. Also verifies that the Probot apps (settings, boring-cyborg, stale) backing those YAML files are actually installed on the GitHub repository via the GitHub API. Invoke when the user asks to audit the project structure, apply the project-structure spec, scaffold missing GitHub configs, add .github/settings.yml, generate release-drafter config, bring this repo in line with project-structure, check that Probot apps are installed, or add missing project configs. Also handles equivalent German-language requests.
---

# Project Structure Apply

Audits and repairs a repository so it matches the Repository Project Structure spec at `spec/project/project-structure/<canonical_language>.md`. The skill both reports findings and—with explicit per-item user consent—writes the missing files in place.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path, or from the `nolte/claude-shared` repository). Never invent requirements that aren't in the spec.

## User-language policy

Detect the user's language and respond in it. Generated file contents (`.github/*.yml`, `Taskfile.yml`, `CLAUDE.md`, `renovate.json5`, workflow YAML, and equivalents) are always written in English so automation and cross-project consistency stay predictable. Comments inside generated files are English as well.

## Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
- Locate a `spec/project/project-structure/` folder—either in the target repo or via the nolte-shared plugin. If neither is reachable, stop and ask the user which spec source to use.
- Check for uncommitted changes in paths the skill may touch (`.github/`, `docs/`, `spec/`, `tests/`, root configs). If the tree is dirty in those paths, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

## Operations

### 1. Audit

Walk through the spec's Acceptance Criteria one item at a time and classify each as:

- **pass**: file or folder exists and content matches the spec (right `_extends:`, required keys present, etc.).
- **missing**: file or folder absent.
- **drift**: present but diverges from the spec (wrong `_extends:` target, stale content, etc.).

Report the findings grouped by spec area: Top-level files, Claude integration, CI and automation, GitHub repository configuration, Documentation, Specifications, Tests, Source layout, Home Assistant, Containerization. Audit is read-only—never autofix during audit.

### 2. Probot app installation check

The Probot-backed YAML files (`.github/settings.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml`) only take effect once the matching GitHub Apps are installed on the repository. Release Drafter runs as a GitHub Action per the branching-model spec, so it's **not** part of this check.

For the three Probot apps, verify installation via `gh api`: cross-reference the `app_slug` values `settings`, `boring-cyborg`, and `stale` against the installations accessible to the authenticated user or owning organization:

1. Resolve `<owner>/<repo>` from `git remote get-url origin`.
2. Determine whether the owner is a user or an org: `gh api "/users/<owner>" --jq '.type'` returns `User` or `Organization`.
3. List installations:
   - Org: `gh api "/orgs/<owner>/installations" --paginate --jq '.installations[] | {slug: .app_slug, id: .id, scope: .repository_selection}'`
   - User: `gh api /user/installations --paginate --jq '.installations[] | {slug: .app_slug, id: .id, scope: .repository_selection}'`
4. For each expected slug (`settings`, `boring-cyborg`, `stale`):
   - If no entry with that slug exists → **app not installed**.
   - If the entry's `repository_selection` is `all` → **installed and has access**.
   - If `repository_selection` is `selected` → verify the repo is in the installation's repository list:
     - Org: `gh api "/orgs/<owner>/installations/<id>/repos" --paginate --jq '.repositories[].full_name'`
     - User: `gh api "/user/installations/<id>/repositories" --paginate --jq '.repositories[].full_name'`
     - Grep for `^<owner>/<repo>$`. If missing → **installed at the owner level but not granted access to this repo**.

Only run this check for Probot YAML files the audit classified as **pass**: warning that the `settings` app is missing makes no sense when `.github/settings.yml` doesn't even exist yet.

Handle API-permission errors gracefully: if `gh api` returns 403 or 404 for the installations endpoint, the token lacks scope (typically `admin:org` for org installations or `read:user` for user installations). Stop the installation check, report which scope is missing, and point the user at `https://github.com/<owner>/settings/installations` (user) or `https://github.com/organizations/<owner>/settings/installations` (org) to verify manually.

Never attempt to *install* an app programmatically—app installation is intentionally a human-approved action. The skill only reports the status and links to the app's install page (`https://github.com/apps/settings`, `https://github.com/apps/boring-cyborg`, `https://github.com/apps/stale`).

### 3. Apply

For each **missing** or **drift** item the audit surfaced, confirm with the user per item (group-level "apply all in this group" is fine when the user asks for it). For each approved item:

- **Missing top-level files**: scaffold with the minimal content the spec requires. `renovate.json5` extends the portfolio preset `github>nolte/gh-plumbing//renovate-configs/common#<tag>` pinned to the current `nolte/gh-plumbing` release tag (fetch via `gh api repos/nolte/gh-plumbing/releases/latest --jq '.tag_name'`; fall back to asking the user). `.pre-commit-config.yaml` pins the stack's current linters; `CLAUDE.md` covers architecture hints and command entry points.
- **`.claude/` directory**: create with a `settings.json` stub (empty `permissions` and `env`) so the directory isn't empty. Never copy plugin-owned skills into `.claude/skills/`.
- **`.github/settings.yml`**: write with `_extends: nolte/gh-plumbing:.github/commons-settings.yml` plus only the repo-specific keys (`name`, `description`, `homepage`, `topics`). Pre-fill values from `git remote get-url origin` and `gh repo view --json ...` when available.
- **`.github/release-drafter.yml`**: `_extends: nolte/gh-plumbing:.github/commons-release-drafter.yml`, nothing else unless the user explicitly requests overrides.
- **`.github/boring-cyborg.yml`**: `_extends: nolte/gh-plumbing:.github/commons-boring-cyborg.yml`.
- **`.github/stale.yml`**: `_extends: nolte/gh-plumbing:.github/commons-stale.yml`.
- **`.github/workflows/`**: if empty, scaffold at minimum a `ci.yml` that invokes Taskfile targets (`task lint`, `task test`, `task docs`). Don't invent language-specific pipelines beyond what Taskfile already exposes.
- **Release-management workflows**: when any of the three required workflows is missing, scaffold it as a thin caller of the matching reusable workflow in `nolte/gh-plumbing`, pinned to the current release tag (ask the user for the tag, or fall back to `@develop` and flag it):
  - `.github/workflows/release-drafter.yml` → `on: push: branches: [develop]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-drafter.yml@<tag>` with `permissions: contents: write, pull-requests: write`
  - `.github/workflows/release-cd-refresh-master.yml` → `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-cd-refresh-master.yml@<tag>` with `target_branch: main` and `permissions: contents: write`
  - `.github/workflows/automerge.yaml` → standard `pull_request` / `pull_request_review` / `check_suite` triggers, calls `nolte/gh-plumbing/.github/workflows/reusable-automerge.yaml@<tag>` with `permissions: contents: write, pull-requests: write`
- **`.github/workflows/release-cd-deliver-docs.yml`**: scaffold only when `mkdocs.yml` exists in the repo. `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml@<tag>` with `requirements: docs/requirements.txt`, `permissions: contents: write, id-token: write, pages: write`, and a `concurrency` group of `pages` with `cancel-in-progress: true`.
- **Repository-specific packaging workflow**: **never** scaffold. If the repo is an HA integration (`hacs.json` present) or otherwise ships a delivery artifact and no packaging workflow exists, report the gap and ask the user how the artifact is produced before writing anything.
- **`Taskfile.yml`**: include `test`, `lint`, `docs` targets at a minimum; wire them to the real stack commands detected in the repo.
- **`docs/` + `mkdocs.yml`**: scaffold an `mkdocs.yml` that points at `docs/` and a stub `docs/index.md`.
- **`spec/` / `tests/`**: create as empty directories with a single `.gitkeep` only when the repo truly has nothing to move there yet.
- **Source layout**: if primary source is loose at the repository root, **never** move files silently. Report the drift and ask the user how to proceed.
- **`.gitignore`**: ensure `.env` is listed whenever `.env.example` exists in the tree.
- **README badges**: insert CI status badges for workflows present under `.github/workflows/` near the top of `README.md`.

After every successful write, re-run the single affected audit check so the user sees the item flip to **pass**. Never batch silent writes—each change requires explicit approval.

### 4. Re-audit

When the user has finished approving changes, re-run Operations 1 and 2 end-to-end and present a fresh grouped summary. Items still **missing**, **drift**, or with an uninstalled Probot app must be called out so the user knows what remains and why (for example, a deliberately deferred scaffold or a pending app install).

## Hard rules

- **Never** overwrite an existing file without explicit per-item confirmation. Merge into existing YAML or JSON configs rather than replacing them wholesale.
- **Never** manage repository settings through the GitHub UI or `gh repo edit`. `.github/settings.yml` is the source of truth, driven by the Probot Settings app.
- **Never** write a `.github/settings.yml` without an `_extends:` pointing at `nolte/gh-plumbing:.github/commons-settings.yml` (or the short form `gh-plumbing:.github/commons-settings.yml` inside the `nolte` org). Same applies to release-drafter, boring-cyborg, and stale.
- **Never** copy plugin-owned skills into `.claude/skills/`. Distribution is the plugin mechanism's job.
- **Never** automatically move source files out of the repository root. Report the drift and let the user decide.
- **Never** commit a real `.env`. When creating `.env.example`, simultaneously ensure `.env` is listed in `.gitignore`.
- **Never** attempt to install a GitHub App programmatically. Report the install status and link to the app's marketplace page so a human can approve the install.
- When `spec/project/project-structure/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- When the Probot app installation check can't run because the token lacks scope, report that explicitly: **never** treat an API error as "app is installed."
