---
title: project-structure-apply
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# project-structure-apply

_Audits a repository against spec/project/project-structure/<canonical_language>.md and scaffolds or patches missing artefacts: README, top-level orientation file, .gitignore, .pre-commit-config.yaml, Renovate config, Taskfile, MkDocs setup, .claude/ directory, and the full .github/ layout (workflows, settings.yml, release-drafter.yml, boring-cyborg.yml, stale.yml) with the portfolio-wide Probot extends pointers. Verifies via the GitHub API that the backing GitHub Apps (Probot apps `settings`, `boring-cyborg`, `stale`, plus Renovate) are installed; for Renovate also points at the Mend dashboard when the App is installed but no activity is visible. Invoke when the user asks to audit project structure, scaffold missing GitHub configs, generate release-drafter config, check Probot/Renovate app installation, or equivalent German-language requests._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`
- **Source:** [skills/project-structure-apply/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/project-structure-apply/SKILL.md)

---

## Project Structure Apply

Audits and repairs a repository so it matches the Repository Project Structure spec at `spec/project/project-structure/<canonical_language>.md`. The skill both reports findings and—with explicit per-item user consent—writes the missing files in place.

### Why this is a skill, not an agent

- **Per-item user approval is the contract.** Every scaffolded file (`.github/settings.yml`, `Taskfile.yml`, `renovate.json5`, …) is written only with explicit per-change confirmation; the audit is read-only and the apply step is a sequence of approvals an agent's fire-and-forget shape can't carry.
- **Output flows back into the main conversation.** The audit table, the per-item proposals, and the GitHub-App-installation status all surface in the conversation so the user can decide; isolating them in a structured-report boundary would obscure the per-file approval surface.
- **Network-side calls require user gating.** Probot-app installation checks read GitHub API state, but app installation itself is intentionally a human-approved action; mid-flow interactivity is load-bearing here.
- Counter-dimension considered: a narrower agent could specialize on file-template generation and gain on context-window protection, but the high-impact part is the per-item approval dialogue, not the boilerplate; skill wins.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path, or from the `nolte/claude-shared` repository). Never invent requirements that aren't in the spec.

### User-language policy

Detect the user's language and respond in it. Generated file contents (`.github/*.yml`, `Taskfile.yml`, `CLAUDE.md`, `renovate.json5`, workflow YAML, and equivalents) are always written in English so automation and cross-project consistency stay predictable. Comments inside generated files are English as well.

### Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
- Locate a `spec/project/project-structure/` folder—either in the target repo or via the nolte-shared plugin. If neither is reachable, stop and ask the user which spec source to use.
- Check for uncommitted changes in paths the skill may touch (`.github/`, `docs/`, `spec/`, `tests/`, root configs). If the tree is dirty in those paths, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

### Operations

#### 1. Audit

Walk through the spec's Acceptance Criteria one item at a time and classify each as:

- **pass**: file or folder exists and content matches the spec (right `_extends:`, required keys present, etc.).
- **missing**: file or folder absent.
- **drift**: present but diverges from the spec (wrong `_extends:` target, stale content, etc.).

Report the findings grouped by spec area: Top-level files, Claude integration, CI and automation, GitHub repository configuration, Documentation, Specifications, Project planning artefacts, Tests, Source layout, Python development, Home Assistant, Containerization. Audit is read-only—never autofix during audit.

#### 2. GitHub App installation check

The Probot-backed YAML files (`.github/settings.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml`) only take effect once the matching GitHub Apps are installed on the repository. The same is true for the Renovate App: a `renovate.json5` config is inert without the Renovate App installed on the repo. Release Drafter runs as a GitHub Action per the branching-model spec, so it's **not** part of this check.

Apps to verify:

| Slug | Backing config | Install page |
|---|---|---|
| `settings` | `.github/settings.yml` | `https://github.com/apps/settings` |
| `boring-cyborg` | `.github/boring-cyborg.yml` | `https://github.com/apps/boring-cyborg` |
| `stale` | `.github/stale.yml` | `https://github.com/apps/stale` |
| `renovate` | `renovate.json5` (or `renovate.json`) | `https://github.com/apps/renovate` |

Verify installation via `gh api`: cross-reference the slugs above against the installations accessible to the authenticated user or owning organization:

1. Resolve `<owner>/<repo>` from `git remote get-url origin`.
2. Determine whether the owner is a user or an org: `gh api "/users/<owner>" --jq '.type'` returns `User` or `Organization`.
3. List installations:
   - Org: `gh api "/orgs/<owner>/installations" --paginate --jq '.installations[] | {slug: .app_slug, id: .id, scope: .repository_selection}'`
   - User: `gh api /user/installations --paginate --jq '.installations[] | {slug: .app_slug, id: .id, scope: .repository_selection}'`
4. For each expected slug (see table above):
   - If no entry with that slug exists → **app not installed**.
   - If the entry's `repository_selection` is `all` → **installed and has access**.
   - If `repository_selection` is `selected` → verify the repo is in the installation's repository list:
     - Org: `gh api "/orgs/<owner>/installations/<id>/repos" --paginate --jq '.repositories[].full_name'`
     - User: `gh api "/user/installations/<id>/repositories" --paginate --jq '.repositories[].full_name'`
     - Grep for `^<owner>/<repo>$`. If missing → **installed at the owner level but not granted access to this repo**.

Only run this check for the configs the audit classified as **pass**: warning that the `renovate` app is missing makes no sense when no `renovate.json(5)` exists yet, and warning about `settings` makes no sense when `.github/settings.yml` doesn't exist either.

Handle API-permission errors gracefully: if `gh api` returns 403 or 404 for the installations endpoint, the token lacks scope (typically `admin:org` for org installations or `read:user` for user installations). Stop the installation check, report which scope is missing, and point the user at `https://github.com/<owner>/settings/installations` (user) or `https://github.com/organizations/<owner>/settings/installations` (org) to verify manually.

For Renovate specifically, when the App is reported installed but no Renovate activity is visible (no onboarding PR, no Dependency-Dashboard issue, no `app/renovate-bot` PRs), point the user at the Mend Renovate dashboard `https://developer.mend.io/github/<owner>/<repo>` to inspect Renovate's run logs. The App being installed and the App actually running on the repo are two separate states, and the Mend dashboard is the only authoritative source of run-level diagnostics from outside the App's own logs.

Never attempt to *install* an app programmatically. App installation is intentionally a human-approved action. The skill only reports the status and links to the app's install page from the table above.

#### 3. Apply

For each **missing** or **drift** item the audit surfaced, confirm with the user per item (group-level "apply all in this group" is fine when the user asks for it). For each approved item:

- **Missing top-level files**: scaffold with the minimal content the spec requires. `.pre-commit-config.yaml` pins the stack's current linters; `CLAUDE.md` covers architecture hints and command entry points.
- **`renovate.json5`** (or `renovate.json` if the repository already uses that name): Renovate is an essential part of every repository per `project-structure` §Goals, not optional. When the file is missing, scaffold it with `extends: ["github>nolte/gh-plumbing//renovate-configs/common#<tag>"]` pinned to the current `nolte/gh-plumbing` release tag (fetch via `gh api repos/nolte/gh-plumbing/releases/latest --jq '.tag_name'`; fall back to asking the user when the API call fails). When the file exists but doesn't extend the portfolio preset, classify it as drift, surface the missing `extends` line to the user, and offer to add it without overwriting per-repository overrides (package groups, automerge rules) the repo legitimately carries on top.
- **`.claude/` directory**: create with a `settings.json` stub (empty `permissions` and `env`) so the directory isn't empty. Never copy plugin-owned skills into `.claude/skills/`.
- **`.github/settings.yml`**: write with `_extends: nolte/gh-plumbing:.github/commons-settings.yml` plus only the repo-specific keys (`name`, `description`, `homepage`, `topics`). Pre-fill values from `git remote get-url origin` and `gh repo view --json ...` when available.
- **`.github/release-drafter.yml`**: `_extends: nolte/gh-plumbing:.github/commons-release-drafter.yml`, nothing else unless the user explicitly requests overrides.
- **`.github/boring-cyborg.yml`**: `_extends: nolte/gh-plumbing:.github/commons-boring-cyborg.yml`.
- **`.github/stale.yml`**: `_extends: nolte/gh-plumbing:.github/commons-stale.yml`.
- **`.github/workflows/`**: if empty, scaffold at minimum a `ci.yml` that invokes Taskfile targets (`task lint`, `task test`, `task docs`). Don't invent language-specific pipelines beyond what Taskfile already exposes.
- **Release-management workflows**: when any of the four required workflows from `spec/project/branching-model/` §Required GitHub workflows is missing, scaffold it as a thin caller of the matching reusable workflow in `nolte/gh-plumbing`, pinned to the current release tag (ask the user for the tag, or fall back to `@develop` and flag it):
  - `.github/workflows/release-drafter.yml` → `on: push: branches: [develop]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-drafter.yml@<tag>` with `permissions: contents: write, pull-requests: write`
  - `.github/workflows/release-publish.yml` → `on: workflow_dispatch` only (no other triggers), calls `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml@<tag>` with `permissions: contents: write`. Per `spec/project/release-automation/` §Operational contract, the workflow is the audit-trail point for the Draft → Published transition; the `release-publish-trigger` skill dispatches it
  - `.github/workflows/release-cd-refresh-master.yml` → `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-cd-refresh-master.yml@<tag>` with `target_branch: main` and `permissions: contents: write`
  - `.github/workflows/automerge.yaml` → standard `pull_request` / `pull_request_review` / `check_suite` triggers, calls `nolte/gh-plumbing/.github/workflows/reusable-automerge.yaml@<tag>` with `permissions: contents: write, pull-requests: write`
- **`.github/workflows/release-cd-deliver-docs.yml`**: scaffold only when `mkdocs.yml` exists in the repo. `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml@<tag>` with `requirements: docs/requirements.txt`, `permissions: contents: write, id-token: write, pages: write`, and a `concurrency` group of `pages` with `cancel-in-progress: true`.
- **Repository-specific packaging workflow**: **never** scaffold. If the repo is an HA integration (`hacs.json` present) or otherwise ships a delivery artifact and no packaging workflow exists, report the gap and ask the user how the artifact is produced before writing anything.
- **`Taskfile.yml`**: include `test`, `lint`, `docs` targets at a minimum; wire them to the real stack commands detected in the repo.
- **`docs/` + `mkdocs.yml`**: scaffold an `mkdocs.yml` that points at `docs/` and a stub `docs/index.md`.
- **`spec/` / `tests/`**: create as empty directories with a single `.gitkeep` only when the repo truly has nothing to move there yet.
- **`project/` planning artefacts**: this skill only audits the layout—it doesn't scaffold the files themselves. When the `project/` directory is present, verify that every file lives under exactly one of the allowed paths (`project/roadmap.md`, `project/goals.md`, `project/sprints/<NNNN>-<slug>.md`, `project/features/<slug>.md`, `project/release-artifacts/out-of-band/<NNNN>-<slug>.md`, `project/release-artifacts/out-of-band/INDEX.md`, or the optional `project/mission.md` per `spec/project/mission/`). Anything else under `project/` is layout drift and is reported back to the user. When the audit finds a missing artefact the user wants to scaffold, route them to the matching planning skill (`roadmap-init` for `roadmap.md` and `goals.md`, `sprint-plan` for new sprint files, `feature-decompose` for feature files, `mission-define` for `mission.md`) instead of writing the artefact here. The per-file shape is owned by `spec/project/{roadmap,sprint,feature,release-artifact,mission}/` respectively—this skill is layout-only and **MUST NOT** redefine any rule from those specs.
- **Source layout**: if primary source is loose at the repository root, **never** move files silently. Report the drift and ask the user how to proceed.
- **`.gitignore`**: ensure `.env` is listed whenever `.env.example` exists in the tree.
- **Python development**: when the repository contains Python source (`*.py` files, `custom_components/<name>/`, or `pyproject.toml`), scaffold a minimal `pyproject.toml` at the repository root for a single-component repo or under each Python-bearing `src/<component>/` for a multi-component repo, declaring `[build-system]`, project metadata (`name`, `version`, `license`, `authors`, `classifiers`, `urls`), and any Python tooling configuration the repo uses (`[tool.ruff]`, `[tool.pytest.ini_options]`, and similar); also scaffold a stub `requirements.txt` at the same location for the runtime install set; and ensure `.gitignore` excludes the local virtual-environment directory (`.venv/`). Keep the responsibility split strict: `pyproject.toml` carries distribution metadata and tooling configuration, `requirements.txt` carries the runtime dependency set; never duplicate runtime dependencies into `[project.dependencies]`. Never create or activate a virtual environment from the skill; virtual-environment creation is an explicit developer action and the spec only requires the repository layout to support one. When the repo already has a `requirements.txt` but tracks dev/test tooling alongside runtime, surface this as drift and ask whether to split into a separate `requirements-dev.txt`; never split silently. When the repo has a `pyproject.toml` whose `[project.dependencies]` shadows or replaces `requirements.txt`, surface this as drift; never silently rewrite either file.
- **Requirements file format**: when scaffolding `requirements.txt` or `requirements-dev.txt`, write only `#`-prefixed comment lines plus `name<specifier>` entries—one per line, every entry pinned with an explicit version specifier (`>=`, `==`, `~=`, etc.). Never emit `-r requirements.txt` (or `--requirement`) inside a scaffolded `requirements-dev.txt`; the Taskfile pattern installs both files independently, so the chain is forbidden by the spec. When auditing existing files, treat each of the following as drift and surface it for user decision before writing: a `-r` / `--requirement` directive in `requirements-dev.txt`, any non-comment, non-blank line lacking a version specifier, and a `requirements.txt` that contains only comments while `pyproject.toml` already declares real runtime dependencies in `[project.dependencies]`. A comment-only `requirements.txt` is an acceptable temporary placeholder when no runtime dependency has been published yet (for example, a pre-release SDK), but flag it so the user remembers to replace it once the first real dependency lands.
- **README badges**: insert CI status badges for workflows present under `.github/workflows/` near the top of `README.md`.

After every successful write, re-run the single affected audit check so the user sees the item flip to **pass**. Never batch silent writes—each change requires explicit approval.

#### 4. Re-audit

When the user has finished approving changes, re-run Operations 1 and 2 end-to-end and present a fresh grouped summary. Items still **missing**, **drift**, or with an uninstalled Probot app must be called out so the user knows what remains and why (for example, a deliberately deferred scaffold or a pending app install).

### Hard rules

- **Never** overwrite an existing file without explicit per-item confirmation. Merge into existing YAML or JSON configs rather than replacing them wholesale.
- **Never** manage repository settings through the GitHub UI or `gh repo edit`. `.github/settings.yml` is the source of truth, driven by the Probot Settings app.
- **Never** write a `.github/settings.yml` without an `_extends:` pointing at `nolte/gh-plumbing:.github/commons-settings.yml` (or the short form `gh-plumbing:.github/commons-settings.yml` inside the `nolte` org). Same applies to release-drafter, boring-cyborg, and stale.
- **Never** copy plugin-owned skills into `.claude/skills/`. Distribution is the plugin mechanism's job.
- **Never** automatically move source files out of the repository root. Report the drift and let the user decide.
- **Never** scaffold or rewrite content inside the `project/` planning tree (`project/roadmap.md`, `project/goals.md`, `project/sprints/`, `project/features/`, `project/release-artifacts/`, `project/mission.md`). The audit verifies the layout only; per-file authoring is delegated to the planning skills (`roadmap-init`, `sprint-plan`, `feature-decompose`, `mission-define`) per the matching specs.
- **Never** commit a real `.env`. When creating `.env.example`, simultaneously ensure `.env` is listed in `.gitignore`.
- **Never** attempt to install a GitHub App programmatically. Report the install status and link to the app's marketplace page so a human can approve the install.
- When `spec/project/project-structure/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
- When the Probot app installation check can't run because the token lacks scope, report that explicitly: **never** treat an API error as "app is installed."

### Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **Probot Settings App sync isn't atomic with `.github/settings.yml` edits.** A repository can carry `delete_branch_on_merge: true` in the file and the platform still leaves merged feature branches behind, because the Settings App pulls on its own webhook cadence. After a `settings.yml` edit, expect a manual catch-up on the first one or two merges and surface that to the user instead of treating the file's intent as the platform's actual state.
- **Token scope for the installation check is `read:user` (user-owned repos) or `admin:org` (org-owned).** A `gh api /user/installations` call returning HTTP 403 means the token lacks the scope, **not** that the apps aren't installed. Route the user at `https://github.com/<owner>/settings/installations` (user) or `https://github.com/organizations/<owner>/settings/installations` (org) for manual verification rather than reporting that apps are missing.
- **Renovate App installed differs from Renovate App active.** A repository can have the Renovate App granted access and still produce zero PRs and zero Dependency-Dashboard issues; the App's own runs are queued separately on Mend's side. When the install check passes but no Renovate activity is visible, point the user at `https://developer.mend.io/github/<owner>/<repo>` rather than re-checking the App permissions.
- **Renovate config file naming is `renovate.json5` by default in this portfolio**, but Renovate also reads `renovate.json` and `.renovaterc` and a few other variants. When auditing, check for the active variant first; when scaffolding for a new repo, default to `renovate.json5` per `spec/project/project-structure/`.
