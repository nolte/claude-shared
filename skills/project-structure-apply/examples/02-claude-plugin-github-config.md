# Example 02 — Add the .github/ Probot config to a Claude plugin repo

## Input prompt

> This Claude-plugin repo is missing its `.github/` Probot setup — wire up `settings.yml`, `release-drafter.yml`, and the automerge workflow per the project-structure spec.

## Input files

The repo is `nolte/example-claude-plugin`, owner type **Organization** (`gh api /users/nolte --jq '.type'` returns `Organization`). Working tree is clean on every path the skill may touch. The user's `gh` token carries `admin:org`.

Files **present**:

- `README.md`, `CLAUDE.md`, `LICENSE`, `.gitignore`
- `Taskfile.yml` (with `lint`, `test`, `docs` targets)
- `renovate.json5` (already extends `github>nolte/gh-plumbing//renovate-configs/common#v2.4.0`)
- `mkdocs.yml`, `docs/index.md`, `docs/requirements.txt` (conforming)
- `.pre-commit-config.yaml`
- `.claude/settings.json` (stub with empty `permissions` and `env`)
- `plugin.json` (Claude plugin manifest, `name: example-claude-plugin`, `version: 0.7.2`)
- `skills/example-skill/SKILL.md` (one shipped skill)
- `agents/example-agent.md` (one shipped agent)
- `.github/workflows/ci.yml` (already calls `task lint` and `task test`)

Files **absent** under `.github/`:

- `.github/settings.yml`
- `.github/release-drafter.yml`
- `.github/boring-cyborg.yml`
- `.github/stale.yml`
- `.github/workflows/release-drafter.yml`
- `.github/workflows/release-publish.yml`
- `.github/workflows/release-cd-refresh-master.yml`
- `.github/workflows/release-cd-deliver-docs.yml` (eligible because `mkdocs.yml` exists)
- `.github/workflows/automerge.yaml`

GitHub Apps state on `nolte/example-claude-plugin` (cross-checked via `gh api /orgs/nolte/installations` and the per-installation repo lists): `settings` is installed at the org level with `repository_selection: all`, `boring-cyborg` is installed at the org level with `repository_selection: all`, `stale` is installed at the org level with `repository_selection: selected` and **does** include `nolte/example-claude-plugin`, `renovate` is installed at the org level with `repository_selection: all`.

## Expected behaviour

1. **Preconditions pass**: confirm git tree, locate the spec (use the in-repo `spec/project/project-structure/` if present, otherwise the nolte-shared plugin copy), confirm clean working tree on `.github/`.
2. **Audit (operation 1, read-only)** reports findings grouped by spec area:
   - Top-level files, Claude integration, CI and automation (`renovate.json5`), Documentation (`mkdocs.yml`), Tests, Source layout: all **pass**.
   - GitHub repository configuration: `.github/settings.yml`, `.github/release-drafter.yml`, `.github/boring-cyborg.yml`, `.github/stale.yml` → **missing**. `.github/workflows/ci.yml` → **pass**. `.github/workflows/release-drafter.yml`, `release-publish.yml`, `release-cd-refresh-master.yml`, `release-cd-deliver-docs.yml`, `automerge.yaml` → **missing**.
3. **GitHub App installation check (operation 2)** runs **only** for configs the audit classified as **pass** — `renovate` is the only app currently checked. Report Renovate as **installed and has access** (`repository_selection: all`). The other three Probot apps (`settings`, `boring-cyborg`, `stale`) are **deferred** with a one-line note that the check will run after their YAML files land in operation 3.
4. **Apply (operation 3)** walks each missing file one at a time, asking for explicit confirmation before each write:
   - `.github/settings.yml`: write with `_extends: nolte/gh-plumbing:.github/commons-settings.yml` plus only `name: example-claude-plugin`, `description`, `homepage`, and `topics` pre-filled from `gh repo view --json name,description,homepageUrl,repositoryTopics` and confirmed with the user before write. **Refuses** to write any other key (no `branches:`, no `labels:`, no `collaborators:`) — those live in the commons file.
   - `.github/release-drafter.yml`: `_extends: nolte/gh-plumbing:.github/commons-release-drafter.yml`, nothing else.
   - `.github/boring-cyborg.yml`: `_extends: nolte/gh-plumbing:.github/commons-boring-cyborg.yml`, nothing else.
   - `.github/stale.yml`: `_extends: nolte/gh-plumbing:.github/commons-stale.yml`, nothing else.
   - Asks the user once for the `nolte/gh-plumbing` release tag to pin reusable workflow callers to (fall back to `@develop` and flag the fallback). Then scaffolds:
     - `.github/workflows/release-drafter.yml` → `on: push: branches: [develop]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-drafter.yml@<tag>`, `permissions: contents: write, pull-requests: write`.
     - `.github/workflows/release-publish.yml` → `on: workflow_dispatch` only (no `push`, no `release`, no `schedule`), calls `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml@<tag>`, `permissions: contents: write`.
     - `.github/workflows/release-cd-refresh-master.yml` → `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-release-cd-refresh-master.yml@<tag>` with `target_branch: main`, `permissions: contents: write`.
     - `.github/workflows/release-cd-deliver-docs.yml` → `on: release: types: [published]`, calls `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml@<tag>` with `requirements: docs/requirements.txt`, `permissions: contents: write, id-token: write, pages: write`, and a `concurrency` group `pages` with `cancel-in-progress: true` (eligible because `mkdocs.yml` is on disk).
     - `.github/workflows/automerge.yaml` → standard `pull_request` / `pull_request_review` / `check_suite` triggers, calls `nolte/gh-plumbing/.github/workflows/reusable-automerge.yaml@<tag>`, `permissions: contents: write, pull-requests: write`.
   - **Refuses** to scaffold a packaging workflow for the plugin (no `hacs.json`, plugin distribution shape isn't covered by the spec's reusable-workflow set); reports the gap and asks the user how the plugin's distribution artifact is produced (in this case via the release-publish workflow itself, so no additional packaging is needed — record that decision and move on).
   - **Does not** touch `README.md`, `CLAUDE.md`, `Taskfile.yml`, `renovate.json5`, `mkdocs.yml`, `.pre-commit-config.yaml`, `.claude/settings.json`, `plugin.json`, `skills/`, `agents/`, or `.github/workflows/ci.yml` — all already **pass**. **Refuses** to copy `skills/example-skill/` into `.claude/skills/` (plugin-mechanism distribution).
5. **Re-runs the affected audit check** after each successful write; each item flips to **pass**.
6. **Re-audit (operation 4)** runs operations 1 + 2 end-to-end. The GitHub App installation check now runs for `settings`, `boring-cyborg`, and `stale` as well — all three report **installed and has access** (org-level installs with `repository_selection: all` for `settings` and `boring-cyborg`; `repository_selection: selected` with `nolte/example-claude-plugin` in the per-installation repo list for `stale`). Renovate stays **installed and has access**. Final summary lists every `.github/` finding as **pass**, plus a one-line note that Probot Settings App sync isn't atomic — the new `.github/settings.yml` may take one or two PR merges before the platform-side state catches up.
