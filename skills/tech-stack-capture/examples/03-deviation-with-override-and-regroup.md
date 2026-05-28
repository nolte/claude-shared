# Example 3 — Deviation: override the docs default and regroup Python

A Portfolio-Member that ships pure-markdown docs (no MkDocs build) and uses Python only for a CI helper script. Demonstrates the `overrides:` mechanism, a `additions:` replacement that doesn't shadow the inheritance, and a `regroup:` record on an inherited entry whose repo-specific purpose differs from the portfolio default.

## Input

- **User prompt** (German): "Wir haben kein MkDocs hier, nur plain Markdown. Außerdem ist Python in diesem Repo nur ein Build-Helper. Bitte den Tech-Stack aktualisieren."
- **Active repository**: `nolte/example-static-docs-repo`. Existing `project/portfolio.yml` has no `tech_stack:` key yet.
- **Repo signals present**:
  - `pyproject.toml` with a single `[project]` table; no `[tool.uv]`, no `[tool.ruff]`.
  - `.tool-versions` with one row: `python 3.12`
  - `Taskfile.yml`
  - `.github/workflows/lint.yml` running markdown linting via Vale.
  - `renovate.json5`
  - `.vale.ini`
  - **No `mkdocs.yml`.** No documentation generator.

## Expected skill behavior

1. **Preconditions** — pass; fresh capture path.
2. **Inherited set** — global active entries include `mkdocs` (kind `docs`, group `documentation`).
3. **Probe** — produces candidates: `python` (kind `language`, group *ask*, lifecycle *ask*, version `3.12`), `task`, `github-actions`, `renovate`, `vale`. **No `mkdocs` candidate** because there's no `mkdocs.yml`.
4. **Drop inherited matches** — `task`, `github-actions`, `renovate`, `vale` match inherited entries; all drop to inherited-confirmed. The remaining `additions` working set: `[python]`.
5. **Group/lifecycle proposal** — for `python`, the skill prompts (since `kind: language` is ask-the-maintainer for both group and lifecycle):
   > "Group for `python`? Options: `documentation` (only used for docs tooling), `quality` (used by linters/tests), `build-tooling` (used at build time), `plugin-platform` (Claude Code plugin runtime), `automation` (CI helper)."
   The operator picks `build-tooling`. Lifecycle prompt: operator picks `build`.
6. **Interactive confirmation, additions pass** — presents the full `python` entry; operator confirms role: "Python is used only by the CI helper that publishes the static markdown to GitHub Pages."
7. **Interactive confirmation, overrides pass** — the skill asks: "You mentioned MkDocs isn't used here. Want to add an `overrides:` record suppressing the inherited `mkdocs` entry?" Operator: yes. Skill drafts:

   ```yaml
   - name: mkdocs
     inherit: false
     rationale: "Static-only repo; documentation ships as plain markdown without a generator."
   ```

8. **Interactive confirmation, regroup pass** — the skill notices the inherited `vale` entry's portfolio default group is `documentation`, matching the consumer's use. No regroup needed for `vale`. But the skill asks: "The inherited `python` would conflict with the new addition; since the addition is repo-specific Python usage, the global has no `python` entry — no regroup needed." Skill skips the regroup pass for inherited entries the consumer hasn't reclassified.

   In a variation where the global stack did carry a `python` entry with `group: plugin-platform` (because the portfolio default is "Python for the plugin"), the skill would offer a regroup record:

   ```yaml
   - name: python
     group: build-tooling
     rationale: "in this repo python is only used for the markdown-publishing CI helper, not as the plugin runtime"
   ```

9. **Validate locally** — checks for shadow-without-override: the `additions` set has `python`, which would shadow an inherited `python` if one existed; in this scenario the global doesn't carry `python`, so no shadow conflict. Override rationale is non-empty. Validation passes.
10. **Write** — composes the block, writes, re-parses.

## Expected `tech_stack:` written

```yaml
tech_stack:
  additions:
    - name: python
      kind: language
      group: build-tooling
      role: Python is used only by the CI helper that publishes the static markdown to GitHub Pages.
      status: active
      lifecycle: build
      version: "3.12"
      source_of_truth: .tool-versions
  overrides:
    - name: mkdocs
      inherit: false
      rationale: "Static-only repo; documentation ships as plain markdown without a generator."
```

## Expected confirmation summary (German, matching user's prompt language)

> "`project/portfolio.yml` aktualisiert. `additions:` 1 (`python`), `overrides:` 1 (`mkdocs`), `regroup:` 0, inherited-confirmed: 4 (`task`, `github-actions`, `renovate`, `vale`). Nächster Schritt: PR via `pull-request-create`."

## What this example exercises

- `additions[]` entry with an ask-the-maintainer `group:` and `lifecycle:` per the discovery spec's MUST.
- `overrides[]` record with a non-empty `rationale` and the literal `inherit: false`.
- The reasoning path for when a regroup record is *not* needed even though the inherited entry exists.
- Version pre-population from `.tool-versions` per the SHOULD.
- User-language policy: skill responds in German throughout; YAML content stays English.
