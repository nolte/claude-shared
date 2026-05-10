# Example 01 — Scaffold a fresh Python application repo

## Input prompt

> Bring this repo in line with the project-structure spec. It's a Python application I just initialised; I haven't added any of the standard portfolio scaffolding yet.

## Input files

The git tree is brand new. `git rev-parse --is-inside-work-tree` returns `true`, the working tree is clean, and `git remote get-url origin` returns `git@github.com:nolte/example-python-app.git`.

Files present at the repository root:

- `pyproject.toml` (Hatch-style, declares `[project]` with `name = "example-python-app"`, `version = "0.0.1"`, no `[tool.ruff]` block yet, no `[project.dependencies]`)
- `src/example_python_app/__init__.py` (empty)
- `src/example_python_app/cli.py` (≈40 lines, click-based entry point)
- `tests/test_cli.py` (one happy-path test)
- `LICENSE` (Apache-2.0)

Files **absent** at the repository root:

- `README.md`
- `CLAUDE.md`
- `.gitignore`
- `.pre-commit-config.yaml`
- `renovate.json5`
- `Taskfile.yml`
- `requirements.txt`
- `mkdocs.yml`, `docs/`
- `.claude/`
- `.github/` in any form (no `settings.yml`, no `release-drafter.yml`, no `boring-cyborg.yml`, no `stale.yml`, no `workflows/`)
- `spec/`, `project/`

The repo owner `nolte` is a GitHub user (not an org). The user's `gh` token carries `read:user`. No GitHub Apps from the portfolio table are installed on `nolte/example-python-app` yet.

## Expected behaviour

1. **Preconditions pass**: confirm git tree, locate the project-structure spec (target repo lacks `spec/`, fall back to the nolte-shared plugin copy), confirm clean working tree on every path the skill may touch.
2. **Audit (operation 1, read-only)** walks the spec's Acceptance Criteria and reports findings grouped by spec area. Every absent file is classified **missing**:
   - Top-level files: `README.md`, `CLAUDE.md`, `.gitignore`, `.pre-commit-config.yaml`, `Taskfile.yml`, `requirements.txt` → **missing**; `pyproject.toml`, `LICENSE` → **pass**.
   - Claude integration: `.claude/` directory → **missing**.
   - CI and automation: `renovate.json5` → **missing**.
   - GitHub repository configuration: `.github/settings.yml`, `.github/release-drafter.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml`, `.github/workflows/ci.yml`, `.github/workflows/release-drafter.yml`, `.github/workflows/release-publish.yml`, `.github/workflows/release-cd-refresh-master.yml`, `.github/workflows/automerge.yaml` → all **missing**. `.github/workflows/release-cd-deliver-docs.yml` is **not** flagged because no `mkdocs.yml` exists yet (the spec gates that workflow on MkDocs presence).
   - Documentation: `mkdocs.yml`, `docs/index.md`, `docs/requirements.txt` → **missing**.
   - Specifications: `spec/` → **missing** (offer to scaffold as `.gitkeep`-only, defer per-spec authoring to the `spec` skill).
   - Project planning artefacts: `project/` → **missing**; route the user to `roadmap-init` / `mission-define` rather than scaffolding any planning file here.
   - Tests: `tests/test_cli.py` → **pass**.
   - Source layout: `src/example_python_app/` → **pass** (not loose at root).
   - Python development: `pyproject.toml` declares no `[tool.ruff]` / `[tool.pytest.ini_options]` and no `requirements.txt` exists → **drift** for the missing tooling config, **missing** for the runtime dependency file.
3. **GitHub App installation check (operation 2)** is **skipped entirely** in this scenario because every Probot- and Renovate-backed config is itself **missing** — the spec gates the install check on the corresponding config being **pass**. Surface a one-line note explaining the skip and that the install check will run on re-audit once the configs land.
4. **Apply (operation 3)** walks the missing items one at a time, asking for explicit confirmation before each write. For each approved item:
   - `.gitignore`: scaffold with the standard Python set (`__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `build/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`) and an `.env` line per the hard rule.
   - `.pre-commit-config.yaml`: pin `ruff` and `ruff-format` at their current pinned versions plus the standard `pre-commit-hooks` entries (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`).
   - `requirements.txt`: scaffold as comment-only placeholder (the application has no published runtime dependency yet); flag the placeholder with a `# Replace with real entries once the first runtime dependency lands` line so the audit can re-detect it later.
   - `pyproject.toml` patch: add `[tool.ruff]` and `[tool.pytest.ini_options]` blocks; do **not** add `[project.dependencies]` (those live in `requirements.txt` per the spec's responsibility split).
   - `Taskfile.yml`: include `lint`, `test`, `docs` targets wired to `ruff check .`, `pytest`, and `mkdocs build` respectively.
   - `renovate.json5`: scaffold with `extends: ["github>nolte/gh-plumbing//renovate-configs/common#<tag>"]` where `<tag>` is fetched via `gh api repos/nolte/gh-plumbing/releases/latest --jq '.tag_name'`.
   - `mkdocs.yml` + `docs/index.md` + `docs/requirements.txt`: scaffold the MkDocs setup pointing at `docs/`; `docs/requirements.txt` lists `mkdocs>=1.6` and `mkdocs-material>=9.5` one entry per line with explicit specifiers.
   - `.claude/settings.json`: stub with empty `permissions` and `env` objects so the directory isn't empty.
   - `.github/settings.yml`: write with `_extends: nolte/gh-plumbing:.github/commons-settings.yml` plus `name`, `description`, `homepage`, `topics` pre-filled from `gh repo view --json name,description,homepageUrl,repositoryTopics` (asking the user to confirm/edit before write).
   - `.github/release-drafter.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml`: each carries only the `_extends:` pointer to `nolte/gh-plumbing:.github/commons-<name>.yml`.
   - `.github/workflows/ci.yml`: minimal pipeline that runs `task lint` and `task test` on `pull_request` and `push: branches: [develop]`.
   - `.github/workflows/release-drafter.yml`, `release-publish.yml`, `release-cd-refresh-master.yml`, `automerge.yaml`: scaffold each as a thin caller of the matching reusable workflow in `nolte/gh-plumbing`, pinned to `<tag>` (ask the user for the tag once and reuse). `release-publish.yml` carries `on: workflow_dispatch` only, no other triggers. **Do not** scaffold `release-cd-deliver-docs.yml` until `mkdocs.yml` is on disk; surface this dependency to the user and offer to revisit once the MkDocs scaffold lands (so on re-audit the file becomes eligible).
   - `README.md`: scaffold with project name, one-paragraph description, install/test/docs commands wired to `task` targets, and CI status badges for every workflow that just landed under `.github/workflows/`.
   - `CLAUDE.md`: scaffold with architecture hints (entry point at `src/example_python_app/cli.py`) and command entry points (`task lint`, `task test`, `task docs`).
   - `spec/.gitkeep`: scaffold the empty directory marker; route the user to the `spec` skill for actual spec authoring.
5. **Refuses** to scaffold anything under `project/` (route the user to `roadmap-init`, `mission-define`, `sprint-plan`, `feature-decompose` instead). **Refuses** to move `src/example_python_app/cli.py` or any source file silently. **Refuses** to commit a real `.env`. **Refuses** to scaffold a `.github/workflows/` packaging workflow without first asking how the artifact is produced (this repo has no `hacs.json` and isn't an HA integration, so no packaging workflow is scaffolded).
6. **Re-runs the affected audit check** after each successful write so the user sees that item flip to **pass**.
7. **Re-audit (operation 4)** runs operations 1 + 2 end-to-end and prints a fresh grouped summary. Now that `.github/settings.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml`, and `renovate.json5` are **pass**, the GitHub App installation check runs and reports all four apps as **not installed** on `nolte/example-python-app`. For each app, the summary cites the install URL from the table (`https://github.com/apps/settings`, `https://github.com/apps/boring-cyborg`, `https://github.com/apps/stale`, `https://github.com/apps/renovate`) and flags the configs as inert until the install lands. The skill **does not** attempt to install any app. `release-cd-deliver-docs.yml` is now flagged as **missing** (eligible after the MkDocs scaffold landed) for a follow-up apply pass.
