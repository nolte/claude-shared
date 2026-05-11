# Example 03 — Renovate config present, Renovate App not installed

## Input prompt

> Audit this repo against the project-structure spec — Renovate hasn't opened a single PR even though I added `renovate.json5` weeks ago. What's wrong?

## Input files

The repo is `nolte/example-quiet-renovate`, owner type **User** (`gh api /users/nolte --jq '.type'` returns `User`). Working tree is clean.

Files **present** at the repository root:

- `README.md`, `CLAUDE.md`, `LICENSE`, `.gitignore`, `.pre-commit-config.yaml`
- `pyproject.toml`, `requirements.txt`, `Taskfile.yml`
- `mkdocs.yml`, `docs/index.md`, `docs/requirements.txt`
- `.claude/settings.json`
- `renovate.json5` (correctly extends `github>nolte/gh-plumbing//renovate-configs/common#v2.4.0`, no per-repository overrides)
- Full `.github/` layout: `settings.yml`, `release-drafter.yml`, `boring-cyborg.yml`, `stale.yml`, plus `workflows/ci.yml`, `release-drafter.yml`, `release-publish.yml`, `release-cd-refresh-master.yml`, `release-cd-deliver-docs.yml`, `automerge.yaml` — all conforming.

GitHub Apps state on `nolte/example-quiet-renovate` (cross-checked via `gh api /user/installations` and the per-installation repo lists with the user's `read:user` token):

- `settings` → installed, `repository_selection: all` → **installed and has access**.
- `boring-cyborg` → installed, `repository_selection: selected`, repo list includes `nolte/example-quiet-renovate` → **installed and has access**.
- `stale` → installed, `repository_selection: all` → **installed and has access**.
- `renovate` → **no entry returned by the installations API at all** → not installed.

There is no Renovate-Bot Dependency-Dashboard issue, no `app/renovate-bot` PR, and no Renovate onboarding PR in the repo's history. The user has been waiting weeks.

## Expected behaviour

1. **Preconditions pass**: confirm git tree, locate the spec, confirm clean working tree.
2. **Audit (operation 1, read-only)** reports every audited item as **pass** — top-level files, Claude integration, CI and automation (`renovate.json5` extends the portfolio preset correctly), GitHub repository configuration, Documentation, Tests, Source layout, Python development. Surface a short note that no audit findings need apply work.
3. **GitHub App installation check (operation 2)** runs for all four configs that landed at **pass** (`settings`, `boring-cyborg`, `stale`, `renovate`):
   - `settings` → **installed and has access**.
   - `boring-cyborg` → **installed and has access** (verified via the per-installation repo list because `repository_selection` is `selected`).
   - `stale` → **installed and has access**.
   - `renovate` → **not installed**. Cite the install URL `https://github.com/apps/renovate` from the table and explain that `renovate.json5` is inert until the App is installed on the repo. **Do not** retry the API, **do not** treat the absent installation entry as a token-scope error (the same call returned three other apps successfully, so the token clearly has scope), **do not** attempt to install the App programmatically.
4. **Surface the Mend dashboard pointer conditionally**: because Renovate is reported **not installed**, the Mend-dashboard guidance does **not** apply — the dashboard pointer is reserved for the case "App reported installed but no Renovate activity visible". Make the distinction explicit in the report so the user understands the two different failure modes:
   - "App not installed" → install via `https://github.com/apps/renovate`, grant access to `nolte/example-quiet-renovate`.
   - "App installed but inactive" (would be the next diagnostic step **after** install) → inspect run logs at `https://developer.mend.io/github/nolte/example-quiet-renovate`.
5. **Apply (operation 3)** has nothing to write — every audited item is **pass**. The only outstanding action is the human-approved Renovate App install, which is explicitly out of scope for the skill. **Refuses** to add Renovate-related configuration to compensate (no scaffolding of GitHub Actions Renovate runners, no edits to `renovate.json5` to "force" runs).
6. **Re-audit (operation 4)** prints a fresh grouped summary that still shows every config at **pass** and the `renovate` App at **not installed**, with the install URL and the conditional Mend-dashboard pointer for the post-install verification step. Final guidance to the user: install the App at the cited URL, wait for the Renovate onboarding PR (or a Dependency-Dashboard issue), and only then — if no activity surfaces within Renovate's documented schedule — escalate to the Mend dashboard.
