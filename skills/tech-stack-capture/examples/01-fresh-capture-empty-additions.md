# Example 1 — Fresh capture, fully inherited stack

A typical first-time capture in a Portfolio-Member repository whose stack matches the portfolio defaults exactly. Demonstrates the legitimate `tech_stack: {}` outcome.

## Input

- **User prompt** (German): "Lass uns den Tech-Stack für dieses Repo erfassen."
- **Active repository**: `nolte/example-skill-pack` (a fresh Portfolio-Member; `project/portfolio.yml` already carries `capabilities:` but no `tech_stack:` key yet).
- **Repo signals present**:
  - `pyproject.toml` with `[tool.uv]` and `[tool.ruff.lint]`
  - `uv.lock`
  - `Taskfile.yml`
  - `.github/workflows/ci.yml`
  - `renovate.json5`
  - `mkdocs.yml`
  - `.vale.ini`
  - `.pre-commit-config.yaml`
  - `.markdownlint.json`
  - `.github/release-drafter.yml`
  - `.github/settings.yml`

## Expected skill behavior

1. **Preconditions** — confirms `project/portfolio.yml` parses, fetches `claude-shared:portfolio/tech-stack.yml` via `gh api`, confirms feature branch.
2. **Inherited set** — resolves the global active/experimental entries: `mkdocs`, `renovate`, `github-actions`, `task`, `vale`, `pre-commit`, `markdownlint`, `gh-plumbing`, `release-drafter`, `probot-settings`, `boring-cyborg`, `stale-bot`, `claude-code`, `claude-code-plugin`.
3. **Probe** — produces candidates: `uv`, `ruff`, `task`, `github-actions`, `renovate`, `mkdocs`, `vale`, `pre-commit`, `markdownlint`, `release-drafter`, `probot-settings`.
4. **Drop inherited matches** — every candidate has a matching inherited entry by `name` and `kind` (the repo uses the portfolio default exactly). All candidates move to the inherited-confirmed list; the `additions` working set is empty.
5. **Group/lifecycle proposal** — nothing to propose because the additions set is empty.
6. **Interactive confirmation** — the skill summarises:
   > "Eleven candidates from your signals all match the inherited global stack. Proposed result: `tech_stack: {}` (you inherit the full active set unmodified). Confirm? Any overrides or regroups to add?"
7. The operator confirms with no overrides and no regroups.
8. **Write** — composes `tech_stack: {}`, validates locally, writes `project/portfolio.yml` with the empty mapping in place, re-parses to confirm.

## Expected `tech_stack:` written

```yaml
tech_stack: {}
```

## Expected confirmation summary

> "`project/portfolio.yml` updated. `additions:` 0, `overrides:` 0, `regroup:` 0, inherited-confirmed: 11. Open the PR via `pull-request-create` when ready — the audit will treat this as a clean inherited stack."

## What this example exercises

- The MUST that `tech_stack: {}` is a legitimate result, written only after explicit confirmation.
- The drop-inherited-matches rule in step 4 of the Capture operation.
- The MUST NOT against re-declaring an inherited entry under `additions:`.
- The user-language policy: skill responds in German because the user prompted in German; YAML stays English.
